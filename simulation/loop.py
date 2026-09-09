from math import pi

from molejo import Arc, Circle, Line, P, Shape

from solid_node.node import MolejoNode
from solid_node.motion.ports import SignalPort
from solid_node.parameters import Length

from . import colors
from .config import BEARING_DEPTH
from .hardware import FILAMENT_RADIUS
from .layout import loop_radius


class Loop(MolejoNode):
    """The slack filament of one channel: a 1.75 mm filament from the point
    it leaves the wheel groove at axis height on one side, straight down by
    `drop`, round a half circle of the groove's radius, and straight back up
    to the groove on the other side.

    Local frame: origin at the first leg's top, legs along +Z, the second leg
    at +X. The root turns the node over so +Z points down and puts the
    origin on the wheel axis height, one loop radius toward -X of the axis.
    """

    color = colors.FILAMENT

    wheel_diameter = Length(70.0, min=0)

    #: Leg length in mm, bound by the root every instant (never below
    #: `layout.DROP_MIN`).
    drop = SignalPort(unit='mm')

    def render(self):
        r = loop_radius(self.wheel_diameter / 2, BEARING_DEPTH, FILAMENT_RADIUS)
        return Shape(
            profile=Circle(radius=FILAMENT_RADIUS),
            path=[
                Line(to=(0.0, 0.0, P.drop)),
                Arc(center=(r, 0.0, P.drop), axis=(0.0, 1.0, 0.0), angle=pi),
                Line(to=(2.0 * r, 0.0, 0.0)),
            ],
            path_samples=160, profile_samples=12,
        )
