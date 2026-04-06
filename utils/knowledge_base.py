"""Structured knowledge base for 3D modeling, printing, and manufacturing education.

Provides searchable concept explanations, best practices, and contextual
help.  Used by education_tools.py to power cad_explain, format_guide,
and cad_best_practices.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Concept explanations — keyed by canonical topic slug
# ---------------------------------------------------------------------------

CONCEPTS: dict[str, dict] = {
    # ── 3D Modeling Fundamentals ──
    "mesh": {
        "title": "Mesh (Triangle Mesh)",
        "category": "3D Modeling",
        "summary": "A 3D surface represented as a collection of triangles (or polygons).  "
                   "The most common geometry representation in 3D printing and games.",
        "explanation": (
            "A mesh approximates a 3D shape using flat triangular faces.  Each triangle "
            "is defined by three vertices (points in 3D space).  The more triangles, the "
            "smoother the approximation — but also the larger the file and slower to process.\n\n"
            "Key properties:\n"
            "- **Vertices**: Points in 3D space (x, y, z coordinates)\n"
            "- **Faces**: Triangles connecting three vertices each\n"
            "- **Edges**: Lines between vertices shared by adjacent faces\n"
            "- **Normals**: Direction vectors perpendicular to each face (determines inside/outside)\n\n"
            "STL, OBJ, PLY, and 3MF are all mesh formats.  Meshes are great for rendering "
            "and manufacturing but lose the mathematical precision of solid models (BREP)."
        ),
        "related": ["manifold", "brep", "stl", "triangulation"],
    },
    "manifold": {
        "title": "Manifold (Watertight Mesh)",
        "category": "3D Modeling",
        "summary": "A mesh where every edge is shared by exactly two faces — like a "
                   "closed, watertight surface with no holes or self-intersections.",
        "explanation": (
            "A manifold mesh is 'watertight' — if you filled it with water, none would leak "
            "out.  This is critical for 3D printing because slicers need to know what's inside "
            "vs. outside the model to generate toolpaths.\n\n"
            "Common non-manifold issues:\n"
            "- **Open edges**: An edge belonging to only one face (a hole in the surface)\n"
            "- **T-junctions**: An edge shared by three or more faces\n"
            "- **Self-intersection**: Faces that pass through each other\n"
            "- **Zero-thickness**: Geometry with no volume (a flat sheet)\n\n"
            "Most slicers will warn about or refuse non-manifold meshes.  Use `mesh_analyze` "
            "to check and `mesh_repair` to fix these issues automatically."
        ),
        "related": ["mesh", "mesh_repair", "watertight"],
    },
    "brep": {
        "title": "BREP (Boundary Representation)",
        "category": "3D Modeling",
        "summary": "Mathematically exact solid geometry defined by surfaces, edges, and "
                   "vertices.  Used by professional CAD tools (SolidWorks, Fusion 360, FreeCAD).",
        "explanation": (
            "BREP represents solids using their boundary surfaces — curves, planes, cylinders, "
            "NURBS surfaces, etc.  Unlike meshes (which approximate with triangles), BREP stores "
            "the exact mathematical definition.\n\n"
            "Advantages over meshes:\n"
            "- **Exact geometry**: A cylinder is stored as a true cylinder, not a faceted approximation\n"
            "- **Editable**: You can modify individual features (fillets, chamfers, holes)\n"
            "- **Resolution-independent**: Can generate meshes at any tessellation quality\n\n"
            "STEP and IGES are the standard interchange formats for BREP data.  Converting "
            "BREP → mesh (STL) is always possible but lossy.  Going mesh → BREP requires "
            "reverse engineering the surfaces."
        ),
        "related": ["step", "solid_modeling", "parametric", "nurbs"],
    },
    "csg": {
        "title": "CSG (Constructive Solid Geometry)",
        "category": "3D Modeling",
        "summary": "Building complex shapes by combining simple primitives using boolean "
                   "operations: union, difference, and intersection.",
        "explanation": (
            "CSG is how OpenSCAD works.  You start with primitives (cubes, cylinders, spheres) "
            "and combine them:\n\n"
            "- **Union**: Merge two shapes into one (like welding)\n"
            "- **Difference**: Subtract one shape from another (like drilling a hole)\n"
            "- **Intersection**: Keep only where two shapes overlap\n\n"
            "CSG is intuitive for mechanical design — 'start with a block, cut a hole, "
            "add a boss' — and produces manifold results by construction.  OpenSCAD, "
            "CadQuery, and ImplicitCAD all use CSG as their primary paradigm."
        ),
        "related": ["openscad", "mesh_boolean", "parametric"],
    },
    "parametric": {
        "title": "Parametric Modeling",
        "category": "3D Modeling",
        "summary": "Designs driven by adjustable parameters (variables).  Change a "
                   "dimension and the entire model updates automatically.",
        "explanation": (
            "In parametric modeling, geometry is defined by parameters rather than fixed "
            "dimensions.  For example: `box_width = 50; wall = 2;` — changing `wall` from "
            "2 to 3 automatically rebuilds every feature that references it.\n\n"
            "Benefits:\n"
            "- **Design families**: One model that produces many variants\n"
            "- **Customization**: Users adjust parameters without CAD expertise\n"
            "- **Version control**: Parameters are code, so they diff and merge cleanly\n\n"
            "OpenSCAD is fully parametric (every dimension is a variable).  Fusion 360 and "
            "SolidWorks use constraint-based parametric modeling.  Use `openscad_list_params` "
            "to discover parameters and `openscad_sweep` to explore the design space."
        ),
        "related": ["openscad", "csg", "design_iteration"],
    },
    "nurbs": {
        "title": "NURBS (Non-Uniform Rational B-Splines)",
        "category": "3D Modeling",
        "summary": "Mathematical curves and surfaces used for smooth, organic shapes "
                   "in professional CAD and industrial design.",
        "explanation": (
            "NURBS are the mathematical foundation of most professional CAD surfaces.  They "
            "can represent any shape — from simple planes and cylinders to complex car bodies "
            "and aircraft fuselages — with mathematical precision.\n\n"
            "NURBS surfaces are defined by:\n"
            "- **Control points**: A grid of points that influence the surface shape\n"
            "- **Knot vectors**: Parameters that control how smoothly the surface flows\n"
            "- **Weights**: How strongly each control point pulls the surface\n\n"
            "STEP files store NURBS surfaces natively.  When you convert STEP → STL, the "
            "NURBS are tessellated (approximated with triangles), losing precision."
        ),
        "related": ["brep", "step", "surface_modeling"],
    },

    # ── 3D Printing Concepts ──
    "overhangs": {
        "title": "Overhangs",
        "category": "3D Printing",
        "summary": "Geometry that extends outward without support from below.  "
                   "FDM printers struggle with overhangs beyond ~45 degrees.",
        "explanation": (
            "An overhang is any part of a print that extends horizontally without material "
            "directly beneath it.  FDM (filament) printers deposit material layer by layer — "
            "each layer needs something to rest on.\n\n"
            "The **45-degree rule**: Most FDM printers can print overhangs up to about 45° "
            "from vertical without support material.  Beyond that, the extruded filament "
            "droops and produces poor surface quality.\n\n"
            "Solutions:\n"
            "- **Reorient the part** to minimize overhangs\n"
            "- **Add support material** (automatically in slicer, or manually designed)\n"
            "- **Design with chamfers** instead of sharp overhangs (45° angle)\n"
            "- **Use bridging** for short horizontal spans (up to ~50mm)\n\n"
            "Use `mesh_analyze` to detect overhangs.  The tool reports what percentage of "
            "faces exceed the 45° threshold."
        ),
        "related": ["supports", "bridging", "orientation", "mesh_analyze"],
    },
    "layer_height": {
        "title": "Layer Height",
        "category": "3D Printing",
        "summary": "The vertical thickness of each printed layer.  Smaller layers = "
                   "smoother surface but longer print time.",
        "explanation": (
            "Layer height is the single most impactful slicer setting:\n\n"
            "- **0.1mm**: Fine detail, smooth surfaces, 2–3x slower\n"
            "- **0.2mm**: Standard quality, good balance of speed and detail\n"
            "- **0.3mm**: Fast drafts, visible layer lines, structural parts\n\n"
            "The maximum layer height should be ~75% of your nozzle diameter.  With a "
            "standard 0.4mm nozzle, the max usable layer height is about 0.3mm.\n\n"
            "Variable layer height (available in most slicers) uses fine layers for "
            "curved surfaces and thick layers for flat sections — best of both worlds."
        ),
        "related": ["nozzle", "print_quality", "print_speed"],
    },
    "infill": {
        "title": "Infill",
        "category": "3D Printing",
        "summary": "The internal structure pattern that fills the inside of a print.  "
                   "Controls strength, weight, and print time.",
        "explanation": (
            "3D prints are rarely solid inside — infill creates an internal lattice "
            "structure.  Common infill percentages:\n\n"
            "- **10–15%**: Decorative items, prototypes (light, fast)\n"
            "- **20–25%**: General purpose (good strength-to-weight)\n"
            "- **40–60%**: Functional parts, load-bearing\n"
            "- **100%**: Maximum strength (heavy, slow, uses lots of material)\n\n"
            "Common patterns:\n"
            "- **Grid/Lines**: Fast, moderate strength\n"
            "- **Gyroid**: Excellent strength in all directions, good for flexible parts\n"
            "- **Honeycomb**: Great rigidity, slightly slower\n"
            "- **Lightning**: Minimal material, just enough to support top surfaces\n\n"
            "Wall count often matters more than infill for strength.  4 walls at 15% infill "
            "is usually stronger than 2 walls at 50% infill."
        ),
        "related": ["walls", "strength", "weight", "print_time"],
    },
    "warping": {
        "title": "Warping",
        "category": "3D Printing",
        "summary": "When corners of a print lift off the bed due to thermal contraction.  "
                   "Most common with ABS, ASA, and large flat parts.",
        "explanation": (
            "As plastic cools, it contracts.  If the bottom of the print is stuck to the bed "
            "but the layers above it shrink, the corners curl upward — this is warping.\n\n"
            "Prevention:\n"
            "- **Heated bed**: 60°C for PLA, 80–100°C for ABS/ASA, 80°C for PETG\n"
            "- **Enclosure**: Maintains ambient temperature (essential for ABS/ASA)\n"
            "- **Brim/raft**: Extra material around the base for better adhesion\n"
            "- **Bed adhesive**: Glue stick, hairspray, or PEI sheet\n"
            "- **Design**: Add fillets/chamfers to large flat bases, avoid sharp corners\n"
            "- **Elephant's foot compensation**: Slight first-layer squish causes a bulge "
            "at the base — compensate in slicer settings"
        ),
        "related": ["bed_adhesion", "elephants_foot", "enclosure", "abs"],
    },
    "elephants_foot": {
        "title": "Elephant's Foot",
        "category": "3D Printing",
        "summary": "A bulge at the bottom of a print caused by the first layer being "
                   "squished for bed adhesion.  Named for its resemblance to an elephant's foot.",
        "explanation": (
            "The first layer is typically pressed into the bed for adhesion, which causes it "
            "to spread wider than intended.  This creates a visible bulge.\n\n"
            "Fixes:\n"
            "- **Elephant's foot compensation** in slicer (shrinks first layer inward by 0.1–0.3mm)\n"
            "- **Reduce first-layer squish** (raise Z offset slightly)\n"
            "- **Lower bed temperature** for the first layer\n"
            "- **Design**: Add a small chamfer (0.5mm) at the bottom edge of parts"
        ),
        "related": ["warping", "first_layer", "bed_adhesion"],
    },
    "supports": {
        "title": "Support Material",
        "category": "3D Printing",
        "summary": "Temporary structures printed beneath overhangs that are removed "
                   "after printing.  Necessary for geometry that can't self-support.",
        "explanation": (
            "Supports are scaffolding printed alongside your model to hold up overhangs, "
            "bridges, and floating geometry.  After printing, they're broken or cut away.\n\n"
            "Types:\n"
            "- **Normal supports**: Same material as the part.  Break away manually.\n"
            "- **Tree supports**: Branch-like structures that use less material and are easier to remove.\n"
            "- **Soluble supports**: PVA or BVOH dissolves in water.  Requires a dual-extruder.\n\n"
            "Design tips to avoid supports:\n"
            "- Keep overhangs under 45°\n"
            "- Use chamfers instead of horizontal shelves\n"
            "- Split models into support-free halves and glue\n"
            "- Reorient the part on the build plate"
        ),
        "related": ["overhangs", "bridging", "dual_extruder", "orientation"],
    },
    "bridging": {
        "title": "Bridging",
        "category": "3D Printing",
        "summary": "Printing a horizontal span between two supports points with no "
                   "material underneath.  Works for short distances (~10–50mm).",
        "explanation": (
            "Bridging is when the printer extrudes filament across empty space, stretching "
            "it between two anchor points (like a suspension bridge).\n\n"
            "For successful bridges:\n"
            "- **Keep spans short** (<50mm for most materials, <30mm for best quality)\n"
            "- **Reduce speed** for bridge layers (most slicers have a bridge speed setting)\n"
            "- **Increase fan cooling** to solidify the filament quickly mid-air\n"
            "- **PLA bridges best** (stiffens quickly).  PETG and ABS are stringier."
        ),
        "related": ["overhangs", "supports", "cooling"],
    },
    "print_in_place": {
        "title": "Print-in-Place",
        "category": "3D Printing",
        "summary": "Mechanisms printed fully assembled with moving parts — hinges, "
                   "chains, and joints that work right off the build plate.",
        "explanation": (
            "Print-in-place designs print multiple interlocking parts simultaneously with "
            "clearance gaps between them.  When the print finishes, the parts are already "
            "assembled and can move freely.\n\n"
            "Key design parameters:\n"
            "- **Clearance**: 0.3–0.5mm between moving parts (PETG typically needs 0.4mm+)\n"
            "- **Layer height**: Must be small enough to resolve the clearance gap\n"
            "- **Orientation**: Hinges work best when the pivot axis is vertical (Z)\n"
            "- **Break-free**: Parts may need gentle flexing after printing to free them\n\n"
            "The cyberdeck camera arm in this project uses print-in-place chain links "
            "with pin hinges — each link prints in place with clearance around the pin."
        ),
        "related": ["clearance", "tolerances", "hinges", "petg"],
    },

    # ── Manufacturing / Design Rules ──
    "tolerances": {
        "title": "Tolerances and Clearances",
        "category": "Manufacturing",
        "summary": "The dimensional accuracy of printed parts and the gaps needed "
                   "for parts to fit together.",
        "explanation": (
            "FDM printers have typical dimensional accuracy of ±0.2–0.3mm.  When "
            "designing parts that fit together, you need clearance gaps:\n\n"
            "**Clearance guide (FDM, 0.4mm nozzle):**\n"
            "- **Press fit**: 0.0–0.1mm gap (tight, needs force to assemble)\n"
            "- **Snug fit**: 0.1–0.2mm gap (firm but hand-assemblable)\n"
            "- **Sliding fit**: 0.2–0.3mm gap (parts slide freely)\n"
            "- **Loose fit**: 0.3–0.5mm gap (easy assembly, some play)\n"
            "- **Print-in-place**: 0.4–0.6mm gap (must break free after printing)\n\n"
            "These vary by material: PETG expands more than PLA.  Always print a "
            "test piece to calibrate for your specific printer and material."
        ),
        "related": ["print_in_place", "fit_types", "calibration"],
    },
    "wall_thickness": {
        "title": "Minimum Wall Thickness",
        "category": "Manufacturing",
        "summary": "The minimum wall thickness for structurally sound 3D prints.",
        "explanation": (
            "Walls that are too thin will be fragile, warped, or may not print at all.\n\n"
            "**Minimum wall thickness by method:**\n"
            "- **FDM (0.4mm nozzle)**: 0.8mm (2 perimeters) minimum, 1.2mm+ recommended\n"
            "- **SLA/resin**: 0.5mm minimum, 1.0mm recommended\n"
            "- **SLS (nylon)**: 0.7mm minimum, 1.0mm recommended\n\n"
            "For functional parts, 2mm walls (5 perimeters) provide good rigidity. "
            "Enclosures and housings typically use 2–3mm walls.\n\n"
            "Wall thickness should be a multiple of your nozzle diameter for best results "
            "(0.4mm nozzle → 0.8mm, 1.2mm, 1.6mm, 2.0mm)."
        ),
        "related": ["nozzle", "perimeters", "strength"],
    },
    "draft_angles": {
        "title": "Draft Angles",
        "category": "Manufacturing",
        "summary": "Slight taper on vertical walls to aid mold release in injection "
                   "molding.  Less critical for 3D printing but still useful.",
        "explanation": (
            "In injection molding, draft angles (1–3°) allow the part to slide out of "
            "the mold.  In 3D printing, draft angles help with:\n\n"
            "- **Print-in-place mechanisms**: Tapered walls release more easily\n"
            "- **Stacking**: Parts with slight draft stack neatly\n"
            "- **Future manufacturing**: If you ever injection-mold the design, draft is needed\n\n"
            "For FDM printing specifically, draft on vertical walls reduces the visible "
            "staircase effect from layer lines."
        ),
        "related": ["injection_molding", "surface_finish", "manufacturing"],
    },
}


# ---------------------------------------------------------------------------
# Best practice collections
# ---------------------------------------------------------------------------

BEST_PRACTICES: dict[str, dict] = {
    "fdm_general": {
        "title": "FDM 3D Printing — General Best Practices",
        "category": "3D Printing",
        "practices": [
            "Design walls as multiples of nozzle diameter (0.4mm → 0.8, 1.2, 1.6, 2.0mm)",
            "Minimum wall thickness: 0.8mm (2 perimeters), 1.2mm+ for structural parts",
            "Avoid overhangs beyond 45° — use chamfers or design supports into the geometry",
            "Add 0.2–0.3mm clearance for sliding fits, 0.4mm+ for print-in-place",
            "Round bottom corners with fillets to prevent elephant's foot and warping",
            "Orient parts to minimize supports and maximize layer adhesion in the stress direction",
            "Bridge spans should be under 50mm for acceptable quality",
            "Use 0.2mm layer height as default; 0.1mm for fine detail, 0.3mm for speed",
            "Always export as manifold (watertight) meshes — use mesh_analyze to verify",
        ],
    },
    "petg": {
        "title": "PETG Printing Best Practices",
        "category": "Material",
        "practices": [
            "Print at 230–250°C nozzle, 80°C bed",
            "PETG is stringy — retraction and wipe settings are critical",
            "Increase clearance by +0.1mm vs PLA for snap fits and moving parts",
            "PETG bonds to PEI beds aggressively — use a release agent or glue stick",
            "Excellent layer adhesion makes it great for functional parts",
            "More flexible than PLA — good for snap fits and living hinges",
            "Hygroscopic — dry filament before printing if it's been open for days",
        ],
    },
    "pla": {
        "title": "PLA Printing Best Practices",
        "category": "Material",
        "practices": [
            "Print at 190–220°C nozzle, 60°C bed",
            "Easiest material to print — great for learning and prototyping",
            "Best bridging performance of common FDM materials",
            "Biodegradable but not heat-resistant (deforms above 50–60°C)",
            "Tight tolerances possible — good for dimensional accuracy",
            "Brittle under impact — not ideal for functional snap fits",
            "Minimal warping — can print without enclosure",
        ],
    },
    "abs_asa": {
        "title": "ABS / ASA Printing Best Practices",
        "category": "Material",
        "practices": [
            "Print at 240–260°C nozzle, 100–110°C bed",
            "REQUIRES an enclosure — drafts cause cracking and warping",
            "ASA is UV-resistant — preferred for outdoor applications",
            "ABS can be vapour-smoothed with acetone for glossy finish",
            "Excellent heat resistance (up to ~100°C)",
            "Strong layer adhesion with proper temperature",
            "Higher shrinkage than PLA/PETG — increase clearances by +0.1–0.2mm",
            "Good for post-processing (sanding, painting, gluing)",
        ],
    },
    "sharing_models": {
        "title": "Sharing 3D Models — Format Best Practices",
        "category": "Workflow",
        "practices": [
            "Share STEP files for engineering collaboration — preserves exact geometry",
            "Share STL or 3MF for print-ready models — 3MF is preferred (carries units + color)",
            "Never share only STL for design collaboration — it's a lossy dead-end format",
            "Include source files (.scad, .f3d, .FCStd) alongside STL exports",
            "Use Git for version control of OpenSCAD and text-based CAD files",
            "Name files with version numbers: part_v2.1.stl, not part_final_final.stl",
            "Document parameters and assembly instructions in a README",
        ],
    },
    "print_in_place": {
        "title": "Print-in-Place Design Best Practices",
        "category": "Design",
        "practices": [
            "Use 0.4–0.6mm clearance gaps for moving parts (tune to your printer + material)",
            "Print test coupons first — a simple hinge test saves hours of reprinting",
            "Hinge axes should be parallel to Z (vertical) for best resolution",
            "Avoid supports inside mechanisms — design self-supporting geometry",
            "PETG is forgiving for PIP (flexible, good layer adhesion)",
            "Use 0.2mm or finer layer height for reliable clearance resolution",
            "Design break-free features (thin bridges that snap when you flex the part)",
            "Add a sacrificial first layer (raft or thick brim) if bed adhesion is tricky",
        ],
    },
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def find_concept(query: str) -> list[dict]:
    """Search concepts by keyword match.  Returns matching concept dicts."""
    query_lower = query.lower().replace("-", "_").replace(" ", "_")
    results = []

    if query_lower in CONCEPTS:
        results.append(CONCEPTS[query_lower])
        return results

    for slug, concept in CONCEPTS.items():
        score = 0
        if query_lower in slug:
            score += 3
        if query_lower in concept["title"].lower():
            score += 3
        if query_lower in concept["summary"].lower():
            score += 1
        if query_lower in concept["category"].lower():
            score += 1
        for related in concept.get("related", []):
            if query_lower in related:
                score += 1
        if score > 0:
            results.append({**concept, "_score": score, "_slug": slug})

    results.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return results[:5]


def find_best_practices(query: str) -> list[dict]:
    """Search best practices by keyword match."""
    query_lower = query.lower().replace("-", "_").replace(" ", "_")
    results = []

    if query_lower in BEST_PRACTICES:
        results.append(BEST_PRACTICES[query_lower])
        return results

    for slug, bp in BEST_PRACTICES.items():
        score = 0
        if query_lower in slug:
            score += 3
        if query_lower in bp["title"].lower():
            score += 2
        if query_lower in bp["category"].lower():
            score += 1
        for practice in bp["practices"]:
            if query_lower in practice.lower():
                score += 1
                break
        if score > 0:
            results.append({**bp, "_score": score, "_slug": slug})

    results.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return results[:3]


def list_all_topics() -> dict:
    """Return a summary of all available topics and practices."""
    topics_by_category: dict[str, list[str]] = {}
    for slug, concept in CONCEPTS.items():
        cat = concept["category"]
        topics_by_category.setdefault(cat, []).append(concept["title"])

    practices_by_category: dict[str, list[str]] = {}
    for slug, bp in BEST_PRACTICES.items():
        cat = bp["category"]
        practices_by_category.setdefault(cat, []).append(bp["title"])

    return {
        "concepts": topics_by_category,
        "best_practices": practices_by_category,
        "total_concepts": len(CONCEPTS),
        "total_practice_sets": len(BEST_PRACTICES),
    }
