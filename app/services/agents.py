# app/services/agents.py
from typing import Dict, Any, List, Optional
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from app.utils.logger import get_logger, log_time
import re
import time
import uuid

# Set up logger
logger = get_logger("agents")

class BaseAgent:
    def __init__(self, groq_api_key: str, model_name: str = "llama3-8b-8192"):
        self.groq_api_key = groq_api_key
        self.model_name = model_name
        logger.info(f"BaseAgent initialized with model: {model_name}")
        
    def _create_chain(self, system_prompt: str, temperature: float = 0.7):
        model = ChatGroq(api_key=self.groq_api_key, model_name=self.model_name, temperature=temperature)
        return model, StrOutputParser()
    
    def _clean_output(self, text: str) -> str:
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    
    @log_time(logger)
    def process_query(self, query: str, conversation_history: Optional[List] = None) -> str:
        # Default implementation that uses the same logic as ConversationService
        
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[ID: {request_id}] Processing query with BaseAgent: '{query[:50]}...'")
        
        system_prompt = """
        Você é um assistente virtual para a cidade do Recife.

        SOBRE VOCÊ:
        - Seu nome é AssistenteRecife
        - Seu propósito é ajudar cidadãos a encontrar informações sobre a cidade
        - Você tem acesso a bancos de dados oficiais da cidade

        COMPORTAMENTO:
        - Seja claro, amigável e direto
        - Quando não souber responder, sugira que o usuário faça uma pergunta específica sobre dados de Recife
        - Explique que você pode consultar dados como estatísticas, serviços públicos, equipamentos urbanos, etc.
        - Não invente dados que não possui
        """
        
        messages = [("system", system_prompt)]
        
        conv_length = 0
        #for entry in conversation_history[-5:]:
        #    if "user" in entry:
        #        messages.append(("human", entry["user"]))
        #        conv_length += 1
        #    if "assistant" in entry:
        #        messages.append(("assistant", entry["assistant"]))
        
        logger.info(f"[ID: {request_id}] Using {conv_length} previous messages in conversation context")
        messages.append(("human", query))
        
        chat_template = ChatPromptTemplate.from_messages(messages)
        model, parser = self._create_chain(system_prompt)
        chain = chat_template | model | parser
        
        try:
            logger.info(f"[ID: {request_id}] Sending request to LLM")
            start_time = time.time()
            response = chain.invoke({})
            elapsed = time.time() - start_time
            logger.info(f"[ID: {request_id}] LLM response received in {elapsed:.2f}s")
            
            cleaned_response = self._clean_output(response)
            logger.info(f"[ID: {request_id}] Response processed successfully")
            return cleaned_response
        except Exception as e:
            logger.exception(f"[ID: {request_id}] Exception in process_query: {str(e)}")
            return "Desculpe, estou tendo dificuldades para processar sua mensagem. Como posso ajudá-lo com informações sobre o Recife?"

class CultureAgent(BaseAgent):
    def __init__(self, groq_api_key: str, model_name: str = "llama3-8b-8192"):
        super().__init__(groq_api_key, model_name)
        logger.info("CultureAgent initialized")
        
    @log_time(logger)
    def process_query(self, query: str, conversation_history: Optional[List] = None) -> str:
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[ID: {request_id}] Processing query with CultureAgent: '{query[:50]}...'")
        
        system_prompt = """
        Você é AnaCultura Agente Cultural do Recife, especializado em:
        - Eventos culturais e festivais da cidade
        - Patrimônio histórico e pontos turísticos
        - Equipamentos culturais (teatros, museus, bibliotecas)
        - Manifestações culturais populares (frevo, maracatu, etc.)
        
        Ao responder:
        - Dê prioridade a informações sobre eventos atuais e locais culturais
        - Destaque a importância histórica dos locais, quando relevante
        - Sugira roteiros culturais relacionados à pergunta
        - Mencione horários de funcionamento e valores se forem conhecidos
        
        Seja amigável, entusiasta e demonstre conhecimento profundo sobre a cultura recifense.
        """
        
        messages = [("system", system_prompt)]
        
        conv_length = 0
        if conversation_history:
            for entry in conversation_history[-5:]:
                if "user" in entry:
                    messages.append(("human", entry["user"]))
                    conv_length += 1
                if "assistant" in entry:
                    messages.append(("assistant", entry["assistant"]))
        
        logger.info(f"[ID: {request_id}] Using {conv_length} previous messages in conversation context")
        messages.append(("human", query))
        
        chat_template = ChatPromptTemplate.from_messages(messages)
        model, parser = self._create_chain(system_prompt)
        chain = chat_template | model | parser
        
        try:
            logger.info(f"[ID: {request_id}] Sending request to LLM (CultureAgent)")
            start_time = time.time()
            response = chain.invoke({})
            elapsed = time.time() - start_time
            logger.info(f"[ID: {request_id}] LLM response received in {elapsed:.2f}s")
            
            cleaned_response = self._clean_output(response)
            logger.info(f"[ID: {request_id}] Response processed successfully")
            return cleaned_response
        except Exception as e:
            logger.exception(f"[ID: {request_id}] Exception in CultureAgent: {str(e)}")
            return f"Desculpe, estou com dificuldades para acessar informações culturais. Pode reformular sua pergunta?"

