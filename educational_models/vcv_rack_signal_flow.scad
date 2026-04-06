/*
 * VCV Rack Signal Flow — Educational 3D Visualization
 *
 * Illustrates the electrical signal path through a classic
 * subtractive synthesis patch:
 *
 *   MIDI/SEQ → [CV+Gate] → VCO → VCF → VCA → OUTPUT
 *                               ↑       ↑
 *                              LFO    ENV
 *
 * Color key (in preview):
 *   Blue   = Control Voltage (CV) — slow, continuous signals
 *   Red    = Audio signal — fast oscillating waveform
 *   Green  = Gate/Trigger — on/off binary signals
 *   Yellow = Modulation — LFO and envelope CV
 */

$fn = 48;

// === Layout parameters ===
module_w      = 20;     // HP-like width
module_h      = 60;     // 3U panel height
module_d      = 8;      // depth
spacing       = 35;     // center-to-center
cable_r       = 1.2;    // patch cable radius
jack_r        = 2.5;    // jack hole radius
jack_depth    = 2;

// === Colors ===
panel_color   = [0.15, 0.15, 0.18];
cv_color      = [0.2, 0.4, 0.9];     // blue — CV
audio_color   = [0.9, 0.2, 0.15];    // red — audio
gate_color    = [0.15, 0.8, 0.3];    // green — gate/trigger
mod_color     = [0.95, 0.75, 0.1];   // yellow — modulation
label_color   = [0.9, 0.9, 0.9];

// === Modules (positioned left to right) ===
// x positions for each module
seq_x   = 0;
vco_x   = spacing;
vcf_x   = spacing * 2;
vca_x   = spacing * 3;
out_x   = spacing * 4;
lfo_x   = spacing * 1.5;  // between VCO and VCF, offset down
env_x   = spacing * 2.5;  // between VCF and VCA, offset down

mod_y_offset = -50;  // modulation row below main signal path

// === Module panel ===
module Module(label, w=module_w, h=module_h, d=module_d,
              n_jacks_top=1, n_jacks_bot=1) {
    color(panel_color)
        cube([w, h, d], center=true);

    // top jacks (inputs)
    for (i = [0:n_jacks_top-1]) {
        jx = (i - (n_jacks_top-1)/2) * 8;
        translate([jx, h/2 - 10, d/2 - jack_depth/2])
            color([0.3, 0.3, 0.3])
            cylinder(r=jack_r, h=jack_depth+0.1, center=true);
    }
    // bottom jacks (outputs)
    for (i = [0:n_jacks_bot-1]) {
        jx = (i - (n_jacks_bot-1)/2) * 8;
        translate([jx, -(h/2 - 10), d/2 - jack_depth/2])
            color([0.3, 0.3, 0.3])
            cylinder(r=jack_r, h=jack_depth+0.1, center=true);
    }
}

// === Patch cable (catenary-like arc between two points) ===
module Cable(p1, p2, col, sag=12) {
    color(col)
    hull() {
        translate(p1) sphere(r=cable_r);
        translate([(p1[0]+p2[0])/2, (p1[1]+p2[1])/2, 
                    max(p1[2], p2[2]) + sag])
            sphere(r=cable_r);
    }
    color(col)
    hull() {
        translate([(p1[0]+p2[0])/2, (p1[1]+p2[1])/2,
                    max(p1[2], p2[2]) + sag])
            sphere(r=cable_r);
        translate(p2) sphere(r=cable_r);
    }
}

// === Arrow showing signal direction ===
module FlowArrow(p1, p2, col) {
    mid = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2, p1[2]];
    dx = p2[0] - p1[0];
    dy = p2[1] - p1[1];
    ang = atan2(dy, dx);

    translate(mid)
    rotate([0, 0, ang])
    color(col, 0.7) {
        // arrow shaft
        translate([0, 0, 0])
            cube([8, 1.5, 1.5], center=true);
        // arrow head
        translate([5.5, 0, 0])
            rotate([0, 0, 0])
            linear_extrude(1.5, center=true)
            polygon([[-2, -2.5], [2, 0], [-2, 2.5]]);
    }
}

