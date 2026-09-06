from build123d import Align, Cylinder, Mode

from solid_node.node import Build123dNode

from . import colors
from .config import BEARING_DEPTH, BEARING_POST_DIAMETER
from .hardware import BEARING_OUTER_DIAMETER


class Bearing(Build123dNode):
    """The sourced MR126 bearing each wheel turns on, as a plain ring:
    12.0 mm outside, 4.0 mm wide, bore at the upstream post diameter (see
    `hardware`). Axis on Z, one face on Z = 0."""

    color = colors.BEARING

    def render(self):
        ring = Cylinder(BEARING_OUTER_DIAMETER / 2, BEARING_DEPTH,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))
        bore = Cylinder(BEARING_POST_DIAMETER / 2, BEARING_DEPTH,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))
        return ring - bore
