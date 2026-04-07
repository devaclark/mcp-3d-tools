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

    # ── SLA / Resin Printing ──
    "sla_resin": {
        "title": "SLA / Resin 3D Printing",
        "category": "3D Printing",
        "summary": "Vat photopolymerization using UV light to cure liquid resin layer "
                   "by layer.  Produces very smooth, highly detailed parts.",
        "explanation": (
            "SLA (Stereolithography) and MSLA (Masked SLA) printers cure liquid photopolymer "
            "resin with UV light (405nm wavelength).  The build plate dips into a vat of resin, "
            "and each layer is exposed to light — either from a laser (SLA), a projector (DLP), "
            "or an LCD mask (MSLA).\n\n"
            "**Resolution and layer heights:**\n"
            "- **25–50 microns**: Jewelry, miniatures, dental models — exceptional detail\n"
            "- **50–100 microns**: General purpose — smooth surfaces with fast print times\n"
            "- XY resolution depends on the LCD pixel pitch (typically 35–50 microns)\n\n"
            "**Advantages over FDM:**\n"
            "- **Surface finish**: Near-injection-mold smoothness with no visible layer lines\n"
            "- **Fine detail**: Can resolve features under 0.1mm (impossible on FDM)\n"
            "- **Isotropic strength**: No weak layer adhesion direction\n\n"
            "**Limitations:**\n"
            "- **Brittle**: Standard resins shatter under impact; use tough/flexible resin for functional parts\n"
            "- **UV degradation**: Parts yellow and become brittle in direct sunlight unless UV-stabilized\n"
            "- **Post-processing required**: Every print needs washing (IPA or water) and UV post-curing\n"
            "- **Smaller build volume**: Most consumer resin printers max out around 200×125×200mm\n\n"
            "Use `mesh_analyze` to check your model before printing — non-manifold geometry "
            "causes even more issues in resin than in FDM."
        ),
        "related": ["cure_time", "resin_safety", "support_orientation_sla"],
    },
    "cure_time": {
        "title": "Cure Time (Resin)",
        "category": "3D Printing",
        "summary": "The UV exposure duration per layer in resin printing.  Too little "
                   "causes failed prints; too much causes loss of detail.",
        "explanation": (
            "Every resin layer needs a precise amount of UV exposure to solidify properly.  "
            "Getting the cure time right is the single most important calibration for resin "
            "printing.\n\n"
            "**Typical exposure times (mono LCD printers):**\n"
            "- **Normal layers**: 1.5–3 seconds (varies by resin brand and color)\n"
            "- **Bottom layers** (first 4–8 layers): 25–60 seconds — much longer to ensure "
            "the print sticks firmly to the build plate\n"
            "- **Transparent/clear resins**: Usually need 10–20% longer exposure\n\n"
            "**Under-curing symptoms:**\n"
            "- Layers delaminate or separate from each other\n"
            "- Print falls off the build plate mid-print\n"
            "- Soft, rubbery surface that dents with a fingernail\n\n"
            "**Over-curing symptoms:**\n"
            "- Fine details merge together and become blobby\n"
            "- Dimensional expansion (holes shrink, walls thicken)\n"
            "- Support tips become too thick to remove cleanly\n\n"
            "**Calibration method:** Print an exposure test model (like the Ameralabs Town "
            "or RERF test) at several exposure times.  Examine the results under magnification "
            "to find the sweet spot where detail is sharp and layers are fully bonded."
        ),
        "related": ["sla_resin"],
    },
    "resin_safety": {
        "title": "Resin Safety",
        "category": "3D Printing",
        "summary": "Essential safety precautions for handling liquid photopolymer resin.  "
                   "Uncured resin is a skin sensitizer and environmental hazard.",
        "explanation": (
            "Liquid UV resin is a chemical irritant and sensitizer — repeated skin exposure "
            "can cause permanent allergic reactions.  Safety is not optional.\n\n"
            "**Required PPE:**\n"
            "- **Nitrile gloves** (not latex — resin penetrates latex).  Change gloves frequently\n"
            "- **Safety glasses** to protect from splashes and UV light\n"
            "- **Ventilation**: Work in a well-ventilated area or use a fume extractor; resin "
            "vapors cause headaches and respiratory irritation\n\n"
            "**Skin sensitization:**\n"
            "- Once sensitized, even trace contact causes allergic dermatitis\n"
            "- Sensitization is cumulative and permanent — there is no desensitization\n"
            "- If resin contacts skin, wash immediately with soap and water (not IPA, which "
            "drives resin deeper into skin)\n\n"
            "**Cleanup:**\n"
            "- Wash prints in 90%+ IPA (isopropyl alcohol) for 2–3 minutes, or use "
            "water-washable resin and rinse under running water\n"
            "- Wipe spills with IPA-dampened paper towels, then dispose properly\n\n"
            "**Disposal:**\n"
            "- **Never pour liquid resin down the drain** — it's toxic to aquatic life\n"
            "- Cure waste resin by exposing it to sunlight or a UV lamp until fully solid, "
            "then dispose as regular plastic waste\n"
            "- Used IPA wash can be left in sunlight to cure dissolved resin, then filtered and reused"
        ),
        "related": ["sla_resin"],
    },
    "support_orientation_sla": {
        "title": "SLA Support and Orientation Strategy",
        "category": "3D Printing",
        "summary": "How to orient and support resin prints to minimize peel forces, "
                   "reduce support scarring, and avoid print failures.",
        "explanation": (
            "Resin printing orientation is critical because each layer is peeled off the FEP "
            "film at the bottom of the vat.  Large flat cross-sections create enormous peel "
            "forces that can tear the print off the build plate.\n\n"
            "**Orientation guidelines:**\n"
            "- **Tilt parts 30–45°** from horizontal to reduce the cross-sectional area peeled "
            "per layer — this is the single most effective strategy\n"
            "- **Avoid large flat surfaces** parallel to the build plate — they create suction "
            "cup effects during peeling\n"
            "- **Orient cosmetic surfaces** facing away from the build plate (upward) to keep "
            "them support-free\n\n"
            "**Support placement:**\n"
            "- Place supports on non-visible or non-functional surfaces\n"
            "- **Support tip diameter**: 0.3–0.5mm for light supports (easy removal, small scars), "
            "0.6–0.8mm for medium, 1.0mm+ for heavy parts\n"
            "- Increase support density around islands (disconnected regions in a layer)\n\n"
            "**Island detection:**\n"
            "- An 'island' is a region of a layer with no connection to the previous layer — "
            "it would print floating in resin without a support\n"
            "- Most resin slicers (ChiTuBox, Lychee) have island detection tools — always run "
            "them before printing\n"
            "- Re-orient or add supports to eliminate all islands"
        ),
        "related": ["sla_resin", "supports"],
    },

    # ── Troubleshooting / Print Defects ──
    "stringing": {
        "title": "Stringing / Oozing",
        "category": "3D Printing",
        "summary": "Thin threads of filament left between travel moves.  Caused by "
                   "filament oozing from the nozzle during non-print moves.",
        "explanation": (
            "Stringing happens when melted filament leaks from the nozzle as the print head "
            "travels between separate sections.  The result is thin, hair-like threads "
            "draped across the print.\n\n"
            "**Primary causes and fixes:**\n"
            "- **Temperature too high**: Reduce nozzle temp in 5°C steps — lower viscosity "
            "means less oozing.  This is the most effective fix.\n"
            "- **Retraction too low**: Increase retraction distance (Bowden: 4–7mm, direct "
            "drive: 0.5–2mm) and speed (25–50mm/s)\n"
            "- **Travel speed too slow**: Increase to 150–200mm/s so the nozzle spends less "
            "time over empty space\n"
            "- **Wet filament**: Moisture causes steam bubbles that push filament out.  Dry "
            "your filament (PLA: 45°C/4h, PETG: 65°C/4h)\n\n"
            "**Material-specific notes:**\n"
            "- **PETG** is the worst offender — it's inherently stringy.  Use 'wipe' and "
            "'coasting' settings in your slicer alongside retraction\n"
            "- **PLA** strings mainly when too hot — usually a 5–10°C reduction fixes it\n"
            "- **TPU** cannot retract effectively — use 'combing' (travel within infill) instead\n\n"
            "Print a retraction tower test to dial in settings.  Most slicers can generate "
            "these automatically."
        ),
        "related": ["retraction", "over_extrusion"],
    },
    "layer_shifting": {
        "title": "Layer Shifting",
        "category": "3D Printing",
        "summary": "A sudden horizontal offset in one or more layers, causing the print "
                   "to appear split or stair-stepped.",
        "explanation": (
            "Layer shifting occurs when the print head loses its position on the X or Y "
            "axis, causing all subsequent layers to be offset.  It's usually a sudden, "
            "dramatic defect rather than gradual.\n\n"
            "**Common causes:**\n"
            "- **Loose belts**: The most common cause.  Belts should be taut — press in the "
            "middle of a belt span; there should be minimal deflection and a low 'twang'\n"
            "- **Stepper motor skipping**: The motor doesn't have enough torque to keep up "
            "with commanded speed.  Reduce acceleration (try 1000–2000mm/s²) and jerk\n"
            "- **Print head collision**: The nozzle hits a curled-up section of the print.  "
            "Caused by warping or over-extrusion creating high spots\n"
            "- **Too-fast acceleration**: The print head changes direction too aggressively, "
            "overwhelming the stepper motors\n"
            "- **Loose grub screws**: Check the set screws on pulleys attached to stepper shafts\n\n"
            "**Fixes:**\n"
            "- Tighten belts and check pulley set screws\n"
            "- Reduce maximum speed and acceleration in firmware/slicer\n"
            "- Enable 'Z hop' to lift the nozzle during travel moves (avoids collisions)\n"
            "- Ensure stepper motor current is set correctly (too low = skipping, too high = overheating)"
        ),
        "related": ["ghosting_ringing"],
    },
    "under_extrusion": {
        "title": "Under-Extrusion",
        "category": "3D Printing",
        "summary": "Not enough filament being deposited, resulting in gaps between lines, "
                   "weak layers, and thin or missing walls.",
        "explanation": (
            "Under-extrusion means the printer is pushing out less plastic than the slicer "
            "expects.  It shows up as gaps between extrusion lines, visible infill through "
            "top surfaces, and weak layer adhesion.\n\n"
            "**Common causes:**\n"
            "- **Partial clog**: Debris or carbonized filament restricts flow.  Do a cold pull "
            "(heat to 230°C, cool to 90°C, pull filament out sharply) to clear clogs\n"
            "- **Temperature too low**: The filament isn't melting fast enough to keep up with "
            "extrusion speed.  Increase in 5°C steps\n"
            "- **Incorrect flow rate**: Calibrate by extruding 100mm of filament and measuring "
            "actual output.  Adjust the flow multiplier (typically 95–105%)\n"
            "- **Filament grinding**: The extruder gear chews into the filament instead of "
            "pushing it.  Check tension, clean gear teeth, and reduce retraction count\n"
            "- **Wrong filament diameter**: Verify slicer is set to 1.75mm (or 2.85mm if applicable)\n"
            "- **Worn nozzle**: Brass nozzles wear over time, especially with abrasive filaments "
            "(carbon fiber, glow-in-dark).  Replace every 500–1000 print hours\n\n"
            "Start diagnosis by calibrating E-steps, then run a flow rate test cube.  If walls "
            "measure thin, increase flow; if thick, decrease."
        ),
        "related": ["over_extrusion", "retraction"],
    },
    "over_extrusion": {
        "title": "Over-Extrusion",
        "category": "3D Printing",
        "summary": "Too much filament being deposited, causing blobby surfaces, rough "
                   "textures, and dimensional inaccuracy.",
        "explanation": (
            "Over-extrusion pushes more plastic than needed, resulting in excess material "
            "that has nowhere to go.  It causes surfaces to feel rough or blobby, dimensions "
            "to be larger than designed, and can trigger nozzle collisions.\n\n"
            "**Symptoms:**\n"
            "- **Blobby/rough surface finish** with bumps and zits\n"
            "- **Parts too large**: Holes are too small, outer dimensions overshoot the design\n"
            "- **Elephant's foot**: Excessive first layer squish from too much material\n"
            "- **Nozzle dragging**: The nozzle scrapes across already-deposited material\n\n"
            "**Common causes:**\n"
            "- **Flow rate too high**: Reduce flow multiplier in 2% increments from 100%.  "
            "Most printers run best at 95–100%\n"
            "- **Temperature too high**: Excess heat makes filament runny; reduce in 5°C steps\n"
            "- **Wrong filament diameter**: Measure your filament with calipers in several spots — "
            "1.75mm filament is often 1.72–1.78mm; enter the measured value\n\n"
            "**Calibration:**\n"
            "Print a single-wall calibration cube and measure the wall thickness with calipers.  "
            "If it should be 0.4mm (one nozzle width) but measures 0.48mm, reduce flow by "
            "~17% (0.40/0.48).  Iterate until walls match the expected width."
        ),
        "related": ["under_extrusion"],
    },
    "bed_adhesion": {
        "title": "Bed Adhesion",
        "category": "3D Printing",
        "summary": "Getting the first layer to stick properly to the print bed — the "
                   "foundation for every successful print.",
        "explanation": (
            "Poor bed adhesion is the most common cause of failed prints.  If the first "
            "layer doesn't stick, the print will detach and become spaghetti.  If it sticks "
            "too aggressively, you risk damaging the bed surface.\n\n"
            "**Bed surfaces and their strengths:**\n"
            "- **Smooth PEI**: Excellent for PLA and PETG; prints pop off when cooled\n"
            "- **Textured PEI**: Great release properties; hides first-layer imperfections\n"
            "- **Glass**: Very flat; use glue stick or hairspray for adhesion\n"
            "- **BuildTak / flexible magnetic**: Easy removal with flex; good all-around adhesion\n\n"
            "**Adhesion helpers:**\n"
            "- **Glue stick** (PVA): Thin layer provides adhesion AND acts as a release agent "
            "for PETG on PEI (prevents permanent bonding)\n"
            "- **Hairspray** (unscented): Light mist provides grip for PLA and ABS\n"
            "- **Brim**: Extra rings of material around the base (5–10mm wide) increase surface "
            "area — use for tall, narrow parts\n"
            "- **Raft**: A full sacrificial base — last resort for very warpy materials\n\n"
            "**Z-offset calibration:**\n"
            "The nozzle-to-bed distance on the first layer is critical.  Too high = filament "
            "doesn't press into the bed; too low = filament is squished flat and causes elephant's "
            "foot.  Adjust in 0.02mm increments until the first layer is smooth and consistent."
        ),
        "related": ["warping", "elephants_foot", "first_layer"],
    },
    "z_wobble": {
        "title": "Z Wobble / Banding",
        "category": "3D Printing",
        "summary": "Periodic patterns visible along the Z axis of a print, usually caused "
                   "by mechanical issues in the Z-axis drive system.",
        "explanation": (
            "Z wobble appears as regular, repeating ridges or waves on the vertical surfaces "
            "of a print.  The pattern period usually corresponds to the lead screw pitch "
            "(typically 2mm or 8mm).\n\n"
            "**Common causes:**\n"
            "- **Bent lead screw**: Even a slight bend causes the X-gantry to wobble as it "
            "travels up.  Straighten or replace the lead screw\n"
            "- **Loose Z couplers**: The coupler connecting the stepper to the lead screw must "
            "be tight.  Flexible (spider/jaw) couplers help absorb minor misalignment\n"
            "- **Binding on Z rods**: Bent or misaligned linear rods cause the gantry to flex "
            "as it moves.  Loosen frame bolts, re-align, and re-tighten\n"
            "- **Inconsistent extrusion**: Varying flow rate creates width changes that look "
            "like Z banding.  Check for partial clogs or filament diameter inconsistencies\n\n"
            "**Diagnosis:**\n"
            "Print a tall, thin cylinder (20mm dia, 100mm tall) and examine the surface under "
            "side light.  If ridges repeat at the lead screw pitch (measure with calipers), "
            "it's a mechanical Z issue.  If random, it's likely extrusion-related.\n\n"
            "**Fixes:**\n"
            "- Replace with a high-quality lead screw (anti-backlash nut helps)\n"
            "- Use a flexible coupler between stepper and lead screw\n"
            "- Ensure the gantry moves freely without binding when motors are off"
        ),
        "related": ["layer_shifting", "ghosting_ringing"],
    },
    "ghosting_ringing": {
        "title": "Ghosting / Ringing",
        "category": "3D Printing",
        "summary": "Ripple patterns on print surfaces after sharp corners or features, "
                   "caused by vibrations in the motion system.",
        "explanation": (
            "Ghosting (also called ringing or echoes) shows up as faint rippled copies of "
            "sharp features — like a corner producing diminishing wave patterns on the "
            "adjacent flat surface.\n\n"
            "**Root cause:** When the print head changes direction sharply (at a corner), "
            "its inertia causes the frame and belts to vibrate like a tuning fork.  Those "
            "vibrations translate into the extrusion path.\n\n"
            "**Common causes:**\n"
            "- **Too-fast acceleration/jerk**: The printer changes direction too aggressively.  "
            "Reduce acceleration to 1000–2000mm/s² and jerk to 5–10mm/s\n"
            "- **Loose belts**: Slack belts amplify vibrations.  Tighten until they 'twang' "
            "at a consistent pitch\n"
            "- **Heavy print head**: Direct-drive extruders add mass, worsening ringing.  "
            "Consider a remote/Bowden setup for high-speed printing\n"
            "- **Unstable frame**: Wobbly tables and loose bolts magnify the effect\n\n"
            "**Advanced fix — Input Shaper:**\n"
            "Modern firmware (Klipper, Marlin 2.1+) supports input shaping, which pre-compensates "
            "the motion commands to cancel the printer's natural resonance frequency.  This "
            "lets you print at high speed with minimal ghosting.  Run the resonance test "
            "(accelerometer required) to measure your printer's resonant frequency, then "
            "configure the shaper type (ZV, MZV, or EI) in firmware."
        ),
        "related": ["layer_shifting"],
    },

    # ── Post-Processing ──
    "post_processing": {
        "title": "Post-Processing Overview",
        "category": "Manufacturing",
        "summary": "Techniques applied after printing to improve surface finish, strength, "
                   "or appearance of 3D printed parts.",
        "explanation": (
            "Raw 3D prints often need finishing work before they're ready for use.  Post-processing "
            "ranges from simple support removal to multi-step painting workflows.\n\n"
            "**Common techniques:**\n"
            "- **Support removal**: Break or cut away support structures.  Use flush cutters and "
            "needle-nose pliers.  Sand support scars smooth\n"
            "- **Sanding**: Progressive grit sanding (120 → 220 → 400 → 800) removes layer lines.  "
            "Wet sanding with 800+ grit produces near-glossy surfaces\n"
            "- **Priming and painting**: Filler primer fills minor surface imperfections before paint.  "
            "Two thin coats are better than one thick coat\n"
            "- **Acetone smoothing**: Dissolves the surface of ABS/ASA for a glossy, injection-mold "
            "appearance.  Does NOT work on PLA or PETG\n"
            "- **Annealing**: Heating PLA or PETG in an oven increases crystallinity and heat "
            "resistance but causes slight dimensional shrinkage (1–3%)\n"
            "- **Assembly**: Gluing, heat-set inserts, and mechanical fastening for multi-part prints\n\n"
            "The right post-processing strategy depends on the material, the application (visual "
            "vs. functional), and the effort you're willing to invest.  Use `cad_best_practices` "
            "for a step-by-step checklist."
        ),
        "related": ["sanding", "vapor_smoothing", "painting_priming", "annealing"],
    },
    "sanding": {
        "title": "Sanding 3D Prints",
        "category": "Manufacturing",
        "summary": "Using abrasive paper to remove layer lines and smooth surfaces.  "
                   "Progressive grits from coarse to fine yield professional results.",
        "explanation": (
            "Sanding is the most accessible post-processing technique — all you need is "
            "sandpaper and patience.\n\n"
            "**Grit progression:**\n"
            "- **120 grit**: Aggressive shaping — removes large bumps, support scars, and blobs.  "
            "Use for initial rough leveling only\n"
            "- **220 grit**: Removes visible layer lines on most prints.  This is the workhorse grit\n"
            "- **400 grit**: Smooths out scratches from 220.  Surface starts to feel smooth to touch\n"
            "- **800 grit**: Prepares surface for primer or paint.  Wet sanding recommended\n"
            "- **1000–2000 grit** (wet): For glossy finishes or clear coating prep\n\n"
            "**Wet sanding:** Starting at 400+ grit, dipping the sandpaper in water prevents "
            "clogging, reduces friction heat (which can melt PLA), and produces a finer finish.\n\n"
            "**Filler primer:** After sanding to 400 grit, spray filler primer fills remaining "
            "micro-scratches.  Sand the primer with 600 grit, re-spray, and repeat until smooth.\n\n"
            "**Material notes:**\n"
            "- **PLA**: Sands well but melts with friction heat — use light pressure and wet sand\n"
            "- **ABS**: Sands and finishes excellently — the best FDM material for sanding\n"
            "- **PETG**: Tends to gum up sandpaper — use wet sanding and lower pressure\n"
            "- **Resin prints**: Already smooth — light sanding (400+) is usually sufficient"
        ),
        "related": ["post_processing", "painting_priming"],
    },
    "vapor_smoothing": {
        "title": "Vapor Smoothing (Acetone)",
        "category": "Manufacturing",
        "summary": "Using acetone vapor to dissolve the surface of ABS/ASA prints, "
                   "producing a glossy, injection-mold-like finish.",
        "explanation": (
            "Acetone vapor smoothing melts the outer surface of ABS and ASA prints, filling "
            "in layer lines and creating a smooth, glossy finish with zero sanding.\n\n"
            "**CRITICAL: Only works with ABS and ASA.**  PLA, PETG, Nylon, and most other "
            "materials are not affected by acetone.\n\n"
            "**Cold vapor method (recommended):**\n"
            "1. Place a paper towel dampened with acetone inside a sealed container\n"
            "2. Set the print on a platform inside the container (not touching the towel)\n"
            "3. Seal and wait 15–60 minutes, checking every 10–15 minutes\n"
            "4. Remove when surfaces are glossy but details are still crisp\n"
            "5. Let the part air-dry for 30+ minutes before handling\n\n"
            "**Warm vapor method (faster, more dangerous):**\n"
            "Heat acetone gently on a hot plate — **never use open flame** (acetone is "
            "extremely flammable with a flash point of -20°C).  Results are faster (5–15min) "
            "but harder to control.\n\n"
            "**Safety:**\n"
            "- Work outdoors or under a fume hood — acetone vapor is flammable and harmful to inhale\n"
            "- Wear nitrile gloves (acetone dissolves latex)\n"
            "- Do not over-smooth — details will be lost and the part becomes dimensionally "
            "inaccurate.  Check every 10 minutes"
        ),
        "related": ["post_processing", "abs_asa"],
    },
    "annealing": {
        "title": "Annealing 3D Prints",
        "category": "Manufacturing",
        "summary": "Heating printed parts to increase crystallinity, improving strength "
                   "and heat resistance at the cost of slight dimensional change.",
        "explanation": (
            "Annealing is a heat-treatment process where you bake a printed part in an oven "
            "to reorganize the polymer chains into a more crystalline structure.  This increases "
            "stiffness, heat deflection temperature, and sometimes layer adhesion.\n\n"
            "**Temperature and time by material:**\n"
            "- **PLA**: 60–70°C for 1–2 hours.  Increases heat resistance from ~55°C to ~110°C.  "
            "Expect 1–5% dimensional shrinkage\n"
            "- **PETG**: 80–90°C for 1–2 hours.  Moderate improvement in rigidity.  "
            "Less shrinkage than PLA (0.5–2%)\n"
            "- **ABS**: 90–100°C for 1–2 hours.  Modest improvement, but ABS is already "
            "fairly heat-resistant\n\n"
            "**Process:**\n"
            "1. Preheat oven to target temperature (use an oven thermometer — kitchen ovens "
            "are notoriously inaccurate)\n"
            "2. Place the part on a flat surface (baking sheet with parchment paper)\n"
            "3. Pack sand, salt, or plaster around the part to support it against warping\n"
            "4. Bake for 1–2 hours, then turn off the oven and let it cool slowly inside\n\n"
            "**When to anneal:** Functional parts under sustained mechanical or thermal load — "
            "brackets, housings near heat sources, structural clips.  Don't anneal cosmetic "
            "parts where dimensional accuracy matters more than strength."
        ),
        "related": ["post_processing"],
    },
    "painting_priming": {
        "title": "Painting and Priming",
        "category": "Manufacturing",
        "summary": "Surface preparation and painting techniques for achieving professional "
                   "finishes on 3D printed parts.",
        "explanation": (
            "A good paint job requires patient surface prep.  Primer fills imperfections, "
            "provides a uniform base color, and helps paint adhere to plastic.\n\n"
            "**Step-by-step workflow:**\n"
            "1. **Sand** the print to at least 400 grit (see sanding topic)\n"
            "2. **Clean** thoroughly — wash with soap and water, dry completely.  Oils from "
            "hands prevent adhesion\n"
            "3. **Filler primer** spray (like Rust-Oleum Filler Primer): 2–3 light coats, "
            "sanding with 600 grit between coats.  This fills remaining layer lines\n"
            "4. **Surface primer** spray: 1–2 thin coats of plastic-specific primer (Tamiya, "
            "Krylon) for paint adhesion.  Let cure 24 hours\n"
            "5. **Paint**: Thin coats, building up color gradually.  2–3 coats minimum\n"
            "   - Spray paint: Hold 20–30cm away, even sweeping motions\n"
            "   - Brush: Use quality synthetic brushes; thin paint slightly\n"
            "   - Airbrush: Best results but steepest learning curve\n"
            "6. **Clear coat**: 2–3 light coats of matte, satin, or gloss clear for protection "
            "and UV resistance\n\n"
            "**Paint types:**\n"
            "- **Acrylic (water-based)**: Easy cleanup, low odor, good for most applications\n"
            "- **Enamel (solvent-based)**: More durable, harder surface, stronger odor\n"
            "- **Lacquer**: Best finish quality but requires spray equipment and ventilation\n\n"
            "Always test paint adhesion on a scrap piece first — some material/paint "
            "combinations peel."
        ),
        "related": ["post_processing", "sanding"],
    },

    # ── Design for Assembly ──
    "heat_set_inserts": {
        "title": "Heat-Set Threaded Inserts",
        "category": "Manufacturing",
        "summary": "Brass knurled inserts that provide durable machine-screw threads in "
                   "3D printed parts.  Far stronger than threading into plastic directly.",
        "explanation": (
            "Heat-set inserts are small brass cylinders with external knurling and internal "
            "machine threads.  You press them into a slightly undersized hole using a soldering "
            "iron, and the heat melts the surrounding plastic, which flows into the knurls and "
            "locks the insert permanently.\n\n"
            "**Common sizes:**\n"
            "- **M3** (most common for 3D printing): Hole diameter 4.0–4.2mm, boss OD ≥7mm\n"
            "- **M4**: Hole diameter 5.2–5.4mm, boss OD ≥9mm\n"
            "- **M5**: Hole diameter 6.2–6.5mm, boss OD ≥10mm\n\n"
            "**Installation:**\n"
            "1. Set soldering iron to 220–260°C (lower for PLA, higher for PETG/ABS)\n"
            "2. Place insert on the hole, resting on the knurled end\n"
            "3. Apply gentle downward pressure with the iron tip — let heat do the work\n"
            "4. Press until the insert is flush with or 0.5mm below the surface\n"
            "5. Let cool before inserting screws\n\n"
            "**Boss design:**\n"
            "- Wall thickness around the insert should be at least 1.5mm (preferably 2mm)\n"
            "- Add a slight chamfer at the top of the hole to guide the insert\n"
            "- Make the hole 0.5–1mm deeper than the insert to leave room for displaced plastic\n\n"
            "Heat-set inserts can handle 20+ assembly/disassembly cycles and torques up to "
            "2–3 Nm for M3 — far exceeding self-tapping screws in plastic."
        ),
        "related": ["screw_bosses", "design_for_assembly"],
    },
    "snap_fits": {
        "title": "Snap Fits",
        "category": "Manufacturing",
        "summary": "Cantilever clips that allow tool-free assembly of 3D printed parts.  "
                   "Print orientation is critical for durability.",
        "explanation": (
            "Snap fits use a flexible arm (cantilever beam) with a hook that deflects during "
            "assembly and snaps into a mating pocket.  They're the fastest way to join printed "
            "parts without hardware.\n\n"
            "**Design guidelines for FDM:**\n"
            "- **Deflection**: Keep maximum deflection under 2–3% of the arm length to avoid "
            "permanent deformation or breakage\n"
            "- **Arm dimensions**: Typical arm is 2–3mm wide, 1–1.5mm thick, 10–20mm long.  "
            "Longer arms deflect more easily with less stress\n"
            "- **Hook overhang**: 0.5–1.5mm overhang provides a positive 'click'.  Add a 30–45° "
            "entry angle for easy insertion\n"
            "- **Return angle**: 90° for permanent assembly, 30–45° for removable clips\n\n"
            "**Print orientation is critical:**\n"
            "- The layer lines must be **perpendicular to the deflection axis** — otherwise "
            "the clip snaps along layer boundaries on the first use\n"
            "- Orient so the bending axis is along the Z axis (print standing up)\n\n"
            "**Best materials:**\n"
            "- **PETG**: Good flexibility and layer adhesion — best overall for snap fits\n"
            "- **TPU**: Extremely flexible — great for clips that need repeated use\n"
            "- **PLA**: Brittle — snap fits tend to break after a few cycles\n"
            "- **ABS**: Decent if printed with good layer adhesion (enclosure required)"
        ),
        "related": ["press_fits", "tolerances"],
    },
    "screw_bosses": {
        "title": "Screw Bosses",
        "category": "Manufacturing",
        "summary": "Reinforced cylindrical posts designed to accept self-tapping screws "
                   "for joining 3D printed parts.",
        "explanation": (
            "Screw bosses are cylindrical protrusions with pilot holes sized for self-tapping "
            "screws.  The screw cuts threads directly into the printed plastic as it's driven "
            "in — no insert or nut needed.\n\n"
            "**Pilot hole sizing (for common screws):**\n"
            "- **M2 self-tapping**: 1.6mm pilot hole\n"
            "- **M2.5 self-tapping**: 2.0mm pilot hole\n"
            "- **M3 self-tapping**: 2.5mm pilot hole\n"
            "- **#4 (US)**: 2.0mm pilot hole\n"
            "- **#6 (US)**: 2.7mm pilot hole\n\n"
            "**Boss design rules:**\n"
            "- **Wall thickness**: At least 2× the screw's outer diameter (M3 screw → ≥6mm boss OD)\n"
            "- **Height**: The engaged thread length should be at least 2× the screw diameter\n"
            "- **Reinforcing ribs**: Add 3–4 triangular gussets around the base of tall bosses "
            "to prevent snapping under torque\n"
            "- **Chamfer the entry**: A 0.5mm chamfer at the top of the pilot hole helps the "
            "screw start without cross-threading\n\n"
            "**Limitations vs. heat-set inserts:**\n"
            "Self-tapping screws degrade the hole with each removal — after 5–10 cycles the "
            "threads strip.  For parts that need repeated assembly, use heat-set inserts instead."
        ),
        "related": ["heat_set_inserts"],
    },
    "press_fits": {
        "title": "Press Fits",
        "category": "Manufacturing",
        "summary": "Joining parts by pushing one into the other with a tight interference "
                   "fit — no fasteners or adhesive needed.",
        "explanation": (
            "A press fit (interference fit) joins two parts by making one slightly larger "
            "than the hole it fits into.  The elastic deformation of the plastic holds the "
            "parts together through friction.\n\n"
            "**Interference values for FDM:**\n"
            "- **Light press fit**: 0.0–0.05mm interference — parts push together by hand, "
            "hold by friction.  Good for caps, covers, and plugs\n"
            "- **Medium press fit**: 0.05–0.10mm interference — requires moderate force.  "
            "Good for bearings, bushings, and permanent joints\n"
            "- **Heavy press fit**: 0.10–0.15mm — risky on FDM; may crack the outer part.  "
            "Only use with ductile materials (PETG, Nylon)\n\n"
            "**Critical factors:**\n"
            "- **Print orientation**: Parts are strongest around the circumference when the "
            "cylinder axis is parallel to Z.  Cross-grain press fits fail easily\n"
            "- **Material choice**: PETG and Nylon flex and grip; PLA cracks.  ABS works well "
            "if printed with an enclosure\n"
            "- **Thermal expansion**: Printed parts expand when warm — a tight press fit at "
            "room temp may loosen in a hot enclosure\n"
            "- **Test first**: Always print a test coupon — a cylinder and a hole at several "
            "interference values (0.00, 0.05, 0.10mm) to find the right fit for your printer"
        ),
        "related": ["tolerances", "snap_fits"],
    },

    # ── Advanced OpenSCAD ──
    "openscad_modules": {
        "title": "OpenSCAD Modules and Functions",
        "category": "3D Modeling",
        "summary": "Reusable building blocks in OpenSCAD — modules create geometry, "
                   "functions compute values.  Essential for clean, maintainable code.",
        "explanation": (
            "Modules and functions are how you organize OpenSCAD code beyond simple scripts.\n\n"
            "**Modules** (create geometry):\n"
            "```\n"
            "module rounded_box(size, radius) {\n"
            "    minkowski() {\n"
            "        cube(size - [radius,radius,0]*2, center=true);\n"
            "        cylinder(r=radius, h=0.01);\n"
            "    }\n"
            "}\n"
            "rounded_box([40,30,10], 3);  // use it\n"
            "```\n\n"
            "**Functions** (compute values, no geometry):\n"
            "```\n"
            "function bolt_circle(n, r) = [for (i=[0:n-1]) [r*cos(i*360/n), r*sin(i*360/n)]];\n"
            "```\n\n"
            "**Key concepts:**\n"
            "- **Parameterized modules**: Accept arguments with defaults — `module box(w=10, h=5)`\n"
            "- **children()**: Access geometry passed as children to a module, enabling "
            "transform-wrapper patterns like `module place_at_corners() { ... children(); }`\n"
            "- **Module vs function**: Modules produce geometry (use `cube`, `cylinder`, etc.); "
            "functions return values (numbers, vectors, strings) — they cannot create geometry\n"
            "- **include vs use**: `include <file.scad>` runs all code; `use <file.scad>` "
            "imports only modules and functions without executing top-level geometry\n\n"
            "Use `openscad_list_params` to discover the parameters of any .scad file's "
            "top-level variables, and `openscad_preview` to visualize the result."
        ),
        "related": ["parametric", "openscad_libraries"],
    },
    "openscad_hull_minkowski": {
        "title": "Hull and Minkowski in OpenSCAD",
        "category": "3D Modeling",
        "summary": "Two powerful but computationally expensive operations for rounding "
                   "edges and connecting shapes in OpenSCAD.",
        "explanation": (
            "Hull and Minkowski are the two main 'shape blending' operations in OpenSCAD.  "
            "Both are extremely useful but can be slow on complex geometry.\n\n"
            "**hull() — Convex Hull:**\n"
            "Creates the smallest convex shape that encloses all children.  Think of it as "
            "wrapping shrink-wrap around a group of objects.\n"
            "- **Rounding rectangles**: `hull() { translate(corners) cylinder(r=3, h=1); }` — "
            "place cylinders at corners, hull connects them into a rounded rectangle\n"
            "- **Connecting shapes**: Hull between two spheres creates a capsule/pill shape\n"
            "- **Limitation**: Result is always convex — no concave features\n\n"
            "**minkowski() — Minkowski Sum:**\n"
            "Sweeps one shape along the surface of another.  The most common use is rounding "
            "all edges of a shape:\n"
            "- `minkowski() { cube([20,20,10]); sphere(r=2); }` rounds all edges with radius 2\n"
            "- **Important**: The result is the original size PLUS the rounding shape's size.  "
            "Subtract the rounding radius from your base dimensions to maintain target size\n"
            "- **Performance warning**: Minkowski on complex geometry is extremely slow "
            "(O(n × m) on mesh faces).  Keep child meshes simple — use low `$fn` (16–32) on "
            "the rounding sphere\n\n"
            "**Performance tips:**\n"
            "- Use hull() instead of minkowski() when you only need to round 2D outlines\n"
            "- For 3D edge rounding, consider BOSL2's `round_corners()` — it's much faster\n"
            "- Set `$fn=16` on the rounding primitive during development, increase for final render"
        ),
        "related": ["csg", "openscad_modules"],
    },
    "openscad_libraries": {
        "title": "OpenSCAD Libraries (BOSL2, MCAD)",
        "category": "3D Modeling",
        "summary": "Community libraries that extend OpenSCAD with advanced features: "
                   "rounding, threading, gears, fasteners, and more.",
        "explanation": (
            "OpenSCAD's built-in primitives are intentionally minimal.  Libraries add the "
            "missing pieces.\n\n"
            "**BOSL2** (Belfry OpenSCAD Library v2) — the most comprehensive:\n"
            "- **Attachments**: Position parts relative to each other using named anchor points "
            "instead of manual translate/rotate calculations\n"
            "- **Rounding**: `cuboid(size, rounding=3)` — rounded cubes without slow minkowski\n"
            "- **Threading**: ISO metric threads, ACME threads, ball screws — `threaded_rod(d=10, pitch=1.5, l=30)`\n"
            "- **Gears**: Spur gears, bevel gears, worm gears, racks\n"
            "- **Distributors**: `grid_copies()`, `arc_copies()` — place children in patterns\n\n"
            "**MCAD** (legacy, bundled with OpenSCAD):\n"
            "- Basic shapes, involute gears, metric fasteners\n"
            "- Included by default — no installation needed\n"
            "- Less actively maintained; prefer BOSL2 for new projects\n\n"
            "**NopSCADlib** (vitamins and hardware):\n"
            "- Parametric models of real components: screws, nuts, bearings, PCBs, fans, motors\n"
            "- Great for enclosure design — drop in an exact M3x10 screw model\n\n"
            "**Installation:**\n"
            "- Download/clone the library into your OpenSCAD library path\n"
            "- Linux/Mac: `~/.local/share/OpenSCAD/libraries/`\n"
            "- Windows: `Documents\\OpenSCAD\\libraries\\`\n"
            "- Use in your file: `include <BOSL2/std.scad>` or `use <MCAD/gears.scad>`"
        ),
        "related": ["openscad_modules", "parametric"],
    },

    # ── Multi-Material / Multi-Color ──
    "multi_material": {
        "title": "Multi-Material Printing",
        "category": "3D Printing",
        "summary": "Printing with multiple filament types or colors in a single print.  "
                   "Requires tool-changing or filament-switching hardware.",
        "explanation": (
            "Multi-material printing lets you combine different colors or material properties "
            "in one print — for example, a rigid body with flexible TPU grips.\n\n"
            "**Hardware approaches:**\n"
            "- **Dual extruder**: Two separate hotends, each loaded with a different material.  "
            "Downsides: oozing from idle nozzle, reduced build volume, complex calibration\n"
            "- **Tool changer**: Swaps entire print heads (e.g., E3D ToolChanger, Prusa XL).  "
            "Clean swaps, minimal oozing, but expensive\n"
            "- **Filament switcher (AMS/MMU)**: Single hotend with automated filament changes.  "
            "Most popular consumer approach — see `ams_printing`\n\n"
            "**Purge tower:**\n"
            "Every material switch requires purging the old material from the nozzle.  The "
            "purge is deposited as a waste tower alongside the print — this uses 1–3g of "
            "filament per switch.  Minimize color changes per layer to reduce waste.\n\n"
            "**Material compatibility:**\n"
            "- PLA + PLA (different colors): No issues\n"
            "- PLA + PETG: Different temps, poor adhesion between them — not recommended\n"
            "- PLA + PVA: Good for soluble supports\n"
            "- PETG + TPU: Works well — rigid structure with flexible inserts\n"
            "- ABS + ABS: Fine, but still needs enclosure\n\n"
            "Use `bambu_compare_materials` to check material compatibility and recommended settings."
        ),
        "related": ["ams_printing"],
    },
    "ams_printing": {
        "title": "AMS (Automatic Material System)",
        "category": "3D Printing",
        "summary": "Bambu Lab's filament switching system — load up to 4 spools and the "
                   "printer automatically swaps between them during a print.",
        "explanation": (
            "The AMS (Automatic Material System) is Bambu Lab's approach to multi-color and "
            "multi-material printing.  It sits on top of the printer and feeds filament to "
            "the single extruder through a long Bowden tube.\n\n"
            "**Key specs:**\n"
            "- **4 slots** per AMS unit (up to 4 AMS units = 16 materials on some printers)\n"
            "- **Automatic loading/unloading**: The AMS retracts the current filament, feeds "
            "the next one, and purges the transition in the waste tower\n"
            "- **RFID tagging**: Bambu-branded spools are auto-detected with material type "
            "and remaining weight\n\n"
            "**Slicer workflow (Bambu Studio / Orca Slicer):**\n"
            "- Assign materials to AMS slots (filament type + color)\n"
            "- Use 'paint on color' to assign colors to specific surfaces of the model\n"
            "- The slicer generates the purge tower and tool-change G-code automatically\n\n"
            "**Tips for reducing waste and time:**\n"
            "- Group same-color regions vertically to minimize switches per layer\n"
            "- Each color change costs ~10–15 seconds and 1–3g of purge waste\n"
            "- Set flush volume in slicer — dark-to-light transitions need more purge\n\n"
            "**Humidity management:**\n"
            "The AMS enclosure provides some moisture protection, but it's not a dryer.  "
            "For hygroscopic materials (PETG, Nylon, TPU), pre-dry before loading.  Bambu "
            "sells desiccant packs that fit inside the AMS.\n\n"
            "Use `bambu_slice` to prepare multi-color prints and `bambu_compare_materials` "
            "to check compatibility between filaments in different AMS slots."
        ),
        "related": ["multi_material"],
    },

    # ── General Printing Concepts ──
    "first_layer": {
        "title": "First Layer",
        "category": "3D Printing",
        "summary": "The foundation of every print.  Getting the first layer right is "
                   "the most important step for print success.",
        "explanation": (
            "The first layer is make-or-break for every print.  A bad first layer causes "
            "adhesion failures, warping, elephant's foot, and dimensional inaccuracy at the "
            "base of the part.\n\n"
            "**Z-offset calibration:**\n"
            "The gap between the nozzle and the bed on the first layer determines everything:\n"
            "- **Too high**: Filament doesn't press into the bed — poor adhesion, rough texture\n"
            "- **Too low**: Filament is smashed flat — elephant's foot, hard to remove from bed\n"
            "- **Just right**: Lines are slightly squished with no gaps between them, smooth "
            "and even surface.  Adjust in 0.02mm increments\n\n"
            "**First-layer settings (typical):**\n"
            "- **Speed**: 50–70% of normal print speed (20–30mm/s) for better adhesion\n"
            "- **Line width**: 120–150% of nozzle diameter for extra squish and coverage\n"
            "- **Bed temperature**: At or slightly above normal (helps adhesion during the "
            "critical first minutes)\n"
            "- **Fan**: Off for the first 1–3 layers to let plastic bond to the bed\n\n"
            "**Skirt, brim, and raft:**\n"
            "- **Skirt**: A few loops around the print — doesn't aid adhesion but primes the "
            "nozzle and lets you verify Z-offset before the real print starts\n"
            "- **Brim**: Extra material attached to the base edge — increases contact area.  "
            "Use 5–10mm width for tall/narrow parts\n"
            "- **Raft**: A full base under the print — maximum adhesion but worst bottom surface"
        ),
        "related": ["bed_adhesion", "warping", "elephants_foot"],
    },
    "retraction": {
        "title": "Retraction",
        "category": "3D Printing",
        "summary": "Pulling filament backward in the hotend during travel moves to "
                   "prevent oozing and stringing.",
        "explanation": (
            "Retraction is the extruder's defense against stringing.  Before the print head "
            "travels across empty space, the extruder motor reverses to pull filament back "
            "from the melt zone, reducing pressure and stopping ooze.\n\n"
            "**Key settings:**\n"
            "- **Retraction distance**: How far to pull back\n"
            "  - Bowden extruder: 4–7mm (long tube means more distance needed)\n"
            "  - Direct drive: 0.5–2mm (short path, less needed)\n"
            "- **Retraction speed**: How fast to pull back — typically 25–50mm/s.  Faster "
            "reduces ooze but too fast shreds the filament\n"
            "- **Retraction count limit**: Maximum retractions per length of filament (typically "
            "10 per mm).  Too many retractions grind the filament — the 'heat creep death zone'\n\n"
            "**Too much retraction:**\n"
            "- Filament grinding (extruder gear chews through filament)\n"
            "- Air gaps in the hotend causing under-extrusion after un-retract\n"
            "- Clogs from pulling cooled filament into the cold zone\n\n"
            "**Too little retraction:**\n"
            "- Stringing and oozing between travel moves\n"
            "- Blobs at travel start/end points\n\n"
            "**Calibration:** Print a retraction test tower — columns separated by gaps.  "
            "Start with middle-of-range values and adjust retraction distance in 0.5mm steps "
            "until stringing disappears without introducing under-extrusion."
        ),
        "related": ["stringing", "under_extrusion"],
    },
    "cooling": {
        "title": "Part Cooling",
        "category": "3D Printing",
        "summary": "The part cooling fan solidifies filament quickly after extrusion.  "
                   "Critical for bridges, overhangs, and fine detail.",
        "explanation": (
            "The part cooling fan blows air directly onto the freshly extruded plastic, "
            "accelerating solidification.  More cooling = sharper detail but weaker layer "
            "adhesion.  Less cooling = stronger bonds but sagging overhangs.\n\n"
            "**Material-specific fan settings:**\n"
            "- **PLA**: 100% fan after the first 2–3 layers.  PLA loves cooling — max fan "
            "produces the best bridges, overhangs, and surface detail\n"
            "- **PETG**: 30–60% fan.  Too much cooling causes layer splitting and poor "
            "adhesion.  Some PETG brands prefer 0% for first 5 layers\n"
            "- **ABS/ASA**: 0–20% fan (or off entirely).  ABS needs to stay warm for layer "
            "bonding.  Cooling causes cracking, warping, and delamination.  Use an enclosure\n"
            "- **TPU**: 30–50% fan.  Moderate cooling helps detail without causing brittleness\n"
            "- **Nylon**: 0–30% fan.  Nylon warps severely with too much cooling\n\n"
            "**When to override:**\n"
            "- **Bridges**: Maximum fan regardless of material — solidify the span quickly\n"
            "- **Overhangs > 45°**: Increase fan by 20–30% above normal for better support-free "
            "performance\n"
            "- **Small layers**: If a layer prints in under 10 seconds, either slow down or "
            "increase fan to prevent heat buildup from melting the previous layer\n"
            "- **First layer**: Always 0% fan — cooling the first layer prevents bed adhesion"
        ),
        "related": ["bridging", "overhangs"],
    },
    "nozzle_sizes": {
        "title": "Nozzle Sizes",
        "category": "3D Printing",
        "summary": "Different nozzle diameters trade off between detail resolution and "
                   "print speed.  0.4mm is the standard, but 0.2–0.8mm all have uses.",
        "explanation": (
            "The nozzle diameter determines the width of each extrusion line and constrains "
            "the maximum layer height, wall thickness, and achievable detail.\n\n"
            "**Common sizes and their sweet spots:**\n"
            "- **0.2mm**: Miniatures, jewelry, fine text.  Very slow, clogs easily.  Max layer "
            "height 0.15mm.  Use hardened steel for longevity\n"
            "- **0.4mm** (standard): The default for good reason — balances speed, detail, and "
            "reliability.  Max layer height 0.3mm\n"
            "- **0.6mm**: 50% faster than 0.4mm with only slight detail loss.  Great for "
            "functional parts, enclosures, and prototypes.  Max layer height 0.45mm\n"
            "- **0.8mm**: Speed demon — 4× the volume flow of 0.4mm.  Visible lines but very "
            "strong parts.  Max layer height 0.6mm.  Ideal for large structural prints\n"
            "- **1.0mm**: Extremely fast vase-mode prints and large-scale objects\n\n"
            "**Key relationships:**\n"
            "- **Max layer height**: ~75% of nozzle diameter\n"
            "- **Line width**: Typically 100–120% of nozzle diameter (0.4mm nozzle → 0.4–0.48mm lines)\n"
            "- **Min feature size**: Roughly 2× the nozzle diameter (0.4mm nozzle can't resolve "
            "features smaller than ~0.8mm)\n\n"
            "**Nozzle materials:**\n"
            "- **Brass**: Standard, good thermal conductivity.  Wears with abrasive filaments "
            "(CF, GF, glow-in-dark) — replace every 500–1000 hours\n"
            "- **Hardened steel**: Resists abrasion but lower thermal conductivity — increase "
            "temp by 5–10°C vs. brass\n"
            "- **Ruby-tipped / tungsten carbide**: Premium, very long-lasting, expensive"
        ),
        "related": ["layer_height", "wall_thickness"],
    },
    "bed_types": {
        "title": "Print Bed Surfaces",
        "category": "3D Printing",
        "summary": "The build surface material affects adhesion, release, and bottom "
                   "surface finish.  Different materials suit different filaments.",
        "explanation": (
            "The print bed surface is where adhesion happens — choosing the right surface "
            "for your filament avoids both adhesion failures and parts permanently bonded "
            "to the bed.\n\n"
            "**Common bed surfaces:**\n"
            "- **Smooth PEI (Ultem)**: The most popular all-around surface.  PLA, PETG, and "
            "ABS all adhere well.  Parts pop off when cooled.  **Warning**: PETG can bond "
            "permanently to smooth PEI — use glue stick as a release agent\n"
            "- **Textured PEI**: Powder-coated PEI with a slightly rough texture.  Excellent "
            "PETG release, good PLA adhesion, attractive textured bottom surface\n"
            "- **Glass** (plain or coated): Very flat, producing mirror-smooth bottoms.  "
            "Needs glue stick or hairspray for adhesion.  Borosilicate glass is best "
            "(thermal-shock resistant)\n"
            "- **BuildTak / magnetic flex plates**: Spring steel sheets with adhesive coating.  "
            "Flex the plate to pop parts off — extremely convenient\n"
            "- **Garolite (G10/FR4)**: The best surface for Nylon — nothing else sticks as well\n\n"
            "**Maintenance:**\n"
            "- Clean with IPA (isopropyl alcohol) between prints to remove finger oils\n"
            "- Deep clean with dish soap and water every 10–20 prints\n"
            "- PEI surfaces lose adhesion over time — light sanding with 1000-grit or acetone "
            "wipe refreshes the surface\n"
            "- Replace flex plates when the coating peels or adhesion degrades consistently\n\n"
            "**Bed temperature by material:**\n"
            "PLA: 55–65°C | PETG: 75–85°C | ABS/ASA: 95–110°C | TPU: 50–60°C | Nylon: 70–90°C"
        ),
        "related": ["bed_adhesion", "first_layer"],
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
    "sla_resin": {
        "title": "SLA / Resin Printing Best Practices",
        "category": "3D Printing",
        "practices": [
            "Wear nitrile gloves and safety glasses at all times when handling resin",
            "Ventilate work area — use a fume extractor or work near an open window",
            "Tilt parts 30–45° to reduce peel forces and minimize large cross-sections",
            "Hollow large parts with drain holes (2–3mm) to save resin and reduce peel force",
            "Wash prints in IPA for 2–3 minutes (or use water-washable resin for easier cleanup)",
            "UV cure after washing — 405nm light for 5–15 minutes depending on resin type",
            "Calibrate exposure with test prints (Ameralabs Town or RERF) for each new resin",
            "Keep resin bottle sealed when not in use — UV light from windows can partially cure it",
            "Filter resin through a paint strainer before pouring back into the bottle",
            "Use water-washable resin for easier cleanup if you don't have an IPA wash station",
        ],
    },
    "tpu_flex": {
        "title": "TPU / Flexible Filament Best Practices",
        "category": "Material",
        "practices": [
            "Direct drive extruder strongly recommended — Bowden tubes allow TPU to buckle and jam",
            "Print slow: 15–30mm/s for reliable extrusion (some printers handle 40mm/s with tuning)",
            "Disable retraction or set very low (0.5–1mm) — TPU compresses instead of retracting cleanly",
            "Print at 220–240°C nozzle / 50°C bed — higher temps improve flow and layer adhesion",
            "Use wider line widths (0.5mm+ with 0.4mm nozzle) for better bed adhesion and fill",
            "Constrain the filament path between extruder gear and hotend to prevent buckling",
            "Gyroid infill provides the most consistent and predictable flex behavior",
            "Shore hardness matters: 95A is standard semi-flexible, 85A is soft, 60A is very soft (needs specialized setup)",
        ],
    },
    "multi_color": {
        "title": "Multi-Color / AMS Printing Best Practices",
        "category": "3D Printing",
        "practices": [
            "Minimize color changes per layer — each change costs ~10–15 seconds plus 1–3g of material waste",
            "Group same-color regions vertically where possible to reduce switches per layer",
            "Purge tower uses 1–3g per color change — a 4-color print can waste 30–50g of filament",
            "Check filament compatibility — don't mix PLA with ABS in the same print (different temps)",
            "Use flush volumes in slicer to set purge amount — dark-to-light transitions need more purge",
            "Paint-on color in Bambu Studio or Orca Slicer for logos, text, and surface details",
            "Dry filaments before loading into AMS — moisture causes steam bubbles during filament switches",
            "Consider using fewer colors with strategic placement — 2 colors often looks better than 4 with less waste",
        ],
    },
    "design_for_assembly": {
        "title": "Design for Assembly Best Practices",
        "category": "Design",
        "practices": [
            "Use heat-set inserts for repeated assembly/disassembly — M3 is the most common size for 3D prints",
            "Design screw bosses with wall thickness of at least 2× the screw outer diameter",
            "Add alignment features (pins, tabs, chamfered edges) to ensure parts mate correctly every time",
            "Print test fit coupons before committing to full parts — saves hours of reprinting",
            "Cantilever snap fits need layer lines perpendicular to the deflection axis to avoid fracture",
            "Leave 0.2–0.3mm clearance for sliding fits — calibrate to your specific printer and material",
            "Chamfer mating edges (0.5–1mm at 45°) for easy alignment during assembly",
            "Include assembly marks or part numbers on hidden surfaces to simplify multi-part builds",
        ],
    },
    "post_processing": {
        "title": "Post-Processing Best Practices",
        "category": "Manufacturing",
        "practices": [
            "Remove supports before any other finishing — use flush cutters and needle-nose pliers",
            "Sand progressively: 120 → 220 → 400 → 800 grit — never skip more than one grit step",
            "Use filler primer spray between sanding passes to fill remaining micro-scratches",
            "Wet sand at 400 grit and above — prevents clogging and reduces friction heat on PLA",
            "Acetone smoothing for ABS/ASA only — does not work on PLA, PETG, or other materials",
            "Prime before painting with a plastic-specific primer for proper adhesion",
            "Apply thin multiple coats over one thick single coat — prevents drips and uneven coverage",
            "Clear coat for durability and UV protection — matte, satin, or gloss depending on desired finish",
            "Test paint adhesion on a scrap piece first — some material/paint combinations peel",
        ],
    },
    "calibration": {
        "title": "Printer Calibration Best Practices",
        "category": "3D Printing",
        "practices": [
            "Calibrate E-steps / flow rate first — extrude 100mm of filament and measure actual output",
            "Run a temperature tower for each new filament brand to find the optimal nozzle temperature",
            "Print a retraction test tower to tune retraction distance and speed for minimal stringing",
            "Run a bed level mesh (auto or manual) before precision prints — especially after moving the printer",
            "Print a 20mm calibration cube and measure with calipers — adjust flow and steps until dimensions match",
            "Tune pressure advance / linear advance for clean corners without bulging or gaps",
            "Check belt tension — belts should twang like a guitar string with no visible slack",
            "Re-calibrate after nozzle changes, maintenance, or firmware updates",
        ],
    },
    "enclosure_design": {
        "title": "Electronics Enclosure Design Best Practices",
        "category": "Design",
        "practices": [
            "Measure PCBs with calipers — datasheets often round or omit tolerances",
            "Add 0.5mm clearance around PCBs for easy insertion and thermal expansion",
            "Design standoffs with M2.5 or M3 mounting holes matching the PCB hole pattern",
            "Include ventilation slots or holes for heat-generating components (5–10% of wall area)",
            "Route cable channels from connectors to board edges — avoid sharp bends in cable paths",
            "Design snap-fit or screw-close lids — screw closures are more reliable for repeated access",
            "Label port openings on the exterior (USB, HDMI, power) for user-friendly assembly",
            "Add draft angles or tapers for stacking multiple enclosures neatly",
            "Use openscad_list_params to parameterize PCB dimensions, wall thickness, and clearances",
        ],
    },
    "large_prints": {
        "title": "Large Print Best Practices",
        "category": "3D Printing",
        "practices": [
            "Split parts along natural seams or flat faces — each piece needs a flat side for bed adhesion",
            "Use alignment pins or dowels (3mm press-fit pins work well) for precise reassembly",
            "Add keyed joints (D-shaped pins, asymmetric tabs) to prevent misalignment during gluing",
            "Apply brim on all split pieces — large parts amplify warping forces at corners",
            "Consider print orientation for strength at joints — layer lines parallel to the glue surface are weakest",
            "Glue with CA (super glue) for PLA, or solvent-weld with acetone for ABS — epoxy for mixed materials",
            "Ensure consistent material batch across all pieces — different batches may have slight color or shrinkage variation",
            "Allow extra time and monitor — large prints amplify small issues (clogs, stringing, adhesion) over hours",
        ],
    },
    "troubleshooting_fdm": {
        "title": "FDM Troubleshooting Quick Reference",
        "category": "3D Printing",
        "practices": [
            "Stringing → increase retraction distance + reduce nozzle temperature by 5–10°C",
            "Layer shifting → check belt tension + reduce print speed and acceleration",
            "Elephant's foot → raise Z offset by 0.02–0.05mm + reduce first-layer bed temp by 5°C",
            "Warping → increase bed temp + add brim + use enclosure for ABS/ASA/Nylon",
            "Under-extrusion → check for clogs (cold pull) + increase temp + calibrate flow rate",
            "Poor bed adhesion → level bed + clean surface with IPA + adjust Z offset closer",
            "Blobs/zits → enable coasting in slicer + tune pressure advance / linear advance",
            "Rough overhangs → increase part cooling fan + reduce speed + add supports above 45°",
        ],
    },
}


