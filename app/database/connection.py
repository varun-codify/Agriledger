"""MongoDB async connection (Motor).

Both the Reflex app layer and the FastAPI API share this single client.

Motor binds operations to the event loop that was active when the client was
first used. Reflex hot-reloads and restarts create a new loop while the old
client object can survive in module state — every subsequent query then fails
with "Event loop is closed". We therefore track the owning loop and rebuild
the client whenever the loop changes or has been closed.
"""

import asyncio
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
_client_loop: asyncio.AbstractEventLoop | None = None
_indexes_ensured = False


def _current_loop() -> asyncio.AbstractEventLoop | None:
    """Return the running loop, or None outside of async context."""
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return None


def _close_client_quietly(client: AsyncIOMotorClient | None) -> None:
    if client is None:
        return
    try:
        client.close()
    except Exception:
        pass


def reset_db_client() -> None:
    """Drop the shared client so the next call rebuilds it on the current loop."""
    global _client, _client_loop, _indexes_ensured
    _close_client_quietly(_client)
    _client = None
    _client_loop = None
    # Allow indexes to be ensured again after a reconnect.
    _indexes_ensured = False


def get_db_client() -> AsyncIOMotorClient | None:
    """Get or create the shared async MongoDB client for the *current* event loop."""
    global _client, _client_loop

    loop = _current_loop()

    if _client is not None:
        # Rebuild when the owning loop is gone/changed (hot-reload, restart).
        stale = False
        if _client_loop is not None and _client_loop.is_closed():
            stale = True
        elif loop is not None and _client_loop is not None and _client_loop is not loop:
            stale = True
        elif loop is not None and _client_loop is None:
            # Client was created outside async context; rebind to running loop.
            stale = True
        if stale:
            logger.info("MongoDB client event loop changed; rebuilding client.")
            reset_db_client()

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
            _client_loop = loop
            logging.info("Created async MongoDB client with connection pooling.")
            if loop is not None and loop.is_running():
                try:
                    loop.create_task(ensure_indexes_once())
                except Exception:
                    pass
        except Exception as e:
            logging.exception(f"Failed to create MongoDB client: {e}")
            _client = None
            _client_loop = None
    return _client


def is_stale_loop_error(exc: BaseException) -> bool:
    """True for errors caused by a Motor client bound to a closed/replaced loop."""
    msg = str(exc)
    return isinstance(exc, RuntimeError) and (
        "Event loop is closed" in msg
        or "Event loop is closed." in msg
        or "attached to a different loop" in msg
        or "is closed" in msg and "loop" in msg.lower()
    )


async def with_loop_retry(fn):
    """Run ``fn`` (a zero-arg coroutine factory), rebuilding the DB client once
    if the failure is a stale-event-loop error."""
    try:
        return await fn()
    except Exception as e:
        if is_stale_loop_error(e):
            logger.warning(f"Stale MongoDB event loop detected ({e}); resetting client and retrying.")
            reset_db_client()
            return await fn()
        raise


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
        await with_loop_retry(lambda: db.command("ping"))
        return True
    except Exception as e:
        logger.warning(f"Database ping failed: {e}")
        return False
