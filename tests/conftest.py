"""Shared pytest fixtures for the AgriLedger test suite.

Setting ``TESTING=true`` keeps test runs hermetic: production fail-fast
checks (e.g. SECRET_KEY required when APP_ENV=production) and telemetry are
suppressed while tests execute.
"""

import os

os.environ.setdefault("TESTING", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci")
os.environ.setdefault("APP_ENV", "development")
