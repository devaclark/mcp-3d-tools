/*
 * VCV Rack Voice Patch — Educational 3D Visualization
 *
 * Classic subtractive synthesis voice architecture:
 *
 *   MIDI-CV → VCO → VCF → VCA → OUT/MIXER
 *              ↑      ↑     ↑
 *             LFO  Flt.ENV  Amp.ENV
 *                     ↑      ↑
 *                   [Gate from MIDI-CV]
 *
 * Color key:
 *   Blue   = CV (pitch, 1V/Oct)
 *   Red    = Audio signal path
 *   Green  = Gate / Trigger
 *   Yellow = Modulation (envelopes, LFO)
 *   Cyan   = LFO modulation
 */

$fn = 48;

// === Layout ===
mod_w     = 22;
mod_h     = 70;
mod_d     = 9;
spacing   = 38;
cable_r   = 1.3;
jack_r    = 2.8;
knob_r    = 3.2;
knob_h    = 3;

// === Colors ===
panel_col    = [0.12, 0.12, 0.15];
panel_top    = [0.18, 0.18, 0.22];
cv_col       = [0.2, 0.4, 0.95];
audio_col    = [0.95, 0.18, 0.12];
gate_col     = [0.1, 0.82, 0.3];
env_col      = [0.95, 0.75, 0.1];
lfo_col      = [0.1, 0.85, 0.9];
label_col    = [0.92, 0.92, 0.92];
jack_col     = [0.25, 0.25, 0.28];
knob_col     = [0.55, 0.55, 0.6];
knob_cap     = [0.85, 0.85, 0.9];

// === Module positions (x) ===
midi_x   = 0;
vco_x    = spacing;
vcf_x    = spacing * 2;
vca_x    = spacing * 3;
mix_x    = spacing * 4;

// Modulation row (below main)
lfo_x    = spacing * 0.7;
fenv_x   = spacing * 1.8;
aenv_x   = spacing * 2.8;

mod_y    = -60;

// === Reusable modules ===

module Jack(col=jack_col) {
    color(col)
    difference() {
        cylinder(r=jack_r, h=3, center=true);
        cylinder(r=jack_r-1, h=4, center=true);
    }
}

module Knob() {
    color(knob_col)
        cylinder(r=knob_r, h=knob_h, center=true);
    translate([0, 0, knob_h/2])
        color(knob_cap)
        cylinder(r=knob_r-0.8, h=1, center=true);
    // pointer line
    translate([0, knob_r*0.5, knob_h/2+0.5])
        color([0.2,0.2,0.2])
        cube([0.6, knob_r*0.8, 0.3], center=true);
}

module Panel(label, w=mod_w, h=mod_h, d=mod_d,
             n_knobs=2, n_jacks_in=1, n_jacks_out=1,
             accent_col=[0.3,0.3,0.35]) {
    // Main panel body
    color(panel_col)
        cube([w, h, d], center=true);

    // Accent strip at top
    translate([0, h/2 - 3, d/2])
        color(accent_col)
        cube([w, 6, 0.5], center=true);

    // Label
    translate([0, h/2 - 3, d/2 + 0.5])
        color(label_col) linear_extrude(0.8)
        text(label, size=5, halign="center", valign="center",
             font="Liberation Sans:style=Bold");

    // Knobs (mid-section)
    for (i = [0:n_knobs-1]) {
        ky = h/2 - 16 - i * 12;
        translate([0, ky, d/2 + knob_h/2])
            Knob();
    }

    // Input jacks (top area, below knobs)
    jack_y_in = -(h/2 - 18);
    for (i = [0:n_jacks_in-1]) {
        jx = (i - (n_jacks_in-1)/2) * 10;
        translate([jx, jack_y_in + 8, d/2])
            Jack();
    }

    // Output jacks (bottom)
    jack_y_out = -(h/2 - 8);
    for (i = [0:n_jacks_out-1]) {
        jx = (i - (n_jacks_out-1)/2) * 10;
        translate([jx, jack_y_out, d/2])
            Jack();
    }
}

// === Patch cable (catenary arc) ===
module Cable(p1, p2, col, sag=15) {
    mid = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2,
           max(p1[2], p2[2]) + sag];
    color(col) {
        hull() {
            translate(p1) sphere(r=cable_r);
            translate(mid) sphere(r=cable_r);
        }
        hull() {
            translate(mid) sphere(r=cable_r);
            translate(p2) sphere(r=cable_r);
        }
    }
    // Jack plugs at each end
    color(col)  {
        translate(p1) sphere(r=cable_r*1.6);
        translate(p2) sphere(r=cable_r*1.6);
    }
}

