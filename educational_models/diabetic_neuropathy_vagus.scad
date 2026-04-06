/*
 * Diabetic Neuropathy & The Vagus Nerve — Educational 3D Visualization
 *
 * Shows how prolonged high blood glucose damages the peripheral nervous
 * system, with the vagus nerve as the central highway connecting:
 *   Brain → Stomach (gastroparesis) → Gut → Peripheral nerves → Feet
 *
 * Color key:
 *   Green        = Healthy nerve fibers
 *   Orange/Red   = Damaged / inflamed nerve fibers
 *   Blue         = Vagus nerve trunk
 *   Yellow       = Sensory nerve signals
 *   Dark red     = Blood vessels (microvasculature)
 *   Pink/Magenta = Affected organs / symptom zones
 */

$fn = 36;

// === Colors ===
healthy_nerve  = [0.2, 0.75, 0.3];
damaged_nerve  = [0.9, 0.35, 0.1];
vagus_col      = [0.2, 0.45, 0.9];
signal_col     = [1.0, 0.9, 0.2];
vessel_col     = [0.6, 0.1, 0.1];
organ_col      = [0.85, 0.55, 0.6];
bone_col       = [0.92, 0.9, 0.85];
skin_col       = [0.85, 0.72, 0.6, 0.3];
label_col      = [0.95, 0.95, 0.95];
bg_col         = [0.06, 0.06, 0.08];
itch_col       = [0.95, 0.5, 0.7];

// === Layout ===
body_h    = 220;
body_w    = 60;
spine_x   = 0;

// =============================================
// BODY OUTLINE (simplified torso + legs)
// =============================================

// Torso silhouette
color(bg_col, 0.15)
translate([0, body_h/2 - 30, -8])
    cube([body_w + 20, body_h - 60, 2], center=true);

// Head
color(bone_col, 0.3)
translate([0, body_h - 20, 0])
    sphere(r=18);

// Spine (vertebral column reference)
color(bone_col, 0.15)
translate([0, body_h/2 - 10, -2])
    cube([4, body_h - 40, 3], center=true);

// =============================================
// BRAIN (top)
// =============================================
translate([0, body_h - 20, 0]) {
    // Brain mass
    color([0.82, 0.72, 0.72, 0.6]) {
        translate([-5, 3, 0]) sphere(r=11);
        translate([5, 3, 0]) sphere(r=11);
    }
    // Brainstem (vagus origin)
    color([0.7, 0.6, 0.6])
    translate([0, -8, 0])
        cylinder(r=4, h=6, center=true);

    // Label
    translate([22, 5, 3])
        color(label_col) linear_extrude(0.8)
        text("BRAIN", size=4, halign="left", valign="center");
    translate([22, -1, 3])
        color(vagus_col) linear_extrude(0.8)
        text("Vagus origin", size=3, halign="left", valign="center");
}

// =============================================
// VAGUS NERVE (the highway — cranial nerve X)
// =============================================

module NerveFiber(points, col, r=1.2) {
    color(col)
    for (i = [0:len(points)-2]) {
        hull() {
            translate(points[i]) sphere(r=r);
            translate(points[i+1]) sphere(r=r);
        }
    }
}

module DamagedFiber(points, col, r=1.0) {
    color(col)
    for (i = [0:len(points)-2]) {
        hull() {
            translate(points[i]) sphere(r=r);
            translate(points[i+1]) sphere(r=r * (0.5 + 0.5 * sin(i * 60)));
        }
        // Damage markers (irregular swelling)
        if (i % 3 == 0) {
            translate((points[i] + points[i+1]) / 2)
                sphere(r=r*1.8);
        }
    }
}

// Main vagus trunk (L+R, simplified as one)
vagus_path = [
    [0, body_h - 28, 0],     // brainstem
    [-3, body_h - 40, 2],    // neck
    [-5, body_h - 55, 3],    // upper chest
    [-6, body_h - 70, 3],    // heart level
    [-5, body_h - 90, 2],    // diaphragm
    [-4, body_h - 105, 1],   // stomach
    [-3, body_h - 120, 0],   // intestines upper
    [-2, body_h - 135, -1],  // intestines lower
    [0, body_h - 150, -1],   // pelvis
];

