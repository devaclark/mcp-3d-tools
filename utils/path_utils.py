"""Shared path resolution utilities for all tool categories."""
from __future__ import annotations

import fnmatch
import os
from datetime import datetime, timezone

WORKSPACE = os.environ.get("WORKSPACE_ROOT", "/workspace")

CAD_EXTENSIONS = {
    ".scad", ".stl", ".3mf", ".step", ".stp", ".iges", ".igs",
    ".obj", ".amf", ".dxf", ".svg", ".png", ".jpg", ".jpeg",
}


def resolve(path: str) -> str:
    """Resolve a workspace-relative path to an absolute container path."""
    if os.path.isabs(path):
        return path
    return os.path.join(WORKSPACE, path)


def relative(path: str) -> str:
    """Convert an absolute path back to workspace-relative."""
    abs_path = os.path.abspath(path)
    ws = os.path.abspath(WORKSPACE)
    if abs_path.startswith(ws):
        rel = os.path.relpath(abs_path, ws)
        return rel
    return path


def ensure_parent(path: str) -> str:
    """Create parent directories for the given path and return it."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def with_suffix(path: str, suffix: str) -> str:
    """Replace the file extension of a path."""
    return os.path.splitext(path)[0] + suffix


def workspace_glob(
    pattern: str = "*",
    extensions: set[str] | None = None,
    recursive: bool = True,
) -> list[dict]:
    """List files in the workspace matching a pattern.

    Returns a list of dicts with path, name, size, modified, and extension.
    """
    if extensions is None:
        extensions = CAD_EXTENSIONS

    results: list[dict] = []
    for root, _dirs, files in os.walk(WORKSPACE):
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if extensions and ext not in extensions:
                continue
            if pattern != "*" and not fnmatch.fnmatch(name.lower(), pattern.lower()):
                continue
            full = os.path.join(root, name)
            try:
                stat = os.stat(full)
                results.append({
                    "path": relative(full),
                    "name": name,
                    "extension": ext,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                })
            except OSError:
                continue
        if not recursive:
            break

    results.sort(key=lambda f: f.get("modified", ""), reverse=True)
    return results


def build_tree(root: str | None = None, max_depth: int = 4) -> str:
    """Build a text-based directory tree of the workspace."""
    if root is None:
        root = WORKSPACE

    lines: list[str] = [os.path.basename(root) + "/"]

    def _walk(directory: str, prefix: str, depth: int) -> None:
        if depth >= max_depth:
            return
        try:
            entries = sorted(os.listdir(directory))
        except OSError:
            return
        dirs = [e for e in entries if os.path.isdir(os.path.join(directory, e))
                and not e.startswith(".")]
        files = [e for e in entries if os.path.isfile(os.path.join(directory, e))
                 and not e.startswith(".")]

        items = [(d, True) for d in dirs] + [(f, False) for f in files]
        for i, (name, is_dir) in enumerate(items):
            connector = "--- " if i < len(items) - 1 else "--- "
            if is_dir:
                lines.append(f"{prefix}{connector}{name}/")
                extension = "|   " if i < len(items) - 1 else "    "
                _walk(os.path.join(directory, name), prefix + extension, depth + 1)
            else:
                lines.append(f"{prefix}{connector}{name}")

    _walk(root, "", 0)
    return "\n".join(lines)
