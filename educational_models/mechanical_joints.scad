/*
 * Mechanical Joint Sampler — Educational Example
 *
 * A reference plate showing five common methods for joining
 * 3D-printed parts, each with labeled dimensions and notes.
 * Print this to learn how each joint type feels and behaves
 * with your specific printer and material.
 *
 * Sections:
 *   1. Heat-set insert boss (M3) — strongest, reusable
 *   2. Self-tapping screw boss (M3) — simple, moderate reuse
 *   3. Cantilever snap fit — tool-free, print orientation matters
 *   4. Press-fit pin joint — no hardware, tight tolerance
 *   5. Dovetail slide joint — alignment + retention
 *
 * Demonstrates:
 *   - Heat-set insert boss sizing and chamfer
 *   - Screw boss pilot holes and reinforcing ribs
 *   - Snap-fit arm geometry and hook design
 *   - Press-fit interference sizing
 *   - Dovetail draft angles and clearances
 *
 * Related tools:
 *   openscad_render(scad_file="mechanical_joints.scad")
 *   openscad_preview(scad_file="mechanical_joints.scad")
 *   cad_explain("heat_set_inserts")
 *   cad_explain("snap_fits")
 *   cad_explain("press_fits")
 *   cad_best_practices("design_for_assembly")
 */

$fn = 48;

// ── Shared parameters ──
base_h       = 3;       // mm — base plate height
section_w    = 35;      // mm — width per section
section_d    = 45;      // mm — depth per section
gap          = 5;       // mm — gap between sections
label_depth  = 0.5;     // mm — engraved text depth
chamfer      = 0.5;     // mm — entry chamfer on holes

// ── Material-specific clearance (tune to your printer) ──
fit_clearance = 0.15;   // mm — per-side clearance for sliding fits

// ── Section X positions ──
function sec_x(i) = i * (section_w + gap);


// ══════════════════════════════════════════════
// BASE PLATE
// ══════════════════════════════════════════════

total_w = 5 * section_w + 4 * gap;

color([0.88, 0.88, 0.85])
translate([total_w/2, section_d/2, base_h/2])
    cube([total_w + 10, section_d + 10, base_h], center=true);


// ══════════════════════════════════════════════
// 1. HEAT-SET INSERT BOSS (M3)
// ══════════════════════════════════════════════

module heat_set_boss() {
    insert_d     = 4.2;   // mm — M3 insert outer diameter
    insert_depth = 5.5;   // mm — embed depth (insert length + 0.5mm)
    boss_od      = 8.0;   // mm — ≥2× insert diameter
    boss_h       = 12;    // mm — total boss height

    translate([section_w/2, section_d/2, base_h]) {
        difference() {
            // Boss cylinder
            cylinder(d=boss_od, h=boss_h);

            // Insert cavity (from top)
            translate([0, 0, boss_h - insert_depth])
                cylinder(d=insert_d, h=insert_depth + 0.1);

            // Entry chamfer
            translate([0, 0, boss_h - 0.01])
                cylinder(d1=insert_d, d2=insert_d + 1.5, h=0.8);
        }

        // Reinforcing ribs (4 radial gussets)
        for (a = [0:3]) {
            rotate([0, 0, a * 90])
            translate([0, 0, 0])
                linear_extrude(boss_h * 0.4)
                polygon([
                    [boss_od/2, -0.8],
                    [boss_od/2 + 3, -0.8],
                    [boss_od/2, 0.8],
                ]);
        }
    }

    // Label
    translate([section_w/2, 3, base_h - label_depth + 0.01])
        linear_extrude(label_depth)
        text("M3 INSERT", size=3, halign="center");
}

color([0.7, 0.8, 0.6])
translate([sec_x(0), 0, 0])
    heat_set_boss();


// ══════════════════════════════════════════════
// 2. SELF-TAPPING SCREW BOSS (M3)
// ══════════════════════════════════════════════

