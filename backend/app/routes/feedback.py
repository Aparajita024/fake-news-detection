from fastapi import APIRouter, status
from ..models.models import FeedbackIn, FeedbackOut
from ..services.feedback_service import save_feedback_service

router = APIRouter()

@router.post("/feedback", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
async def receive_feedback(request: FeedbackIn):
    """Accepts a user rating (1-5) and stores it."""
    new_feedback = await save_feedback_service(request)
    return new_feedback