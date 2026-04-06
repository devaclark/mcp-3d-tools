"""Educational MCP tools: explain concepts, format guides, best practices.

Makes the MCP server an educator — the AI can teach users about 3D modeling,
file formats, printing techniques, and manufacturing best practices.
"""
from __future__ import annotations

import json
import logging
from typing import Callable

from utils.knowledge_base import find_concept, find_best_practices, list_all_topics
from utils import format_registry as fmt

logger = logging.getLogger(__name__)


async def cad_explain(
    topic: str,
) -> list:
    """Explain any 3D modeling, printing, or manufacturing concept.

    Searches the built-in knowledge base for the topic and returns a
    detailed explanation with related concepts.  Topics include mesh,
    manifold, BREP, CSG, parametric modeling, overhangs, layer height,
    infill, warping, tolerances, wall thickness, print-in-place, and more.

    Args:
        topic: The concept to explain (e.g. "manifold", "overhangs",
            "print in place", "BREP", "layer height", "tolerances").

    Returns:
        JSON metadata with detailed explanation, related topics, and
        a list of all available topics if no match is found.
    """
    if not topic.strip():
        all_topics = list_all_topics()
        return [json.dumps({
            "message": "Provide a topic to learn about.  Here's what I can teach:",
            **all_topics,
        })]

    results = find_concept(topic)

    if not results:
        all_topics = list_all_topics()
        return [json.dumps({
            "query": topic,
            "found": False,
            "message": f"No concept matched '{topic}'.  Here are all available topics:",
            **all_topics,
        })]

    best = results[0]
    clean = {k: v for k, v in best.items() if not k.startswith("_")}

    also_relevant = []
    for r in results[1:]:
        also_relevant.append({
            "title": r["title"],
            "summary": r["summary"],
        })

    response: dict = {
        "query": topic,
        "found": True,
        **clean,
    }
    if also_relevant:
        response["also_relevant"] = also_relevant

    return [json.dumps(response)]


async def format_guide(
    format_name: str,
) -> list:
    """Get a comprehensive industry guide for a specific 3D file format.

    Returns detailed information about what the format is, who uses it,
    when to use it, its strengths and limitations, recommended programs,
    and conversion compatibility.

    Args:
        format_name: Format name or extension (e.g. "STEP", ".stl",
            "obj", "3mf", "scad", "iges", "glb").

    Returns:
        JSON metadata with complete format guide and conversion analysis.
    """
    if not format_name.strip():
        all_formats = {
            ext: {"name": info.name, "description": info.description[:100] + "..."}
            for ext, info in sorted(fmt.FORMATS.items())
        }
        return [json.dumps({
            "message": "Provide a format name to get a detailed guide.  "
                       "Available formats:",
            "formats": all_formats,
        })]

    info = fmt.lookup(format_name)
    if info is None:
        query = format_name.lower().strip(".")
        for ext, candidate in fmt.FORMATS.items():
            if query in candidate.name.lower() or query in ext:
                info = candidate
                break

    if info is None:
        return [json.dumps({
            "query": format_name,
            "found": False,
            "message": f"Format '{format_name}' not recognized.  "
                       f"Available: {', '.join(fmt.all_supported_extensions())}",
        })]

    conversions: dict[str, str] = {}
    for ext in fmt.all_supported_extensions():
        if ext not in info.extensions:
            if fmt.can_convert(info.extensions[0], ext):
                conversions[ext] = fmt.conversion_fidelity(info.extensions[0], ext)

    return [json.dumps({
        "query": format_name,
        "found": True,
        "format": info.to_dict(),
        "when_to_use": info.industry,
        "conversion_options": conversions,
        "conversion_notes": info.conversion_notes,
        "can_preview_in_mcp": fmt.can_preview(info.extensions[0]),
        "recommended_workflow": _format_workflow_hint(info),
    })]


async def cad_best_practices(
    topic: str,
) -> list:
    """Get best practices for a given material, technique, or workflow.

    Returns actionable checklists and design rules for topics like
    PETG printing, print-in-place design, sharing models, FDM general
    practices, and more.

    Args:
        topic: The topic area (e.g. "PETG", "print in place",
            "sharing models", "FDM", "ABS", "PLA", "tolerances").

    Returns:
        JSON metadata with prioritized best practices and related topics.
    """
    if not topic.strip():
        all_topics = list_all_topics()
        return [json.dumps({
            "message": "Provide a topic to get best practices.  Available areas:",
            "best_practices": all_topics.get("best_practices", {}),
        })]

    results = find_best_practices(topic)

    if not results:
        concept_results = find_concept(topic)
        if concept_results:
            best = concept_results[0]
            clean = {k: v for k, v in best.items() if not k.startswith("_")}
            return [json.dumps({
                "query": topic,
                "found_practices": False,
                "found_concept": True,
                "message": f"No specific best-practice checklist for '{topic}', "
                           f"but here's the concept explanation:",
                **clean,
            })]

        all_topics = list_all_topics()
        return [json.dumps({
            "query": topic,
            "found_practices": False,
            "found_concept": False,
            "message": f"No best practices found for '{topic}'.  Available topics:",
            "best_practices": all_topics.get("best_practices", {}),
            "concepts": all_topics.get("concepts", {}),
        })]

    best = results[0]
    clean = {k: v for k, v in best.items() if not k.startswith("_")}

    also_relevant = []
    for r in results[1:]:
        also_relevant.append({
            "title": r["title"],
            "category": r["category"],
        })

    response: dict = {
        "query": topic,
        "found_practices": True,
        **clean,
    }
    if also_relevant:
        response["also_relevant"] = also_relevant

    return [json.dumps(response)]


def _format_workflow_hint(info: fmt.FormatInfo) -> str:
    """Generate a workflow hint for a given format."""
    if info.loader == fmt.Loader.OPENSCAD:
        return (
            "Use openscad_preview to see the design, openscad_render to export STL, "
            "openscad_list_params to discover parameters, and openscad_sweep to "
            "explore the design space."
        )
    if info.loader == fmt.Loader.TRIMESH:
        return (
            "Use model_preview to visualize, model_info for geometry metrics, "
            "mesh_analyze for printability, and model_convert to change formats."
        )
    if info.loader == fmt.Loader.OCP:
        return (
            "Use model_preview to visualize the solid, model_info for geometry metrics, "
            "and model_convert to export as STL or 3MF for printing."
        )
    if info.loader == fmt.Loader.HOST:
        return (
            f"This format requires {', '.join(info.recommended_programs)}.  "
            f"Export to STEP or STL from the native application, then use MCP tools."
        )
    return "Use format_detect to check compatibility."


def register(tool_decorator: Callable) -> None:
    """Register all education tools with the MCP server."""
    tool_decorator(cad_explain)
    tool_decorator(format_guide)
    tool_decorator(cad_best_practices)
