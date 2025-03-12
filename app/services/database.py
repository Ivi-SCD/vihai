import requests
from typing import List, Dict, Any, Optional

class DatabaseService:
    def __init__(self, api_url: str):
        self.api_url = api_url
        
    def get_database_list(self) -> List[str]:
        try:
            response = requests.get(f'{self.api_url}/package_list')
            if response.status_code == 200:
                return response.json().get('result', [])
            else:
                print(f"Error getting database list: {response.status_code}")
                return []
        except Exception as e:
            print(f"Exception getting database list: {str(e)}")
            return []
    
    def get_resource_list(self, nome: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(f'{self.api_url}/package_show?id={nome}')
            if response.status_code == 200:
                return response.json().get('result', None)
            else:
                print(f"Error getting resource list: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception getting resource list: {str(e)}")
            return None
    
    def get_metadata_from_resource_list(self, resource_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not resource_json or resource_json.get('state') != 'active':
            return None
        
        metadata = {}
        for i, resource in enumerate(resource_json.get('resources', [])):
            metadata[f'resource_{i}'] = {
                'resource_id': resource.get('id', ''),
                'formato_dataset': resource.get('format', ''),
                'nome_dataset': resource.get('name', ''),
                'descricao_dataset': resource.get('description', ''),
                'tamanho_dataset': resource.get('size', '')
            }
        return metadata
    
    def get_metadata_from_resource_id(self, resource_id: str) -> Dict[str, Any]:
        metadata = {'resultados_exemplos': [], 'resultados_campos': []}
        try:
            QUERY = f'SELECT * FROM "{resource_id}" LIMIT 3'
            response = requests.get(f'{self.api_url}/datastore_search_sql?sql={QUERY}')
            response_json = response.json()
            
            if 'result' in response_json:
                metadata['resultados_exemplos'] = response_json['result'].get('records', [])
                metadata['resultados_campos'] = response_json['result'].get('fields', [])
            else:
                print(f"Error getting metadata: {response_json}")
        except Exception as e:
            print(f"Exception getting metadata: {str(e)}")
        
        return metadata