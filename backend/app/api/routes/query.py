from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import StreamingResponse
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import QueryService
from app.observability.logger import JsonLogger
import asyncio
import json

router = APIRouter()
logger = JsonLogger("query-api")

query_service = QueryService()


@router.post("/query/stream")
async def query_stream(request: Request, payload: QueryRequest):
    """
    Process a query with real-time progress updates via Server-Sent Events.
    
    Returns a streaming response with progress events:
    - starting: Initialization
    - planning: Creating execution plan
    - retrieving: Retrieving document contexts
    - verifying: Generating answer
    - evaluating: Assessing answer quality
    - refining: Refining query (if needed)
    - complete: Final result
    """
    trace_id = getattr(request.state, "trace_id", None)
    
    try:
        # Validate request payload
        if not payload.question or not payload.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        question = payload.question.strip()
        
        # Create a queue for progress events
        progress_queue = asyncio.Queue()
        
        async def event_generator():
            try:
                # Start query processing in background
                query_task = asyncio.create_task(
                    process_query_with_progress(question, trace_id, progress_queue)
                )
                
                # Stream events from queue
                while True:
                    try:
                        # Get event from queue with timeout
                        event = await asyncio.wait_for(progress_queue.get(), timeout=1.0)
                        
                        if event.get("type") == "complete":
                            yield f"data: {json.dumps(event)}\n\n"
                            break
                        elif event.get("type") == "error":
                            yield f"data: {json.dumps(event)}\n\n"
                            break
                        else:
                            yield f"data: {json.dumps(event)}\n\n"
                    
                    except asyncio.TimeoutError:
                        # Check if query task is done
                        if query_task.done():
                            break
                        continue
                
                # Wait for query task to complete
                await query_task
                
            except Exception as e:
                logger.log("ERROR", "sse_stream_failed", trace_id=trace_id, error=str(e))
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        async def process_query_with_progress(question: str, trace_id: str | None, queue: asyncio.Queue):
            """Process query and emit progress events"""
            try:
                def progress_callback(stage: str, message: str, data: dict = None):
                    """Callback to emit progress events"""
                    event = {
                        "type": "progress",
                        "stage": stage,
                        "message": message
                    }
                    if data:
                        event.update(data)
                    asyncio.create_task(queue.put(event))
                
                # Process query
                result = await query_service.process_query(question, trace_id, progress_callback)
                
                # Emit final result
                await queue.put({
                    "type": "complete",
                    "result": result.dict() if hasattr(result, 'dict') else result
                })
                
            except Exception as e:
                await queue.put({
                    "type": "error",
                    "message": str(e)
                })
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.log(
            "ERROR",
            "stream_query_setup_failed",
            trace_id=trace_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup query streaming"
        )


@router.post("/query", response_model=QueryResponse)
async def query(request: Request, payload: QueryRequest):
    """
    Process a query using the multi-agent RAG pipeline.
    
    Flow:
    1. Planner agent determines which tools to use
    2. Executor agent retrieves relevant document contexts
    3. Verifier agent generates answer from contexts
    4. Evaluator agent assesses answer quality (with feedback loop)
    """
    trace_id = getattr(request.state, "trace_id", None)
    
    try:
        # Validate request payload
        if not payload.question or not payload.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        # Process query through service layer
        result = await query_service.process_query(
            payload.question.strip(),
            trace_id
        )
        
        return result
    
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, etc.)
        raise
    
    except asyncio.TimeoutError as e:
        logger.log(
            "ERROR",
            "query_timeout",
            trace_id=trace_id,
            question=payload.question[:100] if payload.question else None
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Query processing timed out. Please try a simpler question or try again later."
        )
    
    except ValueError as e:
        # Validation errors from service/agents
        logger.log(
            "WARN",
            "query_validation_error",
            trace_id=trace_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        # Unexpected errors
        logger.log(
            "ERROR",
            "query_processing_failed",
            trace_id=trace_id,
            question=payload.question[:100] if payload.question else None,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your query. Please try again later."
        )
