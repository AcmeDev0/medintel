"""
MedIntel AI — Device Classification API Routes.
AI-powered medical device classification helper.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_engine import rag_engine

router = APIRouter()


class ClassifyRequest(BaseModel):
    """Device classification request."""
    description: str = Field(
        ...,
        min_length=10,
        max_length=3000,
        description="Detailed description of the medical device"
    )


class ClassifyResponse(BaseModel):
    """Device classification response."""
    classification: str
    sources: list
    device_description: str


@router.post("/classify", response_model=ClassifyResponse)
async def classify_device(request: ClassifyRequest):
    """
    Classify a medical device based on its description according to
    NAFDAC's risk-based classification system (Class A-D).
    """
    try:
        result = await rag_engine.classify_device(request.description)
        return ClassifyResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error classifying device: {str(e)}"
        )
