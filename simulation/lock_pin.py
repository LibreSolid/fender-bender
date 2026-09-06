from solid_node.node import Build123dNode
from solid_node.parameters import Count, Flag, Length

from . import colors
from .config import bender_config


class LockPin(Build123dNode):
    """The upstream lock pin with its tie loop, at the printed tolerance.
    Along Y, its loop at +Y, resting on Z = 0."""

    color = colors.PIN

    filament_count = Count(5, min=1)
    tolerance = Length(0.2, min=0)

    def render(self):
        from lock_pin import LockPin as Upstream
        cfg = bender_config(filament_count=self.filament_count,
                            tolerance=self.tolerance)
        return Upstream(cfg.lock_pin_config).lock_pin(
            inset=cfg.frame_lock_pin_tolerance / 2, tie_loop=True)
