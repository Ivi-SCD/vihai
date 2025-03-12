import requests
from typing import List, Dict, Any, Optional
from app.utils.logger import get_logger, log_time

logger = get_logger("database")

class DatabaseService:
    def __init__(self, api_url: str):
        self.api_url = api_url
        logger.info(f"DatabaseService initialized with API URL: {api_url}")
        
    @log_time(logger)
    def get_database_list(self) -> List[str]:
        try:
            logger.info("Fetching database list")
            response = requests.get(f'{self.api_url}/package_list')
            if response.status_code == 200:
                result = response.json().get('result', [])
                logger.info(f"Retrieved {len(result)} databases")
                return result
            else:
                logger.error(f"Error getting database list: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.exception(f"Exception getting database list: {str(e)}")
            return []
    
    @log_time(logger)
    def get_resource_list(self, nome: str) -> Optional[Dict[str, Any]]:
        try:
            logger.info(f"Fetching resource list for: {nome}")
            response = requests.get(f'{self.api_url}/package_show?id={nome}')
            if response.status_code == 200:
                result = response.json().get('result', None)
                if result:
                    logger.info(f"Retrieved package with {len(result.get('resources', []))} resources")
                else:
                    logger.warning(f"No resources found for package: {nome}")
                return result
            else:
                logger.error(f"Error getting resource list: HTTP {response.status_code}")
                return None
        except Exception as e:
            logger.exception(f"Exception getting resource list: {str(e)}")
            return None
    
    def get_metadata_from_resource_list(self, resource_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not resource_json or resource_json.get('state') != 'active':
            logger.warning("Resource is inactive or empty")
            return None
        
        logger.info("Extracting metadata from resource list")
        metadata = {}
        for i, resource in enumerate(resource_json.get('resources', [])):
            metadata[f'resource_{i}'] = {
                'resource_id': resource.get('id', ''),
                'formato_dataset': resource.get('format', ''),
                'nome_dataset': resource.get('name', ''),
                'descricao_dataset': resource.get('description', ''),
                'tamanho_dataset': resource.get('size', '')
            }
        
        logger.info(f"Extracted metadata for {len(metadata)} resources")
        return metadata
    
    @log_time(logger)
    def get_metadata_from_resource_id(self, resource_id: str) -> Dict[str, Any]:
        metadata = {'resultados_exemplos': [], 'resultados_campos': []}
        try:
            logger.info(f"Fetching metadata for resource ID: {resource_id}")
            QUERY = f'SELECT * FROM "{resource_id}" LIMIT 3'
            logger.debug(f"SQL query: {QUERY}")
            
            response = requests.get(f'{self.api_url}/datastore_search_sql?sql={QUERY}')
            response_json = response.json()
            
            if 'result' in response_json:
                metadata['resultados_exemplos'] = response_json['result'].get('records', [])
                metadata['resultados_campos'] = response_json['result'].get('fields', [])
                logger.info(f"Retrieved {len(metadata['resultados_campos'])} fields and {len(metadata['resultados_exemplos'])} example records")
            else:
                logger.error(f"Error getting metadata: {response_json}")
        except Exception as e:
            logger.exception(f"Exception getting metadata: {str(e)}")
        
        return metadata