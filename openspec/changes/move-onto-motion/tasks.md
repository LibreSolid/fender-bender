# Tasks

Behaviour-preserving throughout: the acceptance is that every leaf's world
matrix is unchanged at every pose of the declared model, so evidence is
captured before the first edit and compared after the last. Never edit a
test: if one blocks, stop and report the assertion and the reason, and wait
for the orchestrator.

**This project is proposed for deferral after stage A** (proposal.md,
Known gaps): the bracket release path is three coordinates on one body,
anchored at each copy's own placed origin, driven per copy through a
`.repeat()`. Stage A is done and committed regardless, so the project runs
against the current framework meanwhile. Stage B is written out below and
is NOT to be started until the orchestrator says the primitive has landed.

## 0. Pre-existing state

- [x] 0.1 `git rev-parse --show-toplevel` names
      `projects/3D-Printers/fender-bender`. `git status --porcelain` is
      expected to show exactly `?? screenshot.png` at HEAD `2a6ac61`,
      branch `main`. That is a scratch screenshot and stays untracked, so
      stage 0 is expected to be a no-op. If anything TRACKED is dirty,
      commit it first as
      `chore: commit the working state before the motion refactor`,
      leaving `screenshot.png`, `_build.lock`, `__pycache__` and editor
      backups untracked.

      Confirmed as expected: `git status --porcelain` reported exactly
      `?? screenshot.png` (plus this change's own untracked
      `openspec/changes/move-onto-motion/`), HEAD `2a6ac61`, branch
      `main`. Stage 0 is a no-op; nothing tracked is dirty.

## 1. Evidence (stage A)

- [x] 1.1 Fix imports only, two lines, no other edit:
      - `simulation/channel.py`:
        `from solid_node.motion.ports import RotationalPort`
        (keep `from solid_node.node import AssemblyNode`).
      - `simulation/loop.py`:
        `from solid_node.motion.ports import SignalPort`
        (keep `from solid_node.node import MolejoNode`).

      Done exactly as written. `grep`-checked every other simulation
      module and every test file for a moved name (`RotationalPort`,
      `TranslationalPort`, `SignalPort`, `Port`, `Time`, `bind`,
      `connect`, `declared_ports` from `solid_node.node`): only these two
      imports carried one; no test file imports a moved name.
