"""OpenSCAD MCP tools: render, preview, export, and measure."""
from __future__ import annotations

import json
import os
import logging
from typing import Callable

from utils.subprocess_runner import run as run_cmd
from utils.geometry import measure_stl as _measure_stl

logger = logging.getLogger(__name__)

OPENSCAD_BIN = os.environ.get("OPENSCAD_BIN", "/usr/bin/openscad")
WORKSPACE = os.environ.get("WORKSPACE_ROOT", "/workspace")


def _resolve(path: str) -> str:
    """Resolve a workspace-relative path to an absolute container path."""
    if os.path.isabs(path):
        return path
    return os.path.join(WORKSPACE, path)


def _build_d_args(variables: dict[str, str] | None) -> list[str]:
    args: list[str] = []
    for k, v in (variables or {}).items():
        args.extend(["-D", f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"])
    return args


async def openscad_render(
    scad_file: str,
    output_file: str = "",
    variables: dict[str, str] | None = None,
    timeout: int = 120,
) -> str:
    """Render an OpenSCAD .scad file to STL.

    Args:
        scad_file: Path to .scad file (absolute or workspace-relative).
        output_file: Output .stl path. Defaults to same name with .stl extension.
        variables: Optional dict of OpenSCAD variable overrides (passed as -D).
        timeout: Max render time in seconds.

    Returns:
        JSON string with render result including output path and timing.
    """
    src = _resolve(scad_file)
    if not output_file:
        output_file = os.path.splitext(src)[0] + ".stl"
    dst = _resolve(output_file)

    os.makedirs(os.path.dirname(dst), exist_ok=True)

    args = [OPENSCAD_BIN, *_build_d_args(variables), "-o", dst, src]
    result = await run_cmd(args, timeout=timeout)

    return json.dumps({
        "success": result.ok,
        "output_file": dst,
        "elapsed_ms": round(result.elapsed_ms),
        "stdout": result.stdout.strip()[-1000:],
        "stderr": result.stderr.strip()[-1000:],
    })


async def openscad_preview(
    scad_file: str,
    output_file: str = "",
    variables: dict[str, str] | None = None,
    imgsize: str = "1024,768",
    camera: str = "",
    timeout: int = 60,
) -> str:
    """Render an OpenSCAD file to a PNG preview image.

    Args:
        scad_file: Path to .scad file.
        output_file: Output .png path. Defaults to same name with .png extension.
        variables: Optional variable overrides.
        imgsize: Image dimensions as "width,height".
        camera: Camera parameters (translate/rotate/distance or eye/center).
        timeout: Max render time in seconds.

    Returns:
        JSON string with preview result.
    """
    src = _resolve(scad_file)
    if not output_file:
        output_file = os.path.splitext(src)[0] + ".png"
    dst = _resolve(output_file)

    os.makedirs(os.path.dirname(dst), exist_ok=True)

    args = [OPENSCAD_BIN, *_build_d_args(variables), "--imgsize", imgsize]
    if camera:
        args.extend(["--camera", camera])
    args.extend(["--autocenter", "--viewall", "-o", dst, src])

    result = await run_cmd(args, timeout=timeout)

    return json.dumps({
        "success": result.ok,
        "output_file": dst,
        "elapsed_ms": round(result.elapsed_ms),
        "stderr": result.stderr.strip()[-500:],
    })


async def openscad_export_3mf(
    scad_file: str,
    output_file: str = "",
    variables: dict[str, str] | None = None,
    timeout: int = 120,
) -> str:
    """Render an OpenSCAD file directly to 3MF geometry format.

    Args:
        scad_file: Path to .scad file.
        output_file: Output .3mf path.
        variables: Optional variable overrides.
        timeout: Max render time in seconds.

    Returns:
        JSON string with export result.
    """
    src = _resolve(scad_file)
    if not output_file:
        output_file = os.path.splitext(src)[0] + ".3mf"
    dst = _resolve(output_file)

    os.makedirs(os.path.dirname(dst), exist_ok=True)

    args = [OPENSCAD_BIN, *_build_d_args(variables), "-o", dst, src]
    result = await run_cmd(args, timeout=timeout)

    return json.dumps({
        "success": result.ok,
        "output_file": dst,
        "elapsed_ms": round(result.elapsed_ms),
        "stderr": result.stderr.strip()[-500:],
    })


async def openscad_measure(
    stl_file: str,
) -> str:
    """Measure an STL file: bounding box, triangle count, and volume.

    Args:
        stl_file: Path to .stl file.

    Returns:
        JSON string with measurement data.
    """
    path = _resolve(stl_file)
    data = _measure_stl(path)
    return json.dumps(data)


def register(tool_decorator: Callable) -> None:
    """Register all OpenSCAD tools with the MCP server."""
    tool_decorator(openscad_render)
    tool_decorator(openscad_preview)
    tool_decorator(openscad_export_3mf)
    tool_decorator(openscad_measure)
