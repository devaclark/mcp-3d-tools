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

from utils.path_utils import resolve, ensure_parent, with_suffix
from utils.content_helpers import success_with_image, error_response
from utils.subprocess_runner import run as run_cmd

WORKSPACE = os.environ.get("WORKSPACE_ROOT", "/workspace")


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
    src = resolve(input_file)
    if not os.path.isfile(src):
        return error_response(f"File not found: {src}")

    if not output_file:
        output_file = with_suffix(src, ".out")
    dst = ensure_parent(resolve(output_file))

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
    "visual": "tools.visual_tools",
    "mesh": "tools.mesh_tools",
    "workspace": "tools.workspace_tools",
    "system": "tools.system_tools",
    "your_category": "tools.your_tools",  # Add this line
}
```

### 3. Enable it

In `.env`, add the category:

```
MCP_TOOL_CATEGORIES=openscad,bambu,visual,mesh,workspace,system,your_category
```

### 4. Update the Dockerfile (if needed)

If your tool requires a new binary, add it to the `apt-get install` or download section in the `Dockerfile`.

### 5. Rebuild

```bash
docker compose build
```

## Shared Utilities

Use the shared utilities instead of duplicating code:

### Path resolution

```python
from utils.path_utils import resolve, ensure_parent, with_suffix, workspace_glob
```

- `resolve(path)` -- Convert workspace-relative path to absolute container path
- `ensure_parent(path)` -- Create parent directories and return the path
- `with_suffix(path, ".stl")` -- Replace file extension
- `workspace_glob(pattern, extensions)` -- List files matching a pattern

### Response builders

```python
from utils.content_helpers import success_with_image, success_with_images, error_response
```

- `success_with_image(metadata, image_path)` -- Return JSON + inline image
- `success_with_images(metadata, image_paths)` -- Return JSON + multiple images
- `error_response(message)` -- Return structured error JSON

### Subprocess execution

```python
from utils.subprocess_runner import run as run_cmd
```

Always use `run_cmd` for external processes. Never use `os.system()` or bare `subprocess.run()`.

### STL rendering

```python
from utils.render_engine import render_stl, render_turntable, render_cross_section
```

Use the render engine to generate PNG previews of STL files for inline chat display.

## Returning Inline Images

To return images that display directly in chat, use `success_with_image`:

```python
from utils.content_helpers import success_with_image

async def my_visual_tool(stl_file: str) -> list:
    # ... generate a PNG ...
    metadata = {"success": True, "output_file": png_path}
    return success_with_image(metadata, png_path)
```

The function returns a list containing a JSON string and a FastMCP `Image` object. Cursor renders the image inline.

## Tool Function Guidelines

- All tool functions must be `async`.
- Accept simple types that serialize well over JSON-RPC: `str`, `int`, `float`, `bool`, `list`, `dict`.
- Return a JSON string or a list (for multi-content responses with images).
- Include a complete docstring with `Args:` and `Returns:` sections -- FastMCP uses these to generate the tool schema.
- Use shared utilities (`path_utils`, `content_helpers`, `subprocess_runner`).
- Set reasonable default timeouts.
- Update `system_tools.py` `TOOL_CATALOG` and `WORKFLOW_TEMPLATES` if adding tools that fit existing workflows.

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

### Check all categories load

```bash
docker run --rm -e MCP_TOOL_CATEGORIES=openscad,bambu,visual,mesh,workspace,system \
  smithie-cad-mcp:latest python -c "
from tools.registry import load_tools
loaded = load_tools(lambda f: print(f'  registered: {f.__name__}'))
print(f'Categories loaded: {loaded}')
"
```

## Pull Request Checklist

- New tool function has a complete docstring with `Args:` and `Returns:`
- `register()` function updated to include the new tool
- Category added to `CATEGORY_MODULES` if new
- Shared utilities used (`path_utils`, `content_helpers`) instead of duplicated code
- Dockerfile updated if new system dependencies are needed
- `docs/TOOLS.md` updated with parameter table and examples
- `docs/ARCHITECTURE.md` tool count updated
- `TOOL_CATALOG` in `system_tools.py` updated
- `README.md` tool reference table updated
- Docker image builds successfully
- Smoke test passes
