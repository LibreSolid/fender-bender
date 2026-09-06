from solid_node.node import Build123dNode
from solid_node.parameters import Count, Flag, Length

from . import colors
from .config import bender_config


class BracketTop(Build123dNode):
    """The upstream top bracket, the cap that slides into the bottom bracket
    and clamps the bearing. Returned as built, to be turned over onto the
    bottom bracket."""

    color = colors.BRACKET_TOP

    filament_count = Count(5, min=1)
    wheel_diameter = Length(70.0, min=0)
    chamber_depth = Length(370.0, min=0)
    tolerance = Length(0.2, min=0)

    def render(self):
        cfg = bender_config(self.filament_count, self.wheel_diameter,
                            self.chamber_depth, self.tolerance)
        from filament_bracket import FilamentBracket as Upstream
        return Upstream(cfg.filament_bracket_config(0)).top_bracket()
