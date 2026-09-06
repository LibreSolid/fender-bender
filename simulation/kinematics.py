"""How the buffer moves. Written over `solid_node.math` so one formula
computes on numbers in tests and builds the viewer's expression on symbolic
time and drivers. The viewer's expression language has arithmetic and the
`solid_node.math` functions but no `min`, `max` or `floor`, so a clamp is
built from `sqrt`: |x| = sqrt(x * x) and clamp(x, 0, 1) = (|x| - |x - 1| + 1) / 2.
Defines no node.
"""

from solid_node.math import sin, sqrt

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


def absolute(x):
    return sqrt(x * x)


def clamp01(x):
    """x clamped to [0, 1]."""
    return (absolute(x) - absolute(x - 1) + 1) / 2


def indicator(a, b):
    """1 when the integers a and b are equal, 0 otherwise."""
    return 1 - clamp01(absolute(a - b))


def piecewise(x, points):
    """Linear interpolation through (x, y) points, clamped at the ends."""
    x0, y = points[0]
    for (xa, ya), (xb, yb) in zip(points, points[1:]):
        y = y + (yb - ya) * clamp01((x - xa) / (xb - xa))
    return y


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


def bump(u):
    """A smooth 0-1-0 pulse over u in [0, 1], zero outside."""
    s = sin(180.0 * clamp01(u))
    return s * s


def demo_slack(time, count, index):
    """The timeline: channel `index` retracts and feeds back inside its
    own 1 / count slice of the cycle."""
    return DEMO_SLACK * bump(time * count - index)
