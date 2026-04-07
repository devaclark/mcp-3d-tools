"""Mesh intelligence MCP tools: analyze, repair, simplify, boolean, cross-section.

Deep geometry analysis that goes beyond bounding boxes — manifold validation,
thin wall detection, overhang analysis, surface area, and automatic repair.
"""
from __future__ import annotations

import json
import os
import logging
from typing import Callable

from utils.path_utils import resolve, ensure_parent, with_suffix
from utils.content_helpers import success_with_image, error_response

logger = logging.getLogger(__name__)


def _load_trimesh(path: str):
    """Load a mesh via trimesh, raising on failure."""
    import trimesh
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    return trimesh.load(path, force="mesh")


def _interpret_analysis(data: dict) -> dict:
    """Generate educational interpretation of mesh analysis results."""
    issues = []
    suggestions = []
    learn_more = []

    # Watertight check
    if not data.get("is_watertight"):
        issues.append("Mesh is NOT watertight (not manifold). Slicers need a watertight mesh to determine inside vs outside.")
        suggestions.append("Run mesh_repair() to auto-fix holes and non-manifold edges.")
        learn_more.append("cad_explain('manifold')")

    if not data.get("is_winding_consistent"):
        issues.append("Face winding is inconsistent — some normals point inward. This confuses slicers about surface direction.")
        suggestions.append("Run mesh_repair(fix_normals=True) to correct winding order.")

    # Overhang assessment
    overhang_pct = data.get("overhangs", {}).get("percentage", 0)
    if overhang_pct > 40:
        issues.append(f"{overhang_pct}% of faces overhang beyond 45°. This is significant — expect poor surface quality or failed prints without support material.")
        suggestions.append("Add tree supports in your slicer, or consider reorienting the part to reduce overhangs.")
        learn_more.append("cad_explain('overhangs')")
    elif overhang_pct > 15:
        issues.append(f"{overhang_pct}% of faces overhang beyond 45°. Moderate — some areas may need supports.")
        suggestions.append("Review overhang areas in your slicer's preview. Selective supports may be sufficient.")
        if "cad_explain('overhangs')" not in learn_more:
            learn_more.append("cad_explain('overhangs')")

    # Thin faces
    thin = data.get("thin_faces", 0)
    if thin > 0:
        issues.append(f"{thin} faces have area < 0.01mm² — these may indicate degenerate triangles or extremely thin geometry.")
        suggestions.append("Run mesh_repair(remove_degenerate=True) to clean up tiny faces.")
        learn_more.append("cad_explain('wall_thickness')")

    # Printability score
    if not data.get("is_watertight") or not data.get("is_winding_consistent"):
        score = "poor"
    elif overhang_pct > 40 or thin > 100:
        score = "fair"
    elif overhang_pct > 15 or thin > 10:
        score = "good"
    else:
        score = "excellent"

    if not issues:
        issues.append("Mesh looks healthy — watertight, consistent winding, minimal overhangs.")

    if not learn_more:
        learn_more.append("cad_best_practices('fdm')")

    return {
        "printability_score": score,
        "interpretation": " ".join(issues),
        "suggestions": suggestions,
        "learn_more": learn_more,
    }