class PublicServicesAgent(BaseAgent):
    def __init__(self, groq_api_key: str, model_name: str = "llama3-8b-8192"):
        super().__init__(groq_api_key, model_name)
        logger.info("PublicServicesAgent initialized")
        
    @log_time(logger)
    def process_query(self, query: str, conversation_history: Optional[List] = None) -> str:
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[ID: {request_id}] Processing query with PublicServicesAgent: '{query[:50]}...'")
        
        system_prompt = """
        Você é a AnaCultura, Agente de Serviços Públicos do Recife, especializado em:
        - Serviços municipais e como acessá-los
        - Programas sociais e critérios de elegibilidade
        - Procedimentos administrativos municipais
        - Atendimento ao cidadão e canais de comunicação
        
        Ao responder:
        - Forneça informações precisas sobre como acessar os serviços
        - Indique documentação necessária e prazos quando relevante
        - Mencione alternativas digitais para serviços presenciais
        - Oriente sobre direitos do cidadão relacionados aos serviços
        
        Seja claro, objetivo e demonstre conhecimento técnico sobre a administração municipal.
        """
        
        messages = [("system", system_prompt)]
        
        conv_length = 0
        if conversation_history:
            for entry in conversation_history[-5:]:
                if "user" in entry:
                    messages.append(("human", entry["user"]))
                    conv_length += 1
                if "assistant" in entry:
                    messages.append(("assistant", entry["assistant"]))
        
        logger.info(f"[ID: {request_id}] Using {conv_length} previous messages in conversation context")
        messages.append(("human", query))
        
        chat_template = ChatPromptTemplate.from_messages(messages)
        model, parser = self._create_chain(system_prompt)
        chain = chat_template | model | parser
        
        try:
            logger.info(f"[ID: {request_id}] Sending request to LLM (PublicServicesAgent)")
            start_time = time.time()
            response = chain.invoke({})
            elapsed = time.time() - start_time
            logger.info(f"[ID: {request_id}] LLM response received in {elapsed:.2f}s")
            
            cleaned_response = self._clean_output(response)
            logger.info(f"[ID: {request_id}] Response processed successfully")
            return cleaned_response
        except Exception as e:
            logger.exception(f"[ID: {request_id}] Exception in PublicServicesAgent: {str(e)}")
            return f"Desculpe, estou com dificuldades para acessar informações sobre serviços municipais. Pode reformular sua pergunta?"

class MobilityAgent(BaseAgent):
    def __init__(self, groq_api_key: str, model_name: str = "llama3-8b-8192"):
        super().__init__(groq_api_key, model_name)
        logger.info("MobilityAgent initialized")
        
    @log_time(logger)
    def process_query(self, query: str, conversation_history: Optional[List] = None) -> str:
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[ID: {request_id}] Processing query with MobilityAgent: '{query[:50]}...'")
        
        system_prompt = """
        Você é a AnaMobi, Agente de Mobilidade do Recife, especializado em:
        - Transporte público (ônibus, metrô, BRT)
        - Ciclovias e mobilidade ativa
        - Trânsito e condições das vias
        - Projetos de mobilidade urbana
        
        Ao responder:
        - Forneça informações atualizadas sobre linhas e horários
        - Sugira rotas otimizadas considerando tempo e conforto
        - Mencione alternativas de transporte quando relevante
        - Indique aplicativos e recursos úteis para mobilidade
        
        Seja pragmático, eficiente e demonstre conhecimento técnico sobre a mobilidade urbana.
        """
        
        messages = [("system", system_prompt)]
        
        conv_length = 0
        if conversation_history:
            for entry in conversation_history[-5:]:
                if "user" in entry:
                    messages.append(("human", entry["user"]))
                    conv_length += 1
                if "assistant" in entry:
                    messages.append(("assistant", entry["assistant"]))
        
        logger.info(f"[ID: {request_id}] Using {conv_length} previous messages in conversation context")
        messages.append(("human", query))
        
        chat_template = ChatPromptTemplate.from_messages(messages)
        model, parser = self._create_chain(system_prompt)
        chain = chat_template | model | parser
        
        try:
            logger.info(f"[ID: {request_id}] Sending request to LLM (MobilityAgent)")
            start_time = time.time()
            response = chain.invoke({})
            elapsed = time.time() - start_time
            logger.info(f"[ID: {request_id}] LLM response received in {elapsed:.2f}s")
            
            cleaned_response = self._clean_output(response)
            logger.info(f"[ID: {request_id}] Response processed successfully")
            return cleaned_response
        except Exception as e:
            logger.exception(f"[ID: {request_id}] Exception in MobilityAgent: {str(e)}")
            return f"Desculpe, estou com dificuldades para acessar informações sobre mobilidade. Pode reformular sua pergunta?"