NerveFiber(vagus_path, vagus_col, r=1.8);

// Vagus label along trunk
translate([-18, body_h - 70, 5])
    color(vagus_col) linear_extrude(0.8)
    text("VAGUS", size=4.5, halign="center", valign="center");
translate([-18, body_h - 76, 5])
    color(vagus_col) linear_extrude(0.8)
    text("NERVE", size=4.5, halign="center", valign="center");
translate([-18, body_h - 82, 5])
    color([0.6, 0.7, 0.9]) linear_extrude(0.8)
    text("(CN X)", size=3, halign="center", valign="center");

// =============================================
// ORGANS & SYMPTOM ZONES
// =============================================

// --- STOMACH (gastroparesis zone) ---
translate([8, body_h - 105, 2]) {
    // Stomach shape
    color(organ_col, 0.6) {
        scale([1.2, 1, 0.6])
            sphere(r=12);
    }
    // Damage indicators on stomach surface
    color(damaged_nerve) {
        translate([5, 4, 5]) sphere(r=1.5);
        translate([-3, -5, 6]) sphere(r=1.2);
        translate([8, -2, 4]) sphere(r=1.3);
    }

    // Vagus branch to stomach
    NerveFiber([
        [-13, 0, -1],
        [-8, 2, 0],
        [-3, 3, 1],
        [0, 0, 2],
    ], damaged_nerve, r=1.0);

    // Label
    translate([18, 2, 5])
        color(label_col) linear_extrude(0.8)
        text("STOMACH", size=3.5, halign="left");
    translate([18, -4, 5])
        color(damaged_nerve) linear_extrude(0.8)
        text("Gastroparesis", size=3, halign="left");
    translate([18, -9, 5])
        color([0.7, 0.7, 0.7]) linear_extrude(0.8)
        text("Vagus damage slows", size=2.5, halign="left");
    translate([18, -13, 5])
        color([0.7, 0.7, 0.7]) linear_extrude(0.8)
        text("stomach emptying", size=2.5, halign="left");
}

// --- INTESTINES (gut issues) ---
translate([6, body_h - 135, 1]) {
    // Intestine coils
    color(organ_col, 0.4) {
        for (i = [0:4]) {
            translate([sin(i*70)*8, i*4 - 8, 0])
                scale([1.5, 1, 0.5])
                sphere(r=5);
        }
    }
    // Damaged nerve branches in gut wall
    DamagedFiber([
        [-10, -5, 2], [-5, 0, 3], [0, 5, 2],
        [5, 2, 3], [10, -3, 2],
    ], damaged_nerve, r=0.6);

    translate([22, 0, 5])
        color(label_col) linear_extrude(0.8)
        text("GUT", size=3.5, halign="left");
    translate([22, -5, 5])
        color(damaged_nerve) linear_extrude(0.8)
        text("Enteric neuropathy", size=2.8, halign="left");
}

// =============================================
// SPINAL CORD & PERIPHERAL NERVES
// =============================================

// Spinal cord
color(healthy_nerve, 0.4)
translate([0, body_h/2 - 10, 0])
    cylinder(r=2.5, h=body_h - 60, center=true);

// --- PERIPHERAL NERVES TO LEGS ---
// Right leg nerve path (sciatic → tibial → foot)
leg_nerve_r = [
    [0, body_h - 155, 0],
    [5, body_h - 165, 0],
    [10, body_h - 175, -1],
    [12, body_h - 190, -1],
    [14, body_h - 205, -1],
    [15, body_h - 215, -1],
    [15, body_h - 225, -1],
];

