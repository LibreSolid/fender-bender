from solid_node.node import Build123dNode
from solid_node.parameters import Count, Flag, Length

from . import colors
from .config import bender_config


class FilamentWheel(Build123dNode):
    """The upstream filament wheel: rim with the diamond groove, five spokes,
    bore for the bearing. Axis on Z, one face on Z = 0."""

    color = colors.WHEEL

    wheel_diameter = Length(70.0, min=0)

    def render(self):
        from filament_wheel import FilamentWheel as Upstream
        cfg = bender_config(wheel_diameter=self.wheel_diameter)
        return Upstream(cfg.wheel).filament_wheel()
