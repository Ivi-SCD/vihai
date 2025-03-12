import requests
from typing import List, Dict, Any

class QueryService:
    def __init__(self, api_url: str):
        self.api_url = api_url
    
    def execute_sql_on_resource_id(self, sql: str) -> List[Dict[str, Any]]:
        try:
            response = requests.get(f'{self.api_url}/datastore_search_sql?sql={sql}')
            response_json = response.json()
            
            if 'result' in response_json and 'records' in response_json['result']:
                return response_json['result']['records']
            else:
                print(f"API error response: {response_json}")
                return []
        except Exception as e:
            print(f"Error executing SQL: {str(e)}")
            return []
