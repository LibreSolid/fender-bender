"""wall-frame-joint: the frames and walls stacked into one closed buffer.
World frame: the top frame's base face on Z = 0, walls below.

The guide walls' click-fit bumps overlap their pockets at rest in the
upstream nominal geometry (the guide wall is 1.5 mm shorter than the gap
between frames, so each bump sits 0.65 mm off its pocket and shares about
1.1 mm³ with the frame). That is the upstream snap fit, recorded as a
finding, not hidden: the interference contract parks the guide walls out of
the way for the whole-stack check and bounds each guide wall / frame pair
by the measured snap volume separately.
"""

from solid_node.test import TestCase


from .frame import Frame

FAR_AWAY = [0, 0, 5000.0]
GUIDEWALL_SNAP = 2.5        # mm³ per guide wall / frame pair (measured 2.26)
STRAIGHT = 125.07           # sidewall straight depth for a 370 mm chamber
CONNECTOR = 9.0             # 2 x tongue depth + minimum thickness
EPS = 0.05


class FrameTest(TestCase):

    node = Frame

    def parked_guidewalls(self):
        """Move the guide walls far away for a whole-stack check."""
        for guide in self.node.guidewalls:
            guide.save_checkpoint()
            guide.translate(FAR_AWAY)

    def unpark_guidewalls(self):
        for guide in self.node.guidewalls:
            guide.restore_checkpoint()

    def frames(self):
        return self.node.top, self.node.connector, self.node.bottom

    # -- integrity -----------------------------------------------------

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    def test_assembly_integrity(self):
        self.parked_guidewalls()
        try:
            self.assertNoSolidInterference(self.node)
        finally:
            self.unpark_guidewalls()
        for guide in self.node.guidewalls:
            for frame in self.frames():
                self.assertIntersectVolumeBelow(guide, frame, GUIDEWALL_SNAP)
            for wall in list(self.node.outer_walls) + list(self.node.sidewalls):
                self.assertNotIntersecting(guide, wall)

    # -- the stack --------------------------------------------------------

    def test_stack_heights(self):
        top, connector, bottom = self.frames()
        self.assertAlmostEqual(connector.mesh.bounds[1][2], -STRAIGHT, delta=EPS)
        self.assertAlmostEqual(connector.mesh.bounds[0][2],
                               -STRAIGHT - CONNECTOR, delta=EPS)
        self.assertAlmostEqual(bottom.mesh.bounds[1][2],
                               -2 * STRAIGHT - CONNECTOR, delta=EPS)

    def test_guidewall_tongues_are_captured_in_their_grooves(self):
        top, connector, bottom = self.frames()
        upper, lower = self.node.guidewalls[0], self.node.guidewalls[2]
        self.assertBlockedBeyond(upper, 0.5, top, along=(1, 0, 0))
        self.assertBlockedBeyond(upper, 0.5, connector, along=(1, 0, 0))
        self.assertBlockedBeyond(lower, 0.5, bottom, along=(1, 0, 0))

    def test_sidewalls_are_captured_in_their_slots(self):
        top, connector, bottom = self.frames()
        upper_inner = self.node.sidewalls[0]
        lower_inner = self.node.sidewalls[len(self.node.sidewalls) // 2]
        self.assertBlockedBeyond(upper_inner, 0.5, top, along=(0, 1, 0))
        self.assertBlockedBeyond(lower_inner, 0.5, bottom, along=(0, 1, 0))
        # Finding: the connector frame does not locate a side wall. Its
        # flat sidewall cut is shallower and wider than the wall's ridge,
        # so the wall's plain end merely rests there (measured free to
        # 1.7 mm either way); the core-cut frames alone hold the walls.
        self.assertFreeWithin(upper_inner, 1.5, connector, along=(0, 1, 0))
        self.assertBlockedBeyond(self.node.outer_walls[0], 0.5, top,
                                 along=(0, 1, 0))
        self.assertBlockedBeyond(self.node.outer_walls[1], 0.5, top,
                                 along=(0, 1, 0))

    def test_wall_count_follows_the_filament_count(self):
        self.assertEqual(len(self.node.sidewalls), 8)
        self.assertEqual(len(self.node.outer_walls), 4)
        three = Frame(filament_count=3)
        three.assemble()
        three.build_stls()
        self.assertEqual(len(three.sidewalls), 4)
        self.assertEqual(len(three.outer_walls), 4)
        for guide in three.guidewalls:
            guide.translate(FAR_AWAY)
        self.assertNoSolidInterference(three)
