"""Bambu Studio CLI MCP tools: slice, arrange, validate, estimate, compare, and profile.

Complete print intelligence — from slicing to cost estimation and material comparison.
"""
from __future__ import annotations

import json
import os
import re
import logging
from typing import Callable

from utils.subprocess_runner import run as run_cmd
from utils.path_utils import resolve, ensure_parent, with_suffix, WORKSPACE
from utils.content_helpers import error_response

logger = logging.getLogger(__name__)

BAMBU_BIN = os.environ.get("BAMBU_BIN", "/opt/bambu-studio/bambu-studio")


def _settings_args(
    printer_override: str = "",
    filament_override: str = "",
) -> list[str]:
    """Build --load-settings and --load-filaments from env presets or overrides."""
    args: list[str] = []
    printer = printer_override or os.environ.get("BAMBU_PRINTER_PRESET", "")
    filament = filament_override or os.environ.get("BAMBU_FILAMENT_PRESET", "")
    process = os.environ.get("BAMBU_PROCESS_PRESET", "")

    if printer or process:
        parts = [p for p in [printer, process] if p]
        args.extend(["--load-settings", ";".join(parts)])
    if filament:
        args.extend(["--load-filaments", filament])
    return args


def _parse_slicer_stats(output: str) -> dict:
    """Extract print time, filament usage, and other stats from slicer output."""
    stats: dict = {}

    time_match = re.search(r"total\s+print\s+time\s*[:=]\s*(.+)", output, re.IGNORECASE)
    if time_match:
        stats["print_time"] = time_match.group(1).strip()

    filament_g = re.search(r"filament\s+(?:used|usage)\s*[:=]\s*([\d.]+)\s*g", output, re.IGNORECASE)
    if filament_g:
        stats["filament_grams"] = float(filament_g.group(1))

    filament_m = re.search(r"filament\s+(?:used|usage)\s*[:=]\s*([\d.]+)\s*m", output, re.IGNORECASE)
    if filament_m:
        stats["filament_meters"] = float(filament_m.group(1))

    layers_match = re.search(r"total\s+layers?\s*[:=]\s*(\d+)", output, re.IGNORECASE)
    if layers_match:
        stats["total_layers"] = int(layers_match.group(1))

    return stats


async def bambu_slice(
    stl_files: list[str],
    output_file: str = "",
    arrange: bool = True,
    orient: bool = True,
    timeout: int = 180,
) -> list:
    """Slice one or more STL files and export a print-ready 3MF.

    Args:
        stl_files: List of STL file paths (absolute or workspace-relative).
        output_file: Output .3mf path. Defaults to first STL name + _sliced.3mf.
        arrange: Auto-arrange parts on the build plate.
        orient: Auto-orient parts for optimal printing.
        timeout: Max slice time in seconds.

    Returns:
        JSON string with slicing result including print statistics.
    """
    resolved = [resolve(f) for f in stl_files]
    if not output_file:
        base = os.path.splitext(resolved[0])[0]
        output_file = f"{base}_sliced.3mf"
    dst = ensure_parent(resolve(output_file))

    args = [BAMBU_BIN]
    if orient:
        args.append("--orient")
    if arrange:
        args.extend(["--arrange", "1"])

    args.extend(_settings_args())
    args.extend(["--slice", "0", "--export-3mf", dst])
    args.extend(resolved)

    result = await run_cmd(args, timeout=timeout)

    combined = result.stdout + "\n" + result.stderr
    stats = _parse_slicer_stats(combined)

    return [json.dumps({
        "success": result.ok,
        "output_file": dst,
        "input_files": resolved,
        "elapsed_ms": round(result.elapsed_ms),
        "print_stats": stats,
        "stdout": result.stdout.strip()[-1000:],
        "stderr": result.stderr.strip()[-1000:],
    })]


async def bambu_arrange(
    stl_files: list[str],
    output_file: str = "",
    timeout: int = 120,
) -> list:
    """Auto-arrange STL parts on the build plate and export 3MF (no slicing).

    Args:
        stl_files: List of STL file paths.
        output_file: Output .3mf path.
        timeout: Max time in seconds.

    Returns:
        JSON string with arrangement result.
    """
    resolved = [resolve(f) for f in stl_files]
    if not output_file:
        output_file = os.path.join(WORKSPACE, "arranged_output.3mf")
    dst = ensure_parent(resolve(output_file))

    args = [BAMBU_BIN, "--orient", "--arrange", "1"]
    args.extend(_settings_args())
    args.extend(["--export-3mf", dst])
    args.extend(resolved)

    result = await run_cmd(args, timeout=timeout)

    return [json.dumps({
        "success": result.ok,
        "output_file": dst,
        "elapsed_ms": round(result.elapsed_ms),
        "stderr": result.stderr.strip()[-500:],
    })]


