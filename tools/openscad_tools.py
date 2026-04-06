"""OpenSCAD MCP tools: render, preview, export, measure, lint, sweep, and diff."""
from __future__ import annotations

import json
import os
import re
import logging
from typing import Callable

from utils.subprocess_runner import run as run_cmd
from utils.geometry import measure_stl as _measure_stl
from utils.path_utils import resolve, ensure_parent, with_suffix, WORKSPACE
from utils.content_helpers import success_with_image, success_with_images, error_response
from utils.render_engine import render_stl

logger = logging.getLogger(__name__)

OPENSCAD_BIN = os.environ.get("OPENSCAD_BIN", "/usr/bin/openscad")


def _build_d_args(variables: dict[str, str] | None) -> list[str]:
    args: list[str] = []
    for k, v in (variables or {}).items():
        args.extend(["-D", f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"])
    return args


async def openscad_render(
    scad_file: str,
    output_file: str = "",
    variables: dict[str, str] | None = None,
    preview: bool = True,
    timeout: int = 120,
):
    """Render an OpenSCAD .scad file to STL and return an inline preview image.

    Args:
        scad_file: Path to .scad file (absolute or workspace-relative).
        output_file: Output .stl path. Defaults to same name with .stl extension.
        variables: Optional dict of OpenSCAD variable overrides (passed as -D).
        preview: Generate and return an inline PNG preview of the rendered STL.
        timeout: Max render time in seconds.

    Returns:
        JSON metadata with render result. If preview=True, also includes an
        inline image visible directly in chat.
    """
    src = resolve(scad_file)
    if not output_file:
        output_file = with_suffix(src, ".stl")
    dst = ensure_parent(resolve(output_file))

    args = [OPENSCAD_BIN, *_build_d_args(variables), "-o", dst, src]
    result = await run_cmd(args, timeout=timeout)

    metadata = {
        "success": result.ok,
        "output_file": dst,
        "elapsed_ms": round(result.elapsed_ms),
        "stdout": result.stdout.strip()[-1000:],
        "stderr": result.stderr.strip()[-1000:],
    }

    if not result.ok or not preview:
        return success_with_image(metadata, None)

    preview_path = with_suffix(dst, "_preview.png")
    try:
        render_stl(dst, preview_path, camera_angle="isometric")
        metadata["preview_file"] = preview_path
        return success_with_image(metadata, preview_path)
    except Exception as exc:
        logger.warning("Auto-preview failed: %s", exc)
        return success_with_image(metadata, None)


async def openscad_preview(
    scad_file: str,
    output_file: str = "",
    variables: dict[str, str] | None = None,
    imgsize: str = "1024,768",
    camera: str = "",
    timeout: int = 60,
):
    """Render an OpenSCAD file to a PNG preview image, displayed inline in chat.

    Args:
        scad_file: Path to .scad file.
        output_file: Output .png path. Defaults to same name with .png extension.
        variables: Optional variable overrides.
        imgsize: Image dimensions as "width,height".
        camera: Camera parameters (translate/rotate/distance or eye/center).
        timeout: Max render time in seconds.

    Returns:
        JSON metadata and an inline image rendered directly in chat.
    """
    src = resolve(scad_file)
    if not output_file:
        output_file = with_suffix(src, ".png")
    dst = ensure_parent(resolve(output_file))

    args = [OPENSCAD_BIN, *_build_d_args(variables), "--imgsize", imgsize]
    if camera:
        args.extend(["--camera", camera])
    args.extend(["--autocenter", "--viewall", "-o", dst, src])

    result = await run_cmd(args, timeout=timeout)

    metadata = {
        "success": result.ok,
        "output_file": dst,
        "elapsed_ms": round(result.elapsed_ms),
        "stderr": result.stderr.strip()[-500:],
    }

    return success_with_image(metadata, dst if result.ok else None)


async def openscad_export_3mf(
    scad_file: str,
    output_file: str = "",
    variables: dict[str, str] | None = None,
    timeout: int = 120,
) -> list:
    """Render an OpenSCAD file directly to 3MF geometry format.

    Args:
        scad_file: Path to .scad file.
        output_file: Output .3mf path.
        variables: Optional variable overrides.
        timeout: Max render time in seconds.

    Returns:
        JSON metadata with export result.
    """
    src = resolve(scad_file)
    if not output_file:
        output_file = with_suffix(src, ".3mf")
    dst = ensure_parent(resolve(output_file))

    args = [OPENSCAD_BIN, *_build_d_args(variables), "-o", dst, src]
    result = await run_cmd(args, timeout=timeout)

    return [json.dumps({
        "success": result.ok,
        "output_file": dst,
        "elapsed_ms": round(result.elapsed_ms),
        "stderr": result.stderr.strip()[-500:],
    })]


async def openscad_measure(
    stl_file: str,
) -> list:
    """Measure an STL file: bounding box, triangle count, and volume.

    Args:
        stl_file: Path to .stl file.

    Returns:
        JSON metadata with measurement data.
    """
    path = resolve(stl_file)
    data = _measure_stl(path)
    return [json.dumps(data)]


async def openscad_lint(
    scad_file: str,
    timeout: int = 30,
) -> list:
    """Syntax-check an OpenSCAD file without rendering (fast feedback loop).

    Runs OpenSCAD with a dummy output to parse the file and report
    any syntax errors or warnings.

    Args:
        scad_file: Path to .scad file.
        timeout: Max time in seconds.

    Returns:
        JSON metadata with lint result: valid flag, errors, and warnings.
    """
    src = resolve(scad_file)
    if not os.path.isfile(src):
        return error_response(f"File not found: {src}")

    dummy_out = os.path.join("/tmp", "lint_dummy.csg")
    args = [OPENSCAD_BIN, "-o", dummy_out, src]
    result = await run_cmd(args, timeout=timeout)

    errors = []
    warnings = []
    for line in result.stderr.splitlines():
        ll = line.lower()
        if "error" in ll or "parse error" in ll:
            errors.append(line.strip())
        elif "warning" in ll or "deprecated" in ll:
            warnings.append(line.strip())

    return [json.dumps({
        "valid": result.ok and len(errors) == 0,
        "errors": errors[:20],
        "warnings": warnings[:20],
        "elapsed_ms": round(result.elapsed_ms),
    })]


async def openscad_list_params(
    scad_file: str,
) -> list:
    """Parse an OpenSCAD file and extract parametric variable declarations.

    Finds top-level variable assignments (e.g. ``wall = 2.0;``) and
    Customizer annotations (``// [min:step:max]``).

    Args:
        scad_file: Path to .scad file.

    Returns:
        JSON metadata with a list of parameters, their defaults, and any annotations.
    """
    src = resolve(scad_file)
    if not os.path.isfile(src):
        return error_response(f"File not found: {src}")

    param_pattern = re.compile(
        r"^\s*(\w+)\s*=\s*(.+?)\s*;\s*(?://\s*(.*))?$"
    )
    params: list[dict] = []

    try:
        with open(src, "r", encoding="utf-8", errors="replace") as f:
            for line_no, line in enumerate(f, 1):
                m = param_pattern.match(line)
                if m:
                    name, default, comment = m.groups()
                    if name in ("module", "function", "use", "include"):
                        continue
                    entry: dict = {
                        "name": name,
                        "default": default.strip(),
                        "line": line_no,
                    }
                    if comment:
                        entry["annotation"] = comment.strip()
                        range_match = re.search(
                            r"\[([^]]+)]", comment
                        )
                        if range_match:
                            entry["customizer_hint"] = range_match.group(1)
                    params.append(entry)
    except Exception as exc:
        return error_response(f"Failed to parse {src}: {exc}")

    return [json.dumps({
        "file": src,
        "parameter_count": len(params),
        "parameters": params,
    })]


async def openscad_sweep(
    scad_file: str,
    variable: str,
    values: list[str | float],
    output_dir: str = "",
    timeout_per_render: int = 120,
):
    """Sweep a variable across values, render each variant, measure each, and
    return a visual comparison with dimensional data.

    Args:
        scad_file: Path to .scad file.
        variable: Name of the OpenSCAD variable to sweep.
        values: List of values to assign to the variable.
        output_dir: Directory for output files. Defaults to workspace /sweep_<variable>.
        timeout_per_render: Max render time per variant in seconds.

    Returns:
        JSON metadata with per-variant measurements and inline preview images.
    """
    src = resolve(scad_file)
    if not output_dir:
        output_dir = os.path.join(WORKSPACE, f"sweep_{variable}")
    output_dir = resolve(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    variants: list[dict] = []
    preview_paths: list[str] = []

    for val in values:
        label = str(val).replace(".", "_")
        stl_path = os.path.join(output_dir, f"{variable}_{label}.stl")
        png_path = os.path.join(output_dir, f"{variable}_{label}.png")

        d_args = _build_d_args({variable: val})
        args = [OPENSCAD_BIN, *d_args, "-o", stl_path, src]
        result = await run_cmd(args, timeout=timeout_per_render)

        variant: dict = {
            "value": val,
            "stl_file": stl_path,
            "render_success": result.ok,
            "elapsed_ms": round(result.elapsed_ms),
        }

        if result.ok and os.path.isfile(stl_path):
            measurement = _measure_stl(stl_path)
            variant["measurement"] = measurement
            try:
                render_stl(stl_path, png_path, camera_angle="isometric", width=512, height=512)
                variant["preview_file"] = png_path
                preview_paths.append(png_path)
            except Exception as exc:
                logger.warning("Preview failed for %s=%s: %s", variable, val, exc)

        variants.append(variant)

    metadata = {
        "success": True,
        "scad_file": src,
        "variable": variable,
        "values_tested": len(values),
        "output_dir": output_dir,
        "variants": variants,
    }

    return success_with_images(metadata, preview_paths)


async def openscad_diff(
    stl_file_a: str,
    stl_file_b: str,
    label_a: str = "A",
    label_b: str = "B",
) -> list:
    """Compare two STL files and report dimensional differences.

    Args:
        stl_file_a: Path to first STL file.
        stl_file_b: Path to second STL file.
        label_a: Label for the first model.
        label_b: Label for the second model.

    Returns:
        JSON metadata with per-axis dimensional deltas and both measurements.
    """
    path_a = resolve(stl_file_a)
    path_b = resolve(stl_file_b)

    meas_a = _measure_stl(path_a)
    meas_b = _measure_stl(path_b)

    if "error" in meas_a:
        return error_response(f"{label_a}: {meas_a['error']}")
    if "error" in meas_b:
        return error_response(f"{label_b}: {meas_b['error']}")

    size_a = meas_a["bounding_box"]["size"]
    size_b = meas_b["bounding_box"]["size"]

    deltas = {
        axis: round(size_b[axis] - size_a[axis], 3)
        for axis in ("width", "depth", "height")
    }
    volume_delta = None
    if meas_a.get("volume_mm3") is not None and meas_b.get("volume_mm3") is not None:
        volume_delta = round(meas_b["volume_mm3"] - meas_a["volume_mm3"], 3)

    return [json.dumps({
        label_a: meas_a,
        label_b: meas_b,
        "deltas": deltas,
        "volume_delta_mm3": volume_delta,
    })]


def register(tool_decorator: Callable) -> None:
    """Register all OpenSCAD tools with the MCP server."""
    tool_decorator(openscad_render)
    tool_decorator(openscad_preview)
    tool_decorator(openscad_export_3mf)
    tool_decorator(openscad_measure)
    tool_decorator(openscad_lint)
    tool_decorator(openscad_list_params)
    tool_decorator(openscad_sweep)
    tool_decorator(openscad_diff)
