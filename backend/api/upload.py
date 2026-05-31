from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config import settings
from utils.logger import get_logger
import os
import aiofiles

logger = get_logger(__name__)
router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/json",
    "text/x-markdown",
}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    content_type = file.content_type or ""
    if not any(ct in content_type for ct in ["pdf", "text", "json", "markdown"]):
        raise HTTPException(400, f"Unsupported file type: {content_type}. Allowed: PDF, TXT, MD, CSV, JSON")

    contents = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(400, f"File exceeds {settings.max_upload_size_mb}MB limit")

    safe_name = os.path.basename(file.filename)
    dest = os.path.join(settings.upload_dir, safe_name)

    async with aiofiles.open(dest, "wb") as f:
        await f.write(contents)

    logger.info(f"Uploaded: {safe_name} ({len(contents):,} bytes)")

   
    indexed = False
    if "pdf" in content_type:
        try:
            from rag.parser import parse_pdf
            from rag.vectorstore import index_document
            docs = parse_pdf(dest)
            index_document(docs, source=safe_name)
            indexed = True
            logger.info(f"RAG indexed {len(docs)} chunks from {safe_name}")
        except Exception as e:
            logger.warning(f"RAG indexing failed for {safe_name}: {e}")

    return {
        "filename": safe_name,
        "size_bytes": len(contents),
        "status": "uploaded",
        "rag_indexed": indexed,
    }


@router.get("/uploads")
def list_uploads():
    try:
        files = os.listdir(settings.upload_dir)
        return {"files": [f for f in files if not f.startswith(".")]}
    except Exception:
        return {"files": []}
