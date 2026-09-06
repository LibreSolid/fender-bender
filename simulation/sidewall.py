from solid_node.node import Build123dNode
from solid_node.parameters import Count, Flag, Length

from . import colors
from .config import bender_config


class Sidewall(Build123dNode):
    """The upstream side wall separating two chambers, or its reinforced
    outer variant. Returned as built, lying flat on XY, rounded top toward
    +Y, thickness along +Z."""

    color = colors.SIDE_WALL

    filament_count = Count(5, min=1)
    wheel_diameter = Length(70.0, min=0)
    chamber_depth = Length(370.0, min=0)
    tolerance = Length(0.2, min=0)
    reinforced = Flag(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.reinforced:
            self.color = colors.REINFORCED_WALL

    def render(self):
        cfg = bender_config(self.filament_count, self.wheel_diameter,
                            self.chamber_depth, self.tolerance)
        from sidewall import Sidewall as Upstream
        part = Upstream(cfg.sidewall_config)._sidewall(reinforced=self.reinforced)
        return part
