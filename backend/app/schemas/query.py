from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class QueryRequest(BaseModel):
    question: str
    metadata: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    answer: str
    confidence: Optional[float] = None
    contexts: Optional[List[Dict[str, Any]]] = None