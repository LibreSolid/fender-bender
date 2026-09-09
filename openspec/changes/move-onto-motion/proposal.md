# Move the Fender-Bender simulation onto solid-node's motion layer

## Why

solid-node main (8b85c02, 2026-09-09) moved ports and the declared time
base out of `solid_node.node` into `solid_node.motion.ports`, with no
re-export, and added the motion layer proper: `solid_node.motion.joints`
(`Revolute`, `Prismatic`) and `solid_node.motion.couplings` (`drives`,
`Affine`, derived coordinates). This simulation does not import today:

    ImportError: module 'solid_node.node' has no attribute 'RotationalPort':
    ports and the declared time base moved to 'solid_node.motion.ports'.

Two files carry the broken imports — `simulation/channel.py`
(`RotationalPort`) and `simulation/loop.py` (`SignalPort`). No test file
imports a moved name.

Fixing the imports is the smaller half. The model states its three moving
things by hand:

- the wheel turns because `Channel.simulate()` calls `self.wheel.rotate()`
  from a value the root pushed into a `RotationalPort` whose only job is
  to carry it one level down;
- the lock pin slides because the root calls `self.pin.translate()`;
- the bracket leaves its pocket because the root calls `rotate()` and
  `translate()` on the channel with a comment explaining which way the
  channel's own frame points ("world Y is local -Z and world Z is local
  +Y") — the hand-inverted frame a joint declaration exists to delete.

The first two are one coordinate on one axis each and become joints and a
relation. The third is not, and it is why this change recommends
**deferral**: see Known gaps.

## What changes

### Stage A — imports only (done and committed whatever the deferral)

- `simulation/channel.py`: `from solid_node.motion.ports import RotationalPort`.
- `simulation/loop.py`: `from solid_node.motion.ports import SignalPort`.

Nothing else. `AssemblyNode`, `Build123dNode`, `MolejoNode` stay on
`solid_node.node`.

### Stage B — the motion refactor (blocked; see Known gaps)

#### Joints to declare

**1. `FilamentWheel.spin`** — in `simulation/filament_wheel.py`:

```python
spin = Revolute(axis=(0, 0, 1), unit='deg')
```

*Parent's frame:* the `Channel`'s, which is the bottom bracket's — base
face on Z = 0, wheel axis on local Z. *Axis:* `(0, 0, 1)`, the wheel axis,
read off `Channel.render()`, which places the wheel with a pure
`translate([0, 0, shelf])` and no rotation, and off
`FilamentWheel`'s own docstring ("Axis on Z, one face on Z = 0").
*Anchor:* the default `(0, 0, 0)`. The wheel's placed origin is
`(0, 0, cfg.bearing_shelf_height)`, but the line `x = y = 0` through the
parent origin **is** the line through the placed origin, so the default
anchor names the same axis; and a rotation about Z commutes with a
translation along Z, so the composed pose is identical to today's
`self.wheel.rotate(angle, [0, 0, 1])` to the last bit. (If the pose
comparison shows float noise from the framework's centring translations,
declare `at` as a callable of the realized node returning
`(0, 0, bearing_shelf_height)` and the two centring translations
disappear; that is a cosmetic fallback, not a different pose.)
*Range:* none. The wheel turns without limit and today's angle is
unbounded (`wheel_angle` is `-2 * slack / r` in radians, about -311° at
the 190 mm end of the slack range).
*Unit:* `'deg'`, the unit `kinematics.wheel_angle()` already returns.

**2. `LockPin.draw`** — in `simulation/lock_pin.py`:

```python
draw = Prismatic(axis=(0, 1, 0), range=(0.0, 100.0), unit='mm')
```

*Parent's frame:* the root's world frame; `FenderBender.render()` places
the pin with a pure translate, no rotation, so the pin's local axes are
the world's. *Axis:* `(0, 1, 0)` — `layout.PIN_DRAW_AXIS` is exactly this
constant and the docstring says "drawn out toward +Y; its tie loop stands
on that side". *Anchor:* not applicable to a `Prismatic` (the spec says
`at` never affects a slide's placement); leave it at the default.
*Range:* `(0.0, 100.0)` mm, the `pin_draw` driver's declared range and the
travel `Unlock`/`Lock` use. See Tests for the one risk this range carries.
*Unit:* `'mm'`.

#### Relations

**1.** in `simulation/fender_bender.py`, in `FenderBender`'s class body,
after the `pin` child and the `pin_draw` driver are declared:

```python
pin_draw.drives(pin.draw)
```

