## 1. Environment, manifest and configuration

- [x] 1.1 Project venv with solid-node (workspace checkout), build123d 0.10, partomatic 0.7.0, fb-library, bd_warehouse 0.2.0, ocp_vscode, molejo; same pins in the shop venv the floor builds with; `.gitignore` covers `_build*`
- [x] 1.2 `pyproject.toml` naming `simulation.fender_bender:FenderBender`; `simulation/__init__.py` making `src/` importable; `simulation/config.py` building the upstream `BenderConfig` for the chosen option from the root knobs; `simulation/layout.py` and `simulation/kinematics.py` skeletons
- [x] 1.3 Root `FenderBender` declaring the four parameters, `check()` guards (filament count, slack range against chamber depth) with red-then-green assertRaises tests, and one imported part (the top frame) so the browser shows something from the first build

## 2. Channel: bracket, cap, wheel, bearing (wheel-bearing-fit)

- [x] 2.1 `BracketBottom`, `BracketTop`, `FilamentWheel` leaves importing the upstream parts; `Bearing` leaf from the bill of materials; `Channel` assembly with the bearing first placed 1 mm high so the shelf contract fails
- [x] 2.2 Write the bearing clamp, post capture, wheel bore capture, wheel lateral capture and float, and full-revolution contracts in `test_channel.py`; watch them fail; seat the bearing and wheel; green

## 3. Frame and walls (wall-frame-joint)

- [x] 3.1 `TopFrame`, `ConnectorFrame`, `BottomFrame`, `Guidewall`, `Sidewall` (with a `reinforced` Flag) leaves; `Frame` assembly with walls at the upstream debug offsets (which interfere on the standing frame) so the stack contract fails
- [x] 3.2 Write the stack interference, tongue capture, slot capture and support contracts in `test_frame.py`; measure the interference-free offsets; record them in `layout.py`; green; prove the three-channel build

## 4. Seat, pin and release path (bracket-frame-seat)

- [x] 4.1 Wire channels and the `LockPin` into the root at rest; write the pocket capture and float, pin channel, pin-blocks-lift and drawn-pin-frees contracts in `test_fender_bender.py`; watch the lift contracts fail with a straight lift
- [x] 4.2 Probe and state the release path in `kinematics.release_pose`; gate the lift on the pin; sweep contract green; instructions `Unlock`/`Lock`/`Lift bracket`/`Seat bracket`

## 5. Filament loop and demonstration (filament-buffer-loop)

- [x] 5.1 `Loop` molejo leaf with `drop` port, placed at the wheel groove; taut-loop clearance and chamber sweep contracts red first (loop first placed at the wheel rim radius so it fouls the wheel), then green
- [x] 5.2 Root `channel`/`slack` drivers, wheel spin coupling, timeline wave per channel, `Retract`/`Feed` instructions; selection, spin and timeline contracts; scenario test triggering the instructions with interference checked on a cadence

## 6. Integrity, evidence and record

- [x] 6.1 Root integrity contracts swept over the timeline; mutation check (drop the pin gate, shift a wall offset, use the rim radius for the loop) noting which contract catches each; full faceted regression then the exact run
- [x] 6.2 `solid build`; read `viewer.json` (drivers, instructions, pieces incl. counts of repeated channels); snapshots at rest, mid-retract, and bracket lifted; inspect
- [x] 6.3 README section: option chosen, environment pins, what is sourced and what is not modelled, drivers and instructions, upstream findings; archive the change, fill each spec's Purpose, commit
