"""The one Fender-Bender option this simulation builds, as the upstream
``BenderConfig`` the part classes are configured from.

The site's part selector offers flow direction, tubing and connector,
filament count, frame style, wall style and extras. This model fixes one
choice of each and exposes the knobs a maker would still turn as root
parameters:

- flow direction: forward (the channel nearest the frame's back runs
  straight, the front one leans 45 degrees outward);
- tubing: 6 mm OD x 3 mm ID PTFE, no connector (the reference design);
- frame style: standing (no wall hanger; the bottom frame carries a stand);
- wall style: hex (the loops are visible through the walls);
- frame lock: the lock pin alone;
- extras: none (no print-in-place bearing, no surface-mount hanger).

The numbers restated below are the reference build configuration's
(``build-configs/release.conf``) for the wheel, its bearing, the tube and
the pin tolerance; everything else keeps the ``BenderConfig`` defaults, which
match that file. This module defines no node.
"""

from bender_config import BenderConfig
from filament_bracket_config import ConnectorConfig, LockStyle, TubeConfig
from filament_wheel_config import BearingConfig, WheelConfig
from frame_config import FrameStyle
from sidewall_config import WallStyle

# Reference configuration values (release.conf) that BenderConfig() alone
# does not reproduce.
WHEEL_SPOKES = 5
WHEEL_LATERAL_TOLERANCE = 0.6      # mm, total axial play of the wheel
WHEEL_RADIAL_TOLERANCE = 0.2       # mm, wheel rim to bracket cut
BEARING_SEAT_DIAMETER = 12.1       # mm, the wheel bore over the bearing
BEARING_POST_DIAMETER = 6.1        # mm, the bracket post into the bearing
BEARING_SHELF_DIAMETER = 8.5       # mm, the shelf the inner race rests on
BEARING_DEPTH = 4.0                # mm, the bearing width
TUBE_OUTER_DIAMETER = 6.5          # mm, 6 mm PTFE tube plus fit
TUBE_INNER_DIAMETER = 3.6          # mm
CONNECTOR_LENGTH = 6.7             # mm
PIN_TOLERANCE = 0.6                # mm, total play around the lock pin


def bender_config(filament_count=5, wheel_diameter=70.0,
                  chamber_depth=370.0, tolerance=0.2):
    """The upstream configuration for the chosen option at these knobs."""
    cfg = BenderConfig()
    cfg.filament_count = int(filament_count)
    cfg.frame_style = FrameStyle.STANDING
    cfg.wall_style = WallStyle.HEX
    cfg.frame_lock_style = LockStyle.PIN
    cfg.frame_chamber_depth = float(chamber_depth)
    cfg.tolerance = float(tolerance)
    cfg.frame_lock_pin_tolerance = PIN_TOLERANCE
    cfg.wheel = WheelConfig(
        diameter=float(wheel_diameter), spoke_count=WHEEL_SPOKES,
        lateral_tolerance=WHEEL_LATERAL_TOLERANCE,
        radial_tolerance=WHEEL_RADIAL_TOLERANCE,
        bearing=BearingConfig(
            diameter=BEARING_SEAT_DIAMETER,
            inner_diameter=BEARING_POST_DIAMETER,
            shelf_diameter=BEARING_SHELF_DIAMETER,
            depth=BEARING_DEPTH),
    )
    cfg.connectors = [ConnectorConfig(
        name="3mmx6mm tube connector", threaded=False,
        diameter=TUBE_OUTER_DIAMETER, length=CONNECTOR_LENGTH,
        thread_pitch=1, thread_angle=30, thread_interference=0.4,
        tube=TubeConfig(inner_diameter=TUBE_INNER_DIAMETER,
                        outer_diameter=TUBE_OUTER_DIAMETER),
    )]
    return cfg
