"""Visual MCP tools: STL preview, turntable, and model comparison.

These tools render STL meshes to PNG images and return them inline in chat
so the user can see their designs without leaving the conversation.
"""
from __future__ import annotations

import json
import os
import logging
from typing import Callable

from utils.path_utils import resolve, ensure_parent, with_suffix, WORKSPACE
from utils.content_helpers import success_with_image, success_with_images, error_response
from utils.render_engine import (
    render_stl,
    render_turntable,
    render_cross_section,
    CAMERA_PRESETS,
)

logger = logging.getLogger(__name__)


async def stl_preview(
    stl_file: str,
    output_file: str = "",
    camera_angle: str = "isometric",
    width: int = 1024,
    height: int = 768,
):
    """Render an STL file to a PNG preview image, displayed inline in chat.

    Works with any STL file — no OpenSCAD source required.  Uses trimesh
    for rendering with a choice of camera angles.

    Args:
        stl_file: Path to .stl file (absolute or workspace-relative).
        output_file: Output .png path. Defaults to <stl_file>_preview.png.
        camera_angle: Camera preset or custom "azimuth,elevation" degrees.
            Presets: isometric, front, back, left, right, top, bottom.
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        JSON metadata and an inline image rendered directly in chat.
    """
    src = resolve(stl_file)
    if not os.path.isfile(src):
        return error_response(f"STL file not found: {src}")

    if not output_file:
        output_file = with_suffix(src, "_preview.png")
    dst = ensure_parent(resolve(output_file))

    try:
        result = render_stl(src, dst, camera_angle=camera_angle, width=width, height=height)
    except Exception as exc:
        return error_response(f"Render failed: {exc}")

    metadata = {
        "success": True,
        "stl_file": src,
        "output_file": result.png_path,
        "camera_angle": result.camera_angle,
        "dimensions": f"{result.width}x{result.height}",
        "available_presets": list(CAMERA_PRESETS.keys()),
    }

    return success_with_image(metadata, result.png_path)


async def turntable_preview(
    stl_file: str,
    output_dir: str = "",
    angles: int = 6,
    width: int = 512,
    height: int = 512,
    elevation: float = 25.0,
):
    """Generate a multi-angle turntable view of an STL model.

    Renders the model from multiple azimuth positions around the Z-axis,
    returning all images inline in chat for a spatial understanding of
    the part without opening a 3D viewer.

    Args:
        stl_file: Path to .stl file.
        output_dir: Directory for output images. Defaults to same dir as STL.
        angles: Number of viewing angles (evenly spaced around 360 degrees).
        width: Image width per frame in pixels.
        height: Image height per frame in pixels.
        elevation: Camera elevation in degrees above the horizon.

    Returns:
        JSON metadata and multiple inline images.
    """
    src = resolve(stl_file)
    if not os.path.isfile(src):
        return error_response(f"STL file not found: {src}")

    if not output_dir:
        base = os.path.splitext(src)[0]
        output_dir = f"{base}_turntable"
    output_dir = resolve(output_dir)

    try:
        results = render_turntable(
            src, output_dir,
            num_angles=angles, width=width, height=height, elevation=elevation,
        )
    except Exception as exc:
        return error_response(f"Turntable render failed: {exc}")

    metadata = {
        "success": True,
        "stl_file": src,
        "output_dir": output_dir,
        "angles_rendered": len(results),
        "files": [r.png_path for r in results],
    }

    return success_with_images(metadata, [r.png_path for r in results])


async def compare_models(
    stl_file_a: str,
    stl_file_b: str,
    label_a: str = "Model A",
    label_b: str = "Model B",
    camera_angle: str = "isometric",
    width: int = 800,
    height: int = 600,
):
    """Visually compare two STL files side by side with dimensional data.

    Renders both models from the same camera angle and returns both images
    along with measurements and dimensional deltas.

    Args:
        stl_file_a: Path to first STL file.
        stl_file_b: Path to second STL file.
        label_a: Display label for the first model.
        label_b: Display label for the second model.
        camera_angle: Camera preset or custom angles.
        width: Image width per model in pixels.
        height: Image height per model in pixels.

    Returns:
        JSON comparison data and inline images of both models.
    """
    from utils.geometry import measure_stl

    src_a = resolve(stl_file_a)
    src_b = resolve(stl_file_b)

    for path, label in [(src_a, label_a), (src_b, label_b)]:
        if not os.path.isfile(path):
            return error_response(f"{label}: file not found: {path}")

    png_a = with_suffix(src_a, "_compare.png")
    png_b = with_suffix(src_b, "_compare.png")

    images: list[str] = []
    try:
        render_stl(src_a, png_a, camera_angle=camera_angle, width=width, height=height)
        images.append(png_a)
    except Exception as exc:
        logger.warning("Render of %s failed: %s", label_a, exc)

    try:
        render_stl(src_b, png_b, camera_angle=camera_angle, width=width, height=height)
        images.append(png_b)
    except Exception as exc:
        logger.warning("Render of %s failed: %s", label_b, exc)

    meas_a = measure_stl(src_a)
    meas_b = measure_stl(src_b)

    deltas = {}
    if "error" not in meas_a and "error" not in meas_b:
        size_a = meas_a["bounding_box"]["size"]
        size_b = meas_b["bounding_box"]["size"]
        deltas = {
            axis: round(size_b[axis] - size_a[axis], 3)
            for axis in ("width", "depth", "height")
        }
        if meas_a.get("volume_mm3") is not None and meas_b.get("volume_mm3") is not None:
            deltas["volume_mm3"] = round(
                meas_b["volume_mm3"] - meas_a["volume_mm3"], 3
            )

    metadata = {
        "success": True,
        label_a: meas_a,
        label_b: meas_b,
        "deltas": deltas,
    }

    return success_with_images(metadata, images)


async def cross_section_preview(
    stl_file: str,
    z_height: float | None = None,
    output_file: str = "",
    width: int = 1024,
    height: int = 768,
):
    """Generate a 2D cross-section view of an STL at a given Z-height.

    Slices the mesh with a horizontal plane and renders the resulting
    2D profile, useful for inspecting internal geometry and wall thickness.

    Args:
        stl_file: Path to .stl file.
        z_height: Z-height for the cut plane in mm. Defaults to model midpoint.
        output_file: Output .png path.
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        JSON metadata and an inline cross-section image.
    """
    src = resolve(stl_file)
    if not os.path.isfile(src):
        return error_response(f"STL file not found: {src}")

    if not output_file:
        output_file = with_suffix(src, "_cross_section.png")
    dst = ensure_parent(resolve(output_file))

    try:
        render_cross_section(src, dst, z_height=z_height, width=width, height=height)
    except Exception as exc:
        return error_response(f"Cross-section failed: {exc}")

    metadata = {
        "success": True,
        "stl_file": src,
        "z_height_mm": z_height,
        "output_file": dst,
    }

    return success_with_image(metadata, dst)


def register(tool_decorator: Callable) -> None:
    """Register all visual tools with the MCP server."""
    tool_decorator(stl_preview)
    tool_decorator(turntable_preview)
    tool_decorator(compare_models)
    tool_decorator(cross_section_preview)
