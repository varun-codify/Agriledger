"""ASGI middleware for the FastAPI API.

Rate limiting is implemented as pure ASGI middleware (not
``BaseHTTPMiddleware``) so it never wraps websocket/lifespan scopes — the API
is mounted inside the Reflex server and must leave the ``/_event`` websocket
untouched. Reflex infrastructure paths (ping, health, event websocket, upload)
are exempt from rate limiting so the UI itself can never be throttled.

Security headers are added to HTTP responses only.
"""

import time
from collections import defaultdict

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.config import config

# Reflex server endpoints that must never be throttled or counted:
# the event websocket drives every UI interaction, health/ping are
# probed by load balancers, and /_static serves the compiled frontend
# bundle (a first visit pulls dozens of chunked assets).
_REFLEX_INFRA_PREFIXES = (
    "/_event",
    "/ping",
    "/_health",
    "/_upload",
    "/_auth",
    "/_server",
    "/_static",
)


class RateLimitMiddleware:
    """In-memory fixed-window rate limiter (pure ASGI, HTTP-only).

    Args:
        app: The wrapped ASGI application.
        max_requests: Maximum requests allowed per window per client.
        window_seconds: Time window in seconds.
    """

    def __init__(self, app: ASGIApp, max_requests: int = 60, window_seconds: int = 60):
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup: float = time.time()

    def _get_client_ip(self, scope: Scope) -> str:
        # Only trust X-Forwarded-For when running behind a reverse proxy that
        # strips and rewrites it; otherwise an attacker can spoof any IP.
        if config.trust_proxy:
            headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
            forwarded = headers.get("x-forwarded-for")
            if forwarded:
                return forwarded.split(",")[0].strip()
        client = scope.get("client")
        return client[0] if client else "unknown"

    def _cleanup_stale_entries(self, cutoff: float) -> None:
        """Evict clients with no recent requests to prevent unbounded memory growth."""
        stale_ips = [
            ip
            for ip, timestamps in self.requests.items()
            if not timestamps or timestamps[-1] <= cutoff
        ]
        for ip in stale_ips:
            self.requests.pop(ip, None)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path.startswith(_REFLEX_INFRA_PREFIXES):
            await self.app(scope, receive, send)
            return

        client_ip = self._get_client_ip(scope)
        now = time.time()
        cutoff = now - self.window_seconds

        # Periodic cleanup of idle IPs to prevent memory leaks.
        if now - self._last_cleanup > 60 or len(self.requests) > 500:
            self._cleanup_stale_entries(cutoff)
            self._last_cleanup = now

        history = [t for t in self.requests[client_ip] if t > cutoff]
        self.requests[client_ip] = history

        if len(history) >= self.max_requests:
            await JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": self.window_seconds,
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )(scope, receive, send)
            return

        self.requests[client_ip].append(now)
        remaining = max(0, self.max_requests - len(self.requests[client_ip]))

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((b"x-ratelimit-limit", str(self.max_requests).encode()))
                headers.append((b"x-ratelimit-remaining", str(remaining).encode()))
            await send(message)

        await self.app(scope, receive, send_with_headers)


class SecurityHeadersMiddleware:
    """Adds standard security headers to HTTP responses (pure ASGI)."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.extend(
                    [
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"SAMEORIGIN"),
                        (b"x-xss-protection", b"1; mode=block"),
                        (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    ]
                )
            await send(message)

        await self.app(scope, receive, send_with_headers)