# ---------------------------------------------------------------------------
# Synonym map — redirects common queries to canonical concept/practice slugs
# ---------------------------------------------------------------------------

SYNONYMS: dict[str, str] = {
    "watertight": "manifold",
    "waterproof": "manifold",
    "holes": "manifold",
    "non_manifold": "manifold",
    "normals": "mesh",
    "stl": "mesh",
    "triangles": "mesh",
    "vertices": "mesh",
    "polygons": "mesh",
    "faces": "mesh",
    "boolean": "csg",
    "union": "csg",
    "difference": "csg",
    "intersection": "csg",
    "variables": "parametric",
    "parameters": "parametric",
    "customizer": "parametric",
    "fdm": "fdm_general",
    "fff": "fdm_general",
    "fused_deposition": "fdm_general",
    "drooping": "overhangs",
    "sagging": "overhangs",
    "angle": "overhangs",
    "resolution": "layer_height",
    "quality": "layer_height",
    "detail": "layer_height",
    "fill": "infill",
    "density": "infill",
    "internal_structure": "infill",
    "curling": "warping",
    "lifting": "warping",
    "detaching": "bed_adhesion",
    "sticking": "bed_adhesion",
    "adhesion": "bed_adhesion",
    "hairy": "stringing",
    "ooze": "stringing",
    "oozing": "stringing",
    "wobble": "z_wobble",
    "banding": "z_wobble",
    "ringing": "ghosting_ringing",
    "ripples": "ghosting_ringing",
    "echoes": "ghosting_ringing",
    "ghost": "ghosting_ringing",
    "gaps": "under_extrusion",
    "blobs": "over_extrusion",
    "zits": "over_extrusion",
    "shifted": "layer_shifting",
    "misaligned": "layer_shifting",
    "smooth": "vapor_smoothing",
    "acetone": "vapor_smoothing",
    "resin": "sla_resin",
    "uv": "sla_resin",
    "dlp": "sla_resin",
    "msla": "sla_resin",
    "inserts": "heat_set_inserts",
    "threaded": "heat_set_inserts",
    "snap": "snap_fits",
    "clip": "snap_fits",
    "screw": "screw_bosses",
    "bolt": "screw_bosses",
    "ams": "ams_printing",
    "multicolor": "multi_material",
    "multi_color": "multi_material",
    "dual_extruder": "multi_material",
    "nozzle": "nozzle_sizes",
    "bed_surface": "bed_types",
    "pei": "bed_types",
    "glass_bed": "bed_types",
    "modules": "openscad_modules",
    "hull": "openscad_hull_minkowski",
    "minkowski": "openscad_hull_minkowski",
    "bosl2": "openscad_libraries",
    "mcad": "openscad_libraries",
    "sand": "sanding",
    "paint": "painting_priming",
    "primer": "painting_priming",
    "anneal": "annealing",
    "heat_treat": "annealing",
    "press_fit": "press_fits",
    "interference_fit": "press_fits",
    "fan": "cooling",
    "part_cooling": "cooling",
}


