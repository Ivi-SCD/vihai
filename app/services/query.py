import requests
from typing import List, Dict, Any
from app.utils.logger import get_logger, log_time
import time

# Set up logger
logger = get_logger("query")

class QueryService:
    def __init__(self, api_url: str):
        self.api_url = api_url
        logger.info(f"QueryService initialized with API URL: {api_url}")
    
    @log_time(logger)
    def execute_sql_on_resource_id(self, sql: str) -> List[Dict[str, Any]]:
        try:
            query_id = f"q-{int(time.time())}"
            logger.info(f"Executing SQL query [ID: {query_id}]")
            logger.debug(f"SQL query [ID: {query_id}]: {sql}")
            
            start_time = time.time()
            response = requests.get(f'{self.api_url}/datastore_search_sql?sql={sql}')
            elapsed = time.time() - start_time
            
            logger.info(f"Query [ID: {query_id}] HTTP response in {elapsed:.2f}s with status: {response.status_code}")
            
            response_json = response.json()
            
            if 'result' in response_json and 'records' in response_json['result']:
                records = response_json['result']['records']
                logger.info(f"Query [ID: {query_id}] returned {len(records)} records")
                return records
            else:
                logger.error(f"API error response for query [ID: {query_id}]: {response_json}")
                return []
        except Exception as e:
            logger.exception(f"Error executing SQL: {str(e)}")
            return []