import os
import time
import uuid
from fastapi import FastAPI, HTTPException, Depends, Request
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.services.database import DatabaseService
from app.services.query import QueryService
from app.services.llm import LLMService
from app.services.conversation import ConversationService
from app.services.agents import AgentFactory
from app.utils.logger import get_logger, log_time
import re

logger = get_logger("main")

load_dotenv()

app = FastAPI(
    title="Recife Data API",
    description="API for querying Recife city data using natural language",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database_service = DatabaseService(os.getenv('API_URL'))
llm_service = LLMService(os.getenv('GROQ_API_KEY'))
query_service = QueryService(os.getenv('API_URL'))
conversation_service = ConversationService(os.getenv('GROQ_API_KEY'))

conversation_history = {}

class QueryRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = Field(None, description="Unique ID for the conversation")
    tipo_agente: Optional[str] = Field("GERAL", description="Agent type: CULTURA, SERVICOS, MOBILIDADE, SAUDE, or GERAL")

class QueryResponse(BaseModel):
    answer: str
    dataset: Optional[str] = None
    resource: Optional[str] = None
    sql_query: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    is_data_query: bool = False
    agent_type: Optional[str] = "GERAL"

@app.get("/")
def read_root():
    return {"status": "active", "message": "Recife Data API is running"}

@app.get("/datasets")
def get_datasets():
    datasets = database_service.get_database_list()
    if not datasets:
        raise HTTPException(status_code=404, detail="No datasets found")
    return {"datasets": datasets}

@app.post("/query", response_model=QueryResponse)
@log_time(logger)
def process_query(request: QueryRequest):
    query = request.query
    request_id = str(uuid.uuid4())[:8]
    
    logger.info(f"[ID: {request_id}] Processing query request: '{query[:50]}...'")
    
    def clean_output(text):
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    
    logger.info(f"[ID: {request_id}] Step 1: Finding relevant dataset")
    start_time = time.time()
    dataset_result = llm_service.find_relevant_dataset(
        query, 
        database_service.get_database_list()
    )
    elapsed = time.time() - start_time
    logger.info(f"[ID: {request_id}] Dataset selection completed in {elapsed:.2f}s")
    
    if "error" in dataset_result:
        logger.error(f"[ID: {request_id}] Dataset selection error: {dataset_result['error']}")
        raise HTTPException(status_code=400, detail=dataset_result["error"])
    
    selected_dataset = dataset_result.get("selected_dataset")
    logger.info(f"[ID: {request_id}] Selected dataset: {selected_dataset}")
    
    logger.info(f"[ID: {request_id}] Step 2: Finding relevant resource")
    start_time = time.time()
    resource_result = llm_service.find_relevant_resource_id(
        query, 
        dataset_result, 
        lambda name: database_service.get_resource_list(name)
    )
    elapsed = time.time() - start_time
    logger.info(f"[ID: {request_id}] Resource selection completed in {elapsed:.2f}s")
    
    if "error" in resource_result:
        logger.error(f"[ID: {request_id}] Resource selection error: {resource_result['error']}")
        raise HTTPException(status_code=400, detail=resource_result["error"])
    
    resource_id = resource_result["resource_id"]
    resource_name = resource_result.get("resource_name", "Desconhecido")
    logger.info(f"[ID: {request_id}] Selected resource: {resource_name} (ID: {resource_id})")
    
    logger.info(f"[ID: {request_id}] Step 3: Fetching resource metadata")
    start_time = time.time()
    metadata = database_service.get_metadata_from_resource_id(resource_id)
    elapsed = time.time() - start_time
    field_count = len(metadata.get("resultados_campos", []))
    sample_count = len(metadata.get("resultados_exemplos", []))
    logger.info(f"[ID: {request_id}] Metadata fetched in {elapsed:.2f}s with {field_count} fields and {sample_count} samples")
    
    logger.info(f"[ID: {request_id}] Step 4: Generating SQL query")
    start_time = time.time()
    sql_query = llm_service.generate_sql_query(query, resource_id, metadata)
    elapsed = time.time() - start_time
    logger.info(f"[ID: {request_id}] SQL generation completed in {elapsed:.2f}s")
    logger.debug(f"[ID: {request_id}] Generated SQL: {sql_query}")
    
    logger.info(f"[ID: {request_id}] Step 5: Executing SQL query")
    start_time = time.time()
    data = query_service.execute_sql_on_resource_id(sql_query)
    elapsed = time.time() - start_time
    logger.info(f"[ID: {request_id}] Query execution completed in {elapsed:.2f}s with {len(data)} results")
    
    logger.info(f"[ID: {request_id}] Step 6: Generating natural language response")
    start_time = time.time()
    response = llm_service.generate_response(query, data)
    elapsed = time.time() - start_time
    logger.info(f"[ID: {request_id}] Response generation completed in {elapsed:.2f}s")
    
    response = clean_output(response)
    logger.info(f"[ID: {request_id}] Query processing completed successfully")
    
    return QueryResponse(
        answer=response,
        dataset=selected_dataset,
        resource=resource_name,
        sql_query=sql_query,
        data=data[:10]
    )

@app.post("/message", response_model=ChatResponse)
def process_message(request: ChatRequest):
    message = request.message
    conversation_id = request.conversation_id or f"conv_{len(conversation_history) + 1}"
    agent_type = request.tipo_agente.upper() if request.tipo_agente else "GERAL"
    request_id = str(uuid.uuid4())[:8]
    
    logger.info(f"[ID: {request_id}] Processing message request: '{message[:50]}...' with agent: {agent_type}")
    
    # Initialize or retrieve conversation history
    # if conversation_id not in conversation_history:
    #    logger.info(f"[ID: {request_id}] Creating new conversation with ID: {conversation_id}")
    #    conversation_history[conversation_id] = []
    #else:
    #    logger.info(f"[ID: {request_id}] Appending to existing conversation ID: {conversation_id} with {len(conversation_history[conversation_id])} messages")
    
    # conversation_history[conversation_id].append({"user": message})
    
    is_data_query = False
    if agent_type == "GERAL":
        logger.info(f"[ID: {request_id}] Classifying message for GERAL agent")
        start_time = time.time()
        classification = conversation_service.classify_message(message)
        elapsed = time.time() - start_time
        
        is_data_query = classification.get("is_query", False)
        logger.info(f"[ID: {request_id}] Message classified in {elapsed:.2f}s as data query: {is_data_query}")
    
    logger.info(f"[ID: {request_id}] Creating agent for type: {agent_type}")
    agent = AgentFactory.create_agent(
        domain=agent_type,
        groq_api_key=os.getenv('GROQ_API_KEY'),
        model_name=os.getenv('MODEL_CHAT_NAME', "llama3-8b-8192")
    )
    
    if is_data_query:
        logger.info(f"[ID: {request_id}] Processing as data query")
        try:
            query_request = QueryRequest(query=message)
            start_time = time.time()
            query_response = process_query(query_request)
            elapsed = time.time() - start_time
            
            answer = query_response.answer
            logger.info(f"[ID: {request_id}] Data query processed successfully in {elapsed:.2f}s")
            
            # conversation_history[conversation_id].append({"assistant": answer})
            
            return ChatResponse(
                answer=answer,
                conversation_id=conversation_id,
                is_data_query=True,
                agent_type=agent_type
            )
        except Exception as e:
            logger.exception(f"[ID: {request_id}] Data query processing failed: {str(e)}")
            logger.info(f"[ID: {request_id}] Falling back to agent processing")
            pass
    
    logger.info(f"[ID: {request_id}] Processing with {agent_type} agent")
    try:
        start_time = time.time()
        answer = agent.process_query(message, conversation_history)
        elapsed = time.time() - start_time
        
        logger.info(f"[ID: {request_id}] Agent processing completed in {elapsed:.2f}s")
        # conversation_history[conversation_id].append({"assistant": answer})
        
        return ChatResponse(
            answer=answer,
            conversation_id=conversation_id,
            is_data_query=False,
            agent_type=agent_type
        )
    except Exception as e:
        logger.exception(f"[ID: {request_id}] Agent processing failed: {str(e)}")
        logger.info(f"[ID: {request_id}] Falling back to general conversation handler")
        
        start_time = time.time()
        answer = conversation_service.handle_conversation(
            message, 
            conversation_history
        )
        elapsed = time.time() - start_time
        
        logger.info(f"[ID: {request_id}] Fallback processing completed in {elapsed:.2f}s")
        # conversation_history[conversation_id].append({"assistant": answer})
        
        return ChatResponse(
            answer=answer,
            conversation_id=conversation_id,
            is_data_query=False,
            agent_type="GERAL"
        )