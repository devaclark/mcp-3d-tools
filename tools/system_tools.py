"""System meta-intelligence MCP tools: health, capabilities, workflow guidance,
and tool recommendations.

Self-awareness tools that let the AI understand what it can do, check system
status, suggest optimal tool chains, and recommend programs to install.
"""
from __future__ import annotations

import json
import os
import shutil
import logging
from typing import Callable

from utils.subprocess_runner import run as run_cmd
from utils.path_utils import WORKSPACE
from utils import format_registry as fmt
from tools.registry import get_enabled_categories

logger = logging.getLogger(__name__)

OPENSCAD_BIN = os.environ.get("OPENSCAD_BIN", "/usr/bin/openscad")
BAMBU_BIN = os.environ.get("BAMBU_BIN", "/opt/bambu-studio/bambu-studio")
HOST_PROGRAMS_ENABLED = os.environ.get("HOST_PROGRAMS_ENABLED", "false").lower() == "true"
HOST_BLENDER_BIN = os.environ.get("HOST_BLENDER_BIN", "")
HOST_FREECAD_BIN = os.environ.get("HOST_FREECAD_BIN", "")

TOOL_CATALOG = {
    "openscad": {
        "description": "OpenSCAD parametric 3D modeling tools",
        "tools": {
            "openscad_render": "Render .scad to STL with inline preview",
            "openscad_preview": "Render .scad to PNG displayed inline in chat",
            "openscad_export_3mf": "Render .scad to 3MF geometry format",
            "openscad_measure": "Measure STL bounding box, volume, triangle count",
            "openscad_lint": "Syntax-check .scad without rendering",
            "openscad_list_params": "Extract parametric variables from .scad source",
            "openscad_sweep": "Sweep a variable across values with visual comparison",
            "openscad_diff": "Compare two STL files dimensionally",
        },
    },
    "bambu": {
        "description": "Bambu Studio slicer and print preparation",
        "tools": {
            "bambu_slice": "Slice STL(s) to print-ready 3MF",
            "bambu_arrange": "Auto-arrange parts on build plate",
            "bambu_validate": "Dry-run validation for printability",
            "bambu_estimate": "Estimate print time, filament, and cost",
            "bambu_compare_materials": "Compare filament presets for a model",
            "bambu_profile_list": "List available printer/filament presets",
        },
    },
    "visual": {
        "description": "Visual preview and comparison tools (inline in chat)",
        "tools": {
            "stl_preview": "Render any STL to PNG inline in chat",
            "turntable_preview": "Multi-angle turntable views of a model",
            "compare_models": "Side-by-side visual comparison of two STLs",
            "cross_section_preview": "2D cross-section at a given Z-height",
        },
    },
    "mesh": {
        "description": "Mesh intelligence — analysis, repair, and operations",
        "tools": {
            "mesh_analyze": "Deep analysis: manifold check, overhangs, thin walls, surface area",
            "mesh_repair": "Auto-fix non-manifold, holes, degenerate triangles",
            "mesh_simplify": "Reduce triangle count while preserving shape",
            "mesh_boolean": "Union, difference, intersection of two meshes",
        },
    },
    "workspace": {
        "description": "Project awareness — files, structure, and search",
        "tools": {
            "workspace_list": "List all CAD files with metadata",
            "workspace_tree": "Visual directory tree of the project",
            "workspace_read": "Read file contents (SCAD source, configs)",
            "workspace_search": "Search files by name or content",
            "workspace_recent": "Show recently modified files",
        },
    },
    "format": {
        "description": "Universal 3D format intelligence — detect, preview, convert any format",
        "tools": {
            "format_detect": "Identify file format, capabilities, and compatible programs",
            "model_info": "Full geometry metadata for any supported 3D file",
            "model_preview": "Render any 3D format to PNG inline in chat",
            "model_convert": "Convert between 3D formats with fidelity analysis",
        },
    },
    "education": {
        "description": "3D modeling and manufacturing education",
        "tools": {
            "cad_explain": "Explain any 3D modeling, printing, or manufacturing concept",
            "format_guide": "Industry guide for a specific 3D file format",
            "cad_best_practices": "Best practices for a given task or material",
            "cad_troubleshoot": "Diagnose 3D printing problems from symptoms",
        },
    },
    "system": {
        "description": "System health, self-documentation, workflow guidance, and tool recommendations",
        "tools": {
            "cad_health": "Check system status, tool availability, and host programs",
            "cad_capabilities": "Full catalog of all available tools",
            "cad_workflow": "Suggest optimal tool chain for a given goal",
            "cad_recommend_tools": "Recommend programs to install for a file type or workflow",
        },
    },
}

