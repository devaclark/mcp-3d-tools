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
        "Advanced 3D modeling, manufacturing, and education toolkit.\n\n"
        "VISUAL PREVIEWS:\n"
        "- model_preview() renders ANY 3D format inline in chat (STL, OBJ, STEP, "
        "PLY, 3MF, GLB, IGES, and more)\n"
        "- openscad_preview() renders OpenSCAD .scad files inline in chat\n"
        "- All preview tools return images directly in the conversation\n\n"
        "FORMAT INTELLIGENCE:\n"
        "- format_detect() identifies any 3D file format and its capabilities\n"
        "- model_info() gives full geometry metadata for any supported format\n"
        "- model_convert() converts between formats with fidelity analysis\n"
        "- Supports: STL, OBJ, PLY, 3MF, GLB, DAE, AMF, STEP, IGES, BREP, SCAD, DXF\n\n"
        "MANUFACTURING:\n"
        "- openscad_render() exports .scad to STL with inline preview\n"
        "- mesh_analyze() checks printability (manifold, overhangs, thin walls)\n"
        "- mesh_repair() auto-fixes common mesh issues\n"
        "- bambu_slice() prepares print-ready 3MF for Bambu Lab printers\n"
        "- bambu_estimate() predicts print time, filament usage, and cost\n\n"
        "EDUCATION:\n"
        "- cad_explain() teaches 45+ 3D modeling and printing concepts\n"
        "- format_guide() provides industry guidance for any file format\n"
        "- cad_best_practices() gives actionable checklists by material or technique\n"
        "- cad_troubleshoot() diagnoses printing problems from symptoms with fixes\n"
        "- cad_recommend_tools() suggests programs to install for any workflow\n\n"
        "Start with cad_capabilities() to see all available tools, or\n"
        "cad_workflow(goal='...') for a recommended tool chain.\n"
        "Use cad_troubleshoot(symptom='...') to diagnose printing problems.\n"
        "Use cad_health() to verify system status."
    ),
)

from tools.registry import load_tools  # noqa: E402

loaded = load_tools(mcp.tool)
logger.info("MCP server ready — loaded categories: %s", loaded)

if __name__ == "__main__":
    mcp.run(transport="stdio")
