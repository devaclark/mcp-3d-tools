"""Universal 3D model rendering engine for visual previews.

Renders meshes and solids to PNG images from any supported format.
Backends: trimesh (STL/OBJ/PLY/3MF/GLB/DAE/AMF/OFF/DXF),
OpenCascade via cadquery (STEP/IGES/BREP).  All rendering is
off-screen via the Xvfb framebuffer in the Docker container.
"""
from __future__ import annotations

import logging
import math
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

CAMERA_PRESETS: dict[str, tuple[float, float]] = {
    "isometric": (45.0, 35.264),
    "front": (0.0, 0.0),
    "back": (180.0, 0.0),
    "left": (270.0, 0.0),
    "right": (90.0, 0.0),
    "top": (0.0, 90.0),
    "bottom": (0.0, -90.0),
}

TRIMESH_EXTENSIONS = {
    ".stl", ".obj", ".ply", ".off", ".glb", ".gltf",
    ".3mf", ".dae", ".amf", ".dxf",
}
OCP_EXTENSIONS = {".step", ".stp", ".iges", ".igs", ".brep", ".brp"}


@dataclass
class RenderResult:
    png_path: str
    width: int
    height: int
    camera_angle: str


def _load_mesh(file_path: str):
    """Load a 3D file as a trimesh mesh.

    Supports all trimesh-native formats directly.  For STEP/IGES/BREP,
    converts via OpenCascade (cadquery) into a tessellated trimesh mesh.
    """
    import trimesh

    ext = os.path.splitext(file_path)[1].lower()

    if ext in OCP_EXTENSIONS:
        return _load_via_ocp(file_path)

    return trimesh.load(file_path, force="mesh")


def _load_via_ocp(file_path: str):
    """Load STEP/IGES/BREP via cadquery + OpenCascade, return trimesh mesh."""
    import trimesh

    try:
        import cadquery as cq
    except ImportError:
        raise ImportError(
            "cadquery is required for STEP/IGES/BREP support.  "
            "Install with: pip install cadquery"
        )

    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".step", ".stp"):
        shape = cq.importers.importStep(file_path)
    elif ext in (".iges", ".igs"):
        shape = cq.importers.importStep(file_path)
    elif ext in (".brep", ".brp"):
        shape = cq.importers.importBrep(file_path)
    else:
        raise ValueError(f"Unsupported OCP format: {ext}")

    vertices, faces = shape.val().tessellate(tolerance=0.1)
    import numpy as np
    verts = np.array([(v.x, v.y, v.z) for v in vertices])
    tris = np.array([(f[0], f[1], f[2]) for f in faces])
    return trimesh.Trimesh(vertices=verts, faces=tris)


def _camera_transform(azimuth_deg: float, elevation_deg: float, distance: float):
    """Build a 4x4 camera transform from spherical coordinates."""
    import numpy as np

    az = math.radians(azimuth_deg)
    el = math.radians(elevation_deg)

    x = distance * math.cos(el) * math.sin(az)
    y = distance * math.cos(el) * math.cos(az)
    z = distance * math.sin(el)

    camera_pos = np.array([x, y, z])
    target = np.array([0.0, 0.0, 0.0])
    up = np.array([0.0, 0.0, 1.0])

    forward = target - camera_pos
    forward = forward / np.linalg.norm(forward)
    right = np.cross(forward, up)
    if np.linalg.norm(right) < 1e-6:
        up = np.array([0.0, 1.0, 0.0])
        right = np.cross(forward, up)
    right = right / np.linalg.norm(right)
    true_up = np.cross(right, forward)

    mat = np.eye(4)
    mat[:3, 0] = right
    mat[:3, 1] = true_up
    mat[:3, 2] = -forward
    mat[:3, 3] = camera_pos
    return mat


