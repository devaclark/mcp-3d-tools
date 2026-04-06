# Tool Reference

Complete reference for all tools exposed by `mcp-3d-tools`.

---

## OpenSCAD Tools

### `openscad_render`

Render an OpenSCAD `.scad` file to STL format. Returns an inline preview image directly in chat.

**Parameters:**

| Name          | Type   | Required | Default           | Description                                         |
| ------------- | ------ | -------- | ----------------- | --------------------------------------------------- |
| `scad_file`   | string | yes      | --                | Path to .scad file (absolute or workspace-relative) |
| `output_file` | string | no       | `<scad_file>.stl` | Output STL path                                     |
| `variables`   | dict   | no       | `null`            | OpenSCAD variable overrides (passed as `-D`)        |
| `preview`     | bool   | no       | `true`            | Generate and return an inline PNG preview            |
| `timeout`     | int    | no       | `120`             | Max render time in seconds                          |

**Returns:** JSON with `success`, `output_file`, `elapsed_ms`, `preview_file` + inline image.

---

### `openscad_preview`

Render an OpenSCAD file to a PNG preview image, displayed inline in chat.

**Parameters:**

| Name          | Type   | Required | Default           | Description                                   |
| ------------- | ------ | -------- | ----------------- | --------------------------------------------- |
| `scad_file`   | string | yes      | --                | Path to .scad file                            |
| `output_file` | string | no       | `<scad_file>.png` | Output PNG path                               |
| `variables`   | dict   | no       | `null`            | Variable overrides                            |
| `imgsize`     | string | no       | `"1024,768"`      | Image dimensions as `"width,height"`          |
| `camera`      | string | no       | `""`              | Camera parameters (translate/rotate/distance) |
| `timeout`     | int    | no       | `60`              | Max render time in seconds                    |

**Returns:** JSON with `success`, `output_file`, `elapsed_ms` + inline image.

---

### `openscad_export_3mf`

Render an OpenSCAD file directly to 3MF geometry format.

**Parameters:**

| Name          | Type   | Required | Default           | Description                |
| ------------- | ------ | -------- | ----------------- | -------------------------- |
| `scad_file`   | string | yes      | --                | Path to .scad file         |
| `output_file` | string | no       | `<scad_file>.3mf` | Output 3MF path            |
| `variables`   | dict   | no       | `null`            | Variable overrides         |
| `timeout`     | int    | no       | `120`             | Max render time in seconds |

**Returns:** JSON with `success`, `output_file`, `elapsed_ms`.

---

### `openscad_measure`

Measure an STL file: bounding box dimensions, triangle count, and estimated volume.

**Parameters:**

| Name       | Type   | Required | Default | Description       |
| ---------- | ------ | -------- | ------- | ----------------- |
| `stl_file` | string | yes      | --      | Path to .stl file |

**Returns:** JSON with `file`, `triangles`, `bounding_box`, `volume_mm3`.

---

### `openscad_lint`

Syntax-check an OpenSCAD file without rendering (fast feedback loop).

**Parameters:**

| Name        | Type   | Required | Default | Description       |
| ----------- | ------ | -------- | ------- | ----------------- |
| `scad_file` | string | yes      | --      | Path to .scad file |
| `timeout`   | int    | no       | `30`    | Max time in seconds |

**Returns:** JSON with `valid`, `errors`, `warnings`, `elapsed_ms`.

---

### `openscad_list_params`

Parse a SCAD file and extract all parametric variable declarations with defaults and Customizer annotations.

**Parameters:**

| Name        | Type   | Required | Default | Description       |
| ----------- | ------ | -------- | ------- | ----------------- |
| `scad_file` | string | yes      | --      | Path to .scad file |

**Returns:** JSON with `parameters` list (name, default, line, annotation, customizer_hint).

---

### `openscad_sweep`

Sweep a variable across values, render each variant, measure each, and return a visual comparison with dimensional data.

**Parameters:**

| Name                 | Type          | Required | Default                      | Description                     |
| -------------------- | ------------- | -------- | ---------------------------- | ------------------------------- |
| `scad_file`          | string        | yes      | --                           | Path to .scad file              |
| `variable`           | string        | yes      | --                           | Variable name to sweep          |
| `values`             | list          | yes      | --                           | Values to assign                |
| `output_dir`         | string        | no       | `sweep_<variable>`           | Output directory                |
| `timeout_per_render` | int           | no       | `120`                        | Max time per variant in seconds |

