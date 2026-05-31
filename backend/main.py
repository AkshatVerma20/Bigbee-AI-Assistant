from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.api.chat import router as chat_router
from backend.api.upload import router as upload_router
from backend.api.history import router as history_router
from utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    os.makedirs(os.path.dirname(settings.sqlite_db_path), exist_ok=True)
    logger.info(f"AI Assistant backend starting | env={settings.app_env}")
    yield
    logger.info("Backend shutting down")


app = FastAPI(
    title="AI Assistant API",
    description="Full-stack agentic AI assistant backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(history_router, prefix="/api", tags=["history"])


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}
