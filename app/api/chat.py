"""
MedIntel AI — Chat API Routes.
Handles regulatory Q&A chat interactions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_engine import rag_engine

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=3, max_length=2000, description="The regulatory question")


class ChatResponse(BaseModel):
    """Chat response model with sources."""
    answer: str
    sources: list
    query: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a regulatory question and get an AI-powered response
    grounded in NAFDAC, FDA, WHO, and other regulatory documents.
    """
    try:
        result = await rag_engine.query(request.message)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your question: {str(e)}"
        )


@router.get("/chat/stats")
async def chat_stats():
    """Get knowledge base statistics."""
    stats = rag_engine.get_collection_stats()
    return stats
