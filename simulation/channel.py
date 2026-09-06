from solid_node.node import AssemblyNode, RotationalPort
from solid_node.parameters import Count, Length

from .bearing import Bearing
from .bracket_bottom import BracketBottom
from .bracket_top import BracketTop
from .config import bender_config
from .filament_wheel import FilamentWheel


class Channel(AssemblyNode):
    """One filament channel's bracket assembly: the bottom bracket, the
    bearing on its shelf, the wheel on the bearing, and the top cap turned
    over onto it. Local frame is the bottom bracket's: base face on Z = 0,
    wheel axis on Z, depth along +Z. The root turns it upright and seats it.
    """

    filament_count = Count(5, min=1)
    wheel_diameter = Length(70.0, min=0)
    chamber_depth = Length(370.0, min=0)
    tolerance = Length(0.2, min=0)

    #: Wheel angle in degrees, bound by the root. Unbound (a channel built
    #: on its own) the wheel turns once per timeline cycle so the part
    #: stays testable alone; that fallback is stated here so it is not
    #: mistaken for a wiring default.
    spin = RotationalPort(unit='deg')

    bottom = BracketBottom(filament_count=filament_count,
                           wheel_diameter=wheel_diameter,
                           chamber_depth=chamber_depth, tolerance=tolerance)
    top = BracketTop(filament_count=filament_count,
                     wheel_diameter=wheel_diameter,
                     chamber_depth=chamber_depth, tolerance=tolerance)
    wheel = FilamentWheel(wheel_diameter=wheel_diameter)
    bearing = Bearing()

    def render(self):
        cfg = bender_config(self.filament_count, self.wheel_diameter,
                            self.chamber_depth, self.tolerance)
        shelf = cfg.bearing_shelf_height
        self.wheel.translate([0, 0, shelf])
        self.bearing.translate([0, 0, shelf])
        self.top.rotate(180, [0, 1, 0])
        self.top.translate([0, 0, cfg.bracket_depth])

    def simulate(self):
        angle = self.spin.value
        if angle is None:
            angle = 360.0 * self.time
        self.wheel.rotate(angle, [0, 0, 1])
