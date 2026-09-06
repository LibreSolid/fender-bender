from solid_node.node import Build123dNode
from solid_node.parameters import Count, Flag, Length

from . import colors
from .config import bender_config


class Guidewall(Build123dNode):
    """The upstream guide wall: the hex-windowed wall along a chamber
    section with the tongues that enter the frame grooves. Returned as
    built, lying flat on XY with its tongues along Y."""

    color = colors.GUIDE_WALL

    filament_count = Count(5, min=1)
    wheel_diameter = Length(70.0, min=0)
    chamber_depth = Length(370.0, min=0)
    tolerance = Length(0.2, min=0)

    def render(self):
        cfg = bender_config(self.filament_count, self.wheel_diameter,
                            self.chamber_depth, self.tolerance)
        from guidewall import Guidewall as Upstream
        return Upstream(cfg.guidewall_config).build_guidewall()
