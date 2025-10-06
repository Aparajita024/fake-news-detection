import motor.motor_asyncio
from ..core.config.settings import settings # <-- Import the central settings object

# --- Database Client ---
# Use the validated and type-safe settings from the config file.
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DETAILS)
database = client[settings.DATABASE_NAME]

# --- Collections ---
feedback_collection = database.get_collection("feedback")

print(f"MongoDB {settings.MONGO_DETAILS} client initialized for database: '{settings.DATABASE_NAME}'")
async def add_feedback(feedback_data: dict):
    """Insert a feedback document and return its ID."""
    result = await feedback_collection.insert_one(feedback_data)
    return result.inserted_id