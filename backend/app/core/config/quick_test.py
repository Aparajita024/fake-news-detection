from pymongo import MongoClient
from settings import settings

client = MongoClient(settings.MONGO_DETAILS)
print(client.list_database_names())