**Returns:** JSON with per-variant measurements + inline preview images for each variant.

---

### `openscad_diff`

Compare two STL files and report dimensional differences.

**Parameters:**

| Name          | Type   | Required | Default | Description            |
| ------------- | ------ | -------- | ------- | ---------------------- |
| `stl_file_a`  | string | yes      | --      | First STL file         |
| `stl_file_b`  | string | yes      | --      | Second STL file        |
| `label_a`     | string | no       | `"A"`   | Label for first model  |
| `label_b`     | string | no       | `"B"`   | Label for second model |

**Returns:** JSON with measurements for both models and per-axis deltas.

---

## Visual Tools

### `stl_preview`

Render any STL file to a PNG preview image, displayed inline in chat. No OpenSCAD source required.

**Parameters:**

| Name           | Type   | Required | Default      | Description                               |
| -------------- | ------ | -------- | ------------ | ----------------------------------------- |
| `stl_file`     | string | yes      | --           | Path to .stl file                         |
| `output_file`  | string | no       | auto         | Output PNG path                           |
| `camera_angle` | string | no       | `"isometric"` | Preset or `"azimuth,elevation"` degrees  |
| `width`        | int    | no       | `1024`       | Image width in pixels                     |
| `height`       | int    | no       | `768`        | Image height in pixels                    |

**Camera presets:** `isometric`, `front`, `back`, `left`, `right`, `top`, `bottom`

**Returns:** JSON metadata + inline image.

---

### `turntable_preview`

Generate a multi-angle turntable view of an STL model. Returns all images inline.

**Parameters:**

| Name         | Type   | Required | Default | Description                    |
| ------------ | ------ | -------- | ------- | ------------------------------ |
| `stl_file`   | string | yes      | --      | Path to .stl file              |
| `output_dir` | string | no       | auto    | Output directory               |
| `angles`     | int    | no       | `6`     | Number of viewing angles       |
| `width`      | int    | no       | `512`   | Image width per frame          |
| `height`     | int    | no       | `512`   | Image height per frame         |
| `elevation`  | float  | no       | `25.0`  | Camera elevation in degrees    |

**Returns:** JSON metadata + multiple inline images.

---

### `compare_models`

Side-by-side visual comparison of two STL files with dimensional data.

**Parameters:**

| Name           | Type   | Required | Default      | Description          |
| -------------- | ------ | -------- | ------------ | -------------------- |
| `stl_file_a`   | string | yes      | --           | First STL file       |
| `stl_file_b`   | string | yes      | --           | Second STL file      |
| `label_a`      | string | no       | `"Model A"`  | Label for first      |
| `label_b`      | string | no       | `"Model B"`  | Label for second     |
| `camera_angle` | string | no       | `"isometric"` | Camera preset       |
| `width`        | int    | no       | `800`        | Image width          |
| `height`       | int    | no       | `600`        | Image height         |

**Returns:** JSON with both measurements and deltas + inline images of both models.

---

### `cross_section_preview`

Generate a 2D cross-section view of an STL at a given Z-height.

**Parameters:**

| Name          | Type   | Required | Default     | Description               |
| ------------- | ------ | -------- | ----------- | ------------------------- |
| `stl_file`    | string | yes      | --          | Path to .stl file         |
| `z_height`    | float  | no       | model midpoint | Z-height for cut plane |
| `output_file` | string | no       | auto        | Output PNG path           |
| `width`       | int    | no       | `1024`      | Image width               |
| `height`      | int    | no       | `768`       | Image height              |

**Returns:** JSON metadata + inline cross-section image.

---

## Mesh Tools

### `mesh_analyze`

Comprehensive mesh analysis: manifold check, surface area, center of mass, overhang detection, thin wall detection, and triangle quality statistics.

**Parameters:**

| Name       | Type   | Required | Default | Description       |
| ---------- | ------ | -------- | ------- | ----------------- |
| `stl_file` | string | yes      | --      | Path to .stl file |

**Returns:** JSON with `is_watertight`, `surface_area_mm2`, `volume_mm3`, `center_of_mass`, `overhangs`, `thin_faces`, `face_area_stats`, `repair_needed`.

---

### `mesh_repair`

Auto-fix common mesh issues for 3D printing.

