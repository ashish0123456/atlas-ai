from fastapi import FastAPI, Request
from app.api.router import api_router
from app.core.config import settings
from app.observability.tracing import generate_trace_id
from app.observability.logger import JsonLogger

logger = JsonLogger("GenAI backend")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    trace_id = generate_trace_id()
    request.state.trace_id = trace_id

    logger.log(
        "INFO",
        "incoming_request",
        trace_id=trace_id,
        path=request.url.path,
        method=request.method
    )

    response = await call_next(request)

    logger.log(
        "INFO",
        "request_completed",
        trace_id=trace_id,
        status_code=response.status_code
    )

    return response

app.include_router(api_router)