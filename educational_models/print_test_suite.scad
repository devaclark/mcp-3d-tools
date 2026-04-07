/*
 * FDM Print Calibration Test Suite — Educational Example
 *
 * A single-print calibration model that tests the key capabilities
 * of any FDM printer.  Print this when setting up a new printer,
 * switching filaments, or diagnosing quality issues.
 *
 * Sections (left to right):
 *   1. Dimensional accuracy cube (20×20×20mm)
 *   2. Tolerance test holes (1mm–6mm in 0.5mm steps)
 *   3. Overhang angle test (15° to 75° in 15° steps)
 *   4. Bridging span test (10mm, 20mm, 30mm, 40mm gaps)
 *   5. Thin wall test (0.4mm, 0.8mm, 1.2mm, 1.6mm walls)
 *   6. Retraction / stringing test (two columns with gap)
 *
 * Demonstrates:
 *   - Tolerances and clearance calibration
 *   - Overhang behavior without supports
 *   - Bridging capability
 *   - Thin wall printing limits
 *   - Retraction tuning
 *
 * Related tools:
 *   openscad_render(scad_file="print_test_suite.scad")
 *   mesh_analyze(stl_file="print_test_suite.stl")
 *   cad_troubleshoot(symptom="stringing")
 *   cad_explain("overhangs")
 *   cad_best_practices("calibration")
 */

$fn = 60;

// ── Layout ──
section_gap = 8;    // mm between test sections
base_h      = 2;    // mm — common base plate height
label_depth = 0.6;  // mm — engraved text depth

// ── Section positions (X offsets) ──
cube_x      = 0;
holes_x     = 30;
overhang_x  = 62;
bridge_x    = 100;
thin_x      = 148;
string_x    = 175;

total_length = string_x + 30;


// ══════════════════════════════════════════════
// SHARED BASE PLATE
// ══════════════════════════════════════════════

color([0.85, 0.85, 0.85])
translate([total_length/2 - 5, 20, base_h/2])
    cube([total_length + 20, 55, base_h], center=true);


// ══════════════════════════════════════════════
// 1. DIMENSIONAL ACCURACY CUBE (20mm)
// ══════════════════════════════════════════════

module accuracy_cube() {
    size = 20;
    difference() {
        translate([0, 0, base_h])
            cube([size, size, size]);

        // Engraved "20" on top face
        translate([size/2, size/2, base_h + size - label_depth + 0.01])
            linear_extrude(label_depth)
            text("20", size=8, halign="center", valign="center");

        // X marker on front face
        translate([size/2, -0.01, base_h + size/2])
            rotate([-90, 0, 0])
            linear_extrude(label_depth)
            text("X", size=6, halign="center", valign="center");

        // Y marker on side face
        translate([size + 0.01, size/2, base_h + size/2])
            rotate([0, -90, 0])
            rotate([0, 0, 90])
            linear_extrude(label_depth)
            text("Y", size=6, halign="center", valign="center");
    }
}

color([0.6, 0.75, 0.9])
translate([cube_x, 10, 0])
    accuracy_cube();


// ══════════════════════════════════════════════
// 2. TOLERANCE TEST HOLES
// ══════════════════════════════════════════════

module tolerance_holes() {
    block_w = 25;
    block_d = 40;
    block_h = 6;
    hole_sizes = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6];
    cols = 3;
    rows = 3;
    x_sp = 8;
    y_sp = 11;

    difference() {
        translate([0, 0, base_h])
            cube([block_w, block_d, block_h]);

        for (i = [0:len(hole_sizes)-1]) {
            col = i % cols;
            row = floor(i / cols);
            d = hole_sizes[i];
            translate([4 + col * x_sp, 5 + row * y_sp, base_h - 0.1])
                cylinder(d=d, h=block_h + 0.2);

            // Size label below each hole
            translate([4 + col * x_sp, 5 + row * y_sp - d/2 - 2.5,
                       base_h + block_h - label_depth + 0.01])
                linear_extrude(label_depth)
                text(str(d), size=2.5, halign="center", valign="center");
        }
    }
}

color([0.9, 0.75, 0.6])
translate([holes_x, 2, 0])
    tolerance_holes();


// ══════════════════════════════════════════════
// 3. OVERHANG ANGLE TEST
// ══════════════════════════════════════════════

module overhang_test() {
    angles = [15, 30, 45, 60, 75];
    step_w = 6;
    step_d = 20;
    step_h = 18;