// === Waveform indicators ===
module WaveLabel(type="saw", col=audio_col) {
    color(col)
    if (type == "saw") {
        linear_extrude(0.8, center=true)
        polygon([[-5,-2.5], [-5,2.5], [-1,-2.5],
                 [-1,2.5], [3,-2.5], [3,2.5], [5,-2.5]]);
    } else if (type == "sine") {
        for (i = [0:9]) {
            x = i * 1.1 - 5;
            y = 2.5 * sin(i * 36);
            translate([x, y, 0]) sphere(r=0.5);
        }
    } else if (type == "tri") {
        linear_extrude(0.8, center=true)
        polygon([[-5,0], [-2.5,2.5], [0,0], [2.5,2.5], [5,0]]);
    } else if (type == "adsr") {
        linear_extrude(0.8, center=true)
        polygon([[-5,0], [-3,3.5], [-1,2], [2,2], [5,0]]);
    } else if (type == "square") {
        linear_extrude(0.8, center=true)
        polygon([[-5,-2], [-5,2], [-2,2], [-2,-2],
                 [1,-2], [1,2], [4,2], [4,-2]]);
    }
}

// =============================================
// MAIN SIGNAL PATH (top row)
// =============================================

// --- MIDI-CV ---
translate([midi_x, 0, 0]) {
    Panel("MIDI", n_knobs=1, n_jacks_in=0, n_jacks_out=2,
          accent_col=[0.15, 0.3, 0.6]);
    // V/Oct and Gate output labels
    translate([-4, -(mod_h/2 - 7), mod_d/2 + 2])
        color(cv_col) linear_extrude(0.5)
        text("V/O", size=2.5, halign="center", valign="center");
    translate([4, -(mod_h/2 - 7), mod_d/2 + 2])
        color(gate_col) linear_extrude(0.5)
        text("GT", size=2.5, halign="center", valign="center");
}

// --- VCO ---
translate([vco_x, 0, 0]) {
    Panel("VCO", n_knobs=3, n_jacks_in=2, n_jacks_out=1,
          accent_col=[0.5, 0.2, 0.2]);
    translate([0, -(mod_h/2 - 3), mod_d/2 + 2])
        WaveLabel("saw", audio_col);
}

// --- VCF ---
translate([vcf_x, 0, 0]) {
    Panel("VCF", n_knobs=3, n_jacks_in=2, n_jacks_out=1,
          accent_col=[0.5, 0.35, 0.1]);
    translate([0, -(mod_h/2 - 3), mod_d/2 + 2])
        WaveLabel("sine", audio_col);
}

// --- VCA ---
translate([vca_x, 0, 0]) {
    Panel("VCA", n_knobs=2, n_jacks_in=2, n_jacks_out=1,
          accent_col=[0.2, 0.45, 0.2]);
}

// --- MIXER/OUT ---
translate([mix_x, 0, 0]) {
    Panel("MIX", n_knobs=2, n_jacks_in=1, n_jacks_out=1,
          accent_col=[0.35, 0.2, 0.5]);
    // Speaker icon
    translate([0, -(mod_h/2 - 3), mod_d/2 + 2])
        color(label_col) linear_extrude(0.8)
        text("♪", size=5, halign="center", valign="center");
}

// =============================================
// MODULATION ROW (bottom)
// =============================================

// --- LFO ---
translate([lfo_x, mod_y, 0]) {
    Panel("LFO", n_knobs=2, n_jacks_in=0, n_jacks_out=1,
          accent_col=[0.1, 0.5, 0.55]);
    translate([0, -(mod_h/2 - 3), mod_d/2 + 2])
        WaveLabel("tri", lfo_col);
}

// --- Filter Envelope ---
translate([fenv_x, mod_y, 0]) {
    Panel("F.ENV", n_knobs=4, n_jacks_in=1, n_jacks_out=1,
          accent_col=[0.6, 0.45, 0.1]);
    translate([0, -(mod_h/2 - 3), mod_d/2 + 2])
        WaveLabel("adsr", env_col);
}

// --- Amp Envelope ---
translate([aenv_x, mod_y, 0]) {
    Panel("A.ENV", n_knobs=4, n_jacks_in=1, n_jacks_out=1,
          accent_col=[0.15, 0.45, 0.15]);
    translate([0, -(mod_h/2 - 3), mod_d/2 + 2])
        WaveLabel("adsr", env_col);
}

// =============================================
// PATCH CABLES
// =============================================

out_z = mod_d/2;
in_z  = mod_d/2;

// --- MIDI-CV V/Oct → VCO pitch in (blue = CV) ---
Cable(
    [midi_x - 4, -(mod_h/2 - 8), out_z],
    [vco_x - 4, -(mod_h/2 - 18) + 8, in_z],
    cv_col, sag=16
);

// --- MIDI-CV Gate → Filter Env gate in (green) ---
Cable(
    [midi_x + 4, -(mod_h/2 - 8), out_z],
    [fenv_x, mod_y + (mod_h/2 - 18) + 8, in_z],
    gate_col, sag=22
);