module screw_boss() {
    pilot_d  = 2.5;    // mm — M3 self-tapping pilot hole
    boss_od  = 7.0;    // mm — ≥2× screw OD
    boss_h   = 12;     // mm
    rib_w    = 1.2;
    rib_h    = boss_h * 0.6;

    translate([section_w/2, section_d/2, base_h]) {
        difference() {
            cylinder(d=boss_od, h=boss_h);

            // Pilot hole (full depth)
            translate([0, 0, -0.1])
                cylinder(d=pilot_d, h=boss_h + 0.2);

            // Entry chamfer
            translate([0, 0, boss_h - 0.01])
                cylinder(d1=pilot_d, d2=pilot_d + 1.2, h=chamfer);
        }

        // 4 triangular gussets at base
        for (a = [0:3]) {
            rotate([0, 0, a * 90 + 45])
            translate([boss_od/2 - 0.5, -rib_w/2, 0])
                cube([3, rib_w, rib_h]);
        }
    }

    // Label
    translate([section_w/2, 3, base_h - label_depth + 0.01])
        linear_extrude(label_depth)
        text("M3 SCREW", size=3, halign="center");
}

color([0.6, 0.7, 0.85])
translate([sec_x(1), 0, 0])
    screw_boss();


// ══════════════════════════════════════════════
// 3. CANTILEVER SNAP FIT
// ══════════════════════════════════════════════

module snap_fit_demo() {
    arm_len    = 15;     // mm — cantilever length
    arm_w      = 6;      // mm
    arm_t      = 1.2;    // mm — thickness (keep thin for flex)
    hook       = 1.0;    // mm — hook overhang depth
    hook_t     = 1.5;    // mm — hook thickness
    base_block = 10;     // mm — mounting block height
    pocket_w   = arm_w + fit_clearance * 2;
    pocket_d   = arm_t + fit_clearance * 2;

    translate([0, section_d/2, base_h]) {
        // Mounting block with snap arm
        translate([8, 0, 0]) {
            // Block
            cube([10, 12, base_block], center=true);

            // Cantilever arm (extending upward from block)
            translate([5, -arm_w/2, base_block/2]) {
                cube([arm_t, arm_w, arm_len]);

                // Hook at the end (30° entry angle for easy insertion)
                translate([-hook, 0, arm_len - hook_t])
                    cube([hook + arm_t, arm_w, hook_t]);

                // Entry ramp
                translate([arm_t, 0, arm_len - hook_t])
                    rotate([0, 0, 0])
                    linear_extrude(arm_w)
                    rotate([0, 0, 90])
                    polygon([[0, 0], [hook_t * 1.5, 0], [0, hook + arm_t]]);
            }
        }

        // Mating pocket block (separate piece to test fit)
        translate([24, 0, 0]) {
            difference() {
                cube([10, 12, base_block + arm_len + 2], center=false);

                // Pocket slot for the snap arm
                translate([-0.1, (12 - pocket_w)/2, base_block - 1])
                    cube([pocket_d + 0.1, pocket_w, arm_len + 4]);

                // Hook retention ledge
                translate([-hook - fit_clearance, (12 - pocket_w)/2,
                           base_block + arm_len - hook_t - 1])
                    cube([hook + fit_clearance + 0.1, pocket_w, hook_t + 1]);
            }
        }
    }

    // Label
    translate([section_w/2, 3, base_h - label_depth + 0.01])
        linear_extrude(label_depth)
        text("SNAP FIT", size=3, halign="center");
}

color([0.85, 0.65, 0.5])
translate([sec_x(2), 0, 0])
    snap_fit_demo();


// ══════════════════════════════════════════════
// 4. PRESS-FIT PIN JOINT
// ══════════════════════════════════════════════

module press_fit_demo() {
    pin_d        = 5.0;     // mm — nominal pin diameter
    pin_h        = 10;      // mm
    interference = 0.05;    // mm — per-side interference
    hole_d       = pin_d - interference * 2;
    receiver_od  = pin_d + 4;
    receiver_h   = 12;

