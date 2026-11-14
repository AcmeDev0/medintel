"""
MedIntel AI — Document Management and Ingestion API.
Supports listing regulatory documents, uploading NAFDAC PDFs, and re-indexing the vector database.
"""

import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from app.config import settings
from app.services.rag_engine import rag_engine

router = APIRouter()


@router.get("/documents")
async def list_documents():
    """List all regulatory documents in the documents directory and vector store stats."""
    docs_path = Path(settings.DOCS_DIR)
    docs_path.mkdir(parents=True, exist_ok=True)

    files = []
    for f in sorted(docs_path.rglob("*")):
        if f.is_file() and f.suffix.lower() in {".pdf", ".txt", ".md"}:
            files.append({
                "name": f.name,
                "size_bytes": f.stat().st_size,
                "extension": f.suffix.lower(),
                "relative_path": str(f.relative_to(docs_path)),
            })

    stats = rag_engine.get_collection_stats()

    return {
        "documents_directory": str(docs_path),
        "total_documents": len(files),
        "documents": files,
        "vector_store_stats": stats,
    }


def _execute_ingestion():
    """Execute ingestion in background."""
    from app.ingest import run_ingestion
    try:
        run_ingestion()
    except Exception as e:
        print(f"Background ingestion error: {e}")


@router.post("/documents/upload")
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
):
    """
    Upload one or more NAFDAC regulatory documents (PDF, TXT, MD)
    and schedule automatic ingestion into ChromaDB.
    """
    docs_path = Path(settings.DOCS_DIR)
    docs_path.mkdir(parents=True, exist_ok=True)

    saved_files = []
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in {".pdf", ".txt", ".md"}:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{file.filename}'. Only PDF, TXT, and MD are allowed.",
            )

        target_file = docs_path / Path(file.filename).name
        with open(target_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append(file.filename)

    # Trigger background re-ingestion so user request doesn't timeout
    background_tasks.add_task(_execute_ingestion)

    return {
        "status": "success",
        "message": f"Successfully uploaded {len(saved_files)} document(s). Knowledge base indexing has been scheduled.",
        "uploaded_files": saved_files,
    }


@router.post("/documents/reindex")
async def reindex_documents(background_tasks: BackgroundTasks):
    """Trigger a manual re-index of all documents in the documents directory."""
    background_tasks.add_task(_execute_ingestion)
    return {
        "status": "success",
        "message": "Re-indexing started in background.",
    }