*Driver end:* `FenderBender.pin_draw`, the root `Driver`, mm.
*Driven end:* `LockPin.draw`, the `Prismatic` coordinate declared above,
mm. *Law:* the implicit `Affine(ratio=1.0, offset=0.0)` — the pin is drawn
by exactly what the driver says, which is what
`self.pin.translate([0, self.pin_draw, 0])` does today. No `ratio=`, no
`offset=`, no `law=`.

That is the only relation this model has. Everything else that would be a
relation crosses a `.repeat()` boundary (see Known gaps 3).

#### Derived coordinates

None. The two candidates are both refused where they would be written:

- `selected * self.slack + demo_slack(self.time, ...)` is a product of two
  driver reads (`indicator(self.channel, index)` times `slack`), not a sum
  of coordinates scaled by numbers.
- `selected * self.lift * gate` is likewise a triple product.

Both stay ordinary arithmetic inside `simulate()`, which is what the
couplings spec points at when it refuses a non-linear derived coordinate.

#### Ports

**`Loop.drop` stays, unchanged.** It is a `SignalPort` that feeds molejo
geometry: `Loop.render()` reads it as `P.drop` inside the `Shape` path, so
the port is the shape parameter of a flexible part — the documented
`driver → port → geometry` chain — not a forwarding port and not a
freedom. The loop body never moves; its *shape* changes. It gets no joint
and it loses nothing.

**`Channel.spin` goes.** It is a forwarding `RotationalPort`: the root
binds it, `Channel.simulate()` reads `self.spin.value` and turns the
wheel. With the joint on the wheel — the body that actually turns — the
root binds the wheel's coordinate by path and the port has no work left.

#### `simulate()` that shrinks or disappears

- **`Channel.simulate()` disappears entirely** (5 lines). With it goes the
  standalone fallback `angle = 360.0 * self.time` when the port is
  unbound. A `Channel` built on its own then stands still instead of
  turning once per timeline cycle. That is a deliberate behaviour change
  and it is honest — a channel alone has nothing feeding it filament —
  but it changes the standalone `Channel`'s pose at every `t > 0`. It does
  not change any pose of the declared model `simulation.fender_bender:FenderBender`,
  where the root binds every channel's wheel at every instant. See Tests.
- **`FenderBender.simulate()` loses its last line**,
  `self.pin.translate([0, self.pin_draw, 0])`, to the relation above, and
  its wheel line becomes a joint binding by path:

```python
channel.wheel.spin = kinematics.wheel_angle(slack, radius)   # was channel.spin = ...
```

  The loop itself stays: the per-copy selection, the per-copy demo phase
  and the per-copy release pose cannot be stated as relations (Known
  gaps 3), and the two lines that place the bracket on its release path
  cannot be stated as joints (Known gaps 1 and 2).

An alternative was considered and rejected: give `Channel` a `slack`
`SignalPort` and state `slack.drives(wheel.spin, law=wheel_pickup)` inside
`Channel`, the law reading the realized wheel's diameter. It reads well,
but it puts back a port whose only job is to carry the root's per-copy
value one level down — the exact thing this change removes — because the
relation still cannot fan out over `.repeat()` and the root must therefore
bind each copy in a loop regardless. Binding `channel.wheel.spin` directly
is one line and no port.

#### Hand-written frame inversions removed

One: the wheel's. `Channel.simulate()`'s `rotate(angle, [0, 0, 1])`
depended on knowing that the channel places the wheel unrotated. Nothing
else leaves, because the bracket release — the model's one real frame
inversion, with the three-line comment that explains it — is what this
change cannot state (Known gaps 1).

## What does not change

- **Drivers.** `channel`, `slack`, `lift`, `pin_draw` keep their names,
  defaults, ranges, units and dtypes. Driver ids are unchanged, so the
  viewer's controls and every `set_state` call are unchanged.
- **Instructions.** All six (`Retract`, `Feed`, `Unlock`, `Lock`,
  `Lift bracket`, `Seat bracket`) keep their targets and durations.
- **Placements.** Every `render()` in the package is untouched: the frame
  stack, the wall placements, the channel pitch, the loop placement, the
  pin's seat. No part moves at rest.
- **Parameters and `check()`.** `filament_count`, `wheel_diameter`,
  `chamber_depth`, `tolerance`, `SLACK_RANGE`, the chamber guard and
  `loop_radius` are untouched.
