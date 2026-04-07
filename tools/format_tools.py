"""Universal 3D format MCP tools: detect, info, preview, and convert.

Format-agnostic tools that work with any supported 3D file type.
The user never needs to know which tool handles which format — these
tools auto-detect and route to the correct backend.
"""
from __future__ import annotations

import json
import os
import logging
from typing import Callable

from utils.path_utils import resolve, ensure_parent, with_suffix
from utils.content_helpers import success_with_image, error_response
from utils.render_engine import render_model, CAMERA_PRESETS
from utils import format_registry as fmt

logger = logging.getLogger(__name__)


async def format_detect(
    file_path: str,
) -> list:
    """Identify the 3D file format and report its capabilities.

    Auto-detects format from the file extension, validates that the file
    exists, and returns detailed format metadata including what programs
    can work with it and what capabilities it supports.

    Args:
        file_path: Path to any 3D file (absolute or workspace-relative).

    Returns:
        JSON metadata with format identification, capabilities, and
        industry recommendations.
    """
    src = resolve(file_path)
    if not os.path.isfile(src):
        return error_response(f"File not found: {src}")

    ext = os.path.splitext(src)[1].lower()
    info = fmt.lookup(ext)

    if info is None:
        return [json.dumps({
            "file": src,
            "extension": ext,
            "recognized": False,
            "message": f"Extension '{ext}' is not in the format registry.  "
                       f"Supported extensions: {', '.join(fmt.all_supported_extensions())}",
        })]

    stat = os.stat(src)

    return [json.dumps({
        "file": src,
        "extension": ext,
        "recognized": True,
        "size_bytes": stat.st_size,
        "format": info.to_dict(),
        "can_preview": fmt.can_preview(ext),
        "convertible_to": [
            e for e in fmt.all_supported_extensions()
            if e != ext and fmt.can_convert(ext, e)
        ],
    })]


async def model_info(
    file_path: str,
) -> list:
    """Comprehensive metadata for any supported 3D model file.

    Loads the file, extracts geometry metrics (vertices, faces, bounds,
    volume), and combines with format registry data.  Works with STL,
    OBJ, PLY, 3MF, GLB, STEP, IGES, and all other supported formats.

    Args:
        file_path: Path to any supported 3D file.

    Returns:
        JSON metadata with geometry metrics, format info, and recommendations.
    """
    src = resolve(file_path)
    if not os.path.isfile(src):
        return error_response(f"File not found: {src}")

    ext = os.path.splitext(src)[1].lower()
    info = fmt.lookup(ext)
    stat = os.stat(src)

    result: dict = {
        "file": src,
        "extension": ext,
        "size_bytes": stat.st_size,
        "format": info.to_dict() if info else {"name": "Unknown", "extension": ext},
    }

    if info and info.loader == fmt.Loader.NONE:
        result["message"] = (
            f"{info.name} is a 2D format and cannot be loaded as a 3D model.  "
            f"{info.conversion_notes}"
        )
        return [json.dumps(result)]

    if info and info.loader == fmt.Loader.HOST:
        result["message"] = (
            f"{info.name} requires {', '.join(info.recommended_programs)} "
            f"installed on the host to load.  Export to STEP or STL for "
            f"analysis within this MCP server."
        )
        return [json.dumps(result)]

    try:
        from utils.render_engine import _load_mesh
        mesh = _load_mesh(src)
    except ImportError as exc:
        result["error"] = str(exc)
        result["message"] = (
            "Required loader is not installed.  "
            "See the error message for installation instructions."
        )
        return [json.dumps(result)]
    except Exception as exc:
        result["error"] = f"Failed to load: {exc}"
        return [json.dumps(result)]

    is_watertight = bool(mesh.is_watertight)
    bounds = mesh.bounds
    extents = mesh.extents

    result["geometry"] = {
        "vertices": len(mesh.vertices),
        "faces": len(mesh.faces),
        "is_watertight": is_watertight,
        "is_winding_consistent": bool(mesh.is_winding_consistent),
        "surface_area_mm2": round(float(mesh.area), 3),
        "bounding_box": {
            "min": [round(float(v), 3) for v in bounds[0]],
            "max": [round(float(v), 3) for v in bounds[1]],
            "size": {
                "width": round(float(extents[0]), 3),
                "depth": round(float(extents[1]), 3),
                "height": round(float(extents[2]), 3),
            },
        },
    }

    if is_watertight:
        try:
            result["geometry"]["volume_mm3"] = round(float(mesh.volume), 3)
            result["geometry"]["center_of_mass"] = [
                round(float(c), 3) for c in mesh.center_mass
            ]
        except Exception:
            pass

    if info:
        result["recommendations"] = {
            "best_programs": list(info.recommended_programs),
            "industry_context": info.industry,
            "conversion_notes": info.conversion_notes,
        }

    return [json.dumps(result)]