- [x] 1.2 Run the suite and record the per-test result here as the
      baseline. One suite at a time, workspace venv, from the project root:
      `PYTHONPATH=. /home/asa/devel/libresolid-studio/.venv/bin/solid test --faceted simulation/fender_bender.py`
      (the one declared model: `FenderBenderTest` 13 +
      `FenderBenderScenarioTest` 2), then the two node test modules that
      name their own nodes — `simulation/test_channel.py` (`ChannelTest`,
      9) and `simulation/test_frame.py` (`FrameTest`, 5). The project's
      `tests/` directory is the UPSTREAM part suite, not part of this
      simulation; run it only if the orchestrator asks.
      Record pass/fail per test, and note any test already red: a red at
      the baseline is recorded, never fixed here.

      **Baseline recorded 2026-09-09**, workspace venv, `--faceted`, one
      suite at a time:

      `simulation/fender_bender.py` — 18 tests actually present (proposal
      counted 13+2=15; the file has 3 more than listed), 14 passed, 4
      failed, in 156-167s:
      - `FenderBenderTest.test_assembly_integrity` FAIL — `AssertionError:
        top should not interfere with bottom (intersection volume
        0.762388665578469)`
      - `FenderBenderTest.test_bracket_is_held_sideways_by_its_pocket`
        FAIL — `AssertionError: bottom should be free displaced 0.1mm
        along [0, 0, 1] against top (intersection volume
        0.7703724352000315)`
      - `FenderBenderTest.test_home_pin_clears_its_channels_and_is_captured`
        FAIL — `AssertionError: pin should not intersect top
        (intersection volume -1.0658141036401503e-14)`
      - `FenderBenderTest.test_solid_integrity` FAIL — `AssertionError:
        top should be one connected body, but its STL contains 57
        connected bodies`
      - All other `FenderBenderTest` tests passed, both
        `FenderBenderScenarioTest` tests passed
        (`test_bracket_change_sequence_stays_clear`,
        `test_retract_and_feed_keep_the_loop_in_its_chamber`).
      - The summary line names all four failures "(faceted kernel, volume
        epsilon 0 mm³)": near-zero/negative intersection volumes and a
        tessellated part's separate facets being counted as separate
        bodies — faceted-kernel tessellation noise, not a motion or
        import matter. Not touched, per instruction.

      `simulation/test_channel.py` — 10 tests (proposal counted 9), 8
      passed, 2 failed, in 2.38s:
      - `ChannelTest.test_assembly_integrity` FAIL — `AssertionError:
        bottom should not interfere with top (intersection volume
        0.00025012609849819396)`
      - `ChannelTest.test_solid_integrity` FAIL — `AssertionError: bottom
        should be one connected body, but its STL contains 9 connected
        bodies`
      - The 8 remaining tests passed, including all four wheel-perturbation
        tests the proposal (Tests §1) flagged as the place a
        `Channel.simulate()` deletion could show up
        (`test_wheel_turns_freely`,
        `test_wheel_is_captured_radially_by_the_bearing`,
        `test_wheel_is_captured_axially_by_the_guides`,
        `test_wheel_floats_within_its_lateral_tolerance`): all four green
        at baseline (`Channel.simulate()` is still present at stage A).
      - Same faceted-kernel/volume-epsilon shape as above.

      `simulation/test_frame.py` — 6 tests (proposal counted 5), 4 passed,
      2 failed, in 81.20s:
      - `FrameTest.test_sidewalls_are_captured_in_their_slots` FAIL —
        `AssertionError: sidewalls-0 should be blocked displaced 0.5mm
        along [0, 1, 0] against top (no intersection)`
      - `FrameTest.test_solid_integrity` FAIL — `AssertionError: top
        should be one connected body, but its STL contains 57 connected
        bodies`
      - `test_assembly_integrity`, `test_guidewall_tongues_are_captured_in_their_grooves`,
        `test_stack_heights` passed.

      Totals: 34 tests run, 26 passed, 8 failed — all 8 failures are
      faceted-kernel/tessellation-noise assertions (near-zero or negative
      interference volumes, or a tessellated single body counted as many
      connected bodies), none touching motion, ports, or the two import
      lines changed. No test imports a moved name and none was edited.
      `tests/` (the upstream part suite) was not run — out of scope for
      this project per this file's own instruction, and the orchestrator
      did not ask for it.
- [x] 1.3 Capture poses for the declared model:
      `PYTHONPATH=. /home/asa/devel/libresolid-studio/.venv/bin/python \
        /home/asa/devel/libresolid-studio/docs/motion-general-refactor/capture_poses.py \
        capture simulation.fender_bender:FenderBender /tmp/fender-bender-before.json`
      and again with an extra pose file for the six named instructions'
      end states (`Retract` slack 150, `Feed` slack 0, `Unlock` pin_draw
      100, `Lock` pin_draw 0, `Lift bracket` lift 100 with pin_draw 100,
      `Seat bracket` lift 0 with pin_draw 100) ->
      `/tmp/fender-bender-before-instructions.json`. Record the pose and
      leaf counts. Note: the `channel` driver is `dtype=int` with range
      `(0, 4)`; if the range-derived poses bind a fractional value to it,
      record what the capture did rather than working around it.

      **Captured 2026-09-09**:
      - `/tmp/fender-bender-before.json` — `captured 13 poses, 45 leaves`
        (default range-derived poses: defaults, each of `slack`,
        `lift`, `pin_draw` and `channel` at 0.4/1.0 of range, `all@0.63`,
        and `time` at 0.25/0.5/0.75).
      - `/tmp/fender-bender-before-instructions.json`, with an extra pose
        file at `.../scratchpad/fender-bender-instructions.json` holding
        the six named-instruction end states in order (`{"slack": 150}`,
        `{"slack": 0}`, `{"pin_draw": 100}`, `{"pin_draw": 0}`,
        `{"lift": 100, "pin_draw": 100}`, `{"lift": 0, "pin_draw": 100}`)
        — `captured 19 poses, 45 leaves` (the 13 above plus the 6 extras).
      - `channel` (`dtype=int`, range `(0, 4)`): `capture_poses.py`
        already rounds a range-derived value to `int` when the driver's
        `dtype` is `int` (see the tool's `poses_for()`), so `channel@0.4`
        and `channel@1.0` bound `2` and `4` respectively, not fractional
        values. No workaround needed; nothing to record beyond this.
- [x] 1.4 Commit as `refactor(simulation): import ports from
      solid_node.motion`, with the baseline in the message, together with
      this change's `proposal.md` and `tasks.md`.

## 2. The gap (deferral)

- [x] 2.1 Report to the orchestrator: the baseline, the pose counts, and
      that the release path is not statable. The finding and the sentence
      the project wants are in proposal.md, Known gaps; the orchestrator
      writes them into `solid-node/workflow/warts.md`, section "Motion
      catalogue refactor, 2026-09-09", as a third sighting of the
      composition-order limit, a further sighting of the own-placed-origin
      anchor, and a further sighting of the `.repeat()` fan-out.

      Reported in the implementer's final response (baseline: 34 tests,
      26 passed, 8 faceted-kernel-noise failures; poses: 13/45 and
      19/45). `solid-node/workflow/warts.md` is the orchestrator's to
      write, not touched from this project.
