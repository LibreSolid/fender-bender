"""wheel-bearing-fit: the bearing between the bracket's shelves, the wheel
on the bearing. The channel's local frame is the bottom bracket's: base
face on Z = 0, wheel axis on Z.

Expectations are this file's own arithmetic over the design's inputs
(the reference configuration restated in `config`), never a derivation
read off the node.
"""

import numpy as np
import trimesh

from solid_node.test import TestCase

from .contracts import assert_no_interference

from .channel import Channel
from .config import (BEARING_DEPTH, BEARING_SEAT_DIAMETER,
                     WHEEL_LATERAL_TOLERANCE, WHEEL_RADIAL_TOLERANCE)
from .hardware import BEARING_OUTER_DIAMETER

# Inputs restated.
BRACKET_DEPTH = 12.6                     # bearing depth + lateral tol + 2 x 4
SHELF = (BRACKET_DEPTH - BEARING_DEPTH) / 2      # 4.3
BORE_CLEARANCE = (BEARING_SEAT_DIAMETER - BEARING_OUTER_DIAMETER) / 2   # 0.05
LATERAL_PLAY = WHEEL_LATERAL_TOLERANCE / 2       # 0.3 per side
EPS = 0.01


class ChannelTest(TestCase):

    node = Channel

    def parts(self):
        n = self.node
        return n.bottom, n.top, n.wheel, n.bearing

    # -- integrity -----------------------------------------------------

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    def test_assembly_integrity(self):
        # Pairwise on the exact solids: the bottom bracket's STL trips the
        # framework's watertight gate (see `contracts`).
        assert_no_interference(self, self.node)

    # -- the bearing between the shelves ---------------------------------

    def test_bearing_sits_on_the_shelf(self):
        bottom, top, wheel, bearing = self.parts()
        z = bearing.mesh.bounds
        self.assertAlmostEqual(z[0][2], SHELF, delta=EPS)
        self.assertAlmostEqual(z[1][2], SHELF + BEARING_DEPTH, delta=EPS)

    def test_bearing_is_clamped_axially(self):
        bottom, top, wheel, bearing = self.parts()
        # Down onto the shelf, up against the cap's shelf: no axial play.
        self.assertBlockedBeyond(bearing, 0.1, bottom, along=(0, 0, -1),
                                 directions='forward')
        self.assertBlockedBeyond(bearing, 0.1, top, along=(0, 0, 1),
                                 directions='forward')

    def test_bearing_is_located_by_the_posts(self):
        bottom, top, wheel, bearing = self.parts()
        self.assertBlockedBeyond(bearing, 0.1, bottom, along=(1, 0, 0))
        self.assertBlockedBeyond(bearing, 0.1, bottom, along=(0, 1, 0))

    # -- the wheel on the bearing ----------------------------------------

    def test_wheel_turns_freely(self):
        bottom, top, wheel, bearing = self.parts()
        for other in (bearing, bottom, top):
            self.assertFreeWithin(wheel, [45.0, 90.0, 135.0, 180.0], other)

    def test_wheel_is_captured_radially_by_the_bearing(self):
        bottom, top, wheel, bearing = self.parts()
        beyond = BORE_CLEARANCE + 0.05
        self.assertBlockedBeyond(wheel, beyond, bearing, along=(1, 0, 0))
        self.assertBlockedBeyond(wheel, beyond, bearing, along=(0, 1, 0))

    def test_wheel_is_captured_axially_by_the_guides(self):
        bottom, top, wheel, bearing = self.parts()
        beyond = LATERAL_PLAY + 0.1
        self.assertBlockedBeyond(wheel, beyond, bottom, along=(0, 0, -1),
                                 directions='forward')
        self.assertBlockedBeyond(wheel, beyond, top, along=(0, 0, 1),
                                 directions='forward')

    def test_wheel_floats_within_its_lateral_tolerance(self):
        bottom, top, wheel, bearing = self.parts()
        within = LATERAL_PLAY - 0.1
        self.assertFreeWithin(wheel, within, bottom, along=(0, 0, 1))
        self.assertFreeWithin(wheel, within, top, along=(0, 0, 1))

    def test_wheel_rim_clears_the_bracket_by_the_radial_tolerance(self):
        bottom, top, wheel, bearing = self.parts()
        self.assertFar(wheel, bottom, WHEEL_RADIAL_TOLERANCE - EPS)
        # The rim's vertices lie on the true surface: the nearest bracket
        # surface to any of them is the wheel cut, one radial tolerance away.
        rim = wheel.mesh.vertices
        radial = np.hypot(rim[:, 0], rim[:, 1])
        rim = rim[radial > radial.max() - EPS]
        gap = trimesh.proximity.closest_point(bottom.mesh, rim)[1].min()
        self.assertAlmostEqual(gap, WHEEL_RADIAL_TOLERANCE, delta=0.05)