// Left leg
leg_nerve_l = [
    [0, body_h - 155, 0],
    [-5, body_h - 165, 0],
    [-10, body_h - 175, -1],
    [-12, body_h - 190, -1],
    [-14, body_h - 205, -1],
    [-15, body_h - 215, -1],
    [-15, body_h - 225, -1],
];

// Upper portions healthy, lower portions damaged
// (stocking-glove pattern — damage starts distally)
NerveFiber([leg_nerve_r[0], leg_nerve_r[1], leg_nerve_r[2],
            leg_nerve_r[3]], healthy_nerve, r=1.0);
DamagedFiber([leg_nerve_r[3], leg_nerve_r[4],
              leg_nerve_r[5], leg_nerve_r[6]], damaged_nerve, r=0.9);

NerveFiber([leg_nerve_l[0], leg_nerve_l[1], leg_nerve_l[2],
            leg_nerve_l[3]], healthy_nerve, r=1.0);
DamagedFiber([leg_nerve_l[3], leg_nerve_l[4],
              leg_nerve_l[5], leg_nerve_l[6]], damaged_nerve, r=0.9);

// --- LEG SILHOUETTES ---
color(bg_col, 0.12) {
    // Right leg
    translate([12, body_h - 195, -6])
        cube([12, 70, 2], center=true);
    // Left leg
    translate([-12, body_h - 195, -6])
        cube([12, 70, 2], center=true);
}

// --- FEET (numbness zone) ---
module Foot(xpos) {
    translate([xpos, body_h - 235, 0]) {
        // Foot shape
        color(bone_col, 0.3)
            scale([1, 1.5, 0.4])
            sphere(r=8);

        // Numbness zone (stocking pattern)
        color(itch_col, 0.35)
            scale([1.1, 1.6, 0.45])
            sphere(r=8);

        // Damaged nerve endings
        DamagedFiber([
            [0, 5, 3], [-3, 0, 2], [0, -4, 2],
            [3, -8, 1], [0, -11, 1],
        ], damaged_nerve, r=0.5);

        // Small nerve ending dots (dying back)
        color(damaged_nerve) {
            for (a = [0:5]) {
                translate([sin(a*60)*5, cos(a*60)*6 - 2, 3])
                    sphere(r=0.7);
            }
        }
    }
}

Foot(15);
Foot(-15);

// Foot labels
translate([30, body_h - 232, 3])
    color(label_col) linear_extrude(0.8)
    text("FEET", size=3.5, halign="left");
translate([30, body_h - 237, 3])
    color(damaged_nerve) linear_extrude(0.8)
    text("Peripheral", size=2.8, halign="left");
translate([30, body_h - 241, 3])
    color(damaged_nerve) linear_extrude(0.8)
    text("neuropathy", size=2.8, halign="left");
translate([30, body_h - 246, 3])
    color([0.7, 0.7, 0.7]) linear_extrude(0.8)
    text("Numbness, tingling", size=2.5, halign="left");
translate([30, body_h - 250, 3])
    color([0.7, 0.7, 0.7]) linear_extrude(0.8)
    text("\"asleep\" feeling", size=2.5, halign="left");

// =============================================
// SKIN / ITCH ZONES (small-fiber neuropathy)
// =============================================

// Itch indicators scattered across torso
module ItchMarker(pos) {
    translate(pos) {
        color(itch_col, 0.6) {
            // Star/burst pattern
            for (a = [0:5]) {
                rotate([0, 0, a * 60])
                    cube([4, 0.5, 0.5], center=true);
            }
        }
    }
}

// Scattered across the body
ItchMarker([20, body_h - 60, 5]);
ItchMarker([18, body_h - 80, 5]);
ItchMarker([-15, body_h - 70, 5]);
ItchMarker([22, body_h - 95, 5]);
ItchMarker([-18, body_h - 90, 5]);
ItchMarker([16, body_h - 150, 4]);
ItchMarker([-14, body_h - 160, 4]);
ItchMarker([20, body_h - 170, 3]);
ItchMarker([-18, body_h - 180, 3]);