    for (i = [0:len(angles)-1]) {
        a = angles[i];
        translate([i * (step_w + 1), 0, base_h]) {
            // Vertical pillar
            cube([step_w, step_d, step_h]);

            // Overhang surface at the specified angle
            translate([0, 0, step_h])
                rotate([0, 0, 0])
                linear_extrude(2)
                polygon([
                    [0, 0],
                    [step_w, 0],
                    [step_w, step_d],
                    [0, step_d],
                ]);

            oh_len = step_h * tan(90 - a);
            clamped_len = min(oh_len, 15);
            translate([step_w, 0, step_h])
                rotate([0, a, 0])
                cube([2, step_d, clamped_len]);

            // Angle label on top
            translate([step_w/2, step_d/2, step_h + 2.01 - label_depth])
                linear_extrude(label_depth)
                text(str(a, "°"), size=3, halign="center", valign="center");
        }
    }
}

color([0.7, 0.9, 0.7])
translate([overhang_x, 10, 0])
    overhang_test();


// ══════════════════════════════════════════════
// 4. BRIDGING SPAN TEST
// ══════════════════════════════════════════════

module bridge_test() {
    spans = [10, 20, 30, 40];
    pillar_w = 4;
    pillar_d = 15;
    pillar_h = 15;
    bridge_t = 2;

    cursor_x = 0;
    for (i = [0:len(spans)-1]) {
        span = spans[i];

        translate([cursor_x + i * (pillar_w + spans[max(0, i-1)] + pillar_w + 2) * (i > 0 ? 0 : 1), 0, base_h]) {
            // Recalculate x position
        }
    }

    // Simpler layout: each bridge section placed sequentially
    x_pos = 0;
    for (i = [0:len(spans)-1]) {
        span = spans[i];
        translate([x_pos, 0, base_h]) {
            // Left pillar
            cube([pillar_w, pillar_d, pillar_h]);

            // Right pillar
            translate([pillar_w + span, 0, 0])
                cube([pillar_w, pillar_d, pillar_h]);

            // Bridge span on top
            translate([pillar_w, 0, pillar_h - bridge_t])
                cube([span, pillar_d, bridge_t]);

            // Span label
            translate([pillar_w + span/2, pillar_d/2,
                       pillar_h + 0.01 - label_depth])
                linear_extrude(label_depth)
                text(str(span), size=3.5, halign="center", valign="center");
        }
        x_pos = x_pos + pillar_w * 2 + span + 3;
    }
}

color([0.9, 0.85, 0.6])
translate([bridge_x, 15, 0])
    bridge_test();


// ══════════════════════════════════════════════
// 5. THIN WALL TEST
// ══════════════════════════════════════════════

module thin_wall_test() {
    widths = [0.4, 0.8, 1.2, 1.6];
    wall_h = 20;
    wall_d = 15;
    gap    = 4;

    for (i = [0:len(widths)-1]) {
        w = widths[i];
        translate([i * (2 + gap), 0, base_h]) {
            cube([w, wall_d, wall_h]);

            // Width label at base
            translate([w/2, wall_d + 1, 0])
                linear_extrude(1)
                text(str(w), size=2.5, halign="center");
        }
    }
}

color([0.8, 0.7, 0.9])
translate([thin_x, 12, 0])
    thin_wall_test();


// ══════════════════════════════════════════════
// 6. RETRACTION / STRINGING TEST
// ══════════════════════════════════════════════

module stringing_test() {
    col_d  = 5;
    col_h  = 25;
    gap    = 15;

    // Two columns separated by a gap — strings appear between them
    translate([0, 0, base_h]) {
        cylinder(d=col_d, h=col_h);
        translate([gap, 0, 0])
            cylinder(d=col_d, h=col_h);

        // Third column offset for triangle pattern
        translate([gap/2, gap * 0.7, 0])
            cylinder(d=col_d, h=col_h);
    }
}

color([0.9, 0.6, 0.6])
translate([string_x, 20, 0])
    stringing_test();


// ══════════════════════════════════════════════
// SECTION LABELS (engraved into base plate)
// ══════════════════════════════════════════════

module base_label(pos, label) {
    translate([pos[0], pos[1], base_h - label_depth + 0.01])
        color([0.3, 0.3, 0.3])
        linear_extrude(label_depth)
        text(label, size=3, halign="center");
}

base_label([cube_x + 10,  1], "CUBE");
base_label([holes_x + 12, -4], "HOLES");
base_label([overhang_x + 17, 3], "OVERHANG");
base_label([bridge_x + 20, 8], "BRIDGE");
base_label([thin_x + 10,  5], "WALLS");
base_label([string_x + 8, 8], "STRING");
