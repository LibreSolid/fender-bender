"""The whole buffer: bracket-frame-seat and filament-buffer-loop, plus
the root integrity and support contracts. World frame: the top frame's
base face on Z = 0, wheel axes at Z = 8, walls below.

See `test_frame` for why the guide walls are parked during the whole-model
interference check. The bracket release path crosses the top frame's two
click-fit spheres (0.75 mm radius), so along that path the bracket body is
bounded by their volume; every other pair stays at zero.
"""

import math

import numpy as np
import trimesh

from solid_node.simulation import ScenarioTest
from solid_node.test import TestCase, testing_steps

from .contracts import assert_no_interference

from .fender_bender import SLACK_RANGE, FenderBender
from .kinematics import DEMO_SLACK, LIFT_MAX

# Inputs restated (the reference configuration at the default knobs).
COUNT = 5
SPACING = 16.0                     # bracket depth 12.6 + wall 3 + 2 x 0.2
BASE = 8.0                         # frame base depth: tongue 4 + structural 4
WHEEL_R = 35.0
GROOVE = 2.0                       # bearing depth / 2
FILAMENT_R = 0.875
LOOP_R = WHEEL_R - GROOVE + FILAMENT_R * math.sqrt(2) + 0.1     # 34.337
DROP_MIN = 0.5
TOLERANCE = 0.2
PIN_TOLERANCE = 0.6
DETENT = 2 * 4.0 / 3.0 * math.pi * 0.75 ** 3                     # 3.53 mm³
# Finding: the upstream pocket admits no rigid interference-free release.
# Its retaining rim needs the bracket at least 8 mm forward while it tilts
# out, and the narrow base of the pocket stops the bracket's lower channel
# block at 5.8 mm forward. The stated path is the least-interference one
# measured: the bracket body crosses the click-fit spheres (bounded by
# DETENT, measured 3.2 mm³) and the cap kisses the narrow base's front
# wall (measured 1.2 mm³). The real part has 0.2 mm of print tolerance and
# flexes; the model records the kiss rather than hiding it.
RELEASE_KISS = 1.5
GUIDEWALL_SNAP = 2.5
FAR_AWAY = [0, 0, 5000.0]
EPS = 0.05


def channel_y(index):
    return (index - (COUNT - 1) / 2.0) * SPACING