WORKFLOW_TEMPLATES = {
    "render_and_view": {
        "goal": "See what a .scad design looks like",
        "steps": [
            "openscad_preview(scad_file='your_file.scad')",
        ],
        "description": "Quick visual preview — image appears directly in chat.",
        "learn_more": "Use cad_explain('csg') to understand how OpenSCAD builds geometry.",
    },
    "preview_any_model": {
        "goal": "Preview any 3D file (STL, OBJ, STEP, PLY, 3MF, etc.)",
        "steps": [
            "model_preview(file_path='model.step') — auto-detects format and renders",
        ],
        "description": "Universal preview — works with any supported 3D format, "
                       "not just OpenSCAD.  The image renders directly in chat.",
        "learn_more": "Use format_guide('step') to learn about the format, or "
                      "format_detect('model.step') to inspect capabilities.",
    },
    "render_to_print": {
        "goal": "Go from .scad source to a print-ready file",
        "steps": [
            "openscad_render(scad_file='...') — get STL with inline preview",
            "mesh_analyze(stl_file='...') — check printability (manifold, overhangs)",
            "bambu_validate(stl_files=['...']) — slicer validation",
            "bambu_slice(stl_files=['...']) — export print-ready 3MF",
        ],
        "description": "Full pipeline from parametric model to build plate.",
        "learn_more": "Use cad_explain('manifold') to understand watertight meshes, "
                      "or cad_best_practices('fdm') for general printing tips.",
    },
    "design_iteration": {
        "goal": "Explore parameter variations of a design",
        "steps": [
            "openscad_list_params(scad_file='...') — discover variables",
            "openscad_sweep(scad_file='...', variable='wall', values=[1.5, 2.0, 2.5, 3.0])",
        ],
        "description": "Sweep a variable range and compare variants visually.",
        "learn_more": "Use cad_explain('parametric') to understand parametric design.",
    },
    "compare_designs": {
        "goal": "Compare two versions of a design",
        "steps": [
            "compare_models(stl_file_a='v1.stl', stl_file_b='v2.stl')",
            "openscad_diff(stl_file_a='v1.stl', stl_file_b='v2.stl')",
        ],
        "description": "Visual and dimensional comparison of two models.",
    },
    "repair_and_print": {
        "goal": "Fix a mesh and prepare it for printing",
        "steps": [
            "mesh_analyze(stl_file='...') — identify issues",
            "mesh_repair(stl_file='...') — auto-fix",
            "mesh_analyze(stl_file='..._repaired.stl') — verify repair",
            "bambu_slice(stl_files=['..._repaired.stl']) — slice for printing",
        ],
        "description": "Diagnose, repair, verify, and slice.",
        "learn_more": "Use cad_explain('manifold') to understand why watertight "
                      "meshes are required for 3D printing.",
    },
    "cost_comparison": {
        "goal": "Compare print cost across materials",
        "steps": [
            "bambu_compare_materials(stl_files=['...'], filament_presets=['PLA', 'PETG', 'ABS'])",
        ],
        "description": "Slice with multiple materials and compare time/cost.",
        "learn_more": "Use cad_best_practices('petg') or cad_best_practices('pla') "
                      "for material-specific printing tips.",
    },
    "project_overview": {
        "goal": "Understand what's in a project",
        "steps": [
            "workspace_tree() — see project structure",
            "workspace_list() — list all CAD files",
            "workspace_recent() — see what was last modified",
        ],
        "description": "Orient yourself in an unfamiliar project.",
    },
    "convert_format": {
        "goal": "Convert a 3D model to a different format",
        "steps": [
            "format_detect(file_path='model.step') — check source format",
            "model_convert(input_file='model.step', output_format='stl') — convert",
            "model_preview(file_path='model.stl') — verify the result",
        ],
        "description": "Convert between formats with fidelity analysis.",
        "learn_more": "Use format_guide('step') to understand what's lost "
                      "in conversion, or cad_best_practices('sharing') for "
                      "format choice guidance.",
    },
    "learn_concept": {
        "goal": "Learn about a 3D modeling or printing concept",
        "steps": [
            "cad_explain(topic='...') — detailed concept explanation",
            "cad_best_practices(topic='...') — actionable practices",
        ],
        "description": "Educational tools that teach concepts and best practices.",
    },
    "troubleshoot_print": {
        "goal": "Diagnose and fix a 3D printing problem",
        "steps": [
            "cad_troubleshoot(symptom='describe the problem') — get diagnosis and fixes",
            "cad_explain(topic='related concept') — understand the underlying cause",
            "cad_best_practices(topic='material') — prevent recurrence with best practices",
        ],
        "description": "Symptom-based diagnosis with causes, fixes, and prevention.",
        "learn_more": "Use cad_troubleshoot('') to see all diagnosable problems.",
    },
}