class HealthAgent(BaseAgent):
    def __init__(self, groq_api_key: str, model_name: str = "llama3-8b-8192"):
        super().__init__(groq_api_key, model_name)
        logger.info("HealthAgent initialized")
        
    @log_time(logger)
    def process_query(self, query: str, conversation_history: Optional[List] = None) -> str:
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[ID: {request_id}] Processing query with HealthAgent: '{query[:50]}...'")
        
        system_prompt = """
        Você é AnaCuida, Agente de Saúde e Bem-estar do Recife, especializado em:
        - Unidades de saúde e serviços disponíveis
        - Academias da cidade e atividades físicas públicas
        - Dados epidemiológicos e campanhas de saúde
        - Programas de bem-estar e qualidade de vida
        
        Ao responder:
        - Forneça informações precisas sobre locais e horários de atendimento
        - Oriente sobre o acesso a serviços de saúde específicos
        - Mencione programas de prevenção relacionados à pergunta
        - Incentive hábitos saudáveis com recomendações práticas
        
        Seja atencioso, informativo e demonstre conhecimento técnico sobre saúde pública.
        """
        
        messages = [("system", system_prompt)]
        
        conv_length = 0
        if conversation_history:
            for entry in conversation_history[-5:]:
                if "user" in entry:
                    messages.append(("human", entry["user"]))
                    conv_length += 1
                if "assistant" in entry:
                    messages.append(("assistant", entry["assistant"]))
        
        logger.info(f"[ID: {request_id}] Using {conv_length} previous messages in conversation context")
        messages.append(("human", query))
        
        chat_template = ChatPromptTemplate.from_messages(messages)
        model, parser = self._create_chain(system_prompt)
        chain = chat_template | model | parser
        
        try:
            logger.info(f"[ID: {request_id}] Sending request to LLM (HealthAgent)")
            start_time = time.time()
            response = chain.invoke({})
            elapsed = time.time() - start_time
            logger.info(f"[ID: {request_id}] LLM response received in {elapsed:.2f}s")
            
            cleaned_response = self._clean_output(response)
            logger.info(f"[ID: {request_id}] Response processed successfully")
            return cleaned_response
        except Exception as e:
            logger.exception(f"[ID: {request_id}] Exception in HealthAgent: {str(e)}")
            return f"Desculpe, estou com dificuldades para acessar informações sobre saúde. Pode reformular sua pergunta?"

# Factory to create the appropriate agent based on domain
class AgentFactory:
    @staticmethod
    def create_agent(domain: str, groq_api_key: str, model_name: str = "llama3-8b-8192") -> BaseAgent:
        domain = domain.upper() if domain else "GERAL"
        logger.info(f"Creating agent for domain: {domain} with model: {model_name}")
        
        if domain == "CULTURA":
            logger.info("Creating CultureAgent")
            return CultureAgent(groq_api_key, model_name)
        elif domain == "SERVICOS":
            logger.info("Creating PublicServicesAgent")
            return PublicServicesAgent(groq_api_key, model_name)
        elif domain == "MOBILIDADE":
            logger.info("Creating MobilityAgent")
            return MobilityAgent(groq_api_key, model_name)
        elif domain == "SAUDE":
            logger.info("Creating HealthAgent")
            return HealthAgent(groq_api_key, model_name)
        else:
            logger.info("Domain not recognized, creating BaseAgent")
            # Return a default general agent that uses the existing conversation service
            return BaseAgent(groq_api_key, model_name)