from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read Mongo URI and DB name from environment variables
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Access the specific database
db: AsyncIOMotorDatabase = client[MONGO_DB_NAME]

# Dependency function to be used in FastAPI routes
def get_db() -> AsyncIOMotorDatabase:
    return db
