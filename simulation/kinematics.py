"""How the buffer moves. Written over `solid_node.math` so one formula
computes on numbers in tests and builds the viewer's expression on symbolic
time and drivers. Defines no node.

The clamp, the waypoint path and the pulse are the framework's now. This
file used to build all three out of `sqrt(x * x)`, believing the viewer's
expression language had no `min`, `max` or `floor`; it has all three, and
OpenSCAD has had them all along.
"""

from solid_node.math import abs, bump, clamp01, piecewise

DEMO_SLACK = 150.0      # mm, the slack each channel reaches on the timeline
PIN_CLEAR = 92.0        # mm, the pin draw at which it has left the frame
PIN_GATE = 8.0          # mm, the draw over which the lift gate opens
LIFT_MAX = 100.0        # mm, the `lift` driver's full range

# The release path the top frame admits, measured by intersecting the
# placed bracket with the frame: (lift, dx, dz, tilt about Y). The bracket
# first slides forward on its rails, tilts back while rising past the
# retaining rim, and straightens once above the frame.
RELEASE_WAYPOINTS = (
    (0.0,   0.0,  0.0,   0.0),
    (5.0,   4.0,  1.0,   0.0),
    (10.0,  4.0,  4.0,  -5.0),
    (15.0,  6.0,  8.0, -10.0),
    (20.0,  6.0, 12.0, -15.0),
    (25.0,  8.0, 15.0, -15.0),
    (35.0, 10.0, 25.0, -15.0),
    (40.0, 10.0, 25.0,   0.0),
    (LIFT_MAX, 10.0, 95.0, 0.0),
)


def indicator(a, b):
    """1 when the integers a and b are equal, 0 otherwise.

    Local, and staying local: for anything but integers this is a
    triangular hat rather than an indicator, and that precondition is this
    file's to keep, not the framework's to bless.
    """
    return 1 - clamp01(abs(a - b))


def release_pose(lift):
    """(dx, dz, tilt) of a bracket at `lift` mm along the release path."""
    dx = piecewise(lift, [(w[0], w[1]) for w in RELEASE_WAYPOINTS])
    dz = piecewise(lift, [(w[0], w[2]) for w in RELEASE_WAYPOINTS])
    tilt = piecewise(lift, [(w[0], w[3]) for w in RELEASE_WAYPOINTS])
    return dx, dz, tilt


def lift_gate(pin):
    """0 while the pin is in the frame, 1 once it is drawn clear."""
    return clamp01((pin - PIN_CLEAR) / PIN_GATE)


def wheel_angle(slack, wheel_radius):
    """Degrees the wheel has turned when `slack` mm hangs in the loop:
    both legs lengthen together, so 2 * slack of filament passed over it."""
    return -2.0 * slack / wheel_radius * 180.0 / 3.14159265358979


def demo_slack(time, count, index):
    """The timeline: channel `index` retracts and feeds back inside its
    own 1 / count slice of the cycle."""
    return DEMO_SLACK * bump(time * count - index)
