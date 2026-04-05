# Architecture

This document describes the internal architecture of `mcp-3d-tools`.

## Transport: stdio over Docker

The MCP server communicates with the IDE using **stdio transport**. Cursor IDE spawns a Docker container as a subprocess:

```
docker run --rm -i smithie-cad-mcp:latest
```

- **`--rm`**: Container is destroyed when the IDE disconnects (no stale state).
- **`-i`**: Interactive mode keeps stdin open for bidirectional JSON-RPC communication.
- JSON-RPC messages flow over stdout (server -> IDE) and stdin (IDE -> server).
- Logging goes to stderr so it never contaminates the protocol stream.

### Why Docker instead of a native process?

1. **Isolation** — OpenSCAD and Bambu Studio CLI run inside the container with all their dependencies. The host only needs Docker.
2. **Portability** — Same image works on Windows, Linux, and macOS.
3. **Reproducibility** — Pinned versions of OpenSCAD and Bambu Studio. No "works on my machine" issues.
4. **Security** — The container only sees files in the mounted workspace volume.

## Plugin Registry

Tools are organized into **categories**, each backed by a Python module:

```
tools/
  registry.py          # Discovers and loads category modules
  openscad_tools.py    # Category: openscad
  bambu_tools.py       # Category: bambu
```

### Loading flow

1. `server.py` calls `load_tools(mcp.tool)` at startup.
2. `registry.py` reads `MCP_TOOL_CATEGORIES` from the environment.
3. For each enabled category, it imports the corresponding module via `CATEGORY_MODULES` mapping.
4. Each module's `register(tool_decorator)` function is called, which registers individual tool functions with FastMCP.

### Adding a new category

1. Create `tools/new_category_tools.py` with async tool functions.
2. Add a `register(tool_decorator)` function that calls `tool_decorator(fn)` for each tool.
3. Add `"new_category": "tools.new_category_tools"` to `CATEGORY_MODULES` in `registry.py`.
4. Add `new_category` to `MCP_TOOL_CATEGORIES` in `.env`.

No changes to `server.py` are needed.

## Volume Mount Bridge

The host filesystem is mounted into the container:

```
-v C:\smithie.co\research\cyber-deck:/workspace
```

- All tool functions resolve paths relative to `WORKSPACE_ROOT` (default `/workspace`).
- Tools can read .scad source files and write .stl/.3mf/.png output.
- The `_resolve()` helper in each tool module handles path normalization.

### Path resolution

```python
def _resolve(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(WORKSPACE, path)
```

The AI passes workspace-relative paths (e.g., `jetson-orin-nano-shell-case/exports/camera_arm_arm.scad`), and the tool resolves them to `/workspace/jetson-orin-nano-shell-case/exports/camera_arm_arm.scad` inside the container.

## Security Model

- **No secrets in the image**: All configuration is injected via `--env-file` at runtime.
- **No network access required**: Tools operate on local files only. The container can run with `--network=none` for extra isolation.
- **Read/write scope**: Limited to the mounted volume. The container cannot access files outside the workspace.
- **No persistent state**: `--rm` ensures the container is destroyed after each session.

## Headless Rendering

OpenSCAD requires a display server for rendering (even in CLI mode). The container runs Xvfb (X Virtual Framebuffer) in the background:

```bash
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
exec python server.py
```

This provides a virtual display without any GPU or physical monitor. The server process itself runs with clean stdout for MCP protocol communication.

## Subprocess Execution

All external tool invocations go through `utils/subprocess_runner.py`:

- **Async execution** via `asyncio.create_subprocess_exec`
- **Configurable timeout** (default 120s, overridable per call)
- **Structured output** via `RunResult` dataclass (exit code, stdout, stderr, timing, timeout flag)
- **Safe cleanup** — processes are killed on timeout
- **Logging** — all commands are logged to stderr with timing data