- [x] 2.2 Stop here. Do not start section 3 without the orchestrator's
      word that the primitive has landed.

      Stopped after this report; section 3 (stage B) not started.

## 3. Joints, relations and the ports that go (stage B — BLOCKED)

- [ ] 3.1 `simulation/filament_wheel.py`: declare
      `spin = Revolute(axis=(0, 0, 1), unit='deg')` on `FilamentWheel`,
      importing `Revolute` from `solid_node.motion.joints`. No `at`, no
      `range` (proposal.md, Joints 1).
- [ ] 3.2 `simulation/lock_pin.py`: declare
      `draw = Prismatic(axis=(0, 1, 0), range=(0.0, 100.0), unit='mm')`
      on `LockPin`. If a binding at exactly 100.0 is refused, drop
      `range=` and record the deviation (proposal.md, Tests 2).
- [ ] 3.3 `simulation/channel.py`: delete the `spin = RotationalPort(...)`
      declaration with its docstring, delete `Channel.simulate()` entire,
      and drop the now-unused `RotationalPort` import.
- [ ] 3.4 `simulation/fender_bender.py`: state `pin_draw.drives(pin.draw)`
      in the class body after both declarations, and delete
      `self.pin.translate([0, self.pin_draw, 0])` from `simulate()`.
- [ ] 3.5 `simulation/fender_bender.py`: in the `simulate()` loop, bind the
      wheel's joint by path — `channel.wheel.spin = kinematics.wheel_angle(
      slack, radius)` — in place of `channel.spin = ...`. The rest of the
      loop (the selection, the demo phase, `loop.drop`, the two release
      lines) is unchanged until the release primitive lands; when it does,
      it replaces the two release lines and this task grows.
- [ ] 3.6 `simulation/loop.py` is untouched: `Loop.drop` is the flexible
      part's shape port, not a forwarding port.

## 4. Evidence again (stage B)

- [ ] 4.1 Re-capture both pose files to `/tmp/fender-bender-after.json`
      and `/tmp/fender-bender-after-instructions.json` and run
      `capture_poses.py compare before after`. Expected: maximum deviation
      0 on every leaf at every pose. A deviation on the five wheels means
      the joint's anchor carried differently from the hand rotation — try
      `at` as a callable returning `(0, 0, bearing_shelf_height)`
      (proposal.md, Joints 1) and record it. A deviation on the pin means
      the relation's sense is wrong.
- [ ] 4.2 Run the three suites again, one at a time: the same tests green
      as the baseline, none newly red. Record the counts. `ChannelTest`
      is the one to read carefully — the standalone wheel no longer turns
      with time (proposal.md, Tests 1).
- [ ] 4.3 Commit as `refactor(simulation): move Fender-Bender onto
      solid-node joints and couplings`, with the pose comparison and the
      test result in the body. Do not sync or archive; the orchestrator
      reviews first.
- [ ] 4.4 Report: the commit hashes, the pose comparison line, the test
      counts before and after, every deviation from the proposal, and
      every test believed to need a change with its reason.
