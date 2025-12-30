from pydantic import BaseModel
from typing import Optional, Dict, Any

class QueryRequest(BaseModel):
    question: str
    metadata: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    answer: str
    confidence: Optional[float] = None