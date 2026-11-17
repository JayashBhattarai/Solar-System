# Solar System

A Python/Pygame/OpenGL orrery with textured planets, tilted spin axes, elliptical orbits, Saturn and Uranus rings, and 1,000 illustrative main-belt asteroids.

## Run

```sh
python -m pip install -r requirements.txt
python SolarSystem.py
```

Requires a desktop display and an OpenGL compatibility context (legacy GL/GLU). Python 3.8+.

## Controls

- Arrow keys: orbit the camera; mouse wheel: zoom.
- 0: Sun overview; 1–8: follow Mercury through Neptune.
- Space: pause; + / -: double / halve simulation speed.
- O: orbital paths; B: asteroid belt; R: reset epoch, speed and camera; Escape: quit.

The title bar shows elapsed days since J2000 and simulation days per real second. Default speed is 10 days/s; slow down to inspect spin without temporal aliasing. The camera remains usable while paused.

## Physics and scale

`physics.py` solves Kepler's equation with Newton iteration, using fixed, rounded J2000 mean elements. Orbital periods follow solar GM and semi-major axis; planets move faster near perihelion. Inclination, ascending node and perihelion orient each ellipse. Time is elapsed seconds, independent of frame rate. Spin uses approximate sidereal periods on the same clock. Venus and Uranus rotate retrograde through their >90-degree axial tilt; no second sign reversal is applied. Spin zero phase and pole azimuth are illustrative.

Distances use a common linear AU scale. Planet and Sun radii are deliberately exaggerated independently of distances and do not enter gravity calculations. Asteroid points are enlarged for visibility: real main-belt objects are very sparsely distributed. Belt orbits are seeded synthetic samples, not a catalogue; resonant gaps and perturbations are not modeled.

This is an independent solar two-body approximation, not an N-body gravity integrator or precision date ephemeris. It omits mutual planetary forces, barycentric Sun motion, secular evolution, relativity and moons. The Earth elements approximate the Earth–Moon barycenter. Fixed elements drift over long intervals. More solver precision cannot remove those model limitations.

## Textures and lighting

Deterministic procedural RGB textures make rotation and surface differences visible without downloads. These are artistic approximations, including Earth's land shapes. For photographic surfaces, put licensed equirectangular maps in `textures/mercury.jpg`, `venus.jpg`, `earth.jpg`, `mars.jpg`, `jupiter.jpg`, `saturn.jpg`, `uranus.jpg`, `neptune.jpg`, or `sun.jpg`. PNG is also supported; JPEG takes precedence. Maps load on startup and replace the corresponding fallback.

A world-space point light at the Sun produces day/night shading. The Sun is self-lit. Small ambient fill and constant light intensity preserve visibility at outer planets; this is not photometric inverse-square exposure. There are **no cast shadows, eclipses, or ring shadows**. Rings and asteroid points use unlit illustrative colors. Real cast shadows need a shadow-map or analytic occlusion renderer; turning on `GL_LIGHTING` alone does not produce them.

Useful next realism steps: photographic maps, normal maps, Earth cloud/atmosphere layers, moons with eclipses, analytic ring shadows, gas-giant flattening, and a JPL ephemeris mode. These are not currently implemented.

## Validation and sources

```sh
python -m unittest -v
```

Tests cover perihelion/aphelion distances, period closure, solar gravitational acceleration, equal-area angular momentum and spin periods.

- JPL mean elements and coordinate method: https://ssd.jpl.nasa.gov/planets/approx_pos.html
- NASA approximate rotation periods and obliquities: https://nssdc.gsfc.nasa.gov/planetary/factsheet/
- Precision ephemerides: https://ssd.jpl.nasa.gov/planets/orbits.html
