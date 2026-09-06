## ADDED Requirements

### Requirement: The frames and walls stack into one closed buffer
The buffer SHALL stack, from the top down: the top frame; an upper wall
section of two guide walls and the side walls; the connector frame; a lower
wall section identical to the upper; and the standing bottom frame. Each
guide wall's tongues SHALL enter the grooves of the frame above and the
frame below it, each side wall SHALL stand in its wall slot in both frames,
and the section height SHALL be the upstream straight sidewall depth
(default 125.07 mm for a 370 mm chamber depth). No two of these solids
SHALL share volume.

#### Scenario: The stack is interference-free
- **WHEN** the buffer is built at the default parameters
- **THEN** no frame or wall shares volume with any other frame, wall, bracket, pin or filament loop, except each guide wall with the two frames it spans, whose click-fit bumps share no more than 2.5 mm³ with each frame (finding: the upstream guide wall is 1.5 mm shorter than the gap between frames, so each 0.75 mm bump sits 0.65 mm off its pocket and overlaps it by 1.1 mm³; the snap fit is recorded, not hidden)

#### Scenario: Guide wall tongues are captured in their grooves
- **WHEN** a guide wall is displaced 0.5 mm along the frame's long axis in either sense
- **THEN** it interferes with the top frame or the connector frame

#### Scenario: Side walls are captured in their slots
- **WHEN** an inner side wall is displaced 0.5 mm along the channel axis in either sense
- **THEN** it interferes with the core-cut frame it stands in (the top frame for the upper section, the bottom frame for the lower), while the connector frame, whose flat sidewall cut is wider than the wall's ridge, leaves it free to 1.5 mm either way (finding: the connector does not locate the side walls)

### Requirement: The standing buffer stands on its bottom frame
With the standing frame option the assembled buffer SHALL rest on the
bottom frame's stand under gravity: every printed and sourced solid rests,
directly or through others, on the stand, and the assembly balances on the
stand's footprint. The bearing, clamped between shelves, and the filament
loops, held by the wheels, SHALL be declared as the press and hold supports
the geometry cannot prove.

#### Scenario: The buffer is supported on its stand
- **WHEN** the buffer is built at the default parameters, pin home, every bracket seated
- **THEN** the assembly is supported under gravity with the bottom frame as ground

### Requirement: The wall count follows the filament count
The buffer SHALL hold `filament_count` channels (default 5): each wall
section has `filament_count - 1` inner side walls and two reinforced outer
side walls, and every frame has `filament_count` pockets or chamber cuts.
A filament count under 1 SHALL be refused before any part is built.

#### Scenario: A three channel buffer
- **WHEN** the model is built with `filament_count` 3
- **THEN** it holds three brackets, three loops, two inner side walls per section and two reinforced side walls per section, and the stack is interference-free
