from ..database.database import feedback_collection
from ..models.models import FeedbackIn

async def save_feedback_service(feedback: FeedbackIn):
    """Saves user feedback to the MongoDB database."""
    feedback_document = feedback.model_dump()
    new_feedback = await feedback_collection.insert_one(feedback_document)
    created_feedback = await feedback_collection.find_one({"_id": new_feedback.inserted_id})
    return created_feedback