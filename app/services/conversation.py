from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
import re

class ConversationService:
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.model_name = "llama3-8b-8192"
    
    def classify_message(self, message: str) -> Dict[str, Any]:
        
        classifier_template = ChatPromptTemplate.from_messages([
            ("system", """
            Você é um classificador de mensagens que determina se um texto é:
            1. Uma pergunta sobre dados de Recife (QUERY)
            2. Uma mensagem conversacional (CHAT)
            
            REGRAS:
            - Classifique como QUERY se a mensagem contém perguntas sobre dados, estatísticas, informações factuais sobre Recife
            - Classifique como CHAT se a mensagem é saudação, conversa casual, pergunta sobre o sistema, ou não relacionada a dados de Recife
            
            Responda apenas com o formato:
            CLASSIFICAÇÃO: [QUERY ou CHAT]
            CONFIANÇA: [0-100]
            """),
            ("human", "{message}")
        ])
        
        model = ChatGroq(api_key=self.groq_api_key, model_name=self.model_name, temperature=0)
        chain = classifier_template | model | StrOutputParser()
        
        try:
            result = chain.invoke({"message": message})
            
            classification = "CHAT"
            confidence = 50
            
            for line in result.split("\n"):
                if "CLASSIFICAÇÃO:" in line:
                    classification = line.split(":", 1)[1].strip()
                elif "CONFIANÇA:" in line:
                    confidence_str = line.split(":", 1)[1].strip()
                    try:
                        confidence = int(confidence_str)
                    except ValueError:
                        pass
            
            return {
                "type": classification,
                "confidence": confidence,
                "is_query": classification == "QUERY" and confidence > 60
            }
        except Exception as e:
            print(f"Classification error: {str(e)}")
            return {"type": "CHAT", "confidence": 50, "is_query": False}
    
    def handle_conversation(self, message: str, conversation_history: Optional[list] = None) -> str:
        
        if conversation_history is None:
            conversation_history = []
        
        system_prompt = """
        Você é uma assistente virtual para a cidade do Recife.

        SOBRE VOCÊ:
        - Seu nome é Ana
        - Seu propósito é ajudar cidadãos a encontrar informações sobre a cidade
        - Você tem acesso a bancos de dados oficiais da cidade

        COMPORTAMENTO:
        - Seja clara, amigável e direta
        - Quando não souber responder, sugira que o usuário faça uma pergunta específica sobre dados de Recife
        - Explique que você pode consultar dados como estatísticas, serviços públicos, equipamentos urbanos, etc.
        - Não invente dados que não possui
        
        IMPORTANTE: Remova qualquer texto entre <think> e </think> da sua resposta final.
        """
        
        messages = [("system", system_prompt)]
        
        #for entry in conversation_history[-5:]:
        #    if "user" in entry:
        #        messages.append(("human", entry["user"]))
        #    if "assistant" in entry:
        #        messages.append(("assistant", entry["assistant"]))
        
        messages.append(("human", message))
        
        chat_template = ChatPromptTemplate.from_messages(messages)
        
        model = ChatGroq(api_key=self.groq_api_key, model_name=self.model_name, temperature=0.7)
        chain = chat_template | model | StrOutputParser()
        
        try:
            response = chain.invoke({})
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
            return response
        except Exception as e:
            print(f"Conversation error: {str(e)}")
            return "Desculpe, estou tendo dificuldades para processar sua mensagem. Como posso ajudá-lo com informações sobre o Recife?"