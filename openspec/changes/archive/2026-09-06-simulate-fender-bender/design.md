## Context

Fender-Bender (`src/`) generates every printed part of a filament buffer
with build123d through partomatic part classes, each configured from one
`BenderConfig` that derives every dimension from a few knobs read out of a
YAML build configuration. The parts are exported one STL at a time; the
only assembled views are hand-placed documentation renders in
`src/debug_view_assembly.py` and `src/assembly_documentation.py`, written
for the hanging frame of the development configuration and dependent on the
`ocp_vscode` viewer.

This change adds `simulation/`, a solid-node 0.6 project (declarative node
API) that imports those part classes and assembles one complete buffer as a
machine: rest placement, repeated channels, sourced parts, drivers,
instructions and contracts. The world frame is the upstream top frame's: X
along the frame's long side (the wheel plane), Y along the channel axis
(the wheel axis), Z up, origin at the top frame's base face; the wheel axis
of every seated bracket lies at Z = the upstream frame base depth (8 mm) and
the walls hang below Z = 0 to the bottom frame, which stands on the table.

## Goals / Non-Goals

**Goals:**
- The layer is as thin as it can be: a part file here is a class that
  names the root parameters it needs, builds the upstream configuration
  from them, and returns the upstream part. Placement lives in one
  `layout.py`; kinematics in one `kinematics.py`; nothing upstream is
  edited, subclassed for geometry, or reimplemented.
- One site option is chosen and built; the maker sees that buffer whole,
  with the bought parts in place and colours that separate part families.
- The buffer demonstrates its function: slack drops into a chamber and
  turns the wheel, the pin unlocks, a bracket lifts out and reseats.
- Fits the upstream design promises are contracts: bracket in pocket, pin
  in channel, bearing between shelves, wheel on bearing, tongues in
  grooves, walls in slots, loop inside chamber, stack standing.

**Non-Goals:**
- Building the site's other options (hanging or hybrid frames, solid or
  drybox walls, threaded connectors, other tubing, clip locks, alternate
  filament counts as separate part sets). They remain upstream
  alternatives; a second option would be a second change.
- The PTFE tubes and connectors, the wall hanger, the surface-mount
  bracket and the print-in-place bearing.
- Filament physics: the loop is a stated U of stated radius, not a
  catenary; friction and stiffness are out of scope.
- Any change to the upstream sources, their tests or their build.

## Decisions

**Import the upstream part classes; do not re-model them.** Each solid-node
leaf is a `Build123dNode` whose `render()` builds a `BenderConfig` through
`config.bender_config(...)` from the parameters it declares and returns the
upstream part (`TopFrame(cfg.frame_config).top_frame()`,
`FilamentBracket(cfg.filament_bracket_config(0)).bottom_bracket()`, ...).
The alternative, porting the geometry into solid-node nodes, was rejected:
it would fork a maintained design and lose every upstream fix. The cost
accepted is that a leaf's rebuild tracking does not see the upstream
sources (they sit outside the package and are reached through `sys.path`),
so an upstream edit needs a manual rebuild; the upstream is treated as a
pinned library.

**One option, stated in `config.py`.** The site's part selector offers
flow direction, tubing/connector, filament count, frame style, wall style
and extras. The model fixes: forward flow, 6 mm x 3 mm tubing with no
connector, the standing frame, hex walls, pin lock, no extras, and exposes
filament count as a parameter. Standing was chosen over the hanging
reference because it needs no wall and gives the support contract a floor
to stand on; hex over solid because the maker can see the loops through
the walls; pin over clip-and-pin because one pin is one part with one
motion. The upstream `BenderConfig` is constructed from defaults and then
set field by field, not from a YAML file, so the choice is code the model
tracks, and the reference configuration's numbers (bearing 12.1/6.1/8.5 x
4, wheel 70 with five spokes, tube 6.5/3.6, pin tolerance 0.6) are
restated there with their source.

