# Tool Reference

Complete reference for all tools exposed by `mcp-3d-tools`.

---

## OpenSCAD Tools

### `openscad_render`

Render an OpenSCAD `.scad` file to STL format.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `scad_file` | string | yes | — | Path to .scad file (absolute or workspace-relative) |
| `output_file` | string | no | `<scad_file>.stl` | Output STL path |
| `variables` | dict | no | `null` | OpenSCAD variable overrides (passed as `-D`) |
| `timeout` | int | no | `120` | Max render time in seconds |

**Returns:** JSON with `success`, `output_file`, `elapsed_ms`, `stdout`, `stderr`.

**Example:**

```json
{
  "scad_file": "jetson-orin-nano-shell-case/exports/camera_arm_arm.scad",
  "variables": {"fit_profile": "tight"},
  "timeout": 60
}
```

---

### `openscad_preview`

Render an OpenSCAD file to a PNG preview image.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `scad_file` | string | yes | — | Path to .scad file |
| `output_file` | string | no | `<scad_file>.png` | Output PNG path |
| `variables` | dict | no | `null` | Variable overrides |
| `imgsize` | string | no | `"1024,768"` | Image dimensions as `"width,height"` |
| `camera` | string | no | `""` | Camera parameters (translate/rotate/distance) |
| `timeout` | int | no | `60` | Max render time in seconds |

**Returns:** JSON with `success`, `output_file`, `elapsed_ms`, `stderr`.

**Camera examples:**

- Auto-fit (default): camera is omitted, `--autocenter --viewall` are used
- Manual: `"0,0,0,55,0,25,200"` (translateX,Y,Z,rotX,Y,Z,distance)

---

### `openscad_export_3mf`

Render an OpenSCAD file directly to 3MF geometry format.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `scad_file` | string | yes | — | Path to .scad file |
| `output_file` | string | no | `<scad_file>.3mf` | Output 3MF path |
| `variables` | dict | no | `null` | Variable overrides |
| `timeout` | int | no | `120` | Max render time in seconds |

**Returns:** JSON with `success`, `output_file`, `elapsed_ms`, `stderr`.

---

### `openscad_measure`

Measure an STL file: bounding box dimensions, triangle count, and estimated volume.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `stl_file` | string | yes | — | Path to .stl file |

**Returns:** JSON with `file`, `triangles`, `bounding_box` (min/max/size), `volume_mm3`.

**Example output:**

```json
{
  "file": "/workspace/output/stl/camera_arm_arm.stl",
  "triangles": 540,
  "bounding_box": {
    "min": {"x": 5.0, "y": -20.0, "z": 0.0},
    "max": {"x": 16.0, "y": 20.0, "z": 10.0},
    "size": {"width": 11.0, "depth": 40.0, "height": 10.0}
  },
  "volume_mm3": 2847.523
}
```

---

## Bambu Studio Tools

### `bambu_slice`

Slice one or more STL files and export a print-ready 3MF file.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `stl_files` | list[string] | yes | — | List of STL file paths |
| `output_file` | string | no | `<first_stl>_sliced.3mf` | Output 3MF path |
| `arrange` | bool | no | `true` | Auto-arrange parts on build plate |
| `orient` | bool | no | `true` | Auto-orient parts for printing |
| `timeout` | int | no | `180` | Max slice time in seconds |

**Returns:** JSON with `success`, `output_file`, `input_files`, `elapsed_ms`, `stdout`, `stderr`.

**Preset configuration:** Printer and filament presets are set via environment variables (`BAMBU_PRINTER_PRESET`, `BAMBU_FILAMENT_PRESET`).

---

### `bambu_arrange`

Auto-arrange STL parts on the build plate and export 3MF without slicing.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `stl_files` | list[string] | yes | — | List of STL file paths |
| `output_file` | string | no | `arranged_output.3mf` | Output 3MF path |
| `timeout` | int | no | `120` | Max time in seconds |

**Returns:** JSON with `success`, `output_file`, `elapsed_ms`, `stderr`.

---

### `bambu_validate`

Dry-run slice to check STL files for printability without producing output.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `stl_files` | list[string] | yes | — | List of STL file paths to validate |
| `timeout` | int | no | `120` | Max time in seconds |

**Returns:** JSON with `valid`, `warnings` (list of error/warning lines), `elapsed_ms`, `stdout`, `stderr`.

---

## Chaining Tools

Tools are designed to be chained in sequence. Common workflows:

### Design iteration

```
openscad_render → openscad_measure → (adjust variables) → openscad_render
```

### Render to print

```
openscad_render → openscad_measure → bambu_validate → bambu_slice
```

### Multi-profile export

```
for profile in [tight, normal, loose]:
    openscad_render(variables={"fit_profile": profile})
    openscad_measure(stl_file=...)
```
