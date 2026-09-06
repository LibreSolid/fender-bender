from solid_node.node import Build123dNode
from solid_node.parameters import Count, Flag, Length

from . import colors
from .config import bender_config


class ConnectorFrame(Build123dNode):
    """The upstream connector frame between the two wall sections: grooves
    and slots on both faces, chamber cuts through. Returned as built, one
    face on Z = 0, the other at the connector depth."""

    color = colors.FRAME

    filament_count = Count(5, min=1)
    wheel_diameter = Length(70.0, min=0)
    chamber_depth = Length(370.0, min=0)
    tolerance = Length(0.2, min=0)

    def render(self):
        cfg = bender_config(self.filament_count, self.wheel_diameter,
                            self.chamber_depth, self.tolerance)
        from frame_connector import ConnectorFrame as Upstream
        return Upstream(cfg.frame_config).connector_frame()
