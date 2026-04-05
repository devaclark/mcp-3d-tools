"""mcp-3d-tools: MCP server bridging Cursor IDE with 3D modeling tools."""
from __future__ import annotations

import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp-3d-tools")

from fastmcp import FastMCP  # noqa: E402

mcp = FastMCP(
    name="mcp-3d-tools",
    instructions=(
        "3D modeling toolkit. Use these tools to render OpenSCAD files, "
        "export STLs/3MFs, slice for Bambu Lab printers, preview geometry, "
        "and measure part dimensions."
    ),
)

from tools.registry import load_tools  # noqa: E402

loaded = load_tools(mcp.tool)
logger.info("MCP server ready — loaded categories: %s", loaded)

if __name__ == "__main__":
    mcp.run(transport="stdio")
