from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.router import api_router
from app.core.config import settings
from app.observability.tracing import generate_trace_id
from app.observability.logger import JsonLogger
from app.auth.api_key import validate_api_key
from app.auth.rate_limit import rate_limit
import traceback

logger = JsonLogger("GenAI backend")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.middleware("http")
async def auth_middleware(request: Request, call_next):

    if request.method == "OPTIONS":
        return await call_next(request)
    
    # Skip auth for health checks and docs
    if request.url.path.startswith("/api/v1/query"):
        validate_api_key(request)
        rate_limit(request)

    return await call_next(request)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    trace_id = getattr(request.state, "trace_id", None)
    
    logger.log(
        "ERROR",
        "unhandled_exception",
        trace_id=trace_id,
        path=request.url.path,
        method=request.method,
        error=str(exc),
        traceback=traceback.format_exc()
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "trace_id": trace_id
        }
    )

app.include_router(api_router)