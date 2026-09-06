# filament-buffer-loop Specification

## Purpose

The slack filament of one channel: where it hangs between the walls of its chamber, how much slack the chamber admits, how the wheel turns with it, and how the drivers and timeline select and demonstrate it.

## Requirements
### Requirement: The slack filament hangs in its own chamber
Each channel SHALL carry one 1.75 mm filament modelled from where it leaves
the bracket's channels, around the lower half of the wheel in the wheel's
groove, and down into the chamber as a U-shaped loop whose two legs hang
from the wheel and whose depth below the wheel axis is the channel's slack plus a
0.5 mm minimum leg (so the path never degenerates; 0 mm slack is the taut
filament on the wheel). The loop SHALL lie in the
plane of its wheel, midway between the side walls of its chamber, and at
every slack in the driver's range it SHALL share no volume with the wheel,
the bracket, the walls or the frames.

#### Scenario: A taut filament clears the wheel groove
- **WHEN** a channel's slack is 0 mm
- **THEN** its loop shares no volume with the wheel or the bracket and its nearest point to the wheel is within 1.0 mm of it

#### Scenario: The loop stays inside its chamber through the slack range
- **WHEN** the selected channel's slack is swept from 0 mm to the full slider range in at least 8 steps
- **THEN** at every step the loop shares no volume with any wall, frame, bracket or wheel

#### Scenario: The slack range fits the chamber
- **WHEN** the model is built at parameters that leave the full slack range less than 5 mm above the bottom frame
- **THEN** construction is refused naming the slack the chamber admits

### Requirement: The wheel turns with the filament
When a channel's slack changes, the wheel SHALL turn by the length of
filament that passed over it: twice the slack change divided by the wheel
radius, in radians, since both legs of the loop lengthen together.

#### Scenario: Slack turns the wheel
- **WHEN** the selected channel's slack is set to half the wheel radius
- **THEN** that wheel has turned one radian (57.3 degrees) from its rest position and the other wheels have not turned

### Requirement: Channel selection and the timeline demonstration
The `channel` driver SHALL select which channel the `slack` and `lift`
drivers act on, 0 being the channel at the negative end of the channel
axis; the timeline SHALL run every channel in turn through a retract-and-
feed cycle in which its slack rises to 150 mm and returns to 0 mm.

#### Scenario: Only the selected channel moves
- **WHEN** `channel` is 2 and `slack` is 100 mm at time 0
- **THEN** channel 2's loop hangs 100 mm and every other loop hangs 0 mm

#### Scenario: The timeline visits every channel
- **WHEN** time is swept through one cycle at 5 x `filament_count` samples
- **THEN** each channel's loop reaches at least 140 mm of slack in its slice and returns to 0 mm, and no two solids share volume at any sample