async def cad_health() -> list:
    """Check system status: tool versions, availability, disk space, host programs.

    Reports whether OpenSCAD, Bambu Studio CLI, cadquery, trimesh, and other
    dependencies are available.  Also probes for host-installed programs
    when HOST_PROGRAMS_ENABLED is true.

    Returns:
        JSON metadata with comprehensive health report.
    """
    health: dict = {
        "workspace": WORKSPACE,
        "workspace_exists": os.path.isdir(WORKSPACE),
    }

    disk = shutil.disk_usage(WORKSPACE) if os.path.isdir(WORKSPACE) else None
    if disk:
        health["disk"] = {
            "total_gb": round(disk.total / (1024 ** 3), 1),
            "used_gb": round(disk.used / (1024 ** 3), 1),
            "free_gb": round(disk.free / (1024 ** 3), 1),
            "usage_percent": round(100 * disk.used / disk.total, 1),
        }

    openscad_ok = os.path.isfile(OPENSCAD_BIN)
    openscad_version = None
    if openscad_ok:
        try:
            r = await run_cmd([OPENSCAD_BIN, "--version"], timeout=10)
            openscad_version = r.stderr.strip() or r.stdout.strip()
        except Exception:
            pass
    health["openscad"] = {
        "available": openscad_ok,
        "path": OPENSCAD_BIN,
        "version": openscad_version,
    }

    bambu_ok = os.path.isfile(BAMBU_BIN)
    health["bambu_studio"] = {
        "available": bambu_ok,
        "path": BAMBU_BIN,
    }

    for lib_name in ("trimesh", "numpy", "stl", "PIL", "pyrender", "cadquery"):
        try:
            __import__(lib_name)
            health[f"python_{lib_name}"] = True
        except ImportError:
            health[f"python_{lib_name}"] = False

    health["host_programs"] = {
        "enabled": HOST_PROGRAMS_ENABLED,
        "blender": {"path": HOST_BLENDER_BIN, "configured": bool(HOST_BLENDER_BIN)},
        "freecad": {"path": HOST_FREECAD_BIN, "configured": bool(HOST_FREECAD_BIN)},
    }

    health["supported_formats"] = fmt.all_supported_extensions()

    health["enabled_categories"] = get_enabled_categories()

    return [json.dumps(health)]


