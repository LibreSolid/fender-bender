from solid_node.node import AssemblyNode
from solid_node.parameters import Count, Length

from . import layout
from .config import bender_config
from .frame_bottom import BottomFrame
from .frame_connector import ConnectorFrame
from .frame_top import TopFrame
from .guidewall import Guidewall
from .sidewall import Sidewall


class Frame(AssemblyNode):
    """The buffer's body: top frame, two wall sections (two guide walls,
    two reinforced outer side walls and `filament_count - 1` inner side
    walls each), the connector frame between them, and the standing bottom
    frame. World frame as the root's: the top frame's base face on Z = 0,
    everything else hanging below."""

    filament_count = Count(5, min=1)
    wheel_diameter = Length(70.0, min=0)
    chamber_depth = Length(370.0, min=0)
    tolerance = Length(0.2, min=0)

    inner_walls = 2 * (filament_count - 1)

    top = TopFrame(filament_count=filament_count, wheel_diameter=wheel_diameter,
                   chamber_depth=chamber_depth, tolerance=tolerance)
    connector = ConnectorFrame(filament_count=filament_count,
                               wheel_diameter=wheel_diameter,
                               chamber_depth=chamber_depth, tolerance=tolerance)
    bottom = BottomFrame(filament_count=filament_count,
                         wheel_diameter=wheel_diameter,
                         chamber_depth=chamber_depth, tolerance=tolerance)
    guidewalls = Guidewall(filament_count=filament_count,
                           wheel_diameter=wheel_diameter,
                           chamber_depth=chamber_depth,
                           tolerance=tolerance).repeat(4)
    outer_walls = Sidewall(filament_count=filament_count,
                           wheel_diameter=wheel_diameter,
                           chamber_depth=chamber_depth, tolerance=tolerance,
                           reinforced=True).repeat(4)
    sidewalls = Sidewall(filament_count=filament_count,
                         wheel_diameter=wheel_diameter,
                         chamber_depth=chamber_depth, tolerance=tolerance,
                         reinforced=False).repeat(inner_walls)

    def render(self):
        cfg = bender_config(self.filament_count, self.wheel_diameter,
                            self.chamber_depth, self.tolerance)
        straight = cfg.sidewall_straight_depth
        connector = cfg.frame_connector_depth
        spacing = cfg.frame_bracket_spacing
        wall = cfg.wall_thickness
        count = self.filament_count

        self.connector.translate([0, 0, -(straight + connector)])
        self.bottom.rotate(180, [1, 0, 0])
        self.bottom.translate([0, 0, -(2 * straight + connector)])

        # Guide walls: one per side per section, tongues along Z, the +X
        # side turned the other way so its guides face the chamber.
        gx = cfg.sidewall_width / 2
        for index, guide in enumerate(self.guidewalls):
            section, side = divmod(index, 2)
            sign = -1 if side == 0 else 1
            guide.rotate(90, [0, 0, 1])
            guide.rotate(90 * sign, [0, 1, 0])
            guide.translate([sign * gx, 0,
                             layout.section_z(section, straight, connector)])

        # Side walls stand in their slots. The upper section's walls point
        # their rounded end up into the top frame's core cut; the lower
        # section's are the same part turned over, rounded end down into
        # the bottom frame's core cut, mirrored about the connector's
        # mid-plane. A wall turned +90 about X has its thickness toward -Y
        # from its origin (turned -90, toward +Y); each outer wall is turned
        # so its reinforcement faces outward.
        mirror_z = -(straight + connector / 2)
        for index, outer in enumerate(self.outer_walls):
            section, side = divmod(index, 2)
            z = layout.SIDEWALL_Z if section == 0 else 2 * mirror_z - layout.SIDEWALL_Z
            if section == 0:
                outer.rotate(90, [1, 0, 0])
                if side == 1:
                    outer.rotate(180, [0, 0, 1])
            else:
                outer.rotate(-90, [1, 0, 0])
                if side == 0:
                    outer.rotate(180, [0, 0, 1])
            y = layout.slot_y(0 if side == 0 else count, count, spacing)
            outer.translate([0, y + (wall / 2 if side == 0 else -wall / 2), z])
        for index, inner in enumerate(self.sidewalls):
            section, slot = divmod(index, count - 1)
            y = layout.slot_y(slot + 1, count, spacing)
            if section == 0:
                inner.rotate(90, [1, 0, 0])
                inner.translate([0, y + wall / 2, layout.SIDEWALL_Z])
            else:
                inner.rotate(-90, [1, 0, 0])
                inner.translate([0, y - wall / 2, 2 * mirror_z - layout.SIDEWALL_Z])
