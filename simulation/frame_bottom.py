from solid_node.node import Build123dNode
from solid_node.parameters import Count, Flag, Length

from . import colors
from .config import bender_config


class BottomFrame(Build123dNode):
    """The upstream standing bottom frame: wall grooves and slots on its
    mating face at Z = 0, the stand rising toward +Z. The frame assembly
    turns it over so the stand meets the table."""

    color = colors.FRAME

    filament_count = Count(5, min=1)
    wheel_diameter = Length(70.0, min=0)
    chamber_depth = Length(370.0, min=0)
    tolerance = Length(0.2, min=0)

    def render(self):
        cfg = bender_config(self.filament_count, self.wheel_diameter,
                            self.chamber_depth, self.tolerance)
        from frame_bottom import BottomFrame as Upstream
        return Upstream(cfg.frame_config).bottom_frame()
