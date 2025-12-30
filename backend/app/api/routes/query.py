from fastapi import APIRouter
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import QueryService

router = APIRouter(prefix='/query')

query_servive = QueryService()

@router.post("/", response_model=QueryResponse)
def query_knowledge(payload: QueryRequest):
    result = query_servive.process_query(payload.question)
    return result