- **`simulation/kinematics.py`, `layout.py`, `config.py`, `hardware.py`,
  `colors.py`.** No formula changes: `release_pose`, `lift_gate`,
  `indicator`, `wheel_angle` and `demo_slack` are all still called from
  the same places with the same arguments.
- **The tree shape.** No child is added, removed, renamed or reparented,
  so every leaf path in the pose capture and every `self.node.channels[i]`
  / `self.node.loops[i]` / `self.node.frame.*` in the tests still
  resolves. In particular the loops stay children of the root rather than
  moving inside their channels — that would read better but it would
  rename every loop leaf and rewrite the tests.
- **Tests and contracts.** No test file is edited by this change; the four
  archived capability specs (`bracket-frame-seat`, `filament-buffer-loop`,
  `wall-frame-joint`, `wheel-bearing-fit`) are unaffected, because nothing
  about what the parts promise each other changes.
- **Upstream `src/`.** Never touched.

## Known gaps

**Recommendation: defer this project after stage A.** The bracket release
is the substantial motion of this model — it is the model's whole reason
for a `lift` driver, six of the eight assembly tests exercise it, and it
is where the hand-written frame arithmetic lives — and it cannot be
stated with the motion API as it stands. Refactoring only the wheel and
the pin around it would leave the one interesting motion hand-written and
the comment about local axes still in the file: cosmetic, by the
campaign's own standard.

The sentence the project wants to write, in `simulation/channel.py`:

```python
class Channel(AssemblyNode):
    # The release path the top frame admits, measured by intersecting the
    # placed bracket with the frame. One freedom, three coordinates.
    tilt  = Revolute(axis=(0, 1, 0), at=OWN_PLACED_ORIGIN, unit='deg')
    slide = Prismatic(axis=(1, 0, 0), unit='mm')
    rise  = Prismatic(axis=(0, 0, 1), unit='mm')
```

with, on the root:

```python
lift.drives(channels.tilt,  law=release_tilt)    # law(root, copy) reads copy.index
lift.drives(channels.slide, law=release_slide)
lift.drives(channels.rise,  law=release_rise)
```

or, better, one declaration for one mechanical freedom — a cam path:

```python
release = Path(RELEASE_WAYPOINTS, at=OWN_PLACED_ORIGIN, unit='mm')
```

where `RELEASE_WAYPOINTS` is the nine `(lift, dx, dz, tilt about Y)`
samples `kinematics.py` already measured, and the path interpolates them
the way `piecewise` does today.

Three separate limits stand in the way, all three already recorded in
`solid-node/workflow/warts.md`; this project is a new sighting of each.

1. **A body with more than one freedom against its parent.** The bracket's
   pose along the path is
   `T(dx, dz, 0) · Rz(-tilt)` in the channel's own frame (confirmed
   against `_insert_motion`: operations placed under a simulate phase go
   at the head of the operation list in call order, so today's `rotate`
   then `translate` composes as rotate-innermost). Three `Prismatic`/
   `Revolute` joints on one body state the three coordinates, but the
   joints spec composes joint motion **in the order the coordinates were
   bound**, and the pose is right only when `tilt` is applied inside the
   two slides. This is the OpenCycloid/hexapod finding exactly; the same
   primitive — joints of one class composing in *declaration* order,
   innermost first, whatever order they are bound in — unblocks this
   project too.
2. **A joint cannot be anchored at a design-placed part's own origin.**
   The tilt is about world Y through the channel's own placed origin,
   which is `(0, layout.channel_y(index, count, spacing) + depth / 2,
   base)` — a different point for each of the five copies, and one the
   parent's `render()` computes. `at` is resolved in `__init__`, before
   the parent has placed the node, and `Channel` carries no index
   parameter to compute it from, so there is no way to write it. Writing
   the parent's layout formula into the `Channel` class would also be the
   second 2026-09-09 finding (a joint's anchor belonging to the
   declaration site) in its worst form: per-copy.
3. **A relation cannot fan out over a repeated child.** `channels` and
   `loops` are `.repeat(filament_count)` children, and every value the
   root pushes into them is per-copy: the selection
   `indicator(self.channel, index)`, the demo phase
   `demo_slack(self.time, count, index)`, and the release pose. Every one
   of them needs the law to read the copy's index. This is the
   OpenCycloid/abacus finding. It does not by itself defer the project —
   the wheel and the loop are bound in a `for` loop today and would stay
   there — but it is why nothing else in this model becomes a relation,
   and it is why the release path could not be driven even if 1 and 2
   were solved.

