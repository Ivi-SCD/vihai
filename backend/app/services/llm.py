import json
from typing import List, Dict, Any, Callable
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from app.utils.logger import get_logger, log_time
import time

# Set up logger
logger = get_logger("llm")

class LLMService:
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.model_name = "deepseek-r1-distill-llama-70b"
        logger.info(f"LLMService initialized with model: {self.model_name}")
    
    @log_time(logger)
    def find_relevant_dataset(self, query: str, dataset_list: List[str]) -> Dict[str, Any]:
        if not dataset_list:
            logger.error("Failed to get datasets list")
            return {"error": "Falha ao obter datasets"}
        
        logger.info(f"Finding relevant dataset for query: '{query[:50]}...' among {len(dataset_list)} datasets")
        
        dataset_selection_template = ChatPromptTemplate.from_messages([
            ("system", """
            Você é um especialista em dados do Recife que analisa datasets disponíveis.
            
            INSTRUÇÕES IMPORTANTES:
            1. Identifique EXATAMENTE UM dataset que melhor responda à pergunta do usuário
            2. Escolha APENAS O NOME EXATO da lista de datasets fornecida
            3. NÃO invente nomes de datasets
            4. Responda em formato único e preciso
            5. VERIFIQUE SE O SEU DATASET ESTÁ DISPONÍVEL NA LISTA
            
            Dataset recomendado: [nome_exato_do_dataset]
            """),
            ("human", "Pergunta: {query}\n\nDatasets disponíveis:\n{datasets}")
        ])
        
        model = ChatGroq(api_key=self.groq_api_key, model_name=self.model_name, temperature=0)
        chain = dataset_selection_template | model | StrOutputParser()
        
        try:
            logger.info("Sending dataset selection request to LLM")
            start_time = time.time()
            result = chain.invoke({
                "query": query, 
                "datasets": json.dumps(dataset_list[:100], ensure_ascii=False)
            })
            elapsed = time.time() - start_time
            logger.info(f"LLM dataset selection completed in {elapsed:.2f}s")
            
            logger.debug(f"LLM dataset selection raw result: {result}")
            
            selected_dataset = None
            for line in result.split("\n"):
                if "Dataset recomendado:" in line:
                    selected_dataset = line.split(":", 1)[1].strip().replace('"', '') 
                    break
            
            if selected_dataset:
                logger.info(f"Selected dataset: {selected_dataset}")
                return {"selected_dataset": selected_dataset}
            else:
                logger.error("Invalid response format from LLM for dataset selection")
                return {"error": "Formato de resposta inválido"}
        except Exception as e:
            logger.exception(f"Exception finding dataset: {str(e)}")
            return {"error": f"Erro: {str(e)}"}
    
    @log_time(logger)
    def find_relevant_resource_id(self, query: str, dataset_result: Dict[str, Any], 
                                get_resource_list_fn: Callable) -> Dict[str, Any]:
        if "error" in dataset_result or not dataset_result.get("selected_dataset"):
            logger.error(f"Invalid dataset result: {dataset_result}")
            return {"error": "Dataset inválido ou não encontrado"}
        
        dataset_name = dataset_result["selected_dataset"]
        logger.info(f"Finding relevant resource ID for dataset: {dataset_name}")
        
        resource_info = get_resource_list_fn(dataset_name)
        
        if not resource_info:
            logger.error(f"No resources found for dataset: {dataset_name}")
            return {"error": f"Não foi possível obter recursos para {dataset_name}"}
        
        # Extract metadata from resources
        metadata = {}
        if resource_info and resource_info.get('state') == 'active':
            for i, resource in enumerate(resource_info.get('resources', [])):
                metadata[f'resource_{i}'] = {
                    'resource_id': resource.get('id', ''),
                    'formato_dataset': resource.get('format', ''),
                    'nome_dataset': resource.get('name', ''),
                    'descricao_dataset': resource.get('description', ''),
                    'tamanho_dataset': resource.get('size', '')
                }
            
            logger.info(f"Extracted metadata for {len(metadata)} resources")
        
        if not metadata:
            logger.error("Dataset inactive or no resources found")
            return {"error": "Dataset inativo ou sem recursos"}
        
        # If there's only one resource, return it directly
        if len(metadata) == 1:
            resource_id = metadata["resource_0"]["resource_id"]
            resource_name = metadata["resource_0"]["nome_dataset"]
            logger.info(f"Only one resource found, using resource ID: {resource_id}")
            return {
                "resource_id": resource_id,
                "resource_name": resource_name
            }
        
        logger.info(f"Multiple resources found ({len(metadata)}), selecting most relevant")
        
        resource_selection_template = ChatPromptTemplate.from_messages([
            ("system", "Identifique o índice do recurso mais relevante para a pergunta. Responda apenas:\nResource index: [número do índice]"),
            ("human", "Pergunta: {query}\n\nRecursos disponíveis:\n{resources}")
        ])
        
        model = ChatGroq(api_key=self.groq_api_key, model_name=self.model_name, temperature=0.2)
        chain = resource_selection_template | model | StrOutputParser()
        
        try:
            logger.info("Sending resource selection request to LLM")
            start_time = time.time()
            result = chain.invoke({"query": query, "resources": json.dumps(metadata, ensure_ascii=False)})
            elapsed = time.time() - start_time
            logger.info(f"LLM resource selection completed in {elapsed:.2f}s")
            
            logger.debug(f"LLM resource selection raw result: {result}")
            
            selected_index = None
            for line in result.split("\n"):
                if "Resource index:" in line:
                    index = line.split(":", 1)[1].strip()
                    resource_key = f"resource_{index.strip()}"
                    if resource_key in metadata:
                        resource_id = metadata[resource_key]["resource_id"]
                        resource_name = metadata[resource_key]["nome_dataset"]
                        logger.info(f"Selected resource: {resource_key} (ID: {resource_id})")
                        return {
                            "resource_id": resource_id,
                            "resource_name": resource_name
                        }
            
            # Fallback to first resource
            logger.warning("Could not parse resource index, falling back to first resource")
            return {
                "resource_id": metadata["resource_0"]["resource_id"],
                "resource_name": metadata["resource_0"]["nome_dataset"]
            }
        except Exception as e:
            logger.exception(f"Exception selecting resource: {str(e)}")
            logger.warning("Falling back to first resource after exception")
            return {
                "resource_id": metadata["resource_0"]["resource_id"],
                "resource_name": metadata["resource_0"]["nome_dataset"]
            }
    
    @log_time(logger)
    def generate_sql_query(self, query: str, resource_id: str, metadata: Dict[str, Any]) -> str:
        field_names = [f.get("id", "") for f in metadata.get("resultados_campos", [])]
        
        logger.info(f"Generating SQL query for resource ID: {resource_id}")
        logger.debug(f"Available fields: {field_names}")
        
        if not field_names:
            logger.warning("No fields found, using fallback query")
            fallback_query = f'SELECT * FROM "{resource_id}" LIMIT 100'
            return fallback_query
        
        sql_generation_template = ChatPromptTemplate.from_messages([
            ("system", """
            Você é um especialista em SQL. Gere uma consulta SQL válida seguindo essas regras:
            
            1. SEMPRE comece com SELECT
            2. SEMPRE use aspas duplas para nomes de tabelas e campos
            3. SEMPRE inclua o resource_id fornecido como FROM "resource_id"
            4. SEMPRE especifique campos exatos
            5. SEMPRE termine com LIMIT 100
            6. SUA RESPOSTA DEVE SER APENAS A CONSULTA SQL, NADA MAIS
            """),
            ("human", """
            Pergunta: {query}
            Resource ID: {resource_id}
            Campos disponíveis: {fields}
            Exemplos de dados: {examples}
            
            Gere APENAS a consulta SQL:
            """)
        ])
        
        model = ChatGroq(api_key=self.groq_api_key, model_name=self.model_name, temperature=0)
        chain = sql_generation_template | model | StrOutputParser()
        
        try:
            logger.info("Sending SQL generation request to LLM")
            start_time = time.time()
            sql_query = chain.invoke({
                "query": query,
                "resource_id": resource_id,
                "fields": json.dumps(field_names),
                "examples": json.dumps(metadata.get("resultados_exemplos", []), ensure_ascii=False)
            }).strip()
            elapsed = time.time() - start_time
            logger.info(f"LLM SQL generation completed in {elapsed:.2f}s")
            
            logger.debug(f"Generated SQL query: {sql_query}")
            
            if not sql_query.upper().startswith("SELECT"):
                logger.warning("Invalid SQL generated, using fallback")
                fields_str = ', '.join([f'"{field}"' for field in field_names[:10]]) 
                sql_query = f'SELECT {fields_str} FROM "{resource_id}" LIMIT 100'
            
            if f'FROM "{resource_id}"' not in sql_query:
                logger.warning("Missing resource_id in FROM clause, fixing query")
                sql_query = sql_query.replace('FROM ', f'FROM "{resource_id}" ')
            
            if "LIMIT" not in sql_query.upper():
                logger.warning("Missing LIMIT clause, adding LIMIT 100")
                sql_query += " LIMIT 100"

            # Fix double resource_id
            if f'FROM "{resource_id}" "resource_id"' in sql_query:
                logger.warning("Double resource_id in FROM clause, fixing query")
                sql_query = sql_query.replace(f'FROM "{resource_id}" "resource_id"', f'FROM "{resource_id}"')
            
            return sql_query
        except Exception as e:
            logger.exception(f"Exception in SQL generation: {str(e)}")
            logger.warning("Using fallback SQL query after exception")
            fields_str = ', '.join([f'"{field}"' for field in field_names[:10]])
            return f'SELECT {fields_str} FROM "{resource_id}" LIMIT 100'
    
    @log_time(logger)
    def generate_response(self, query: str, data: List[Dict[str, Any]]) -> str:
        logger.info(f"Generating response for query with {len(data)} data points")
        
        if not data:
            logger.warning("No data available for response generation")
            return "Não foi possível encontrar dados relevantes para responder à sua pergunta."
        
        response_template = ChatPromptTemplate.from_messages([
            ("system", """
            Você é um assistente oficial do Recife que responde perguntas com dados oficiais.
            
            INSTRUÇÕES:
            1. Responda diretamente à pergunta usando apenas os dados fornecidos
            2. Destaque informações mais relevantes dos dados
            3. Use linguagem clara e natural, como um funcionário municipal falaria
            4. Inclua números específicos quando relevantes
            5. Se os dados forem insuficientes, informe isso claramente
            """),
            ("human", "Pergunta: {query}\n\nDados obtidos: {data}")
        ])
        
        model = ChatGroq(api_key=self.groq_api_key, model_name=self.model_name, temperature=0.6)
        chain = response_template | model | StrOutputParser()
        
        try:
            logger.info("Sending response generation request to LLM")
            start_time = time.time()
            response = chain.invoke({
                "query": query,
                "data": json.dumps(data[:20], ensure_ascii=False)
            })
            elapsed = time.time() - start_time
            logger.info(f"LLM response generation completed in {elapsed:.2f}s")
            
            # Clean response
            response = self._clean_response(response)
            
            return response
        except Exception as e:
            logger.exception(f"Exception generating response: {str(e)}")
            return f"Com base nos dados obtidos: {json.dumps(data[:5], indent=2, ensure_ascii=False)}"
    
    def _clean_response(self, text: str) -> str:
        import re
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)