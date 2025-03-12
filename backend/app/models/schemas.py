from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    """Request model for natural language queries"""
    query: str = Field(..., description="Natural language question about Recife data")

class QueryResponse(BaseModel):
    """Response model for query results"""
    answer: str = Field(..., description="Natural language answer to the query")
    dataset: Optional[str] = Field(None, description="Name of the dataset used")
    resource: Optional[str] = Field(None, description="Name of the resource used")
    sql_query: Optional[str] = Field(None, description="Generated SQL query")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Sample data from the results")

class ErrorResponse(BaseModel):
    """Model for error responses"""
    detail: str = Field(..., description="Error message")