**Parameters:**

| Name                | Type   | Required | Default                  | Description                 |
| ------------------- | ------ | -------- | ------------------------ | --------------------------- |
| `stl_file`          | string | yes      | --                       | Input STL file              |
| `output_file`       | string | no       | `<name>_repaired.stl`    | Output repaired STL         |
| `fix_normals`       | bool   | no       | `true`                   | Fix face normals/winding    |
| `fill_holes`        | bool   | no       | `true`                   | Fill holes in the mesh      |
| `remove_degenerate` | bool   | no       | `true`                   | Remove degenerate triangles |

**Returns:** JSON with `repairs_applied`, `before`/`after` metrics.

---

### `mesh_simplify`

Reduce triangle count while preserving shape.

**Parameters:**

| Name           | Type   | Required | Default                    | Description                   |
| -------------- | ------ | -------- | -------------------------- | ----------------------------- |
| `stl_file`     | string | yes      | --                         | Input STL file                |
| `target_ratio` | float  | no       | `0.5`                      | Ratio of faces to keep (0-1)  |
| `output_file`  | string | no       | `<name>_simplified.stl`    | Output simplified STL         |

**Returns:** JSON with `original_faces`, `actual_faces`, `reduction_percent`.

---

### `mesh_boolean`

Boolean operation on two STL meshes.

**Parameters:**

| Name          | Type   | Required | Default  | Description                                 |
| ------------- | ------ | -------- | -------- | ------------------------------------------- |
| `stl_file_a`  | string | yes      | --       | First STL file                              |
| `stl_file_b`  | string | yes      | --       | Second STL file                             |
| `operation`   | string | no       | `"union"` | `"union"`, `"difference"`, `"intersection"` |
| `output_file` | string | no       | auto     | Output STL file                             |

**Returns:** JSON with `result_triangles`, `result_is_watertight`.

---

## Bambu Studio Tools

### `bambu_slice`

Slice one or more STL files and export a print-ready 3MF file.

**Parameters:**

| Name          | Type         | Required | Default                  | Description                       |
| ------------- | ------------ | -------- | ------------------------ | --------------------------------- |
| `stl_files`   | list[string] | yes      | --                       | List of STL file paths            |
| `output_file` | string       | no       | `<first_stl>_sliced.3mf` | Output 3MF path                  |
| `arrange`     | bool         | no       | `true`                   | Auto-arrange parts on build plate |
| `orient`      | bool         | no       | `true`                   | Auto-orient parts for printing    |
| `timeout`     | int          | no       | `180`                    | Max slice time in seconds         |

**Returns:** JSON with `success`, `output_file`, `print_stats`.

---

### `bambu_arrange`

Auto-arrange STL parts on the build plate and export 3MF without slicing.

**Parameters:**

| Name          | Type         | Required | Default               | Description            |
| ------------- | ------------ | -------- | --------------------- | ---------------------- |
| `stl_files`   | list[string] | yes      | --                    | List of STL file paths |
| `output_file` | string       | no       | `arranged_output.3mf` | Output 3MF path        |
| `timeout`     | int          | no       | `120`                 | Max time in seconds    |

**Returns:** JSON with `success`, `output_file`.

---

### `bambu_validate`

Dry-run slice to check STL files for printability without producing output.

**Parameters:**

| Name        | Type         | Required | Default | Description                        |
| ----------- | ------------ | -------- | ------- | ---------------------------------- |
| `stl_files` | list[string] | yes      | --      | List of STL file paths to validate |
| `timeout`   | int          | no       | `120`   | Max time in seconds                |

**Returns:** JSON with `valid`, `warnings`.

---

### `bambu_estimate`

Estimate print time, filament usage, and material cost by running a full slice.

**Parameters:**

| Name                   | Type         | Required | Default | Description                     |
| ---------------------- | ------------ | -------- | ------- | ------------------------------- |
| `stl_files`            | list[string] | yes      | --      | List of STL file paths          |
| `filament_cost_per_kg` | float        | no       | `25.0`  | Cost per kg in your currency    |
| `timeout`              | int          | no       | `180`   | Max slice time in seconds       |

**Returns:** JSON with `print_time`, `filament_grams`, `filament_meters`, `estimated_cost`.

---

### `bambu_compare_materials`

Compare how a model prints with different filament presets.

**Parameters:**