**Root parameters are the upstream knobs a maker would turn.**
`filament_count` (Count, 5), `wheel_diameter` (Length, 70), `chamber_depth`
(Length, 370; the upstream `frame_chamber_depth`) and `tolerance` (Length,
0.2; the upstream fit tolerance). Each leaf declares only those it reads so
that turning one rebuilds exactly the parts that depend on it. Every
upstream derived quantity used for placement (`frame_base_depth`,
`sidewall_straight_depth`, `frame_connector_depth`, `frame_bracket_spacing`,
`bearing_shelf_height`, `lock_pin_point`) is read from a `BenderConfig`
built in the assembly's `render()`; nothing derived is retyped as a
literal here.

**Sourced parts are modelled from the bill of materials, at the fit the
upstream design assumes.** The bearing is an MR126 ring: outside 12.0 mm,
width 4.0 mm, bore modelled at the upstream post diameter (6.1 mm) rather
than the catalogue 6.0 mm, because the upstream post is a press fit into the
real bore and adjacency discipline forbids shared volume; this is recorded
as a finding, not hidden. The filament is a molejo `Shape`: a 1.75 mm
circle swept along two straight legs and a 180 degree arc, parameter `drop`
the leg length, radius `wheel_radius - groove_depth + 1.3 mm` so the
filament sits in the wheel's diamond groove with about 0.05 mm to the groove
flanks and 0.025 mm inside the bracket's wheel cut. Tubes are not modelled
(their channel geometry is deep in `filament_channels.py`), and the README
says so.

**Motion is drivers on the root, fed to repeated channels through ports.**
`channel` (int, 0..4 for the default five) selects a channel; `slack` (mm)
is that channel's loop depth; `lift` (mm) moves that bracket along the
release path; `pin` (mm) draws the pin along +Y. A `Channel` assembly
(bracket bottom, top cap, wheel, bearing) carries `spin` and `lift` ports;
a `Loop` leaf carries the molejo `drop` port. The root's `simulate()` feeds
each channel `indicator(channel, i) * slack` plus the timeline wave, and
turns the wheel by `2 * slack / wheel_radius` radians. Instructions are
`Retract`/`Feed` (slack 150/0), `Unlock`/`Lock` (pin 100/0) and `Lift
bracket`/`Seat bracket` (lift full/0).

**The lift is gated by the pin.** A bracket's effective lift is `lift *
clamp01((pin - PIN_CLEAR) / 8)`, so a lift commanded against a home pin
does nothing and a ramp of both together seats the bracket before the pin
re-enters. Sequencing inside an instruction was rejected because an
instruction ramps all targets together; the gate keeps every pose the
viewer can reach interference-free, which is what the release-path contract
sweeps.

**The release path follows the usage instructions.** The pocket is a half
cylinder about the wheel axis with 0.2 mm around a bracket whose flanks are
the same arc, so a straight lift fouls the pocket flanks (measured 85 mm³ of
interference at 1 mm). The path is stated in `kinematics.release_pose(lift)`
as a forward shift and a lift, in the combination the probe of the frame
shows interference-free (recorded in Outcomes below once measured), and the
contract sweeps it.

**Rest placement comes from the upstream debug view, corrected by
measurement.** The upstream assembly scripts place walls for the hanging
configuration; their offsets were probed against the standing frames by
intersection volume and the interference-free offsets recorded in
`layout.py` with the measurement that chose them.

**Colours.** Frames `#4C6A92` (slate), guide walls `#2A9D8F` (teal), inner
side walls `#8ECAE6` (sky), reinforced side walls `#219EBC`, bracket
`#F4A261` (amber), top cap `#E76F51` (coral), wheel `#FFD166` (gold),
bearing `#C0C0C0` (steel), pin `#D62828` (red), filament `#FF2E93`
(magenta). Neighbouring families never share a hue.

**Tests run faceted during the build and exact once at the end.** The hex
walls make exact booleans slow (about 25 s to build each wall); the loop
runs `solid test --faceted`, and the exact run certifies the commit.

## Risks / Trade-offs

- [Upstream source edits are invisible to rebuild tracking] → the upstream
  is pinned by commit in the README; after pulling upstream, build once
  with a fresh build directory.
- [partomatic API drift: 0.8 renamed `_config` to `config`] → the
  environment pins partomatic 0.7.0 and bd_warehouse 0.2.0 (bd_warehouse
  0.3 drags build123d past the 0.10 series solid-node pins); recorded in
  the README's environment section.
