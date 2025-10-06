from ..database.database import feedback_collection
from ..models.models import FeedbackIn, FeedbackOut

async def save_feedback_service(request: FeedbackIn) -> FeedbackOut:
    result = await feedback_collection.insert_one(request.dict())
    new_feedback = await feedback_collection.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to str here before returning
    new_feedback["_id"] = str(new_feedback["_id"])
    
    return FeedbackOut(**new_feedback)