    translate([0, section_d/2, base_h]) {
        // Pin (slightly oversized)
        translate([8, 0, 0])
            cylinder(d=pin_d, h=pin_h);

        // Chamfer on pin tip for easy insertion
        translate([8, 0, pin_h])
            cylinder(d1=pin_d, d2=pin_d - 1, h=1);

        // Receiver block with interference hole
        translate([24, 0, 0])
        difference() {
            cylinder(d=receiver_od, h=receiver_h);
            translate([0, 0, -0.1])
                cylinder(d=hole_d, h=receiver_h + 0.2);

            // Entry chamfer
            translate([0, 0, receiver_h - 0.01])
                cylinder(d1=hole_d, d2=hole_d + 1.5, h=1);
        }

        // Dimensional callout pins
        // Show three interference levels for testing
        for (i = [0:2]) {
            intf = [0.00, 0.05, 0.10][i];
            d = pin_d - intf * 2;
            translate([8 + 12 * (i + 1) + 8, -10, 0]) {
                difference() {
                    cylinder(d=receiver_od, h=8);
                    translate([0, 0, -0.1])
                        cylinder(d=d, h=8.2);
                }
                // Label with interference value
                translate([0, receiver_od/2 + 2, 0])
                    linear_extrude(1)
                    text(str(intf), size=2.5, halign="center");
            }
        }
    }

    // Label
    translate([section_w/2, 3, base_h - label_depth + 0.01])
        linear_extrude(label_depth)
        text("PRESS FIT", size=3, halign="center");
}

color([0.75, 0.6, 0.8])
translate([sec_x(3), 0, 0])
    press_fit_demo();


// ══════════════════════════════════════════════
// 5. DOVETAIL SLIDE JOINT
// ══════════════════════════════════════════════

module dovetail_demo() {
    dt_w_top    = 10;      // mm — wide end of dovetail
    dt_w_bot    = 7;       // mm — narrow end
    dt_h        = 5;       // mm — dovetail height
    dt_len      = 30;      // mm — slide length
    rail_h      = 8;       // mm — rail base height

    cl = fit_clearance;

    // Dovetail cross-section profile
    module dt_profile(w_top, w_bot, h) {
        polygon([
            [-w_bot/2, 0],
            [-w_top/2, h],
            [w_top/2, h],
            [w_bot/2, 0],
        ]);
    }

    translate([0, section_d/2 - dt_len/2, base_h]) {
        // Rail base with dovetail channel
        translate([section_w/2 - 8, 0, 0]) {
            difference() {
                cube([16, dt_len, rail_h + dt_h]);

                // Dovetail channel (with clearance)
                translate([8, -0.1, rail_h])
                    rotate([0, 0, 0])
                    linear_extrude(dt_len + 0.2)
                    rotate([0, 0, 0])
                    dt_profile(dt_w_top + cl*2, dt_w_bot + cl*2, dt_h + 0.1);
            }
        }

        // Sliding dovetail key (separate piece)
        translate([section_w/2 + 12, 0, 0]) {
            // Base with dovetail tongue
            cube([12, dt_len * 0.6, rail_h]);
            translate([6, 0, rail_h])
                linear_extrude(dt_len * 0.6)
                dt_profile(dt_w_top, dt_w_bot, dt_h);
        }
    }

    // Label
    translate([section_w/2, 3, base_h - label_depth + 0.01])
        linear_extrude(label_depth)
        text("DOVETAIL", size=3, halign="center");
}

color([0.9, 0.8, 0.6])
translate([sec_x(4), 0, 0])
    dovetail_demo();


// ══════════════════════════════════════════════
// TITLE LABEL
// ══════════════════════════════════════════════

translate([total_w/2, section_d + 5, base_h - label_depth + 0.01])
    color([0.3, 0.3, 0.3])
    linear_extrude(label_depth)
    text("JOINT SAMPLER", size=5, halign="center");