// === Signal waveform indicators ===
module Waveform(type="sine", col=audio_color) {
    color(col)
    if (type == "sine") {
        // sine wave approximation
        for (i = [0:11]) {
            x = i * 1.2;
            y = 3 * sin(i * 30);
            translate([x - 6, y, 0])
                sphere(r=0.6);
        }
    } else if (type == "square") {
        // square wave (gate)
        linear_extrude(0.8, center=true)
        polygon([
            [-6, -2], [-6, 2], [-3, 2], [-3, -2],
            [0, -2], [0, 2], [3, 2], [3, -2], [6, -2]
        ]);
    } else if (type == "triangle") {
        // LFO triangle
        linear_extrude(0.8, center=true)
        polygon([
            [-6, 0], [-3, 3], [0, 0], [3, 3], [6, 0]
        ]);
    } else if (type == "adsr") {
        // envelope shape
        linear_extrude(0.8, center=true)
        polygon([
            [-6, 0], [-4, 4], [-2, 2.5], [2, 2.5], [5, 0]
        ]);
    }
}

// =============================================
// BUILD THE PATCH
// =============================================

// --- Main signal path modules ---
translate([seq_x, 0, 0]) {
    Module("SEQ", n_jacks_top=0, n_jacks_bot=2);
    translate([0, module_h/2 + 5, 0])
        color(label_color) linear_extrude(1)
        text("SEQ", size=5, halign="center", valign="center");
    // gate output indicator
    translate([0, -(module_h/2 - 10), module_d/2 + 2])
        Waveform("square", gate_color);
}

translate([vco_x, 0, 0]) {
    Module("VCO", n_jacks_top=2, n_jacks_bot=1);
    translate([0, module_h/2 + 5, 0])
        color(label_color) linear_extrude(1)
        text("VCO", size=5, halign="center", valign="center");
    // audio output indicator
    translate([0, -(module_h/2 - 10), module_d/2 + 2])
        Waveform("sine", audio_color);
}

translate([vcf_x, 0, 0]) {
    Module("VCF", n_jacks_top=2, n_jacks_bot=1);
    translate([0, module_h/2 + 5, 0])
        color(label_color) linear_extrude(1)
        text("VCF", size=5, halign="center", valign="center");
    translate([0, -(module_h/2 - 10), module_d/2 + 2])
        Waveform("sine", audio_color);
}

translate([vca_x, 0, 0]) {
    Module("VCA", n_jacks_top=2, n_jacks_bot=1);
    translate([0, module_h/2 + 5, 0])
        color(label_color) linear_extrude(1)
        text("VCA", size=5, halign="center", valign="center");
    translate([0, -(module_h/2 - 10), module_d/2 + 2])
        Waveform("sine", audio_color);
}

translate([out_x, 0, 0]) {
    Module("OUT", n_jacks_top=1, n_jacks_bot=0);
    translate([0, module_h/2 + 5, 0])
        color(label_color) linear_extrude(1)
        text("OUT", size=5, halign="center", valign="center");
}

// --- Modulation modules (below main path) ---
translate([lfo_x, mod_y_offset, 0]) {
    Module("LFO", n_jacks_top=0, n_jacks_bot=1);
    translate([0, module_h/2 + 5, 0])
        color(label_color) linear_extrude(1)
        text("LFO", size=5, halign="center", valign="center");
    translate([0, -(module_h/2 - 10), module_d/2 + 2])
        Waveform("triangle", mod_color);
}

translate([env_x, mod_y_offset, 0]) {
    Module("ENV", n_jacks_top=1, n_jacks_bot=1);
    translate([0, module_h/2 + 5, 0])
        color(label_color) linear_extrude(1)
        text("ENV", size=5, halign="center", valign="center");
    translate([0, -(module_h/2 - 10), module_d/2 + 2])
        Waveform("adsr", mod_color);
}

