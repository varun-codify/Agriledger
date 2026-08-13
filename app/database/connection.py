"""MongoDB async connection (Motor).

Both the Reflex app layer and the FastAPI API share this single client.
"""

import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import config

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None


def get_db_client() -> AsyncIOMotorClient | None:
    """Get or create the shared async MongoDB client."""
    global _client
    if _client is None:
        try:
            _client = AsyncIOMotorClient(config.mongodb.uri)
            logging.info("Created async MongoDB client.")
        except Exception as e:
            logging.exception(f"Failed to create MongoDB client: {e}")
            _client = None
    return _client


def get_db() -> AsyncIOMotorDatabase:
    """Get the application database from the shared client."""
    client = get_db_client()
    if client:
        return client[config.mongodb.database_name]
    raise ConnectionError("Database client is not available.")
