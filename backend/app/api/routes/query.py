from fastapi import APIRouter, Request
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import QueryService

router = APIRouter()

query_servive = QueryService()

@router.post("/query", response_model=QueryResponse)
async def query(request: Request, payload: QueryRequest):
    trace_id = request.state.trace_id
    return await query_servive.process_query(payload.question, trace_id)