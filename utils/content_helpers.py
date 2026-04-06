"""Standardized response builders for MCP tool returns.

Provides helpers to return structured JSON alongside inline images,
so Cursor can render visual previews directly in the chat.
"""
from __future__ import annotations

import json
import logging
import os

from fastmcp.utilities.types import Image

logger = logging.getLogger(__name__)


def success_with_image(
    metadata: dict,
    image_path: str | None = None,
) -> list:
    """Return JSON metadata and an inline image in a single tool response.

    If the image file exists, it is included as an ``Image`` content block
    that Cursor renders directly in chat.  Otherwise only the JSON is returned.
    """
    parts: list = [json.dumps(metadata)]
    if image_path and os.path.isfile(image_path):
        try:
            parts.append(Image(path=image_path))
        except Exception as exc:
            logger.warning("Could not attach image %s: %s", image_path, exc)
    return parts


def success_with_images(
    metadata: dict,
    image_paths: list[str],
) -> list:
    """Return JSON metadata and multiple inline images."""
    parts: list = [json.dumps(metadata)]
    for p in image_paths:
        if os.path.isfile(p):
            try:
                parts.append(Image(path=p))
            except Exception as exc:
                logger.warning("Could not attach image %s: %s", p, exc)
    return parts


def error_response(message: str, **extra: object) -> list:
    """Return a structured error as a list for consistent outputSchema compliance."""
    payload: dict = {"success": False, "error": message}
    payload.update(extra)
    return [json.dumps(payload)]
