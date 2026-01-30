import os
from pymongo import MongoClient
from pymongo.database import Database
import logging

DEFAULT_MONGO_URI = "mongodb://localhost:27017/agriledger_db"
_client = None


def get_db_client():
    """Get or create a MongoDB client."""
    global _client
    if _client is None:
        mongo_uri = os.getenv("MONGODB_URI", DEFAULT_MONGO_URI)
        try:
            _client = MongoClient(mongo_uri)
            _client.admin.command("ping")
            logging.info("Successfully connected to MongoDB.")
        except Exception as e:
            logging.exception(f"Failed to connect to MongoDB: {e}")
            return _client
    return _client


def get_db() -> Database:
    """Get the application database."""
    client = get_db_client()
    if client:
        return client.get_database("agriledger")
    raise ConnectionError("Database client is not available.")