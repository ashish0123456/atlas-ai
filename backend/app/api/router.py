from fastapi import APIRouter
from app.api.routes import health, documents, query 

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=['health'])
api_router.include_router(documents.router, tags=['documents'])
api_router.include_router(query.router, tags=['query'])