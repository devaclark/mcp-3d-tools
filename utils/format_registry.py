"""3D format intelligence registry.

Maps file extensions to format metadata, loader backends, conversion paths,
and industry recommendations.  Used by format_tools and education_tools to
provide format-aware behaviour across the entire MCP server.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Loader(Enum):
    TRIMESH = "trimesh"
    OCP = "opencascade"
    OPENSCAD = "openscad"
    HOST = "host_program"
    NONE = "none"


class Capability(Enum):
    MESH = "mesh"
    SOLID = "solid_brep"
    PARAMETRIC = "parametric"
    ASSEMBLY = "assembly"
    MULTI_BODY = "multi_body"
    COLOR = "color"
    TEXTURE = "texture"
    ANIMATION = "animation"
    UNITS = "units"
    METADATA = "metadata"


@dataclass(frozen=True)
class FormatInfo:
    name: str
    extensions: tuple[str, ...]
    description: str
    loader: Loader
    capabilities: tuple[Capability, ...] = ()
    industry: str = ""
    recommended_programs: tuple[str, ...] = ()
    mime_type: str = "application/octet-stream"
    is_text: bool = False
    conversion_notes: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "extensions": list(self.extensions),
            "description": self.description,
            "loader": self.loader.value,
            "capabilities": [c.value for c in self.capabilities],
            "industry": self.industry,
            "recommended_programs": list(self.recommended_programs),
            "is_text": self.is_text,
            "conversion_notes": self.conversion_notes,
        }


# ---------------------------------------------------------------------------
# Master format registry
# ---------------------------------------------------------------------------

FORMATS: dict[str, FormatInfo] = {}

def _register(*infos: FormatInfo) -> None:
    for info in infos:
        for ext in info.extensions:
            FORMATS[ext.lower()] = info


_register(
    # -- Mesh formats (trimesh-native) --
    FormatInfo(
        name="STL",
        extensions=(".stl",),
        description="Stereolithography — the de-facto standard for 3D printing. "
                    "Stores triangle meshes without colour, texture, or units.",
        loader=Loader.TRIMESH,
        capabilities=(Capability.MESH,),
        industry="3D printing, rapid prototyping, CNC.  Nearly every slicer and "
                 "printer accepts STL.  Use it as the final export for manufacturing, "
                 "but avoid it for design interchange because it discards parametric "
                 "data, units, and dimensional accuracy.",
        recommended_programs=("PrusaSlicer", "Bambu Studio", "Cura", "Meshmixer",
                              "Blender", "FreeCAD"),
        mime_type="model/stl",
        conversion_notes="Conversion to STL is lossy from any solid/parametric format "
                         "(STEP, SCAD).  Tessellation resolution is fixed at export time.",
    ),
    FormatInfo(
        name="OBJ",
        extensions=(".obj",),
        description="Wavefront OBJ — widely-supported mesh format with optional "
                    "materials (.mtl).  Common in game dev, VFX, and 3D scanning.",
        loader=Loader.TRIMESH,
        capabilities=(Capability.MESH, Capability.COLOR, Capability.TEXTURE),
        industry="Game development, VFX, 3D scanning, photogrammetry.  Good for "
                 "colour meshes but lacks units.  Not ideal for engineering or "
                 "3D printing without conversion.",
        recommended_programs=("Blender", "MeshLab", "Meshmixer", "Maya"),
        mime_type="model/obj",
        is_text=True,
        conversion_notes="OBJ preserves vertex colours and UVs but has no unit system.  "
                         "Converting from parametric formats loses all design history.",
    ),
    FormatInfo(
        name="3MF",
        extensions=(".3mf",),
        description="3D Manufacturing Format — the modern replacement for STL.  "
                    "Supports colour, multi-material, build-plate layout, and units.",
        loader=Loader.TRIMESH,
        capabilities=(Capability.MESH, Capability.COLOR, Capability.UNITS,
                      Capability.MULTI_BODY, Capability.METADATA),
        industry="3D printing (next-gen).  Endorsed by Microsoft, HP, Bambu Lab, "
                 "Stratasys.  Preferred over STL when your slicer supports it because "
                 "it carries units, colour, and multi-part information.",
        recommended_programs=("Bambu Studio", "PrusaSlicer", "Cura", "Windows 3D Builder"),
        mime_type="application/vnd.ms-package.3dmanufacturing-3dmodel+xml",
        conversion_notes="3MF is a mesh format like STL but richer.  Solid/parametric "
                         "data is still lost when exporting from STEP or SCAD.",
    ),
    FormatInfo(
        name="PLY",
        extensions=(".ply",),
        description="Polygon File Format — stores meshes with per-vertex colour. "
                    "Common output from 3D scanners and photogrammetry pipelines.",
        loader=Loader.TRIMESH,
        capabilities=(Capability.MESH, Capability.COLOR),
        industry="3D scanning, photogrammetry, point-cloud processing, research.",
        recommended_programs=("MeshLab", "CloudCompare", "Blender"),
        mime_type="application/x-ply",
        conversion_notes="PLY carries vertex colours faithfully.  No unit system.",
    ),
    FormatInfo(
        name="OFF",
        extensions=(".off",),
        description="Object File Format — minimal ASCII mesh format used in "
                    "computational geometry research.",
        loader=Loader.TRIMESH,
        capabilities=(Capability.MESH,),
        industry="Academic / computational geometry research.",
        recommended_programs=("MeshLab", "Blender"),
        is_text=True,
        conversion_notes="Minimal format.  No colours, units, or metadata.",
    ),
    FormatInfo(
        name="glTF / GLB",
        extensions=(".glb", ".gltf"),
        description="GL Transmission Format — the 'JPEG of 3D'.  Efficient web and "
                    "mobile delivery with PBR materials, animations, and scene graphs.",
        loader=Loader.TRIMESH,
        capabilities=(Capability.MESH, Capability.COLOR, Capability.TEXTURE,
                      Capability.ANIMATION, Capability.METADATA),
        industry="Web, AR/VR, mobile, game engines (Unity, Unreal, Godot).  The "
                 "industry standard for real-time 3D content delivery.",
        recommended_programs=("Blender", "three.js", "Babylon.js", "Unity", "Unreal Engine"),
        mime_type="model/gltf-binary",
        conversion_notes="Rich scene format.  Converting from engineering formats "
                         "(STEP) loses parametric data but preserves visual fidelity.",
    ),
    FormatInfo(
        name="DAE (Collada)",
        extensions=(".dae",),
        description="COLLADA — XML-based interchange format for 3D assets with "
                    "scenes, materials, and animations.",
        loader=Loader.TRIMESH,
        capabilities=(Capability.MESH, Capability.COLOR, Capability.ANIMATION),
        industry="Legacy interchange, SketchUp, older game pipelines.  "
                 "Largely superseded by glTF for new projects.",
        recommended_programs=("Blender", "SketchUp", "Maya"),
        mime_type="model/vnd.collada+xml",
        is_text=True,
        conversion_notes="XML-based, can be large.  Superseded by glTF for most uses.",
    ),
    FormatInfo(
        name="AMF",
        extensions=(".amf",),
        description="Additive Manufacturing File Format — XML-based format supporting "
                    "colour, materials, and curved triangles.  ISO/ASTM 52915.",
        loader=Loader.TRIMESH,
        capabilities=(Capability.MESH, Capability.COLOR, Capability.MULTI_BODY,
                      Capability.UNITS),
        industry="Additive manufacturing (ISO standard).  Less adopted than 3MF "
                 "in practice despite being an ISO standard.",
        recommended_programs=("Meshmixer", "Cura"),
        is_text=True,
        conversion_notes="Similar capability to 3MF.  Less slicer support in practice.",
    ),

    # -- Solid / BREP formats (OpenCascade via cadquery) --
    FormatInfo(
        name="STEP",
        extensions=(".step", ".stp"),
        description="Standard for the Exchange of Product Data (ISO 10303).  "
                    "The gold standard for engineering CAD interchange.  Stores "
                    "exact solid geometry (BREP) with units and tolerances.",
        loader=Loader.OCP,
        capabilities=(Capability.SOLID, Capability.ASSEMBLY, Capability.MULTI_BODY,
                      Capability.UNITS, Capability.METADATA),
        industry="Mechanical engineering, aerospace, automotive, product design.  "
                 "THE industry standard for exchanging CAD data between SolidWorks, "
                 "Fusion 360, CATIA, NX, FreeCAD, and other professional CAD tools.  "
                 "Always prefer STEP over STL for design collaboration.",
        recommended_programs=("FreeCAD", "Fusion 360", "SolidWorks", "CATIA", "NX",
                              "OnShape", "Inventor"),
        mime_type="model/step",
        is_text=True,
        conversion_notes="STEP → STL is lossy (tessellation, loses exact geometry).  "
                         "STEP → STEP between CAD tools usually preserves geometry but "
                         "may lose feature tree / parametric history.",
    ),
    FormatInfo(
        name="IGES",
        extensions=(".iges", ".igs"),
        description="Initial Graphics Exchange Specification — older CAD interchange "
                    "format.  Supports surfaces and solids but largely superseded by STEP.",
        loader=Loader.OCP,
        capabilities=(Capability.SOLID, Capability.ASSEMBLY, Capability.UNITS),
        industry="Legacy CAD interchange.  Still found in aerospace and automotive "
                 "supply chains.  Prefer STEP for new work.",
        recommended_programs=("FreeCAD", "Fusion 360", "SolidWorks"),
        mime_type="model/iges",
        is_text=True,
        conversion_notes="IGES has known ambiguity issues (surface stitching).  "
                         "Convert to STEP when possible for better reliability.",
    ),
    FormatInfo(
        name="BREP",
        extensions=(".brep", ".brp"),
        description="OpenCascade native boundary representation format.",
        loader=Loader.OCP,
        capabilities=(Capability.SOLID, Capability.MULTI_BODY),
        industry="OpenCascade ecosystem, FreeCAD internal use.",
        recommended_programs=("FreeCAD", "CadQuery"),
        conversion_notes="Native OCC format.  Not widely used outside the ecosystem.",
    ),

    # -- Parametric source formats --
    FormatInfo(
        name="OpenSCAD",
        extensions=(".scad",),
        description="OpenSCAD script — a programmable, code-first 3D modeling language "
                    "using Constructive Solid Geometry (CSG).  Models are defined as "
                    "source code, making them version-controllable and parametric.",
        loader=Loader.OPENSCAD,
        capabilities=(Capability.PARAMETRIC, Capability.SOLID, Capability.ASSEMBLY),
        industry="Maker/hacker community, parametric design, customizable parts.  "
                 "Ideal for designs that need to be adjustable via parameters "
                 "(e.g., enclosures sized to components).",
        recommended_programs=("OpenSCAD",),
        is_text=True,
        conversion_notes="SCAD → STL/3MF via OpenSCAD rendering.  The source code "
                         "IS the design — always keep .scad files as your master.",
    ),

    # -- Host-only formats --
    FormatInfo(
        name="Blender",
        extensions=(".blend",),
        description="Blender native project file — stores meshes, materials, "
                    "animations, scenes, compositing, and physics simulations.",
        loader=Loader.HOST,
        capabilities=(Capability.MESH, Capability.COLOR, Capability.TEXTURE,
                      Capability.ANIMATION, Capability.ASSEMBLY),
        industry="VFX, animation, game art, product visualization, 3D printing prep.",
        recommended_programs=("Blender",),
        conversion_notes="Requires Blender CLI to export to other formats.  "
                         "Rich format that can contain entire projects.",
    ),
    FormatInfo(
        name="FreeCAD",
        extensions=(".fcstd",),
        description="FreeCAD native project file — parametric solid modeling with "
                    "full feature tree, constraints, and assembly support.",
        loader=Loader.HOST,
        capabilities=(Capability.PARAMETRIC, Capability.SOLID, Capability.ASSEMBLY,
                      Capability.MULTI_BODY, Capability.UNITS),
        industry="Open-source mechanical engineering, hobbyist CAD, education.",
        recommended_programs=("FreeCAD",),
        conversion_notes="Export to STEP for interchange.  Feature tree is not "
                         "portable to other CAD tools.",
    ),

    # -- 2D / vector formats --
    FormatInfo(
        name="DXF",
        extensions=(".dxf",),
        description="AutoCAD Drawing Exchange Format — 2D/3D vector drawings.  "
                    "Used for laser cutting, CNC routing, and 2D engineering drawings.",
        loader=Loader.TRIMESH,
        capabilities=(Capability.MESH,),
        industry="Laser cutting, CNC routing, 2D engineering drawings, architecture.",
        recommended_programs=("LibreCAD", "AutoCAD", "FreeCAD", "Inkscape"),
        is_text=True,
        conversion_notes="DXF is primarily 2D.  3D DXF exists but is uncommon.  "
                         "For 2D profiles that need extrusion, import into OpenSCAD.",
    ),
    FormatInfo(
        name="SVG",
        extensions=(".svg",),
        description="Scalable Vector Graphics — 2D vector format.  Can be imported "
                    "by OpenSCAD for extrusion into 3D shapes.",
        loader=Loader.NONE,
        capabilities=(),
        industry="Web graphics, laser cutting profiles, OpenSCAD 2D import.",
        recommended_programs=("Inkscape", "Adobe Illustrator", "OpenSCAD"),
        mime_type="image/svg+xml",
        is_text=True,
        conversion_notes="2D only.  Import into OpenSCAD with linear_extrude() "
                         "to create 3D geometry from 2D profiles.",
    ),
)


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def lookup(ext_or_path: str) -> FormatInfo | None:
    """Look up format info by extension or file path."""
    import os
    if "." in ext_or_path and not ext_or_path.startswith("."):
        ext = os.path.splitext(ext_or_path)[1]
    else:
        ext = ext_or_path if ext_or_path.startswith(".") else f".{ext_or_path}"
    return FORMATS.get(ext.lower())


def all_supported_extensions() -> list[str]:
    """Return all extensions this registry knows about."""
    return sorted(FORMATS.keys())


def can_preview(ext: str) -> bool:
    """Return True if we can generate a visual preview for this format."""
    info = lookup(ext)
    if info is None:
        return False
    return info.loader in (Loader.TRIMESH, Loader.OCP, Loader.OPENSCAD)


def can_convert(src_ext: str, dst_ext: str) -> bool:
    """Return True if conversion from src to dst is possible."""
    src = lookup(src_ext)
    dst = lookup(dst_ext)
    if src is None or dst is None:
        return False
    if src.loader == Loader.NONE or dst.loader == Loader.NONE:
        return False
    if src.loader == Loader.HOST or dst.loader == Loader.HOST:
        return False
    return True


def conversion_fidelity(src_ext: str, dst_ext: str) -> str:
    """Describe what is lost when converting between two formats."""
    src = lookup(src_ext)
    dst = lookup(dst_ext)
    if src is None or dst is None:
        return "Unknown formats."

    lost = []
    for cap in src.capabilities:
        if cap not in dst.capabilities:
            lost.append(cap.value)

    if not lost:
        return "No capability loss — both formats support the same features."

    return (
        f"Converting {src.name} → {dst.name} loses: {', '.join(lost)}.  "
        f"{src.conversion_notes}"
    )


def get_conversion_matrix() -> dict:
    """Return the full conversion compatibility matrix."""
    mesh_exts = [e for e, f in FORMATS.items()
                 if f.loader in (Loader.TRIMESH, Loader.OCP, Loader.OPENSCAD)
                 and Capability.MESH in f.capabilities or Capability.SOLID in f.capabilities]

    matrix: dict[str, dict[str, str]] = {}
    for src in mesh_exts:
        matrix[src] = {}
        for dst in mesh_exts:
            if src == dst:
                matrix[src][dst] = "identity"
            elif can_convert(src, dst):
                matrix[src][dst] = "supported"
            else:
                matrix[src][dst] = "unsupported"
    return matrix
