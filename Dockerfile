# AgriLedger — production image.
# Compiles the Reflex frontend at build time so the running server serves
# both the API and the SPA on one port. Runs as a non-root user.

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_MAJOR=20 \
    REFLEX_ENV=prod

WORKDIR /app

# Node.js is required to compile the Reflex frontend during the build.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source.
COPY . .

# Compile the frontend bundle into .web/_static. The app imports cleanly
# without touching the database (lazy clients), so this works at build time.
# A non-root user owns the tree so the running server never needs root.
RUN useradd --create-home --shell /bin/bash appuser \
    && reflex export --frontend-only --no-zip \
    && chown -R appuser:appuser /app

USER appuser
ENV HOME=/home/appuser

EXPOSE 8000

# Reflex /_health pings the DB and mounts nothing; safe for orchestration.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://localhost:8000/_health || exit 1

# Prod mode serves the compiled frontend + API + websockets on one port.
CMD ["reflex", "run", "--env", "prod", "--backend-host", "0.0.0.0"]