class FenderBenderTest(TestCase):

    def tearDown(self):
        self.node.set_state(channel=0, slack=0.0, lift=0.0, pin_draw=0.0)

    # -- helpers ------------------------------------------------------------

    def parked_guidewalls(self):
        for guide in self.node.frame.guidewalls:
            guide.save_checkpoint()
            guide.translate(FAR_AWAY)

    def unpark_guidewalls(self):
        for guide in self.node.frame.guidewalls:
            guide.restore_checkpoint()

    def channel_solids(self, index):
        c = self.node.channels[index]
        return c.bottom, c.top, c.wheel, c.bearing

    def loop_bottom(self, index):
        return self.node.loops[index].mesh.bounds[0][2]

    # -- integrity -----------------------------------------------------

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    @testing_steps(6)
    def test_assembly_integrity(self):
        self.parked_guidewalls()
        try:
            assert_no_interference(self, self.node)
        finally:
            self.unpark_guidewalls()
        frames = (self.node.frame.top, self.node.frame.connector,
                  self.node.frame.bottom)
        for guide in self.node.frame.guidewalls:
            for frame in frames:
                self.assertIntersectVolumeBelow(guide, frame, GUIDEWALL_SNAP)
            for index in range(COUNT):
                for solid in self.channel_solids(index):
                    self.assertNotIntersecting(guide, solid)
                self.assertNotIntersecting(guide, self.node.loops[index])

    # Gap: `assertAssemblySupported(self.node)` cannot run on this model.
    # The framework reads every printed solid through a Manifold cache and
    # refuses the upstream frames' and walls' STLs, which trimesh calls
    # non-watertight (T-junctions between tessellated faces) although
    # Manifold accepts them with matching volumes. The wall-frame-joint
    # support requirement is therefore unverified until the framework's
    # watertight gate trusts Manifold's verdict; recorded in the design.

    # -- bracket-frame-seat -----------------------------------------------

    def test_brackets_sit_on_their_channel_pitch(self):
        for index in range(COUNT):
            bottom = self.channel_solids(index)[0]
            lo, hi = bottom.mesh.bounds
            self.assertAlmostEqual((lo[1] + hi[1]) / 2, channel_y(index), delta=EPS)
            # The wheel axis is at the frame base depth.
            wheel = self.channel_solids(index)[2]
            wlo, whi = wheel.mesh.bounds
            self.assertAlmostEqual((wlo[2] + whi[2]) / 2, BASE, delta=EPS)

    # A bracket leaf carries no operations of its own, so a perturbation on
    # it is expressed in the channel's frame, which the root turns +90 about
    # X: channel +Y is world +Z (up), channel +Z is world -Y (across).
    UP = (0, 1, 0)
    ACROSS = (0, 0, 1)

    def test_bracket_is_held_sideways_by_its_pocket(self):
        bottom = self.channel_solids(2)[0]
        self.assertBlockedBeyond(bottom, TOLERANCE + 0.1, self.node.frame.top,
                                 along=self.ACROSS)
        # Finding: the float is one-sided. Toward -Y (channel +Z) the
        # bracket has its 0.2 mm; toward +Y the rear corner of its lower
        # channel block sits 0.04 mm from the frame (exact), so it is
        # blocked there already at 0.1 mm.
        self.assertFreeWithin(bottom, TOLERANCE - 0.1, self.node.frame.top,
                              along=self.ACROSS, directions='forward')
        self.assertBlockedBeyond(bottom, 0.1, self.node.frame.top,
                                 along=(0, 0, -1), directions='forward')

    def test_home_pin_clears_its_channels_and_is_captured(self):
        pin = self.node.pin
        self.assertNotIntersecting(pin, self.node.frame.top)
        for index in range(COUNT):
            bottom = self.channel_solids(index)[0]
            self.assertNotIntersecting(pin, bottom)
        # Captured across the channel: up and down.
        self.assertBlockedBeyond(pin, PIN_TOLERANCE / 2 + 0.2,
                                 self.channel_solids(2)[0], along=(0, 0, 1))
        # Its tie loop stands outside the frame on the +Y side.
        frame_y = self.node.frame.top.mesh.bounds[1][1]
        self.assertGreater(pin.mesh.bounds[1][1], frame_y + 5.0)

    def test_home_pin_blocks_a_lift(self):
        bottom = self.channel_solids(0)[0]
        self.assertBlockedBeyond(bottom, 1.0, self.node.pin, along=self.UP,
                                 directions='forward')

    def test_drawn_pin_frees_the_bracket(self):
        self.node.set_state(pin_draw=100.0)
        pin = self.node.pin
        self.assertNotIntersecting(pin, self.node.frame.top)
        for index in range(COUNT):
            for solid in self.channel_solids(index):
                self.assertNotIntersecting(pin, solid)
        bottom = self.channel_solids(0)[0]
        self.assertFreeWithin(bottom, 1.0, pin, along=self.UP)

    def test_lift_is_ignored_while_the_pin_is_home(self):
        bottom = self.channel_solids(0)[0]
        seated = bottom.mesh.bounds.copy()
        self.node.set_state(lift=LIFT_MAX, pin_draw=0.0)
        np.testing.assert_allclose(bottom.mesh.bounds, seated, atol=1e-6)
        self.assertNotIntersecting(bottom, self.node.pin)

    def test_release_path_clears_the_frame(self):
        top = self.node.frame.top
        others = [self.node.frame.guidewalls[0], self.node.frame.guidewalls[1],
                  self.node.frame.outer_walls[0], self.node.frame.sidewalls[0],
                  self.node.pin]
        others += list(self.channel_solids(1))
        for lift in np.linspace(0.0, LIFT_MAX, 26):
            self.node.set_state(channel=0, pin_draw=100.0, lift=float(lift))
            bottom, cap, wheel, bearing = self.channel_solids(0)
            with self.subTest(lift=round(float(lift), 1)):
                self.assertIntersectVolumeBelow(bottom, top, DETENT)
                self.assertIntersectVolumeBelow(cap, top, RELEASE_KISS)
                for solid in (wheel, bearing):
                    self.assertNotIntersecting(solid, top)
                for other in others:
                    for solid in (bottom, cap, wheel, bearing):
                        self.assertNotIntersecting(solid, other)
        # And it really left: the lifted bracket's lowest point is above
        # the frame.
        bottom = self.channel_solids(0)[0]
        self.assertGreater(bottom.mesh.bounds[0][2], top.mesh.bounds[1][2])

    # -- filament-buffer-loop -----------------------------------------------

    def test_taut_filament_sits_in_the_groove(self):
        for index in range(COUNT):
            loop = self.node.loops[index]
            bottom, cap, wheel, bearing = self.channel_solids(index)
            self.assertNotIntersecting(loop, wheel)
            self.assertNotIntersecting(loop, bottom)
            gap = trimesh.proximity.closest_point(wheel.mesh, loop.mesh.vertices)[1].min()
            self.assertLess(gap, 1.0)
            # Legs one loop radius either side of the axis, in the wheel plane.
            lo, hi = loop.mesh.bounds
            self.assertAlmostEqual(lo[0], -LOOP_R - FILAMENT_R, delta=EPS)
            self.assertAlmostEqual(hi[0], LOOP_R + FILAMENT_R, delta=EPS)
            self.assertAlmostEqual((lo[1] + hi[1]) / 2, channel_y(index), delta=EPS)
            # The sweep starts with its profile in the plane of the axis.
            self.assertAlmostEqual(hi[2], BASE, delta=EPS)
            self.assertAlmostEqual(lo[2], BASE - DROP_MIN - LOOP_R - FILAMENT_R,
                                   delta=EPS)

    def test_loop_stays_inside_its_chamber_through_the_slack_range(self):
        frame = self.node.frame
        walls = [frame.top, frame.connector, frame.bottom,
                 frame.guidewalls[0], frame.guidewalls[1],
                 frame.guidewalls[2], frame.guidewalls[3],
                 frame.outer_walls[0], frame.outer_walls[2],
                 frame.sidewalls[0], frame.sidewalls[COUNT - 1]]
        loop = self.node.loops[0]
        bottom, cap, wheel, bearing = self.channel_solids(0)
        for slack in np.linspace(0.0, SLACK_RANGE[1], 9):
            self.node.set_state(channel=0, slack=float(slack))
            with self.subTest(slack=float(slack)):
                self.assertAlmostEqual(
                    self.loop_bottom(0),
                    BASE - DROP_MIN - slack - LOOP_R - FILAMENT_R, delta=EPS)
                for other in walls + [bottom, wheel]:
                    self.assertNotIntersecting(loop, other)

    def test_a_shallow_chamber_refuses_the_slack_range(self):
        with self.assertRaises(ValueError):
            FenderBender(chamber_depth=330.0)
        FenderBender(chamber_depth=340.0)     # the development configuration fits

    def test_only_the_selected_channel_moves(self):
        rest = BASE - DROP_MIN - LOOP_R - FILAMENT_R
        self.node.set_state(channel=2, slack=100.0)
        for index in range(COUNT):
            expected = rest - (100.0 if index == 2 else 0.0)
            self.assertAlmostEqual(self.loop_bottom(index), expected, delta=EPS)

    def wheel_angle(self, index):
        """Angle of a reference rim vertex of wheel `index` in the wheel
        plane (X, Z about the axis at Y), degrees."""
        mesh = self.node.channels[index].wheel.mesh
        v = mesh.vertices
        r = np.hypot(v[:, 0], v[:, 2] - BASE)
        i = int(np.argmax(r))
        return math.degrees(math.atan2(v[i, 2] - BASE, v[i, 0])), i

    def test_slack_turns_the_wheel(self):
        before, i = self.wheel_angle(0)
        other_before, j = self.wheel_angle(1)
        self.node.set_state(channel=0, slack=WHEEL_R / 2)
        v = self.node.channels[0].wheel.mesh.vertices
        after = math.degrees(math.atan2(v[i, 2] - BASE, v[i, 0]))
        turned = (after - before + 180) % 360 - 180
        self.assertAlmostEqual(abs(turned), math.degrees(1.0), delta=0.1)
        w = self.node.channels[1].wheel.mesh.vertices
        other_after = math.degrees(math.atan2(w[j, 2] - BASE, w[j, 0]))
        self.assertAlmostEqual(other_after, other_before, delta=1e-6)

    @testing_steps(5, start=0.1, end=0.9)
    def test_timeline_visits_every_channel(self):
        t = self.node.time
        active = int(round(t * COUNT - 0.5))
        rest = BASE - DROP_MIN - LOOP_R - FILAMENT_R
        for index in range(COUNT):
            depth = rest - self.loop_bottom(index)
            if index == active:
                self.assertGreater(depth, 140.0)
            else:
                self.assertLess(depth, 1.0)


