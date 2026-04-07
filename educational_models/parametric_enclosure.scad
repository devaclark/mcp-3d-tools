/*
 * Parametric Electronics Enclosure — Educational Example
 *
 * A fully parametric box with snap-fit lid, heat-set insert bosses,
 * ventilation slots, and cable routing cutouts.  Change the variables
 * below (or via openscad_list_params / openscad_render) to adapt to
 * any PCB size.
 *
 * Demonstrates:
 *   - Parametric design (all dimensions driven by top-level variables)
 *   - OpenSCAD modules for reusable geometry
 *   - Heat-set insert bosses (M3)
 *   - Snap-fit cantilever clips on the lid
 *   - Ventilation slot patterns
 *   - Cable port cutouts
 *   - Proper wall thickness and draft for FDM printing
 *
 * Related tools:
 *   openscad_render(scad_file="parametric_enclosure.scad",
 *                   variables={"pcb_length": 70, "pcb_width": 50})
 *   openscad_preview(scad_file="parametric_enclosure.scad")
 *   mesh_analyze(stl_file="parametric_enclosure.stl")
 *   cad_explain("heat_set_inserts")
 *   cad_best_practices("enclosure_design")
 */

$fn = 40;

// ── PCB dimensions (measure with calipers!) ──
pcb_length      = 65;     // mm — X dimension
pcb_width       = 45;     // mm — Y dimension
pcb_thickness   = 1.6;    // mm — standard PCB
pcb_clearance   = 0.5;    // mm — gap around PCB for easy insertion

// ── Enclosure parameters ──
wall            = 2.0;    // mm — wall thickness (≥1.6mm for FDM strength)
floor_t         = 1.6;    // mm — floor thickness
lid_t           = 1.6;    // mm — lid thickness
pcb_standoff_h  = 5.0;    // mm — height of PCB standoffs above floor
component_h     = 15;     // mm — tallest component above PCB
lid_clearance   = 0.15;   // mm — fit tolerance between lid and box

// ── Fastening ──
insert_od       = 4.2;    // mm — M3 heat-set insert outer diameter
insert_depth    = 5.0;    // mm — insert embed depth
insert_boss_od  = 8.0;    // mm — boss outer diameter (≥2× insert OD)
screw_hole_d    = 3.2;    // mm — M3 clearance hole in lid

// ── Snap-fit clips (lid retention) ──
clip_width      = 5;      // mm
clip_arm_len    = 8;      // mm — longer = easier flex, less stress
clip_thickness  = 1.2;    // mm
clip_hook       = 0.8;    // mm — overhang depth for the 'click'

// ── Ventilation ──
vent_slot_w     = 1.5;    // mm — slot width
vent_slot_h     = 12;     // mm — slot height
vent_count      = 6;      // number of slots per side
vent_spacing    = 3.5;    // mm — center-to-center

// ── Cable port ──
port_w          = 12;     // mm — USB-C / barrel jack width
port_h          = 7;      // mm — port height
port_y_offset   = 0;      // mm — offset from center on the short wall

// ── Show control ──
show_box = true;
show_lid = true;
explode  = 10;            // mm — vertical separation for exploded view

// ── Derived dimensions ──
inner_l = pcb_length + pcb_clearance * 2;
inner_w = pcb_width  + pcb_clearance * 2;
inner_h = floor_t + pcb_standoff_h + pcb_thickness + component_h;
outer_l = inner_l + wall * 2;
outer_w = inner_w + wall * 2;
outer_h = inner_h + floor_t;

// Corner boss inset from inner wall
boss_inset = insert_boss_od / 2 + 0.5;


// ══════════════════════════════════════════════
// MODULES
// ══════════════════════════════════════════════

module rounded_cube(size, r=2) {
    hull() {
        for (x = [-1, 1], y = [-1, 1]) {
            translate([x * (size[0]/2 - r), y * (size[1]/2 - r), 0])
                cylinder(r=r, h=size[2]);
        }
    }
}

module insert_boss() {
    difference() {
        cylinder(d=insert_boss_od, h=pcb_standoff_h + floor_t);
        translate([0, 0, floor_t])
            cylinder(d=insert_od, h=insert_depth + 0.1);
    }
}

module snap_clip() {
    // Cantilever arm with hook — print with layer lines along Z
    translate([0, 0, 0]) {
        cube([clip_width, clip_thickness, clip_arm_len], center=false);
        translate([0, -clip_hook, clip_arm_len - clip_thickness])
            cube([clip_width, clip_hook + clip_thickness, clip_thickness]);
    }
}

module vent_pattern() {
    total_w = (vent_count - 1) * vent_spacing;
    for (i = [0:vent_count - 1]) {
        translate([i * vent_spacing - total_w/2, 0, 0])
            cube([vent_slot_w, wall + 1, vent_slot_h], center=true);
    }
}


// ══════════════════════════════════════════════
// BOX (bottom half)
// ══════════════════════════════════════════════

module box() {
    difference() {
        // Outer shell
        rounded_cube([outer_l, outer_w, outer_h], r=3);

        // Inner cavity
        translate([0, 0, floor_t])
            rounded_cube([inner_l, inner_w, inner_h + 1], r=1.5);

        // Ventilation slots — left wall
        translate([-(outer_l/2), 0, floor_t + pcb_standoff_h + pcb_thickness + vent_slot_h/2 + 2])
            rotate([0, 0, 0])
            vent_pattern();

        // Ventilation slots — right wall
        translate([outer_l/2, 0, floor_t + pcb_standoff_h + pcb_thickness + vent_slot_h/2 + 2])
            vent_pattern();

        // Cable port cutout — front wall
        translate([0, -(outer_w/2), floor_t + pcb_standoff_h + port_h/2])
            translate([port_y_offset, 0, 0])
            cube([port_w, wall + 1, port_h], center=true);
    }

    // Corner bosses for heat-set inserts
    for (sx = [-1, 1], sy = [-1, 1]) {
        translate([sx * (inner_l/2 - boss_inset),
                   sy * (inner_w/2 - boss_inset), 0])
            insert_boss();
    }
}


// ══════════════════════════════════════════════
// LID (top half)
// ══════════════════════════════════════════════

module lid() {
    lid_inner_l = inner_l - lid_clearance * 2;
    lid_inner_w = inner_w - lid_clearance * 2;
    lip_h       = 3;  // mm — lip that slides into the box

    difference() {
        union() {
            // Main lid plate
            rounded_cube([outer_l, outer_w, lid_t], r=3);

            // Inner lip for alignment
            translate([0, 0, -lip_h])
                rounded_cube([lid_inner_l, lid_inner_w, lip_h], r=1);
        }

        // Screw clearance holes at corners
        for (sx = [-1, 1], sy = [-1, 1]) {
            translate([sx * (inner_l/2 - boss_inset),
                       sy * (inner_w/2 - boss_inset), -lip_h - 0.1])
                cylinder(d=screw_hole_d, h=lid_t + lip_h + 0.2);
        }
    }

    // Snap-fit clips on long edges
    for (sy = [-1, 1]) {
        mirror([0, (sy < 0) ? 1 : 0, 0])
        translate([-clip_width/2, lid_inner_w/2 - clip_thickness, -lip_h])
            snap_clip();
    }
}


// ══════════════════════════════════════════════
// ASSEMBLY
// ══════════════════════════════════════════════

if (show_box) {
    color([0.3, 0.3, 0.35])
        box();
}

if (show_lid) {
    color([0.4, 0.6, 0.8, 0.85])
        translate([0, 0, outer_h + explode])
        lid();
}