translate([-35, body_h - 70, 5])
    color(itch_col) linear_extrude(0.8)
    text("ITCH", size=3.5, halign="center");
translate([-35, body_h - 75, 5])
    color([0.7, 0.7, 0.7]) linear_extrude(0.8)
    text("Small-fiber", size=2.5, halign="center");
translate([-35, body_h - 79, 5])
    color([0.7, 0.7, 0.7]) linear_extrude(0.8)
    text("neuropathy", size=2.5, halign="center");

// =============================================
// BLOOD VESSEL DAMAGE (microvasculature)
// =============================================

// Small damaged vessels near nerves
module DamagedVessel(p1, p2) {
    color(vessel_col, 0.5) {
        hull() {
            translate(p1) sphere(r=0.5);
            translate(p2) sphere(r=0.5);
        }
    }
}

// Around stomach
DamagedVessel([12, body_h-100, 8], [18, body_h-98, 7]);
DamagedVessel([14, body_h-108, 7], [20, body_h-112, 6]);

// Along leg nerves
DamagedVessel([16, body_h-210, 1], [19, body_h-208, 2]);
DamagedVessel([13, body_h-218, 0], [16, body_h-216, 1]);
DamagedVessel([-16, body_h-212, 1], [-19, body_h-210, 2]);

// =============================================
// GLUCOSE DAMAGE MECHANISM (annotation)
// =============================================

translate([-42, body_h - 110, 5]) {
    color([0.9, 0.6, 0.1]) linear_extrude(0.8)
        text("HIGH GLUCOSE", size=3, halign="center");
    translate([0, -5, 0])
        color([0.7, 0.7, 0.7]) linear_extrude(0.8)
        text("damages tiny", size=2.5, halign="center");
    translate([0, -9, 0])
        color([0.7, 0.7, 0.7]) linear_extrude(0.8)
        text("blood vessels", size=2.5, halign="center");
    translate([0, -13, 0])
        color([0.7, 0.7, 0.7]) linear_extrude(0.8)
        text("that feed nerves", size=2.5, halign="center");
    // Arrow
    translate([0, -18, 0])
        color([0.9, 0.6, 0.1])
        linear_extrude(1)
        polygon([[-2,-3], [0,0], [2,-3]]);
    translate([0, -23, 0])
        color(damaged_nerve) linear_extrude(0.8)
        text("→ nerve starves", size=2.5, halign="center");
    translate([0, -27, 0])
        color(damaged_nerve) linear_extrude(0.8)
        text("→ signals fail", size=2.5, halign="center");
}

// =============================================
// LEGEND
// =============================================

translate([-48, body_h - 170, 5]) {
    color(label_col) linear_extrude(0.8)
        text("LEGEND", size=3.5, halign="center");

    translate([0, -7, 0]) {
        color(healthy_nerve) cube([6, 2, 2], center=true);
        translate([10, 0, 0]) color(label_col) linear_extrude(0.8)
            text("Healthy nerve", size=2.5, valign="center");
    }
    translate([0, -13, 0]) {
        color(damaged_nerve) cube([6, 2, 2], center=true);
        translate([10, 0, 0]) color(label_col) linear_extrude(0.8)
            text("Damaged nerve", size=2.5, valign="center");
    }
    translate([0, -19, 0]) {
        color(vagus_col) cube([6, 2, 2], center=true);
        translate([10, 0, 0]) color(label_col) linear_extrude(0.8)
            text("Vagus nerve", size=2.5, valign="center");
    }
    translate([0, -25, 0]) {
        color(itch_col) cube([6, 2, 2], center=true);
        translate([10, 0, 0]) color(label_col) linear_extrude(0.8)
            text("Itch / numbness", size=2.5, valign="center");
    }
    translate([0, -31, 0]) {
        color(vessel_col) cube([6, 2, 2], center=true);
        translate([10, 0, 0]) color(label_col) linear_extrude(0.8)
            text("Damaged vessels", size=2.5, valign="center");
    }
}
