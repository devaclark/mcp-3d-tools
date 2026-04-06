"""Workspace awareness MCP tools: list, tree, read, search, recent.

Give the AI spatial awareness of the project so it can discover files,
understand structure, and suggest what to work on.
"""
from __future__ import annotations

import fnmatch
import json
import os
import logging
from typing import Callable

from utils.path_utils import (
    resolve, relative, workspace_glob, build_tree,
    WORKSPACE, CAD_EXTENSIONS,
)
from utils.content_helpers import error_response

logger = logging.getLogger(__name__)


async def workspace_list(
    pattern: str = "*",
    extensions: str = "",
) -> list:
    """List all CAD-related files in the workspace with metadata.

    Discovers .scad, .stl, .3mf, .step, .png, and other CAD files,
    sorted by most recently modified.

    Args:
        pattern: Filename glob pattern (e.g. "camera_*" or "*.stl").
        extensions: Comma-separated list of extensions to filter (e.g. ".stl,.scad").
            Defaults to all CAD-related extensions.

    Returns:
        JSON string with list of files and their metadata.
    """
    ext_set: set[str] | None = None
    if extensions:
        ext_set = {e.strip().lower() if e.strip().startswith(".")
                   else f".{e.strip().lower()}" for e in extensions.split(",")}

    files = workspace_glob(pattern=pattern, extensions=ext_set)

    by_type: dict[str, int] = {}
    for f in files:
        ext = f["extension"]
        by_type[ext] = by_type.get(ext, 0) + 1

    return [json.dumps({
        "workspace": WORKSPACE,
        "total_files": len(files),
        "by_extension": by_type,
        "files": files,
    })]


async def workspace_tree(
    root: str = "",
    max_depth: int = 4,
) -> list:
    """Return a visual directory tree of the workspace or a subdirectory.

    Provides a bird's-eye view of the project structure for orientation.

    Args:
        root: Subdirectory to start from (workspace-relative). Defaults to workspace root.
        max_depth: Maximum directory depth to traverse.

    Returns:
        The directory tree as formatted text.
    """
    start = resolve(root) if root else WORKSPACE
    if not os.path.isdir(start):
        return error_response(f"Directory not found: {start}")

    tree = build_tree(start, max_depth=max_depth)
    return [tree]


async def workspace_read(
    file_path: str,
    max_lines: int = 500,
) -> list:
    """Read the contents of a file in the workspace.

    Useful for the AI to read OpenSCAD source code, configuration files,
    or any text file to understand the design.

    Args:
        file_path: Path to file (absolute or workspace-relative).
        max_lines: Maximum number of lines to return (prevents huge file dumps).

    Returns:
        JSON string with file contents and metadata.
    """
    src = resolve(file_path)
    if not os.path.isfile(src):
        return error_response(f"File not found: {src}")

    try:
        stat = os.stat(src)
        with open(src, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception as exc:
        return error_response(f"Cannot read file: {exc}")

    total_lines = len(lines)
    truncated = total_lines > max_lines
    content = "".join(lines[:max_lines])

    return [json.dumps({
        "file": src,
        "relative_path": relative(src),
        "size_bytes": stat.st_size,
        "total_lines": total_lines,
        "truncated": truncated,
        "content": content,
    })]


async def workspace_search(
    query: str,
    pattern: str = "*",
    extensions: str = "",
    max_results: int = 50,
) -> list:
    """Search workspace files by name or content.

    If query looks like a glob pattern (contains * or ?), matches filenames.
    Otherwise, searches file contents for the query string.

    Args:
        query: Search term — filename pattern or content substring.
        pattern: Additional filename glob filter.
        extensions: Comma-separated extension filter.
        max_results: Maximum number of results to return.

    Returns:
        JSON string with matching files and context.
    """
    ext_set: set[str] | None = None
    if extensions:
        ext_set = {e.strip().lower() if e.strip().startswith(".")
                   else f".{e.strip().lower()}" for e in extensions.split(",")}

    is_name_search = "*" in query or "?" in query

    results: list[dict] = []

    if is_name_search:
        all_files = workspace_glob(pattern=query, extensions=ext_set)
        results = all_files[:max_results]
    else:
        text_exts = {".scad", ".py", ".txt", ".md", ".json", ".yaml", ".yml",
                     ".toml", ".cfg", ".ini", ".csv", ".svg", ".dxf"}
        search_exts = ext_set if ext_set else text_exts
        all_files = workspace_glob(pattern=pattern, extensions=search_exts)

        query_lower = query.lower()
        for f in all_files:
            if len(results) >= max_results:
                break
            full_path = resolve(f["path"])
            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as fh:
                    for line_no, line in enumerate(fh, 1):
                        if query_lower in line.lower():
                            results.append({
                                **f,
                                "match_line": line_no,
                                "match_text": line.strip()[:200],
                            })
                            break
            except Exception:
                continue

    return [json.dumps({
        "query": query,
        "search_type": "filename" if is_name_search else "content",
        "total_results": len(results),
        "results": results,
    })]


async def workspace_recent(
    count: int = 10,
    extensions: str = "",
) -> list:
    """Show the most recently modified files in the workspace.

    Helps the AI pick up where you left off by showing what was
    changed most recently.

    Args:
        count: Number of recent files to return.
        extensions: Comma-separated extension filter.

    Returns:
        JSON string with recently modified files.
    """
    ext_set: set[str] | None = None
    if extensions:
        ext_set = {e.strip().lower() if e.strip().startswith(".")
                   else f".{e.strip().lower()}" for e in extensions.split(",")}

    files = workspace_glob(extensions=ext_set)
    recent = files[:count]

    return [json.dumps({
        "workspace": WORKSPACE,
        "count": len(recent),
        "recent_files": recent,
    })]


def register(tool_decorator: Callable) -> None:
    """Register all workspace tools with the MCP server."""
    tool_decorator(workspace_list)
    tool_decorator(workspace_tree)
    tool_decorator(workspace_read)
    tool_decorator(workspace_search)
    tool_decorator(workspace_recent)