- [The wheel groove is a diamond; the filament's fit in it is geometric
  guesswork] → the loop radius is a constant with its derivation, and the
  taut-loop contract measures clearance to the wheel, so a wrong guess
  fails a test rather than hiding.
- [Support contract may not resolve a bearing clamped between shelves or
  loops held by wheels] → both are declared as press supports; if the proof
  still fails on the seated brackets the contract is reported as a gap,
  never weakened.
- [Exact interference over ~30 hex-patterned solids is slow] → the
  interference sweep uses coarse steps and the faceted kernel in the loop;
  exact once per commit.
- [Symbolic driver ranges are refused by the framework] → `channel` range
  is the constant `(0, 4)` for the default count; a wider buffer is driven
  past the slider by value (same limitation the abacus recorded).

## Outcomes recorded while building

- **Placement.** The bracket seats at X = 0 (the standing frame has no
  hanger offset) with its wheel axis at the frame base depth; side walls
  centred on their slots at Z = -1.5 (interference-free window -2.25 to
  -1.0); guide walls at X = +-(sidewall width / 2), turned +90 about Z then
  -90 about Y on the -X side and +90 on the +X side; the lower section's
  side walls are the upper section's mirrored about the connector's
  mid-plane (rounded end down into the bottom frame's core cut).
- **Release path.** Measured pose by pose against the top frame:
  (lift, dx, dz, tilt) = (5, 4, 1, 0), (10, 4, 4, -5), (15, 6, 8, -10),
  (20, 6, 12, -15), (25, 8, 15, -15), (35, 10, 25, -15), (40, 10, 25, 0),
  (100, 10, 95, 0). No rigid interference-free path exists: the retaining
  rim needs dx >= 8 during the tilt and the pocket's narrow base stops the
  bracket's lower channel block at dx = 5.8. Along this path the bracket
  body shares at most 3.2 mm³ with the frame (the two click-fit spheres,
  bound 3.53) and the cap at most 1.2 mm³ at the narrow base's front wall
  (bound 1.5); wheel and bearing stay clear. Both allowances are stated in
  the spec and test as findings.
- **Guide wall snap.** Upstream sizes the guide wall core 1.5 mm shorter
  than the frame gap; each click-fit bump then overlaps its pocket by
  1.13 mm³ at rest (2.26 per wall per frame, bound 2.5). The whole-model
  interference check parks the guide walls and bounds those pairs
  separately.
- **Molejo.** `Arc.angle` is in radians (a 180 there is a 28-turn coil);
  parameters may sit inside coordinate tuples; a zero-length first `Line`
  is avoided by a 0.5 mm minimum drop.
- **Framework gaps met.** (1) The faceted kernel and every Manifold-backed
  assertion (`assertNoSolidInterference`, `assertAssemblySupported`) refuse
  seven of the upstream STLs that trimesh calls non-watertight although
  Manifold accepts them with matching volumes; the project checks
  interference pairwise on the exact solids (`contracts.py`) and leaves the
  support contract unverified. (2) A perturbation on a leaf with no
  operations of its own is expressed in its parent's frame, so bracket
  directions are given in the channel's rotated frame. (3) A bare float
  cannot be added to a `Length` token in a class body, so the loop radius is
  derived on instances. (4) `range=` on a driver cannot follow `Count`.
- **Partomatic.** 0.8 renamed `_config` to `config`; the upstream sources
  (October 2025) need 0.7.0. bd_warehouse 0.3 drags build123d to 0.11 and
  installs `cadquery-ocp-novtk`, which breaks cadquery 2.7's OCP binding;
  0.2.0 is pinned.

- **Mutation checks.** Dropping the pin gate fails only the lift-ignored
  contract; moving the side walls to Z = -3 fails the frame stack, slot
  capture and count contracts; seating the loop 1.4 mm further out fails
  the taut-loop, chamber-sweep, selection and timeline contracts; turning
  the guide walls the other way (an actual slip while porting the probe)
  raised the snap bound from 2.3 to 504 mm³ and was caught by it.

## Open Questions

- Whether the maker wants the hanging reference frame simulated too; that
  is the wall hanger plus a second option of the frame parts and would be
  its own change.