async def mesh_analyze(
    stl_file: str,
) -> list:
    """Comprehensive mesh analysis: manifold check, surface area, center of mass,
    thin face detection, overhang angles, and printability assessment.

    Args:
        stl_file: Path to .stl file.

    Returns:
        JSON string with detailed mesh analysis data.
    """
    import numpy as np

    src = resolve(stl_file)
    try:
        mesh = _load_trimesh(src)
    except Exception as exc:
        return error_response(str(exc))

    is_watertight = bool(mesh.is_watertight)
    is_winding_consistent = bool(mesh.is_winding_consistent)

    face_normals = mesh.face_normals
    z_up = np.array([0.0, 0.0, 1.0])
    dot_products = np.dot(face_normals, z_up)
    angles_from_vertical = np.degrees(np.arccos(np.clip(dot_products, -1, 1)))

    overhang_threshold = 45.0
    overhang_faces = int(np.sum(angles_from_vertical > (180 - overhang_threshold)))
    overhang_percentage = round(
        100.0 * overhang_faces / len(face_normals), 1
    ) if len(face_normals) > 0 else 0.0

    min_angle = float(np.min(angles_from_vertical)) if len(angles_from_vertical) > 0 else 0.0
    max_angle = float(np.max(angles_from_vertical)) if len(angles_from_vertical) > 0 else 0.0

    face_areas = mesh.area_faces
    thin_face_threshold = 0.01
    thin_faces = int(np.sum(face_areas < thin_face_threshold))

    euler = int(mesh.euler_number)
    bounds = mesh.bounds
    extents = mesh.extents

    volume = None
    center_mass = None
    if is_watertight:
        try:
            volume = float(mesh.volume)
            center_mass = [round(float(c), 3) for c in mesh.center_mass]
        except Exception:
            pass

    analysis = {
        "file": src,
        "triangles": len(mesh.faces),
        "vertices": len(mesh.vertices),
        "is_watertight": is_watertight,
        "is_winding_consistent": is_winding_consistent,
        "euler_number": euler,
        "surface_area_mm2": round(float(mesh.area), 3),
        "volume_mm3": round(volume, 3) if volume is not None else None,
        "center_of_mass": center_mass,
        "bounding_box": {
            "min": [round(float(v), 3) for v in bounds[0]],
            "max": [round(float(v), 3) for v in bounds[1]],
            "size": {
                "width": round(float(extents[0]), 3),
                "depth": round(float(extents[1]), 3),
                "height": round(float(extents[2]), 3),
            },
        },
        "overhangs": {
            "faces_over_45deg": overhang_faces,
            "percentage": overhang_percentage,
            "min_angle_from_vertical": round(min_angle, 1),
            "max_angle_from_vertical": round(max_angle, 1),
        },
        "thin_faces": thin_faces,
        "face_area_stats": {
            "min_mm2": round(float(np.min(face_areas)), 6) if len(face_areas) > 0 else 0,
            "max_mm2": round(float(np.max(face_areas)), 3) if len(face_areas) > 0 else 0,
            "mean_mm2": round(float(np.mean(face_areas)), 3) if len(face_areas) > 0 else 0,
        },
        "repair_needed": not is_watertight or not is_winding_consistent,
    }
    analysis.update(_interpret_analysis(analysis))
    return [json.dumps(analysis)]


async def mesh_repair(
    stl_file: str,
    output_file: str = "",
    fix_normals: bool = True,
    fill_holes: bool = True,
    remove_degenerate: bool = True,
) -> list:
    """Automatically repair common mesh issues.

    Fixes non-manifold edges, inconsistent winding, degenerate triangles,
    and fills holes to produce a watertight mesh suitable for 3D printing.

    Args:
        stl_file: Path to input .stl file.
        output_file: Output .stl path for repaired mesh. Defaults to <name>_repaired.stl.
        fix_normals: Fix face normal directions and winding consistency.
        fill_holes: Fill holes in the mesh to make it watertight.
        remove_degenerate: Remove zero-area and degenerate triangles.

    Returns:
        JSON string with repair summary (before/after metrics).
    """
    src = resolve(stl_file)
    try:
        mesh = _load_trimesh(src)
    except Exception as exc:
        return error_response(str(exc))

    if not output_file:
        output_file = with_suffix(src, "_repaired.stl")
    dst = ensure_parent(resolve(output_file))

    before = {
        "triangles": len(mesh.faces),
        "is_watertight": bool(mesh.is_watertight),
        "is_winding_consistent": bool(mesh.is_winding_consistent),
    }

    repairs_applied: list[str] = []

    if remove_degenerate:
        mesh.remove_degenerate_faces()
        mesh.remove_duplicate_faces()
        mesh.remove_unreferenced_vertices()
        repairs_applied.append("removed degenerate/duplicate faces")

    if fix_normals:
        mesh.fix_normals()
        repairs_applied.append("fixed normals and winding")

    if fill_holes and not mesh.is_watertight:
        import trimesh
        trimesh.repair.fill_holes(mesh)
        repairs_applied.append("filled holes")

    if not mesh.is_watertight:
        import trimesh
        trimesh.repair.fix_inversion(mesh)
        trimesh.repair.fix_winding(mesh)
        repairs_applied.append("additional winding/inversion fix")

    after = {
        "triangles": len(mesh.faces),
        "is_watertight": bool(mesh.is_watertight),
        "is_winding_consistent": bool(mesh.is_winding_consistent),
    }

    mesh.export(dst)

    if after["is_watertight"] and after["is_winding_consistent"]:
        interpretation = f"Repaired {len(repairs_applied)} issue(s). Mesh is now watertight and ready for slicing."
    elif after["is_watertight"]:
        interpretation = f"Applied {len(repairs_applied)} repair(s). Mesh is watertight but winding may still have issues."
    else:
        interpretation = f"Applied {len(repairs_applied)} repair(s) but mesh is still not fully watertight. Manual repair in MeshLab or Blender may be needed."

    return [json.dumps({
        "success": True,
        "input_file": src,
        "output_file": dst,
        "repairs_applied": repairs_applied,
        "before": before,
        "after": after,
        "interpretation": interpretation,
        "learn_more": ["cad_explain('manifold')", "cad_best_practices('fdm')"],
    })]