async def bambu_validate(
    stl_files: list[str],
    timeout: int = 120,
) -> list:
    """Dry-run slice to validate STL files for printability without exporting.

    Args:
        stl_files: List of STL file paths to validate.
        timeout: Max time in seconds.

    Returns:
        JSON string with validation result (errors/warnings from slicer).
    """
    resolved = [resolve(f) for f in stl_files]

    args = [BAMBU_BIN, "--orient", "--arrange", "1"]
    args.extend(_settings_args())
    args.extend(["--slice", "0", "--debug", "3"])
    args.extend(resolved)

    result = await run_cmd(args, timeout=timeout)

    warnings = [
        line for line in result.stderr.splitlines()
        if any(kw in line.lower() for kw in ("warn", "error", "invalid", "repair"))
    ]

    return [json.dumps({
        "valid": result.ok and not any("error" in w.lower() for w in warnings),
        "warnings": warnings[:20],
        "elapsed_ms": round(result.elapsed_ms),
        "stdout": result.stdout.strip()[-500:],
        "stderr": result.stderr.strip()[-500:],
    })]


async def bambu_estimate(
    stl_files: list[str],
    filament_cost_per_kg: float = 25.0,
    timeout: int = 180,
) -> list:
    """Estimate print time, filament usage, and material cost.

    Runs a full slice to extract accurate estimates from the slicer engine.

    Args:
        stl_files: List of STL file paths.
        filament_cost_per_kg: Cost per kilogram of filament in your currency.
        timeout: Max slice time in seconds.

    Returns:
        JSON string with print time, filament weight/length, and estimated cost.
    """
    resolved = [resolve(f) for f in stl_files]

    args = [BAMBU_BIN, "--orient", "--arrange", "1"]
    args.extend(_settings_args())
    args.extend(["--slice", "0"])
    args.extend(resolved)

    result = await run_cmd(args, timeout=timeout)

    combined = result.stdout + "\n" + result.stderr
    stats = _parse_slicer_stats(combined)

    cost = None
    if stats.get("filament_grams"):
        cost = round(stats["filament_grams"] / 1000.0 * filament_cost_per_kg, 2)

    return [json.dumps({
        "success": result.ok,
        "input_files": resolved,
        "print_time": stats.get("print_time"),
        "filament_grams": stats.get("filament_grams"),
        "filament_meters": stats.get("filament_meters"),
        "total_layers": stats.get("total_layers"),
        "estimated_cost": cost,
        "cost_per_kg": filament_cost_per_kg,
        "elapsed_ms": round(result.elapsed_ms),
    })]


async def bambu_compare_materials(
    stl_files: list[str],
    filament_presets: list[str],
    timeout_per_slice: int = 180,
) -> list:
    """Compare how a model prints with different filament presets.

    Slices the same model with each filament and compares print time,
    filament usage, and cost.

    Args:
        stl_files: List of STL file paths.
        filament_presets: List of Bambu filament preset names to compare.
        timeout_per_slice: Max slice time per material in seconds.

    Returns:
        JSON string with per-material comparison data.
    """
    resolved = [resolve(f) for f in stl_files]
    comparisons: list[dict] = []

    for preset in filament_presets:
        args = [BAMBU_BIN, "--orient", "--arrange", "1"]
        args.extend(_settings_args(filament_override=preset))
        args.extend(["--slice", "0"])
        args.extend(resolved)

        result = await run_cmd(args, timeout=timeout_per_slice)
        combined = result.stdout + "\n" + result.stderr
        stats = _parse_slicer_stats(combined)

        comparisons.append({
            "filament_preset": preset,
            "slice_success": result.ok,
            "print_time": stats.get("print_time"),
            "filament_grams": stats.get("filament_grams"),
            "filament_meters": stats.get("filament_meters"),
            "total_layers": stats.get("total_layers"),
            "elapsed_ms": round(result.elapsed_ms),
        })

    return [json.dumps({
        "success": True,
        "input_files": resolved,
        "materials_compared": len(comparisons),
        "comparisons": comparisons,
    })]


async def bambu_profile_list() -> list:
    """List available printer, filament, and process presets.

    Returns the presets configured via environment variables and any
    additional presets discovered from the Bambu Studio configuration.

    Returns:
        JSON string with available presets.
    """
    presets = {
        "printer_preset": os.environ.get("BAMBU_PRINTER_PRESET", "not set"),
        "filament_preset": os.environ.get("BAMBU_FILAMENT_PRESET", "not set"),
        "process_preset": os.environ.get("BAMBU_PROCESS_PRESET", "not set"),
    }

    bambu_config_dir = "/opt/bambu-studio/squashfs-root/resources/profiles"
    discovered: dict[str, list[str]] = {
        "printers": [],
        "filaments": [],
        "processes": [],
    }

    for category in discovered:
        cat_dir = os.path.join(bambu_config_dir, category)
        if os.path.isdir(cat_dir):
            try:
                for f in sorted(os.listdir(cat_dir)):
                    if f.endswith(".json"):
                        discovered[category].append(os.path.splitext(f)[0])
            except OSError:
                pass

    return [json.dumps({
        "current_presets": presets,
        "available": discovered,
        "bambu_bin": BAMBU_BIN,
        "bambu_bin_exists": os.path.isfile(BAMBU_BIN),
    })]


def register(tool_decorator: Callable) -> None:
    """Register all Bambu Studio tools with the MCP server."""
    tool_decorator(bambu_slice)
    tool_decorator(bambu_arrange)
    tool_decorator(bambu_validate)
    tool_decorator(bambu_estimate)
    tool_decorator(bambu_compare_materials)
    tool_decorator(bambu_profile_list)
