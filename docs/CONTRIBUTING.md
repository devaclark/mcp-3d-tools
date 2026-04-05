# Contributing to mcp-3d-tools

## Adding a New Tool Module

### 1. Create the module

Create `tools/your_tools.py`:

```python
"""Your tool category MCP tools."""
from __future__ import annotations

import json
import os
from typing import Callable

from utils.subprocess_runner import run as run_cmd

WORKSPACE = os.environ.get("WORKSPACE_ROOT", "/workspace")


def _resolve(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(WORKSPACE, path)


async def your_tool_name(
    input_file: str,
    output_file: str = "",
    timeout: int = 60,
) -> str:
    """One-line description of what this tool does.

    Args:
        input_file: Path to input file.
        output_file: Path to output file.
        timeout: Max execution time in seconds.

    Returns:
        JSON string with result data.
    """
    src = _resolve(input_file)
    # ... your implementation ...
    return json.dumps({"success": True, "output_file": dst})


def register(tool_decorator: Callable) -> None:
    """Register all tools in this category."""
    tool_decorator(your_tool_name)
```

### 2. Register the category

In `tools/registry.py`, add your module to `CATEGORY_MODULES`:

```python
CATEGORY_MODULES: dict[str, str] = {
    "openscad": "tools.openscad_tools",
    "bambu": "tools.bambu_tools",
    "your_category": "tools.your_tools",  # Add this line
}
```

### 3. Enable it

In `.env`, add the category:

```
MCP_TOOL_CATEGORIES=openscad,bambu,your_category
```

### 4. Update the Dockerfile (if needed)

If your tool requires a new binary, add it to the `apt-get install` or download section in the `Dockerfile`.

### 5. Rebuild

```bash
docker compose build
```

## Tool Function Guidelines

- All tool functions must be `async`.
- Accept simple types that serialize well over JSON-RPC: `str`, `int`, `float`, `bool`, `list`, `dict`.
- Return a JSON string (not a dict). FastMCP handles the serialization boundary.
- Include a complete docstring with `Args:` and `Returns:` sections — FastMCP uses these to generate the tool schema.
- Use `utils.subprocess_runner.run()` for any external process calls. Never use `os.system()` or bare `subprocess.run()`.
- Resolve all file paths through `_resolve()` to handle workspace-relative paths.
- Set reasonable default timeouts.

## Testing

### Smoke test (container starts and loads tools)

```bash
docker run --rm smithie-cad-mcp:latest python -c \
  "from tools.registry import load_tools; print('OK')"
```

### Tool-level test (renders a file)

```bash
docker run --rm -i -v /path/to/project:/workspace smithie-cad-mcp:latest \
  python -c "
import asyncio
from tools.openscad_tools import openscad_render
print(asyncio.run(openscad_render('path/to/file.scad')))
"
```

## Pull Request Checklist

- [ ] New tool function has a complete docstring
- [ ] `register()` function updated to include the new tool
- [ ] Category added to `CATEGORY_MODULES` if new
- [ ] Dockerfile updated if new system dependencies are needed
- [ ] `docs/TOOLS.md` updated with parameter table and examples
- [ ] `README.md` tool reference table updated
- [ ] Docker image builds successfully
- [ ] Smoke test passes