async def cad_capabilities() -> list:
    """Return the full catalog of all available MCP tools with descriptions.

    Self-documentation tool — the AI can call this to understand what
    tools are available and how to use them.

    Returns:
        JSON string with the complete tool catalog organized by category.
    """
    enabled = get_enabled_categories()

    catalog = {}
    total_tools = 0
    for category, info in TOOL_CATALOG.items():
        is_enabled = category in enabled
        catalog[category] = {
            "enabled": is_enabled,
            "description": info["description"],
            "tools": info["tools"],
            "tool_count": len(info["tools"]),
        }
        if is_enabled:
            total_tools += len(info["tools"])

    return [json.dumps({
        "total_categories": len(TOOL_CATALOG),
        "enabled_categories": len(enabled),
        "total_tools_available": total_tools,
        "catalog": catalog,
    })]


async def cad_workflow(
    goal: str = "",
) -> list:
    """Suggest the optimal tool chain for a given goal.

    Matches the user's intent to a known workflow template and returns
    the recommended sequence of tool calls.

    Args:
        goal: What you want to accomplish (e.g. "print this part",
            "compare two designs", "explore parameter space").

    Returns:
        JSON string with matching workflow(s) and step-by-step guidance.
    """
    if not goal:
        return [json.dumps({
            "available_workflows": {
                name: {"goal": wf["goal"], "description": wf["description"]}
                for name, wf in WORKFLOW_TEMPLATES.items()
            },
        })]

    goal_lower = goal.lower()
    scored: list[tuple[str, dict, int]] = []

    keywords_map = {
        "render_and_view": ["preview scad", "view scad", "openscad preview"],
        "preview_any_model": ["preview", "view", "see", "look", "show", "display", "visualize", "render"],
        "render_to_print": ["print", "slice", "3mf", "build plate", "manufacture"],
        "design_iteration": ["sweep", "parameter", "explore", "iterate", "vary", "range", "optimize"],
        "compare_designs": ["compare", "diff", "difference", "versus", "vs", "side by side"],
        "repair_and_print": ["repair", "fix", "manifold", "watertight", "broken", "heal"],
        "cost_comparison": ["cost", "material", "filament", "price", "budget", "compare material"],
        "project_overview": ["overview", "project", "structure", "orient", "files", "what", "list"],
        "convert_format": ["convert", "export", "transform", "change format", "step to stl", "obj to"],
        "learn_concept": ["learn", "explain", "teach", "understand", "what is", "how does"],
        "troubleshoot_print": ["troubleshoot", "diagnose", "problem", "issue", "fix", "wrong", "fail", "error", "broken", "bad", "help"],
    }

    for name, keywords in keywords_map.items():
        score = sum(1 for kw in keywords if kw in goal_lower)
        if score > 0:
            scored.append((name, WORKFLOW_TEMPLATES[name], score))

    scored.sort(key=lambda x: x[2], reverse=True)

    if not scored:
        return [json.dumps({
            "message": f"No workflow matched '{goal}'. Here are all available workflows.",
            "available_workflows": {
                name: {"goal": wf["goal"], "description": wf["description"]}
                for name, wf in WORKFLOW_TEMPLATES.items()
            },
        })]

    best_name, best_wf, _ = scored[0]
    alternatives = [
        {"name": name, "goal": wf["goal"]}
        for name, wf, _ in scored[1:3]
    ]

    response = {
        "recommended_workflow": best_name,
        "goal": best_wf["goal"],
        "description": best_wf["description"],
        "steps": best_wf["steps"],
        "alternatives": alternatives,
    }
    if best_wf.get("learn_more"):
        response["learn_more"] = best_wf["learn_more"]

    return [json.dumps(response)]


