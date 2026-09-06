from solid_node.node import AssemblyNode
from solid_node.parameters import Count, Length
from solid_node.simulation import Driver, Instruction

from . import kinematics, layout
from .channel import Channel
from .config import BEARING_DEPTH, bender_config
from .frame import Frame
from .hardware import FILAMENT_RADIUS
from .lock_pin import LockPin
from .loop import Loop

#: The `slack` slider's range (mm). A range is presentation metadata and
#: cannot follow the parameters; `check()` refuses a buffer whose chamber
#: cannot take this much slack.
SLACK_RANGE = (0.0, 190.0)
LOOP_FLOOR_MARGIN = 5.0     # mm the deepest loop keeps above the bottom frame


class FenderBender(AssemblyNode):
    """One complete Fender-Bender filament buffer in the standing, hex-wall,
    pin-locked, 6 mm tube configuration, assembled from the upstream part
    generators.

    World frame: the upstream top frame's. X along the frame's long side
    (the plane the wheels turn in), Y along the channel axis, Z up, origin
    at the top frame's base face. Every seated wheel axis lies at Z = the
    frame base depth; the walls hang below Z = 0 to the bottom frame, which
    stands on the table.
    """

    filament_count = Count(5, min=1)
    wheel_diameter = Length(70.0, min=0)
    chamber_depth = Length(370.0, min=0)
    tolerance = Length(0.2, min=0)

    frame = Frame(filament_count=filament_count, wheel_diameter=wheel_diameter,
                  chamber_depth=chamber_depth, tolerance=tolerance)
    channels = Channel(filament_count=filament_count,
                       wheel_diameter=wheel_diameter,
                       chamber_depth=chamber_depth,
                       tolerance=tolerance).repeat(filament_count)
    loops = Loop(wheel_diameter=wheel_diameter).repeat(filament_count)
    pin = LockPin(filament_count=filament_count, tolerance=tolerance)

    #: Which channel `slack` and `lift` act on, 0 at the -Y end. The range
    #: is stated for the default five channels (a symbolic range cannot be
    #: published); a wider buffer is driven past the slider by value.
    channel = Driver(default=0, range=(0, 4), dtype=int)
    #: Filament slack hanging below the wheel axis in the selected channel.
    slack = Driver(default=0.0, range=SLACK_RANGE, unit='mm')
    #: The selected bracket's travel along the release path; ignored while
    #: the pin is home.
    lift = Driver(default=0.0, range=(0.0, kinematics.LIFT_MAX), unit='mm')
    #: How far the lock pin is drawn out toward +Y.
    pin_draw = Driver(default=0.0, range=(0.0, 100.0), unit='mm')

    instructions = {
        'Retract': Instruction({'slack': kinematics.DEMO_SLACK}, duration=2.0),
        'Feed': Instruction({'slack': 0.0}, duration=2.0),
        'Unlock': Instruction({'pin_draw': 100.0}, duration=1.5),
        'Lock': Instruction({'pin_draw': 0.0}, duration=1.5),
        'Lift bracket': Instruction({'lift': kinematics.LIFT_MAX}, duration=2.0),
        'Seat bracket': Instruction({'lift': 0.0}, duration=2.0),
    }

    def check(self):
        cfg = self._config()
        floor = -(2 * cfg.sidewall_straight_depth + cfg.frame_connector_depth)
        deepest = (cfg.frame_base_depth - layout.DROP_MIN - SLACK_RANGE[1]
                   - self.loop_radius - FILAMENT_RADIUS)
        room = deepest - floor
        if room < LOOP_FLOOR_MARGIN:
            admitted = SLACK_RANGE[1] + room - LOOP_FLOOR_MARGIN
            raise ValueError(
                f"FenderBender: a {cfg.frame_chamber_depth} mm chamber admits "
                f"{admitted:.1f} mm of slack, less than the {SLACK_RANGE[1]} mm "
                f"the slack slider offers (loop bottom {room:.1f} mm above the "
                f"bottom frame, {LOOP_FLOOR_MARGIN} mm needed)")

    @property
    def loop_radius(self):
        """Wheel axis to filament centre in the groove (a plain number;
        the algebra refuses adding a bare constant to a Length token)."""
        return layout.loop_radius(self.wheel_diameter / 2, BEARING_DEPTH,
                                  FILAMENT_RADIUS)

    def _config(self):
        return bender_config(self.filament_count, self.wheel_diameter,
                             self.chamber_depth, self.tolerance)

    def render(self):
        cfg = self._config()
        base = cfg.frame_base_depth
        depth = cfg.bracket_depth
        spacing = cfg.frame_bracket_spacing
        for index, channel in enumerate(self.channels):
            y = layout.channel_y(index, self.filament_count, spacing)
            channel.rotate(90, [1, 0, 0])
            channel.translate([0, y + depth / 2, base])
        for index, loop in enumerate(self.loops):
            y = layout.channel_y(index, self.filament_count, spacing)
            loop.rotate(180, [1, 0, 0])
            loop.translate([-self.loop_radius, y, base])
        self.pin.translate([cfg.lock_pin_point.x, 0,
                            cfg.lock_pin_point.y + base
                            + cfg.frame_lock_pin_tolerance / 2])

    def simulate(self):
        radius = self.wheel_diameter / 2
        gate = kinematics.lift_gate(self.pin_draw)
        for index, (channel, loop) in enumerate(zip(self.channels, self.loops)):
            selected = kinematics.indicator(self.channel, index)
            slack = (selected * self.slack
                     + kinematics.demo_slack(self.time, self.filament_count, index))
            loop.drop = layout.DROP_MIN + slack
            channel.spin = kinematics.wheel_angle(slack, radius)
            dx, dz, tilt = kinematics.release_pose(selected * self.lift * gate)
            # The channel's local frame is turned +90 about X at rest: world
            # Y is local -Z and world Z is local +Y.
            channel.rotate(-tilt, [0, 0, 1])
            channel.translate([dx, dz, 0])
        self.pin.translate([0, self.pin_draw, 0])
