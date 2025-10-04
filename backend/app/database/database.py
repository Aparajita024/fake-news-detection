import motor.motor_asyncio
from pydantic import BaseModel

# --- Configuration ---
MONGO_DETAILS = "mongodb://localhost:27017"
DATABASE_NAME = "fakenews_detector"

# --- Database Client ---
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client[DATABASE_NAME]

# --- Collections ---
feedback_collection = database.get_collection("feedback")


# --- Helper for MongoDB ObjectID ---
# Pydantic doesn't natively handle MongoDB's ObjectId, so we can create a helper if needed.
# For this simple feedback model, we won't need to fetch by ID, but this is good practice.
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str) and not hasattr(v, 'to_bson'):
            raise TypeError('ObjectId required')
        return str(v)