async def cad_recommend_tools(
    file_path_or_extension: str = "",
    goal: str = "",
) -> list:
    """Recommend the best programs and tools for a file type or workflow goal.

    Given a file path, extension, or goal description, recommends:
    - The best tool already available in the current environment
    - Industry-standard programs to install for the best experience
    - Why each recommendation matters

    Args:
        file_path_or_extension: A file path or extension (e.g. ".step", "model.obj").
        goal: A workflow goal (e.g. "edit STEP files", "prepare for 3D printing").

    Returns:
        JSON metadata with prioritized tool recommendations and rationale.
    """
    recommendations: list[dict] = []

    if file_path_or_extension:
        info = fmt.lookup(file_path_or_extension)
        if info is None:
            return [json.dumps({
                "query": file_path_or_extension,
                "recognized": False,
                "message": f"Format not recognized.  Supported: {', '.join(fmt.all_supported_extensions())}",
            })]

        available_now: list[str] = []
        if info.loader == fmt.Loader.TRIMESH:
            available_now.append("trimesh (built-in)")
        if info.loader == fmt.Loader.OCP:
            try:
                __import__("cadquery")
                available_now.append("cadquery/OpenCascade (built-in)")
            except ImportError:
                recommendations.append({
                    "action": "install",
                    "program": "cadquery",
                    "reason": f"Required to load {info.name} files.  "
                              f"Add to Docker image: pip install cadquery",
                    "priority": "high",
                })
        if info.loader == fmt.Loader.OPENSCAD:
            if os.path.isfile(OPENSCAD_BIN):
                available_now.append("OpenSCAD (built-in)")
        if info.loader == fmt.Loader.HOST:
            recommendations.append({
                "action": "install_on_host",
                "program": info.recommended_programs[0] if info.recommended_programs else "unknown",
                "reason": f"{info.name} files require a host-installed program.  "
                          f"Set HOST_PROGRAMS_ENABLED=true and configure the program path.",
                "priority": "high",
            })

        for prog in info.recommended_programs:
            if prog not in [r.get("program") for r in recommendations]:
                recommendations.append({
                    "action": "recommended",
                    "program": prog,
                    "reason": f"Industry-standard tool for {info.name} files.",
                    "priority": "medium",
                })

        return [json.dumps({
            "query": file_path_or_extension,
            "format": info.to_dict(),
            "available_now": available_now,
            "can_preview": fmt.can_preview(file_path_or_extension),
            "recommendations": recommendations,
        })]

    if goal:
        goal_lower = goal.lower()
        if any(kw in goal_lower for kw in ("step", "solid", "brep", "mechanical", "engineering")):
            recommendations.extend([
                {"program": "FreeCAD", "reason": "Free, open-source parametric CAD with STEP support.", "priority": "high"},
                {"program": "Fusion 360", "reason": "Professional cloud-based CAD (free for personal use).", "priority": "high"},
                {"program": "cadquery", "reason": "Code-first STEP modeling in Python (already in Docker).", "priority": "medium"},
            ])
        if any(kw in goal_lower for kw in ("print", "slice", "3d print", "manufacture")):
            recommendations.extend([
                {"program": "Bambu Studio", "reason": "Best slicer for Bambu Lab printers.", "priority": "high"},
                {"program": "PrusaSlicer", "reason": "Excellent open-source slicer for any FDM printer.", "priority": "high"},
                {"program": "OpenSCAD", "reason": "Parametric modeling ideal for printable parts.", "priority": "medium"},
            ])
        if any(kw in goal_lower for kw in ("render", "visual", "animation", "vfx")):
            recommendations.extend([
                {"program": "Blender", "reason": "Industry-standard free 3D creation suite.", "priority": "high"},
            ])
        if any(kw in goal_lower for kw in ("scan", "photogrammetry", "point cloud")):
            recommendations.extend([
                {"program": "MeshLab", "reason": "Best free tool for scan/point cloud processing.", "priority": "high"},
                {"program": "CloudCompare", "reason": "Advanced point cloud analysis.", "priority": "medium"},
            ])

        if not recommendations:
            recommendations.append({
                "program": "OpenSCAD",
                "reason": "Versatile parametric 3D modeling — good starting point.",
                "priority": "medium",
            })

        return [json.dumps({
            "goal": goal,
            "recommendations": recommendations,
        })]

    return [json.dumps({
        "message": "Provide a file_path_or_extension or goal to get recommendations.",
        "supported_formats": fmt.all_supported_extensions(),
    })]


def register(tool_decorator: Callable) -> None:
    """Register all system tools with the MCP server."""
    tool_decorator(cad_health)
    tool_decorator(cad_capabilities)
    tool_decorator(cad_workflow)
    tool_decorator(cad_recommend_tools)
