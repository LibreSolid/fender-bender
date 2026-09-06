## Why

Fender-Bender is a published, printable filament buffer whose parts are
generated one at a time by build123d scripts and shown assembled only in
static documentation renders. Nothing in the repository puts the printed
parts together with the parts a maker buys (the MR126 wheel bearings), and
nothing shows the buffer doing its job: a bracket lifting out of the frame
for a filament change, the lock pin that holds it, a wheel turning as
filament moves, or the slack loop dropping into a chamber when the printer
retracts. A maker choosing between the site's options cannot see the chosen
buffer as one machine before printing it.

## What Changes

- A solid-node model of one complete Fender-Bender, assembled from the
  upstream part generators unchanged: `simulation/` imports the classes
  under `src/` and only places, repeats, colours and drives what they
  return. Nothing under `src/` is edited or redesigned.
- One option is chosen from the site's part selector and stated as the
  model's configuration: five filament channels (Prusa MMU3), the standing
  frame, hex walls, 6 mm OD x 3 mm ID PTFE tubing with no connector, forward
  flow direction, and the lock pin as the frame lock. The site's other
  options remain upstream alternatives the model does not build.
- The sourced parts the upstream scripts leave to the maker are modelled
  here from the site's bill of materials: the MR126 bearing (12 mm x 6 mm x
  4 mm) each wheel turns on, and the 1.75 mm filament as a flexible loop in
  each chamber whose depth follows the buffered length.
- Root parameters drive the whole machine through the upstream
  configuration: filament count, wheel diameter, chamber depth and the
  printer's fit tolerance. A parameter set the upstream generators refuse,
  or that leaves no room for a loop, is refused before any part is built.
- Drivers and instructions make the buffer demonstrate itself in the viewer:
  a selected channel's slack loop drops and lifts (turning that wheel), the
  lock pin withdraws, and a selected bracket lifts out of the frame and
  seats again; the timeline runs every channel through a retract-and-feed
  cycle in turn.
- Colours separate the part families so the assembly reads at a glance:
  frame, guide walls, side walls, brackets, wheels, bearings, pin and
  filament each distinct.

## Capabilities

### New Capabilities
- `bracket-frame-seat`: the filament bracket in the top frame — the seat it
  drops into, the fit tolerance around it, the lift that frees it, and the
  lock pin that holds it seated.
- `wheel-bearing-fit`: the wheel, its bearing and the bracket's bearing
  shelf — the bearing seated on the shelf, the wheel bore over the bearing,
  and the radial and lateral running clearances that let the wheel spin.
- `wall-frame-joint`: the wall assembly between the frames — guide walls in
  the frame grooves, side walls in their slots, the stack of top frame,
  walls, connector frame and bottom frame, and the standing frame's
  footprint under gravity.
- `filament-buffer-loop`: the slack filament in a chamber — the loop's
  place between the walls of its own chamber, the slack range the chamber
  depth admits, and the wheel turning with the filament.

### Modified Capabilities
- (none; this is the project's first design change)

## Impact

- New `pyproject.toml` naming `simulation.fender_bender:FenderBender` as
  the model; new package `simulation/` with one node file per part family,
  a `config.py` that builds the upstream `BenderConfig` for the chosen
  option from the root parameters, a `layout.py` of rest placements, and
  companion tests per node file.
- New `openspec/` record (this change) and a `README.md` section on the
  simulation: how to build it, what the drivers do, what is sourced.
- The upstream sources gain no changes. The model depends on the same
  libraries the upstream build does (build123d, partomatic, fb-library,
  bd_warehouse) plus solid-node and molejo for the flexible loop; the
  partomatic version must be the one the upstream `_config` convention was
  written against (0.7.x or older), and build123d must stay at the 0.10
  series solid-node pins.
