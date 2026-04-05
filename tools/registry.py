from __future__ import annotations

import importlib
import logging
import os
from typing import Callable

logger = logging.getLogger(__name__)

CATEGORY_MODULES: dict[str, str] = {
    "openscad": "tools.openscad_tools",
    "bambu": "tools.bambu_tools",
}


def get_enabled_categories() -> list[str]:
    raw = os.environ.get("MCP_TOOL_CATEGORIES", "openscad,bambu")
    return [c.strip().lower() for c in raw.split(",") if c.strip()]


def load_tools(register_fn: Callable) -> list[str]:
    """Import each enabled category module and call its ``register(register_fn)``."""
    enabled = get_enabled_categories()
    loaded: list[str] = []

    for category in enabled:
        module_path = CATEGORY_MODULES.get(category)
        if module_path is None:
            logger.warning("Unknown tool category: %s (skipped)", category)
            continue
        try:
            mod = importlib.import_module(module_path)
            if hasattr(mod, "register"):
                mod.register(register_fn)
                loaded.append(category)
                logger.info("Loaded tool category: %s", category)
            else:
                logger.warning("Module %s has no register() function", module_path)
        except Exception:
            logger.exception("Failed to load tool category: %s", category)

    return loaded
