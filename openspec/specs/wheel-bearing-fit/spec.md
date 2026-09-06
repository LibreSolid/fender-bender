# wheel-bearing-fit Specification

## Purpose

The wheel, its sourced MR126 bearing and the bracket's bearing shelves: the clamp that locates the bearing and the clearances that let the wheel spin.

## Requirements
### Requirement: The bearing is clamped between the bracket's two shelves
The sourced bearing (MR126: 12.0 mm outside diameter, 4.0 mm wide) SHALL
sit on the bottom bracket's bearing shelf with its axis on the wheel axis,
its lower face on the shelf at the upstream bearing shelf height (default
4.3 mm above the bracket's base face) and its upper face against the top
cap's shelf, so that the two shelves hold it with no axial play. The
bracket's posts SHALL enter the bearing bore from each side by the upstream
post length (default 1.4 mm). The bearing bore SHALL be modelled at the
upstream post diameter (default 6.1 mm), so that the post-to-bore press fit
the upstream design intends is represented as contact and never as shared
volume.

#### Scenario: The bearing rests on the shelf and under the cap
- **WHEN** the bracket is assembled at the default parameters
- **THEN** the bearing shares no volume with the bottom bracket or the top cap, and displacing it 0.1 mm along its axis in either sense interferes with one of them

#### Scenario: The bearing is located radially by the posts
- **WHEN** the bearing is displaced 0.1 mm perpendicular to its axis in either sense along either perpendicular direction
- **THEN** it interferes with a bracket post

### Requirement: The wheel spins on the bearing inside the bracket
The wheel bore SHALL close over the bearing's outside diameter with the
upstream bore clearance (default 12.1 mm bore over a 12.0 mm bearing, 0.05
mm per side), the wheel SHALL sit at the bearing's axial position with the
upstream lateral tolerance split evenly to each wheel guide (default 0.6 mm,
0.3 mm per side), and the wheel rim SHALL clear the bracket's wheel cut by
the upstream radial tolerance (default 0.2 mm). The wheel SHALL turn freely
about the bearing axis.

#### Scenario: The wheel turns freely through a full revolution
- **WHEN** the wheel is rotated to 0, 45, 90, 135 and 180 degrees about its axis
- **THEN** at each angle it shares no volume with the bearing, the bottom bracket or the top cap

#### Scenario: The wheel is captured radially by the bearing
- **WHEN** the wheel is displaced 0.1 mm perpendicular to its axis in either sense along either perpendicular direction
- **THEN** it interferes with the bearing

#### Scenario: The wheel is captured axially by the guides
- **WHEN** the wheel is displaced 0.4 mm along its axis in either sense
- **THEN** it interferes with the bottom bracket or the top cap

#### Scenario: The wheel floats within its lateral tolerance
- **WHEN** the wheel is displaced 0.2 mm along its axis in either sense
- **THEN** it shares no volume with the bottom bracket or the top cap