| Name                | Type         | Required | Default | Description                       |
| ------------------- | ------------ | -------- | ------- | --------------------------------- |
| `stl_files`         | list[string] | yes      | --      | List of STL file paths            |
| `filament_presets`  | list[string] | yes      | --      | Filament preset names to compare  |
| `timeout_per_slice` | int          | no       | `180`   | Max time per material in seconds  |

**Returns:** JSON with per-material `print_time`, `filament_grams`, `total_layers`.

---

### `bambu_profile_list`

List available printer, filament, and process presets.

**Returns:** JSON with `current_presets` and `available` presets.

---

## Workspace Tools

### `workspace_list`

List all CAD-related files in the workspace with metadata.

**Parameters:**

| Name         | Type   | Required | Default | Description                        |
| ------------ | ------ | -------- | ------- | ---------------------------------- |
| `pattern`    | string | no       | `"*"`   | Filename glob pattern              |
| `extensions` | string | no       | all CAD | Comma-separated extension filter   |

**Returns:** JSON with `files` list (path, size, modified, extension) and `by_extension` counts.

---

### `workspace_tree`

Return a visual directory tree of the workspace.

**Parameters:**

| Name        | Type   | Required | Default | Description              |
| ----------- | ------ | -------- | ------- | ------------------------ |
| `root`      | string | no       | `""`    | Subdirectory to start at |
| `max_depth` | int    | no       | `4`     | Max depth to traverse    |

**Returns:** Formatted text tree.

---

### `workspace_read`

Read the contents of a file in the workspace.

**Parameters:**

| Name        | Type   | Required | Default | Description              |
| ----------- | ------ | -------- | ------- | ------------------------ |
| `file_path` | string | yes      | --      | Path to file             |
| `max_lines` | int    | no       | `500`   | Max lines to return      |

**Returns:** JSON with `content`, `total_lines`, `truncated`.

---

### `workspace_search`

Search workspace files by name or content.

**Parameters:**

| Name          | Type   | Required | Default | Description                    |
| ------------- | ------ | -------- | ------- | ------------------------------ |
| `query`       | string | yes      | --      | Search term or filename glob   |
| `pattern`     | string | no       | `"*"`   | Additional filename filter     |
| `extensions`  | string | no       | `""`    | Extension filter               |
| `max_results` | int    | no       | `50`    | Max results                    |

**Returns:** JSON with `results` list and `search_type`.

---

### `workspace_recent`

Show recently modified files.

**Parameters:**

| Name         | Type   | Required | Default | Description          |
| ------------ | ------ | -------- | ------- | -------------------- |
| `count`      | int    | no       | `10`    | Number of files      |
| `extensions` | string | no       | `""`    | Extension filter     |

**Returns:** JSON with `recent_files` list.

---

## System Tools

### `cad_health`

Check system status: tool versions, disk space, Python dependencies.

**Returns:** JSON with OpenSCAD/Bambu availability, Python library status, disk usage, enabled categories.

---

### `cad_capabilities`

Return the full catalog of all available tools organized by category.

**Returns:** JSON with `catalog` containing every category, its tools, and descriptions.

---

### `cad_workflow`

Suggest the optimal tool chain for a given goal.

**Parameters:**

| Name   | Type   | Required | Default | Description                                |
| ------ | ------ | -------- | ------- | ------------------------------------------ |
| `goal` | string | no       | `""`    | What you want to accomplish                |

**Returns:** JSON with `recommended_workflow`, `steps`, and `alternatives`.

**Example goals:** `"print this part"`, `"compare two designs"`, `"explore parameter space"`, `"repair a mesh"`, `"see project overview"`

---

## Chaining Tools

Tools are designed to be chained in sequence. Common workflows:

### Render and view
```
openscad_preview(scad_file="...") → inline image in chat
```

### Render to print
```
openscad_render → mesh_analyze → bambu_validate → bambu_slice
```

### Design iteration with sweep
```
openscad_list_params → openscad_sweep(variable="wall", values=[1.5, 2.0, 2.5, 3.0])
```

### Repair and print
```
mesh_analyze → mesh_repair → mesh_analyze (verify) → bambu_slice
```

### Cost comparison
```
bambu_compare_materials(filament_presets=["PLA", "PETG", "ABS"])
```

### Project orientation
```
workspace_tree → workspace_list → workspace_recent
```
