"""Bambu Studio CLI MCP tools: slice, arrange, validate."""
from __future__ import annotations

import json
import os
import logging
from typing import Callable

from utils.subprocess_runner import run as run_cmd

logger = logging.getLogger(__name__)

BAMBU_BIN = os.environ.get("BAMBU_BIN", "/opt/bambu-studio/bambu-studio")
WORKSPACE = os.environ.get("WORKSPACE_ROOT", "/workspace")


def _resolve(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(WORKSPACE, path)


def _settings_args() -> list[str]:
    """Build --load-settings and --load-filaments from env presets if available."""
    args: list[str] = []
    printer = os.environ.get("BAMBU_PRINTER_PRESET")
    filament = os.environ.get("BAMBU_FILAMENT_PRESET")
    process = os.environ.get("BAMBU_PROCESS_PRESET")

    if printer or process:
        parts = [p for p in [printer, process] if p]
        args.extend(["--load-settings", ";".join(parts)])
    if filament:
        args.extend(["--load-filaments", filament])
    return args


async def bambu_slice(
    stl_files: list[str],
    output_file: str = "",
    arrange: bool = True,
    orient: bool = True,
    timeout: int = 180,
) -> str:
    """Slice one or more STL files and export a print-ready 3MF.

    Args:
        stl_files: List of STL file paths (absolute or workspace-relative).
        output_file: Output .3mf path. Defaults to first STL name + _sliced.3mf.
        arrange: Auto-arrange parts on the build plate.
        orient: Auto-orient parts for optimal printing.
        timeout: Max slice time in seconds.

    Returns:
        JSON string with slicing result.
    """
    resolved = [_resolve(f) for f in stl_files]
    if not output_file:
        base = os.path.splitext(resolved[0])[0]
        output_file = f"{base}_sliced.3mf"
    dst = _resolve(output_file)

    os.makedirs(os.path.dirname(dst), exist_ok=True)

    args = [BAMBU_BIN]
    if orient:
        args.append("--orient")
    if arrange:
        args.extend(["--arrange", "1"])

    args.extend(_settings_args())
    args.extend(["--slice", "0", "--export-3mf", dst])
    args.extend(resolved)

    result = await run_cmd(args, timeout=timeout)

    return json.dumps({
        "success": result.ok,
        "output_file": dst,
        "input_files": resolved,
        "elapsed_ms": round(result.elapsed_ms),
        "stdout": result.stdout.strip()[-1000:],
        "stderr": result.stderr.strip()[-1000:],
    })


async def bambu_arrange(
    stl_files: list[str],
    output_file: str = "",
    timeout: int = 120,
) -> str:
    """Auto-arrange STL parts on the build plate and export 3MF (no slicing).

    Args:
        stl_files: List of STL file paths.
        output_file: Output .3mf path.
        timeout: Max time in seconds.

    Returns:
        JSON string with arrangement result.
    """
    resolved = [_resolve(f) for f in stl_files]
    if not output_file:
        output_file = os.path.join(WORKSPACE, "arranged_output.3mf")
    dst = _resolve(output_file)

    os.makedirs(os.path.dirname(dst), exist_ok=True)

    args = [BAMBU_BIN, "--orient", "--arrange", "1"]
    args.extend(_settings_args())
    args.extend(["--export-3mf", dst])
    args.extend(resolved)

    result = await run_cmd(args, timeout=timeout)

    return json.dumps({
        "success": result.ok,
        "output_file": dst,
        "elapsed_ms": round(result.elapsed_ms),
        "stderr": result.stderr.strip()[-500:],
    })


async def bambu_validate(
    stl_files: list[str],
    timeout: int = 120,
) -> str:
    """Dry-run slice to validate STL files for printability without exporting.

    Args:
        stl_files: List of STL file paths to validate.
        timeout: Max time in seconds.

    Returns:
        JSON string with validation result (errors/warnings from slicer).
    """
    resolved = [_resolve(f) for f in stl_files]

    args = [BAMBU_BIN, "--orient", "--arrange", "1"]
    args.extend(_settings_args())
    args.extend(["--slice", "0", "--debug", "3"])
    args.extend(resolved)

    result = await run_cmd(args, timeout=timeout)

    warnings = [
        line for line in result.stderr.splitlines()
        if any(kw in line.lower() for kw in ("warn", "error", "invalid", "repair"))
    ]

    return json.dumps({
        "valid": result.ok and not any("error" in w.lower() for w in warnings),
        "warnings": warnings[:20],
        "elapsed_ms": round(result.elapsed_ms),
        "stdout": result.stdout.strip()[-500:],
        "stderr": result.stderr.strip()[-500:],
    })


def register(tool_decorator: Callable) -> None:
    """Register all Bambu Studio tools with the MCP server."""
    tool_decorator(bambu_slice)
    tool_decorator(bambu_arrange)
    tool_decorator(bambu_validate)