async def model_preview(
    file_path: str,
    output_file: str = "",
    camera_angle: str = "isometric",
    width: int = 1024,
    height: int = 768,
):
    """Render any supported 3D model to a PNG preview, displayed inline in chat.

    Universal preview tool — auto-detects the file format and uses the
    correct backend (trimesh for meshes, OpenCascade for STEP/IGES).
    No need to know which specific preview tool to call.

    Supported formats: STL, OBJ, PLY, 3MF, GLB, GLTF, DAE, AMF, OFF,
    DXF, STEP, STP, IGES, IGS, BREP.

    Args:
        file_path: Path to any supported 3D file.
        output_file: Output .png path. Defaults to <file>_preview.png.
        camera_angle: Camera preset or custom "azimuth,elevation" degrees.
            Presets: isometric, front, back, left, right, top, bottom.
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        JSON metadata and an inline image rendered directly in chat.
    """
    src = resolve(file_path)
    if not os.path.isfile(src):
        return error_response(f"File not found: {src}")

    ext = os.path.splitext(src)[1].lower()
    info = fmt.lookup(ext)

    if info and info.loader == fmt.Loader.NONE:
        return error_response(
            f"{info.name} is a 2D format and cannot be rendered as a 3D model.  "
            f"Supported 3D formats: STL, OBJ, PLY, 3MF, GLB, STEP, IGES, and more."
        )
    if info and info.loader == fmt.Loader.HOST:
        return error_response(
            f"{info.name} requires {', '.join(info.recommended_programs)} "
            f"to render.  Export to STL or STEP first."
        )

    if not output_file:
        output_file = with_suffix(src, "_preview.png")
    dst = ensure_parent(resolve(output_file))

    try:
        result = render_model(
            src, dst, camera_angle=camera_angle, width=width, height=height,
        )
    except ImportError as exc:
        return error_response(str(exc))
    except Exception as exc:
        return error_response(f"Render failed: {exc}")

    metadata = {
        "success": True,
        "file": src,
        "format": info.name if info else ext,
        "output_file": result.png_path,
        "camera_angle": result.camera_angle,
        "dimensions": f"{result.width}x{result.height}",
        "available_presets": list(CAMERA_PRESETS.keys()),
    }

    return success_with_image(metadata, result.png_path)


async def model_convert(
    input_file: str,
    output_format: str,
    output_file: str = "",
) -> list:
    """Convert a 3D model between formats.

    Handles mesh-to-mesh conversions (STL, OBJ, PLY, 3MF, GLB, etc.)
    and solid-to-mesh conversions (STEP/IGES to STL/OBJ/3MF).
    Reports what fidelity is lost in the conversion.

    Args:
        input_file: Path to input 3D file.
        output_format: Target format extension (e.g. "stl", "obj", "3mf").
        output_file: Output file path. Defaults to input name + new extension.

    Returns:
        JSON metadata with conversion result and fidelity analysis.
    """
    src = resolve(input_file)
    if not os.path.isfile(src):
        return error_response(f"File not found: {src}")

    src_ext = os.path.splitext(src)[1].lower()
    dst_ext = output_format if output_format.startswith(".") else f".{output_format}"
    dst_ext = dst_ext.lower()

    src_info = fmt.lookup(src_ext)
    dst_info = fmt.lookup(dst_ext)

    if src_info is None:
        return error_response(f"Source format '{src_ext}' is not recognized.")
    if dst_info is None:
        return error_response(f"Target format '{dst_ext}' is not recognized.")

    if not fmt.can_convert(src_ext, dst_ext):
        return error_response(
            f"Cannot convert {src_info.name} → {dst_info.name}.  "
            f"Source loader: {src_info.loader.value}, "
            f"target loader: {dst_info.loader.value}."
        )

    if not output_file:
        output_file = with_suffix(src, dst_ext)
    dst = ensure_parent(resolve(output_file))

    try:
        from utils.render_engine import _load_mesh
        mesh = _load_mesh(src)
    except Exception as exc:
        return error_response(f"Failed to load source: {exc}")

    try:
        mesh.export(dst)
    except Exception as exc:
        return error_response(f"Export to {dst_ext} failed: {exc}")

    fidelity = fmt.conversion_fidelity(src_ext, dst_ext)

    stat = os.stat(dst)
    return [json.dumps({
        "success": True,
        "input_file": src,
        "input_format": src_info.name,
        "output_file": dst,
        "output_format": dst_info.name,
        "output_size_bytes": stat.st_size,
        "vertices": len(mesh.vertices),
        "faces": len(mesh.faces),
        "fidelity_analysis": fidelity,
        "interpretation": f"Converted {src_info.name} to {dst_info.name}. {fidelity}",
        "learn_more": [f"format_guide('{src_info.extensions[0]}')", "cad_explain('brep')" if any(c.value == 'solid_brep' for c in src_info.capabilities) else "cad_explain('mesh')"],
    })]


def register(tool_decorator: Callable) -> None:
    """Register all format intelligence tools with the MCP server."""
    tool_decorator(format_detect)
    tool_decorator(model_info)
    tool_decorator(model_preview)
    tool_decorator(model_convert)