// --- Patch cables ---
// SEQ CV out → VCO V/Oct in (blue = pitch CV)
Cable(
    [seq_x, -(module_h/2 - 10), module_d/2],
    [vco_x - 4, module_h/2 - 10, module_d/2],
    cv_color, sag=15
);

// SEQ Gate out → ENV Gate in (green = gate)
Cable(
    [seq_x + 4, -(module_h/2 - 10), module_d/2],
    [env_x, mod_y_offset + module_h/2 - 10, module_d/2],
    gate_color, sag=20
);

// VCO audio out → VCF audio in (red = audio)
Cable(
    [vco_x, -(module_h/2 - 10), module_d/2],
    [vcf_x - 4, module_h/2 - 10, module_d/2],
    audio_color, sag=14
);

// VCF audio out → VCA audio in (red = audio)
Cable(
    [vcf_x, -(module_h/2 - 10), module_d/2],
    [vca_x - 4, module_h/2 - 10, module_d/2],
    audio_color, sag=14
);

// VCA audio out → OUT in (red = audio)
Cable(
    [vca_x, -(module_h/2 - 10), module_d/2],
    [out_x, module_h/2 - 10, module_d/2],
    audio_color, sag=14
);

// LFO mod out → VCF cutoff CV in (yellow = modulation)
Cable(
    [lfo_x, mod_y_offset - (module_h/2 - 10), module_d/2],
    [vcf_x + 4, module_h/2 - 10, module_d/2],
    mod_color, sag=18
);

// ENV out → VCA CV in (yellow = modulation)
Cable(
    [env_x, mod_y_offset - (module_h/2 - 10), module_d/2],
    [vca_x + 4, module_h/2 - 10, module_d/2],
    mod_color, sag=18
);

// --- Flow arrows along main path ---
FlowArrow([seq_x + 10, 5, -module_d/2 - 2],
          [vco_x - 10, 5, -module_d/2 - 2], cv_color);
FlowArrow([vco_x + 10, 5, -module_d/2 - 2],
          [vcf_x - 10, 5, -module_d/2 - 2], audio_color);
FlowArrow([vcf_x + 10, 5, -module_d/2 - 2],
          [vca_x - 10, 5, -module_d/2 - 2], audio_color);
FlowArrow([vca_x + 10, 5, -module_d/2 - 2],
          [out_x - 10, 5, -module_d/2 - 2], audio_color);

// --- Modulation arrows ---
FlowArrow([lfo_x, mod_y_offset + module_h/2 + 3, -module_d/2 - 2],
          [vcf_x, -module_h/2 - 3, -module_d/2 - 2], mod_color);
FlowArrow([env_x, mod_y_offset + module_h/2 + 3, -module_d/2 - 2],
          [vca_x, -module_h/2 - 3, -module_d/2 - 2], mod_color);

// === Base plate ===
translate([out_x/2, -15, -module_d/2 - 1.5])
    color([0.1, 0.1, 0.12])
    cube([out_x + module_w + 20, module_h + abs(mod_y_offset) + 40, 1], center=true);

// === Legend ===
legend_x = out_x + module_w;
legend_y = module_h/2;
translate([legend_x, legend_y, 0]) {
    color(cv_color) cube([8, 2, 2], center=true);
    translate([14, 0, 0])
        color(label_color) linear_extrude(1)
        text("CV", size=4, valign="center");
}
translate([legend_x, legend_y - 8, 0]) {
    color(audio_color) cube([8, 2, 2], center=true);
    translate([14, 0, 0])
        color(label_color) linear_extrude(1)
        text("Audio", size=4, valign="center");
}
translate([legend_x, legend_y - 16, 0]) {
    color(gate_color) cube([8, 2, 2], center=true);
    translate([14, 0, 0])
        color(label_color) linear_extrude(1)
        text("Gate", size=4, valign="center");
}
translate([legend_x, legend_y - 24, 0]) {
    color(mod_color) cube([8, 2, 2], center=true);
    translate([14, 0, 0])
        color(label_color) linear_extrude(1)
        text("Mod", size=4, valign="center");
}