Nothing about limit 3 in the framework's list of *three known limits*
(one-class-body relation chains, and a node's own derived coordinate
unbound inside its own `simulate()`) bites here: this model has no
relation chain and no derived coordinate.

What stays hand-written under the deferral: `FenderBender.simulate()`
entire, `Channel.simulate()` entire, both `RotationalPort`/`SignalPort`
imports repointed but otherwise as they are.

## Pre-existing state

`git status --porcelain` in
`projects/3D-Printers/fender-bender` reports exactly one entry:

    ?? screenshot.png

An untracked scratch screenshot, which stays untracked. Nothing tracked is
dirty; HEAD is `2a6ac61` on branch `main`. **Stage 0 is a no-op** — there
is nothing to commit before the refactor — and this change's `proposal.md`
and `tasks.md` are committed with the stage A commit.

## Tests

Three test modules run against this simulation, all under the project's
own OpenSpec capabilities. `pyproject.toml` declares one model,
`simulation.fender_bender:FenderBender`; the `Channel` and `Frame` test
cases name their own nodes.

- `simulation/test_frame.py` — `FrameTest` (5 tests, `node = Frame`):
  the wall/frame stack, the guide-wall snap volume, the wall count against
  `filament_count`. **No motion at all.** Unaffected by every part of this
  change.
- `simulation/test_channel.py` — `ChannelTest` (9 tests, `node = Channel`):
  the bearing on its shelf, the wheel on the bearing, clearances and
  perturbation contracts.
- `simulation/test_fender_bender.py` — `FenderBenderTest` (13 tests) and
  `FenderBenderScenarioTest` (2 scenario tests): whole-model integrity and
  support, the bracket-frame seat, the release path, the buffer loop, the
  timeline.

Flagged — the orchestrator decides, this proposal only names them:

1. **`ChannelTest`, all nine, if stage B goes ahead.** Deleting
   `Channel.simulate()` removes the standalone fallback that turns the
   wheel with time. No assertion in the file reads the wheel's angle, so I
   expect all nine to stay green — but four of them
   (`test_wheel_turns_freely`, `test_wheel_is_captured_radially_by_the_bearing`,
   `test_wheel_is_captured_axially_by_the_guides`,
   `test_wheel_floats_within_its_lateral_tolerance`) perturb the wheel,
   and the wheel's operation list changes shape (an angle-0 `Rotation`
   disappears when the model is built standalone). If the framework's
   perturbation frame depends on whether a leaf carries operations of its
   own — the trap `test_fender_bender.py` documents for the bracket leaves
   — these are where it would show. The wheel keeps its `render()`
   translate either way, so it keeps its own frame; I expect no change.
2. **`FenderBenderTest.test_drawn_pin_frees_the_bracket` and the
   `Unlock` instruction, if stage B goes ahead.** Both bind
   `pin_draw = 100.0`, exactly the upper end of the proposed
   `Prismatic(range=(0.0, 100.0))`, and the joints spec refuses a plain
   numeric binding outside a declared range. If the check is exclusive at
   the endpoint, or a scenario ramp lands a float hair above 100.0, this
   goes red. The fix is not a test change: **drop `range=` from the joint**
   (the `pin_draw` driver already carries the presentation range) and
   record it. Flagged so the implementer does not silently widen a test's
   expectation.
3. **No test needs a change for stage A**, and none imports a moved name.
   The baseline is unknown until it is run: this simulation last ran green
   at `2a6ac61` against an older framework tree, and the campaign has
   already found projects that were red before the motion move
   (BCN3D-Moveo, Thor). Stage A establishes the truth; a test red at
   stage A is recorded, not fixed.
4. **`test_slack_turns_the_wheel`** asserts channel 0's wheel turned
   `degrees(1.0)` and channel 1's wheel did not move, to 1e-6. It is the
   one test that reads a wheel angle, so it is the test that would catch a
   wrong joint axis or anchor. Expected green: the angle formula, the
   axis and the anchoring line are all unchanged.

## Deferred (2026-09-09)

The orchestrator deferred this project after stage A. The bracket release
is three coordinates on one body — the composition order of several
joints on one body, an anchor at a repeated copy's own placed origin, and
a relation fanning out over a repeated child (see Known gaps above) — and
none of the three is yet stated by the motion API. All three are recorded
as findings in `solid-node/workflow/warts.md`, section "Motion catalogue
refactor, 2026-09-09"; stage B waits for the framework to state them.
Stage A (imports fixed, baseline established, poses captured) is
committed regardless, so the project runs against the current framework
meanwhile.