# ---------------------------------------------------------------------------
# Troubleshooting guide — symptom-based diagnosis
# ---------------------------------------------------------------------------

TROUBLESHOOTING: dict[str, dict] = {
    "stringing": {
        "title": "Stringing / Oozing",
        "symptom": "Thin strings or hairs between parts of the print, especially across travel moves.",
        "causes": [
            "Retraction distance too low",
            "Nozzle temperature too high",
            "Travel speed too low",
            "Wet/moisture-absorbed filament",
        ],
        "fixes": [
            "Increase retraction distance (5-7mm for Bowden, 1-2mm for direct drive)",
            "Reduce nozzle temperature by 5-10°C",
            "Increase travel speed to 150-200mm/s",
            "Dry filament (PLA: 45°C 4h, PETG: 65°C 4h)",
            "Enable 'wipe' or 'coasting' in slicer settings",
        ],
        "materials_most_affected": ["PETG (worst)", "ABS", "TPU", "PLA (least)"],
        "severity": "cosmetic",
        "related_concepts": ["retraction", "over_extrusion"],
    },
    "layer_shifting": {
        "title": "Layer Shifting",
        "symptom": "Sudden horizontal offset in one or more layers — the top half of the print is shifted sideways.",
        "causes": [
            "Loose belt on X or Y axis",
            "Stepper motor skipping steps (current too low or speed too high)",
            "Print head colliding with curled-up part",
            "Acceleration/jerk settings too aggressive",
        ],
        "fixes": [
            "Tighten belts — they should twang like a guitar string",
            "Increase stepper motor current (check firmware/driver settings)",
            "Reduce print speed and acceleration",
            "Enable Z-hop during travel to avoid collisions",
            "Check for mechanical obstructions on rails",
        ],
        "materials_most_affected": ["All materials equally"],
        "severity": "structural",
        "related_concepts": ["ghosting_ringing"],
    },
    "warping_lifting": {
        "title": "Warping / Corner Lifting",
        "symptom": "Corners or edges of the print lift off the bed, curling upward.",
        "causes": [
            "Bed temperature too low for the material",
            "No heated enclosure (critical for ABS/ASA)",
            "Poor bed adhesion surface",
            "Large flat geometry with sharp corners",
            "Drafts or ambient temperature changes",
        ],
        "fixes": [
            "Increase bed temperature (PLA: 60°C, PETG: 80°C, ABS: 100-110°C)",
            "Add a brim (5-10mm) for better adhesion area",
            "Use adhesion helpers: glue stick, hairspray, or clean PEI",
            "Use an enclosure for ABS/ASA/Nylon",
            "Add fillets to sharp bottom corners in the design",
            "Reduce part cooling fan for first 3-5 layers",
        ],
        "materials_most_affected": ["ABS (worst)", "ASA", "Nylon", "PETG", "PLA (least)"],
        "severity": "structural",
        "related_concepts": ["warping", "bed_adhesion", "elephants_foot"],
    },
    "poor_bed_adhesion": {
        "title": "Poor Bed Adhesion / First Layer Not Sticking",
        "symptom": "First layer doesn't stick to the bed, filament drags around or balls up.",
        "causes": [
            "Z-offset too high (nozzle too far from bed)",
            "Bed not level or mesh not calibrated",
            "Dirty bed surface (oils from fingers)",
            "Wrong bed temperature",
            "First layer speed too fast",
        ],
        "fixes": [
            "Re-calibrate Z-offset — first layer should lightly squish",
            "Run bed leveling mesh calibration",
            "Clean bed with IPA (isopropyl alcohol)",
            "Apply glue stick or hairspray for stubborn adhesion",
            "Reduce first layer speed to 20-30mm/s",
            "Increase first layer line width to 120-150%",
        ],
        "materials_most_affected": ["PETG", "ABS", "Nylon", "PLA"],
        "severity": "critical",
        "related_concepts": ["bed_adhesion", "first_layer", "bed_types"],
    },
    "under_extrusion": {
        "title": "Under-Extrusion",
        "symptom": "Gaps between lines, thin/weak walls, visible infill gaps, rough surfaces.",
        "causes": [
            "Partially clogged nozzle",
            "Nozzle temperature too low",
            "Flow rate / e-steps not calibrated",
            "Filament grinding at the extruder gear",
            "Tangled or high-friction spool",
            "Wrong filament diameter in slicer (1.75 vs 2.85mm)",
        ],
        "fixes": [
            "Do a cold pull to clear partial clogs (heat to 200°C, cool to 90°C, pull)",
            "Increase nozzle temperature by 5-10°C",
            "Calibrate e-steps: extrude 100mm and measure actual output",
            "Increase flow rate by 2-5% in slicer",
            "Check extruder gear tension — not too tight (grinding) or loose (slipping)",
            "Verify filament diameter setting in slicer matches actual filament",
        ],
        "materials_most_affected": ["All — most common with PETG and flexible filaments"],
        "severity": "structural",
        "related_concepts": ["under_extrusion", "retraction", "nozzle_sizes"],
    },
    "over_extrusion": {
        "title": "Over-Extrusion",
        "symptom": "Blobby surfaces, dimensional inaccuracy (parts too big), rough surface finish.",
        "causes": [
            "Flow rate / e-steps too high",
            "Nozzle temperature too high",
            "Wrong filament diameter setting (slicer thinks filament is thinner than it is)",
        ],
        "fixes": [
            "Calibrate e-steps: extrude 100mm and measure",
            "Reduce flow rate by 2-5%",
            "Reduce nozzle temperature by 5-10°C",
            "Verify filament diameter with calipers (measure in 3 spots, average)",
        ],
        "materials_most_affected": ["All materials"],
        "severity": "cosmetic",
        "related_concepts": ["over_extrusion", "stringing"],
    },
    "elephants_foot": {
        "title": "Elephant's Foot",
        "symptom": "The bottom 1-2 layers of the print bulge outward, wider than the rest.",
        "causes": [
            "First layer squished too much (Z-offset too low)",
            "Bed temperature too high",
            "Weight of upper layers compressing soft first layers",
        ],
        "fixes": [
            "Raise Z-offset slightly (less first-layer squish)",
            "Enable elephant's foot compensation in slicer (0.1-0.3mm)",
            "Lower bed temperature for first layer by 5°C",
            "Add a small chamfer (0.5mm at 45°) to bottom edges in the CAD design",
        ],
        "materials_most_affected": ["PLA", "PETG", "ABS"],
        "severity": "cosmetic",
        "related_concepts": ["elephants_foot", "first_layer", "bed_adhesion"],
    },
    "ghosting_ringing": {
        "title": "Ghosting / Ringing",
        "symptom": "Ripple-like patterns on surfaces after sharp corners or direction changes.",
        "causes": [
            "Print speed or acceleration too high",
            "Loose belts causing vibration",
            "Heavy print head with too much inertia",
            "Frame not rigid enough",
        ],
        "fixes": [
            "Reduce acceleration and jerk settings (try halving acceleration)",
            "Enable input shaper / resonance compensation if firmware supports it",
            "Tighten belts and check for play in linear rails",
            "Reduce print speed for outer walls (40-60mm/s)",
            "Brace the printer frame to reduce vibration",
        ],
        "materials_most_affected": ["All — more visible on smooth materials like PLA and PETG"],
        "severity": "cosmetic",
        "related_concepts": ["ghosting_ringing", "layer_shifting"],
    },
    "clogged_nozzle": {
        "title": "Clogged Nozzle",
        "symptom": "No filament comes out, filament grinds at extruder, or extrusion is extremely thin and inconsistent.",
        "causes": [
            "Heat creep (filament softens too early in the heat break)",
            "Carbonized filament from printing too hot",
            "Foreign material or debris in the nozzle",
            "Switching materials without proper purge",
        ],
        "fixes": [
            "Cold pull: heat to printing temp, cool to 90°C, pull filament out firmly",
            "Use a cleaning needle (acupuncture needle) while nozzle is hot",
            "Atomic method: load nylon at high temp, cool and pull repeatedly",
            "Replace the nozzle (brass nozzles are consumable — replace every few months)",
            "Ensure heat break cooling fan is working (prevents heat creep)",
        ],
        "materials_most_affected": ["All — worse with carbon-fiber or glow-in-the-dark filaments"],
        "severity": "critical",
        "related_concepts": ["under_extrusion", "retraction"],
    },
    "poor_overhangs": {
        "title": "Poor Overhang Quality",
        "symptom": "Drooping, curling, or rough surfaces on overhanging geometry.",
        "causes": [
            "Part cooling fan speed too low",
            "Print speed too fast for overhanging sections",
            "Layer height too thick for the overhang angle",
            "No support material for angles >60°",
        ],
        "fixes": [
            "Increase part cooling fan to 100% for overhangs (except ABS/ASA)",
            "Reduce overhang speed in slicer settings",
            "Use thinner layer heights (0.1-0.15mm) for better overhang resolution",
            "Add supports for angles beyond 45-50°",
            "Redesign with chamfers instead of sharp overhangs",
        ],
        "materials_most_affected": ["PETG (droops easily)", "ABS (no fan possible)", "PLA (best overhang performance)"],
        "severity": "cosmetic",
        "related_concepts": ["overhangs", "cooling", "supports"],
    },
    "delamination": {
        "title": "Layer Delamination / Splitting",
        "symptom": "Layers separate or crack apart, especially on tall prints or between color changes.",
        "causes": [
            "Nozzle temperature too low (poor inter-layer adhesion)",
            "Part cooling fan too high (layers cool before bonding)",
            "Drafts or cold ambient temperature",
            "Moisture in filament",
        ],
        "fixes": [
            "Increase nozzle temperature by 5-10°C",
            "Reduce part cooling fan (especially for ABS/ASA — use 0%)",
            "Use an enclosure to maintain ambient temperature",
            "Dry filament before printing",
            "Reduce layer height for better layer bonding",
        ],
        "materials_most_affected": ["ABS (worst)", "ASA", "Nylon", "PETG"],
        "severity": "structural",
        "related_concepts": ["warping", "cooling"],
    },
    "dimensional_inaccuracy": {
        "title": "Dimensional Inaccuracy",
        "symptom": "Printed parts are larger or smaller than designed — holes too tight, mating parts don't fit.",
        "causes": [
            "E-steps / flow rate not calibrated",
            "Over-extrusion (parts too big) or under-extrusion (parts too small)",
            "Thermal expansion / contraction not accounted for",
            "Elephant's foot on first layers",
            "Belt stretch or backlash",
        ],
        "fixes": [
            "Print a 20mm calibration cube and measure with calipers",
            "Calibrate e-steps and flow rate",
            "Apply horizontal expansion compensation in slicer (-0.1 to -0.2mm typical)",
            "Account for material shrinkage in design (ABS shrinks ~0.7%)",
            "Use `mesh_analyze` to verify the STL dimensions match design intent",
        ],
        "materials_most_affected": ["ABS (high shrinkage)", "Nylon (high shrinkage)", "PLA (most accurate)"],
        "severity": "functional",
        "related_concepts": ["tolerances", "over_extrusion", "under_extrusion", "elephants_foot"],
    },
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def find_concept(query: str) -> list[dict]:
    """Search concepts by keyword match with synonym support."""
    query_lower = query.lower().replace("-", "_").replace(" ", "_")
    results = []

    # Direct match
    if query_lower in CONCEPTS:
        results.append(CONCEPTS[query_lower])
        return results

    # Synonym redirect
    if query_lower in SYNONYMS:
        canonical = SYNONYMS[query_lower]
        if canonical in CONCEPTS:
            results.append(CONCEPTS[canonical])
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
    """Search best practices by keyword match with synonym support."""
    query_lower = query.lower().replace("-", "_").replace(" ", "_")
    results = []

    # Direct match
    if query_lower in BEST_PRACTICES:
        results.append(BEST_PRACTICES[query_lower])
        return results

    # Synonym redirect
    if query_lower in SYNONYMS:
        canonical = SYNONYMS[query_lower]
        if canonical in BEST_PRACTICES:
            results.append(BEST_PRACTICES[canonical])
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


def find_troubleshooting(query: str) -> list[dict]:
    """Search troubleshooting entries by symptom keyword match."""
    query_lower = query.lower().replace("-", "_").replace(" ", "_")
    results = []

    # Direct slug match
    if query_lower in TROUBLESHOOTING:
        results.append(TROUBLESHOOTING[query_lower])
        return results

    # Synonym redirect
    if query_lower in SYNONYMS:
        canonical = SYNONYMS[query_lower]
        if canonical in TROUBLESHOOTING:
            results.append(TROUBLESHOOTING[canonical])
            return results

    # Keyword scoring
    for slug, entry in TROUBLESHOOTING.items():
        score = 0
        if query_lower in slug:
            score += 3
        if query_lower in entry["title"].lower():
            score += 3
        if query_lower in entry["symptom"].lower():
            score += 2
        for cause in entry["causes"]:
            if query_lower in cause.lower():
                score += 1
                break
        for fix in entry["fixes"]:
            if query_lower in fix.lower():
                score += 1
                break
        if score > 0:
            results.append({**entry, "_score": score, "_slug": slug})

    results.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return results[:5]


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

    troubleshooting_titles = [entry["title"] for entry in TROUBLESHOOTING.values()]

    return {
        "concepts": topics_by_category,
        "best_practices": practices_by_category,
        "troubleshooting": troubleshooting_titles,
        "total_concepts": len(CONCEPTS),
        "total_practice_sets": len(BEST_PRACTICES),
        "total_troubleshooting": len(TROUBLESHOOTING),
        "total_synonyms": len(SYNONYMS),
    }
