from solid_node.node import Build123dNode
from solid_node.parameters import Count, Length

from . import colors
from .config import bender_config


class TopFrame(Build123dNode):
    """The upstream top frame: the brackets' pockets, the upper wall
    grooves and slots. Returned as the upstream generator builds it, base
    face on Z = 0 and the bracket axis at the frame base depth."""

    color = colors.FRAME

    filament_count = Count(5, min=1)
    wheel_diameter = Length(70.0, min=0)
    chamber_depth = Length(370.0, min=0)
    tolerance = Length(0.2, min=0)

    def render(self):
        from frame_top import TopFrame as Upstream
        cfg = bender_config(self.filament_count, self.wheel_diameter,
                            self.chamber_depth, self.tolerance)
        return Upstream(cfg.frame_config).top_frame()
