// Universe Scale Model - Our Solar System
// Planet radii are exaggerated vs orbital distances so you can see them

// === THE SUN ===
color("orange")
  sphere(r=25, $fn=64);

// Sun glow
color([1, 0.85, 0.2], 0.3)
  sphere(r=28, $fn=48);

// === INNER PLANETS ===

// Mercury - tiny, gray, closest
color([0.6, 0.6, 0.6])
translate([38, 0, 0])
  sphere(r=1.5, $fn=24);

// Venus - similar size to Earth, yellowish
color([0.9, 0.8, 0.5])
translate([52, 15, 0])
  sphere(r=3, $fn=32);

// Earth - our pale blue dot!
color([0.2, 0.5, 0.9])
translate([68, -5, 0])
  sphere(r=3.2, $fn=32);

// Moon orbiting Earth
color([0.8, 0.8, 0.8])
translate([73, -5, 2])
  sphere(r=0.9, $fn=16);

// Mars - the red planet
color([0.8, 0.3, 0.15])
translate([82, 10, 0])
  sphere(r=2.2, $fn=32);

// === GAS GIANTS ===

// Jupiter - king of the planets
color([0.85, 0.7, 0.5])
translate([110, -8, 0])
  sphere(r=11, $fn=48);

// Jupiter's Great Red Spot hint
color([0.75, 0.4, 0.3])
translate([110, -8, 8])
  sphere(r=2.5, $fn=16);

// Saturn - the ringed beauty
color([0.9, 0.8, 0.55])
translate([148, 8, 0]) {
  sphere(r=9, $fn=48);

  // Saturn's iconic rings
  color([0.85, 0.75, 0.5], 0.7)
  rotate([70, 0, 15])
    difference() {
      cylinder(h=0.4, r=16, center=true, $fn=64);
      cylinder(h=0.8, r=11, center=true, $fn=64);
    }

  // Ring gap
  color([0.75, 0.65, 0.4], 0.5)
  rotate([70, 0, 15])
    difference() {
      cylinder(h=0.5, r=19, center=true, $fn=64);
      cylinder(h=0.9, r=16.5, center=true, $fn=64);
    }
}

// Uranus - icy blue-green, tilted
color([0.6, 0.85, 0.88])
translate([180, -12, 0])
  sphere(r=5.5, $fn=40);

// Neptune - deep blue, far out
color([0.25, 0.35, 0.85])
translate([205, 5, 0])
  sphere(r=5, $fn=40);

// === ASTEROID BELT (between Mars and Jupiter) ===
for (i = [0:30]) {
  color([0.5, 0.45, 0.4])
  translate([
    93 + 8 * cos(i * 12),
    8 * sin(i * 12),
    3 * sin(i * 37)
  ])
    sphere(r=0.3 + 0.2 * sin(i * 53), $fn=8);
}

