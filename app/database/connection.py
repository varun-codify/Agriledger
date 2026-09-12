"""MongoDB async connection (Motor).

Both the Reflex app layer and the FastAPI API share this single client.
"""

import logging

try:
    import dns.resolver
    # Ensure MongoDB SRV DNS lookup uses ultra-fast public DNS (8.8.8.8, 1.1.1.1)
    # instead of timing out on local router/ISP DNS servers (saving 5.4+ seconds per connect)
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
    dns.resolver.default_resolver.timeout = 2.0
    dns.resolver.default_resolver.lifetime = 3.0
except Exception as _dns_e:
    logging.debug(f"DNS resolver configuration: {_dns_e}")

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import config

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_indexes_ensured = False



def get_db_client() -> AsyncIOMotorClient | None:
    """Get or create the shared async MongoDB client with production connection pooling."""
    global _client
    if _client is None:
        try:
            _client = AsyncIOMotorClient(
                config.mongodb.uri,
                maxPoolSize=50,
                minPoolSize=5,
                serverSelectionTimeoutMS=5000,
                maxIdleTimeMS=45000,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000,
            )
            logging.info("Created async MongoDB client with connection pooling.")
            # Trigger index creation automatically in background
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(ensure_indexes_once())
            except Exception:
                pass
        except Exception as e:
            logging.exception(f"Failed to create MongoDB client: {e}")
            _client = None
    return _client



def get_db() -> AsyncIOMotorDatabase:
    """Get the application database from the shared client."""
    client = get_db_client()
    if client is not None:
        return client[config.mongodb.database_name]
    raise ConnectionError("Database client is not available.")


async def ensure_indexes_once() -> bool:
    """Create database indexes exactly once per process (idempotent, lazy).

    Called from the API health check, which the deployment platform probes
    before routing real traffic — so indexes exist before the first user
    query, without requiring a separate migration step or blocking app import
    (import-time DB calls break frontend-only compilation).
    """
    global _indexes_ensured
    if _indexes_ensured:
        return True
    try:
        from app.database.indexes import create_indexes

        await create_indexes(get_db())
        _indexes_ensured = True
        return True
    except Exception as e:
        logger.warning(f"Index creation deferred (will retry): {e}")
        return False


async def ping_db() -> bool:
    """Ping MongoDB server to verify live connectivity."""
    try:
        client = get_db_client()
        if client is None:
            return False
        db = client[config.mongodb.database_name]
        await db.command("ping")
        return True
    except Exception as e:
        logger.warning(f"Database ping failed: {e}")
        return False