def render_model(
    file_path: str,
    output_path: str,
    camera_angle: str = "isometric",
    width: int = 1024,
    height: int = 768,
) -> RenderResult:
    """Render any supported 3D file to a PNG image.

    Supports STL, OBJ, PLY, 3MF, GLB, DAE, AMF, OFF, DXF, STEP, IGES, BREP.
    Uses pyrender for high-quality GL renders, matplotlib as fallback.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    mesh = _load_mesh(file_path)
    center = mesh.centroid
    mesh.apply_translation(-center)

    extents = mesh.extents
    max_extent = max(extents) if len(extents) else 1.0
    distance = max_extent * 2.5

    if camera_angle in CAMERA_PRESETS:
        az, el = CAMERA_PRESETS[camera_angle]
    else:
        parts = camera_angle.split(",")
        az = float(parts[0]) if len(parts) > 0 else 45.0
        el = float(parts[1]) if len(parts) > 1 else 35.264

    try:
        _render_with_pyrender(mesh, output_path, az, el, distance, width, height)
    except Exception as exc:
        logger.warning("pyrender failed (%s), falling back to matplotlib", exc)
        _render_with_matplotlib(mesh, output_path, az, el, distance, width, height)

    return RenderResult(
        png_path=output_path,
        width=width,
        height=height,
        camera_angle=camera_angle,
    )


# Backward-compatible alias
render_stl = render_model


def render_turntable(
    stl_path: str,
    output_dir: str,
    num_angles: int = 6,
    width: int = 512,
    height: int = 512,
    elevation: float = 25.0,
) -> list[RenderResult]:
    """Render multiple views around the model and return paths to each image."""
    os.makedirs(output_dir, exist_ok=True)
    results: list[RenderResult] = []
    base = os.path.splitext(os.path.basename(stl_path))[0]

    for i in range(num_angles):
        az = (360.0 / num_angles) * i
        angle_name = f"{az:.0f},{elevation:.0f}"
        out = os.path.join(output_dir, f"{base}_angle_{i:02d}.png")
        r = render_stl(stl_path, out, camera_angle=angle_name, width=width, height=height)
        results.append(r)

    return results


def render_cross_section(
    stl_path: str,
    output_path: str,
    z_height: float | None = None,
    plane_normal: tuple[float, float, float] = (0, 0, 1),
    width: int = 1024,
    height: int = 768,
) -> str:
    """Slice a mesh at a plane and render the 2D cross-section profile."""
    import trimesh
    import numpy as np

    mesh = _load_mesh(stl_path)

    if z_height is None:
        z_height = float((mesh.bounds[0][2] + mesh.bounds[1][2]) / 2)

    origin = np.array([0, 0, z_height])
    normal = np.array(plane_normal, dtype=float)

    try:
        section = mesh.section(plane_origin=origin, plane_normal=normal)
        if section is None:
            raise ValueError("No intersection at the given plane")
        path_2d, _to_3d = section.to_planar()
    except Exception as exc:
        raise ValueError(f"Cross-section failed: {exc}") from exc

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 1, figsize=(width / 100, height / 100), dpi=100)
        for entity in path_2d.entities:
            verts = path_2d.vertices[entity.points]
            ax.plot(verts[:, 0], verts[:, 1], "b-", linewidth=1.5)
        ax.set_aspect("equal")
        ax.set_title(f"Cross-section at Z={z_height:.2f}mm")
        ax.set_xlabel("mm")
        ax.set_ylabel("mm")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(output_path, dpi=100, bbox_inches="tight")
        plt.close(fig)
    except Exception:
        path_2d.export(output_path)

    return output_path


def _render_with_pyrender(mesh, output_path, az, el, distance, width, height):
    """Render using pyrender (requires OpenGL / Xvfb)."""
    import numpy as np
    import pyrender
    import trimesh as tm

    scene = pyrender.Scene(
        ambient_light=np.array([0.3, 0.3, 0.3, 1.0]),
        bg_color=np.array([0.95, 0.95, 0.97, 1.0]),
    )

    material = pyrender.MetallicRoughnessMaterial(
        baseColorFactor=[0.35, 0.55, 0.85, 1.0],
        metallicFactor=0.2,
        roughnessFactor=0.6,
    )
    py_mesh = pyrender.Mesh.from_trimesh(mesh, material=material, smooth=True)
    scene.add(py_mesh)

    camera = pyrender.PerspectiveCamera(yfov=math.radians(45))
    cam_pose = _camera_transform(az, el, distance)
    scene.add(camera, pose=cam_pose)

    light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
    scene.add(light, pose=cam_pose)

    fill_dir = _camera_transform(az + 120, el - 20, distance)
    fill_light = pyrender.DirectionalLight(color=np.ones(3), intensity=1.5)
    scene.add(fill_light, pose=fill_dir)

    renderer = pyrender.OffscreenRenderer(width, height)
    try:
        color, _ = renderer.render(scene)
    finally:
        renderer.delete()

    from PIL import Image as PILImage
    img = PILImage.fromarray(color)
    img.save(output_path)


def _render_with_matplotlib(mesh, output_path, az, el, distance, width, height):
    """Fallback renderer using matplotlib 3D projection."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_subplot(111, projection="3d")

    verts = mesh.vertices[mesh.faces]
    poly = Poly3DCollection(
        verts,
        alpha=0.85,
        facecolor="#5b8dd9",
        edgecolor="#3a5fa0",
        linewidth=0.15,
    )
    ax.add_collection3d(poly)

    bounds = mesh.bounds
    for i in range(3):
        span = bounds[1][i] - bounds[0][i]
        mid = (bounds[0][i] + bounds[1][i]) / 2
        getattr(ax, f"set_{'xyz'[i]}lim")(mid - span / 2, mid + span / 2)

    ax.view_init(elev=el, azim=az)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_box_aspect([1, 1, 1])

    fig.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close(fig)