// --- MIDI-CV Gate → Amp Env gate in (green) ---
Cable(
    [midi_x + 6, -(mod_h/2 - 8), out_z + 1],
    [aenv_x, mod_y + (mod_h/2 - 18) + 8, in_z],
    gate_col, sag=28
);

// --- VCO audio out → VCF audio in (red) ---
Cable(
    [vco_x, -(mod_h/2 - 8), out_z],
    [vcf_x - 4, -(mod_h/2 - 18) + 8, in_z],
    audio_col, sag=14
);

// --- VCF audio out → VCA audio in (red) ---
Cable(
    [vcf_x, -(mod_h/2 - 8), out_z],
    [vca_x - 4, -(mod_h/2 - 18) + 8, in_z],
    audio_col, sag=14
);

// --- VCA audio out → Mixer in (red) ---
Cable(
    [vca_x, -(mod_h/2 - 8), out_z],
    [mix_x, -(mod_h/2 - 18) + 8, in_z],
    audio_col, sag=14
);

// --- LFO → VCO FM/mod in (cyan) ---
Cable(
    [lfo_x, mod_y - (mod_h/2 - 8), out_z],
    [vco_x + 4, -(mod_h/2 - 18) + 8, in_z],
    lfo_col, sag=20
);

// --- Filter Env → VCF cutoff CV in (yellow) ---
Cable(
    [fenv_x, mod_y - (mod_h/2 - 8), out_z],
    [vcf_x + 4, -(mod_h/2 - 18) + 8, in_z],
    env_col, sag=18
);

// --- Amp Env → VCA CV in (yellow) ---
Cable(
    [aenv_x, mod_y - (mod_h/2 - 8), out_z],
    [vca_x + 4, -(mod_h/2 - 18) + 8, in_z],
    env_col, sag=18
);

// =============================================
// FLOW ARROWS along audio path
// =============================================
module Arrow(pos, col) {
    translate(pos)
    color(col, 0.8)
    rotate([0,0,0])
    linear_extrude(2, center=true)
    polygon([[-2,-2.5], [3,0], [-2,2.5]]);
}

Arrow([midi_x + spacing/2, 8, -mod_d/2 - 2], cv_col);
Arrow([vco_x + spacing/2, 8, -mod_d/2 - 2], audio_col);
Arrow([vcf_x + spacing/2, 8, -mod_d/2 - 2], audio_col);
Arrow([vca_x + spacing/2, 8, -mod_d/2 - 2], audio_col);

// Modulation arrows (upward)
module UpArrow(pos, col) {
    translate(pos)
    color(col, 0.7)
    rotate([0,0,90])
    linear_extrude(2, center=true)
    polygon([[-2,-2], [2.5,0], [-2,2]]);
}

UpArrow([lfo_x + 5, mod_y/2, -mod_d/2 - 2], lfo_col);
UpArrow([fenv_x, mod_y/2, -mod_d/2 - 2], env_col);
UpArrow([aenv_x, mod_y/2, -mod_d/2 - 2], env_col);

// =============================================
// BASE PLATE + RAILS
// =============================================
translate([mix_x/2, -15, -mod_d/2 - 1.5])
    color([0.08, 0.08, 0.1])
    cube([mix_x + mod_w + 30, mod_h + abs(mod_y) + 50, 1], center=true);

// Rail strips (like Eurorack rails)
for (yy = [mod_h/2 + 2, -(mod_h/2 + 2)])
    translate([mix_x/2, yy, -mod_d/2 - 0.5])
        color([0.3, 0.3, 0.32])
        cube([mix_x + mod_w + 30, 3, 1.5], center=true);

for (yy = [mod_y + mod_h/2 + 2, mod_y - (mod_h/2 + 2)])
    translate([(lfo_x + aenv_x)/2, yy, -mod_d/2 - 0.5])
        color([0.3, 0.3, 0.32])
        cube([aenv_x - lfo_x + mod_w + 20, 3, 1.5], center=true);

// =============================================
// LEGEND
// =============================================
leg_x = mix_x + mod_w + 5;
leg_y = mod_h/2 - 2;
leg_sp = 8;

module LegendItem(pos, col, label) {
    translate(pos) {
        color(col) cube([7, 2.5, 2.5], center=true);
        translate([12, 0, 0])
            color(label_col) linear_extrude(0.8)
            text(label, size=3.5, valign="center");
    }
}

LegendItem([leg_x, leg_y, 0], cv_col, "CV");
LegendItem([leg_x, leg_y - leg_sp, 0], audio_col, "Audio");
LegendItem([leg_x, leg_y - leg_sp*2, 0], gate_col, "Gate");
LegendItem([leg_x, leg_y - leg_sp*3, 0], env_col, "Env");
LegendItem([leg_x, leg_y - leg_sp*4, 0], lfo_col, "LFO");
