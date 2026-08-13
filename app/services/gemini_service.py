"""Shared Gemini client helpers.

Provides ``retry_across_models`` so any AI feature (chat, insights, milk-bill
OCR) transparently fails over to an available model when the configured one is
deprecated, blocked for the key, or otherwise unusable.
"""

import json
import logging
import re

from app.config import config

logger = logging.getLogger(__name__)


def extract_json(text: str | None):
    """Parse the first JSON object out of a model response.

    Gemini is asked for ``response_mime_type="application/json"`` but can still
    occasionally wrap the payload or append stray text (a trailing brace, a
    sentence, markdown fences). This finds the first balanced ``{...}`` block
    and parses it, returning ``None`` when nothing parses.
    """
    if not text:
        return None
    stripped = text.strip()
    # Drop markdown code fences if the model wrapped the answer.
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```\s*$", "", stripped)
    try:
        return json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        pass
    # Fall back to the first balanced { ... } block anywhere in the text.
    start = stripped.find("{")
    while start != -1:
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(stripped)):
            ch = stripped[i]
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
            elif ch == '"':
                in_string = not in_string
            elif not in_string:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = stripped[start : i + 1]
                        try:
                            return json.loads(candidate)
                        except (json.JSONDecodeError, ValueError):
                            break
        start = stripped.find("{", start + 1)
    return None


async def retry_across_models(operation, models: list[str] | None = None):
    """Run ``operation(model)`` over candidate models until one succeeds.

    Args:
        operation: An async callable taking a single model-name argument and
            returning the response (or text). May raise on failure.
        models: Optional explicit candidate list (mainly for tests). Defaults to
            ``config.gemini.model_candidates`` (configured model first, then
            fallbacks), so the preferred model is always tried first.

    Returns:
        The first successful result, or ``None`` if every candidate failed.
    """
    candidates = models if models is not None else config.gemini.model_candidates
    last_error: Exception | None = None
    for model in candidates:
        try:
            result = await operation(model)
            if result is not None:
                return result
        except Exception as e:  # noqa: BLE001 - failover is the point
            last_error = e
            # Individual failures are expected during failover — only surface
            # a warning when every candidate has failed.
            logger.debug("Gemini model '%s' failed: %s", model, e)
    if last_error is not None:
        logger.warning(
            "All Gemini models failed (%d tried); last error: %s",
            len(candidates),
            last_error,
        )
    else:
        logger.debug(
            "All Gemini models returned empty results (%d tried)",
            len(candidates),
        )
    return None