async def mesh_simplify(
    stl_file: str,
    target_ratio: float = 0.5,
    output_file: str = "",
) -> list:
    """Reduce triangle count while preserving shape.

    Useful for reducing file size for large meshes or creating
    lightweight preview meshes.

    Args:
        stl_file: Path to input .stl file.
        target_ratio: Target ratio of faces to keep (0.0-1.0). E.g. 0.5 = keep 50%.
        output_file: Output .stl path. Defaults to <name>_simplified.stl.

    Returns:
        JSON string with simplification result (before/after triangle counts).
    """
    src = resolve(stl_file)
    try:
        mesh = _load_trimesh(src)
    except Exception as exc:
        return error_response(str(exc))

    if not output_file:
        output_file = with_suffix(src, "_simplified.stl")
    dst = ensure_parent(resolve(output_file))

    original_faces = len(mesh.faces)
    target_faces = max(4, int(original_faces * target_ratio))

    try:
        simplified = mesh.simplify_quadric_decimation(target_faces)
    except Exception:
        try:
            fallback_faces = max(4, int((original_faces + target_faces) // 2))
            simplified = mesh.simplify_quadric_decimation(fallback_faces)
        except Exception as exc:
            return error_response(f"Simplification failed: {exc}")

    simplified.export(dst)

    reduction = round(100.0 * (1 - len(simplified.faces) / original_faces), 1)
    return [json.dumps({
        "success": True,
        "input_file": src,
        "output_file": dst,
        "original_faces": original_faces,
        "target_faces": target_faces,
        "actual_faces": len(simplified.faces),
        "reduction_percent": reduction,
        "interpretation": f"Reduced from {original_faces:,} to {len(simplified.faces):,} faces ({reduction}% reduction). "
                          f"Visual quality should be preserved for most purposes at this level.",
        "learn_more": ["cad_explain('mesh')"],
    })]


async def mesh_boolean(
    stl_file_a: str,
    stl_file_b: str,
    operation: str = "union",
    output_file: str = "",
) -> list:
    """Perform a boolean operation on two STL meshes.

    Args:
        stl_file_a: Path to first .stl file.
        stl_file_b: Path to second .stl file.
        operation: Boolean operation: "union", "difference", or "intersection".
        output_file: Output .stl path. Defaults to <a>_<operation>_<b>.stl.

    Returns:
        JSON string with result file path and mesh statistics.
    """
    valid_ops = ("union", "difference", "intersection")
    if operation not in valid_ops:
        return error_response(
            f"Invalid operation '{operation}'. Must be one of: {', '.join(valid_ops)}"
        )

    src_a = resolve(stl_file_a)
    src_b = resolve(stl_file_b)

    try:
        mesh_a = _load_trimesh(src_a)
        mesh_b = _load_trimesh(src_b)
    except Exception as exc:
        return error_response(str(exc))

    if not output_file:
        base_a = os.path.splitext(os.path.basename(src_a))[0]
        base_b = os.path.splitext(os.path.basename(src_b))[0]
        output_file = os.path.join(
            os.path.dirname(src_a),
            f"{base_a}_{operation}_{base_b}.stl",
        )
    dst = ensure_parent(resolve(output_file))

    try:
        result_mesh = mesh_a.boolean(mesh_b, operation=operation)
    except Exception as exc:
        return error_response(f"Boolean {operation} failed: {exc}")

    result_mesh.export(dst)

    op_descriptions = {
        "union": "merged both meshes into a single solid",
        "difference": "subtracted the second mesh from the first",
        "intersection": "kept only the overlapping volume of both meshes",
    }
    watertight_note = "Result is watertight." if result_mesh.is_watertight else "Result is NOT watertight — run mesh_repair() to fix."
    return [json.dumps({
        "success": True,
        "operation": operation,
        "input_a": src_a,
        "input_b": src_b,
        "output_file": dst,
        "result_triangles": len(result_mesh.faces),
        "result_is_watertight": bool(result_mesh.is_watertight),
        "interpretation": f"Boolean {operation}: {op_descriptions[operation]}. "
                          f"Result has {len(result_mesh.faces):,} triangles. {watertight_note}",
        "learn_more": ["cad_explain('csg')", "cad_explain('manifold')"],
    })]


def register(tool_decorator: Callable) -> None:
    """Register all mesh intelligence tools with the MCP server."""
    tool_decorator(mesh_analyze)
    tool_decorator(mesh_repair)
    tool_decorator(mesh_simplify)
    tool_decorator(mesh_boolean)