class FenderBenderScenarioTest(ScenarioTest):
    """The instructions in motion: unlock, lift, seat, lock; retract, feed."""

    node = FenderBender
    dt = 0.1
    meshes = True

    def check_channel_zero_pose(self):
        root = self.node
        top = root.frame.top
        c = root.channels[0]
        self.assertIntersectVolumeBelow(c.bottom, top, DETENT)
        self.assertIntersectVolumeBelow(c.top, top, RELEASE_KISS)
        for solid in (c.wheel, c.bearing):
            self.assertNotIntersecting(solid, top)
        for solid in (c.bottom, c.top, c.wheel, c.bearing):
            self.assertNotIntersecting(solid, root.pin)
            self.assertNotIntersecting(solid, root.channels[1].bottom)

    def test_bracket_change_sequence_stays_clear(self):
        sim = self.simulation()
        sim.at(0.0).trigger('Unlock')
        sim.at(2.0).trigger('Lift bracket')
        sim.at(4.5).trigger('Seat bracket')
        sim.at(7.0).trigger('Lock')
        sim.every(0.5, self.check_channel_zero_pose)
        sim.run(9.0)
        self.assertAlmostEqual(sim.state['pin_draw'], 0.0, delta=1e-6)
        self.assertAlmostEqual(sim.state['lift'], 0.0, delta=1e-6)

    def test_retract_and_feed_keep_the_loop_in_its_chamber(self):
        sim = self.simulation()
        loop = self.node.loops[0]
        frame = self.node.frame
        sim.at(0.0).trigger('Retract')
        sim.at(3.0).trigger('Feed')
        sim.every(0.5, self.assertNotIntersecting, loop, frame.connector)
        sim.every(0.5, self.assertNotIntersecting, loop, frame.guidewalls[0])
        sim.every(0.5, self.assertNotIntersecting, loop, self.node.channels[0].wheel)
        sim.run(6.0)
        self.assertAlmostEqual(sim.state['slack'], 0.0, delta=1e-6)
