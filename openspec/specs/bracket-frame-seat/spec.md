# bracket-frame-seat Specification

## Purpose

The filament bracket in the top frame: the pocket it seats in, the fit tolerance around it, the lock pin that holds it, and the release path along which it is lifted out and reseated.

## Requirements
### Requirement: A filament bracket seats in the top frame on the fit tolerance
Each filament bracket SHALL sit in its own pocket of the top frame with the
bracket's wheel axis horizontal and level with the frame's bracket axis, the
bracket centred on its channel pitch (default 16.0 mm between channels),
and the upstream fit tolerance (default 0.2 mm) as the only gap between the
bracket's curved flanks and the pocket. Every bracket, its wheel, its bearing
and its top cap SHALL share no volume with the frame or with a neighbouring
channel's parts at rest.

#### Scenario: Brackets rest in their pockets without interference
- **WHEN** the buffer is built at the default parameters with every bracket seated
- **THEN** no bracket part shares volume with the top frame, the walls, the lock pin or another bracket

#### Scenario: A seated bracket is held sideways by its pocket
- **WHEN** a seated bracket is displaced 0.3 mm along the wheel axis in either sense
- **THEN** it interferes with the top frame

#### Scenario: A seated bracket floats within the tolerance on its open side
- **WHEN** a seated bracket is displaced 0.1 mm along the wheel axis toward the frame's -Y side
- **THEN** it shares no volume with the top frame (finding: toward +Y the rear corner of the bracket's lower channel block sits 0.04 mm from the frame, so the fit tolerance is one-sided there and 0.1 mm already interferes)

### Requirement: The lock pin holds every seated bracket
The lock pin SHALL run through the top frame's pin channel and every seated
bracket's pin channel along the channel axis, with the upstream pin tolerance
(default 0.6 mm, 0.3 mm per side) as its clearance, and its tie loop SHALL
stand outside the frame on the side the pin is drawn from. While the pin is
home, a bracket SHALL be blocked from lifting; with the pin drawn fully out of
the frame, the bracket SHALL be free to lift.

#### Scenario: The home pin clears its channels
- **WHEN** the pin is home
- **THEN** it shares no volume with the frame or any bracket, and it is held vertically in a bracket's pin channel: displacing it 0.5 mm up or down interferes with the bracket (finding: along the frame's long axis the upstream channel leaves the pin more than 2 mm of play, so it is not held that way)

#### Scenario: The home pin blocks a lift
- **WHEN** the pin is home and a bracket is lifted 1.0 mm along its release path
- **THEN** the bracket interferes with the pin

#### Scenario: The drawn pin frees the bracket
- **WHEN** the pin is drawn 100 mm out along its axis
- **THEN** the pin shares no volume with any part, and a bracket lifted 1.0 mm along its release path shares no volume with the pin

### Requirement: A bracket is removed along the frame's release path
A bracket SHALL leave and re-enter its pocket along a stated release path
that the frame admits without interference: the motion the upstream usage
instructions describe (forward and up out of the pocket, back and down to
click in). The model SHALL drive that path from one `lift` value, 0 at the
seated position and increasing as the bracket leaves, and SHALL refuse to
move a bracket while the pin is not drawn.

#### Scenario: The release path clears the frame
- **WHEN** the pin is drawn and the selected bracket's `lift` is swept from 0 to its full range in at least 10 steps
- **THEN** at every step the bracket's wheel and bearing share no volume with the frame, no part of the bracket shares volume with the walls, the pin or the other brackets, the bracket body shares with the top frame no more than the click-fit detent's volume (the frame's two 0.75 mm spheres, 3.6 mm³), and the cap shares with the top frame no more than 1.5 mm³ (finding: the upstream pocket admits no rigid interference-free release; its retaining rim needs 8 mm of forward shift during the tilt while its narrow base allows 5.8 mm, so the least-interference path measured kisses the base's front wall by 1.2 mm³, within the real part's 0.2 mm print tolerance and flex)

#### Scenario: The bracket ends clear of the frame
- **WHEN** `lift` is at its full range with the pin drawn
- **THEN** the bracket's lowest point is above the top frame's highest point

#### Scenario: The bracket cannot move against a home pin
- **WHEN** the pin is home and `lift` is set to its full range
- **THEN** the selected bracket stays seated and shares no volume with the pin
