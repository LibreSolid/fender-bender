"""Where the parts sit at rest, in the top frame's world frame: X along
the frame's long side, Y along the channel axis, Z up, origin on the top
frame's base face. Every number that is not a plain constant is read off
the upstream ``BenderConfig`` the model is built from, so nothing derived
is retyped here. Defines no node.

Offsets marked *measured* were chosen by intersecting the placed upstream
part with the frames and taking the interference-free offset; the upstream
debug views place the walls for the hanging frame and do not fit the
standing one.
"""

from solid_node.math import sqrt

# The lock pin is drawn out toward +Y; its tie loop stands on that side.
PIN_DRAW_AXIS = (0, 1, 0)

# Depth of the wheel's diamond groove below the rim: the upstream cuts a
# diamond torus of radius bearing depth / 2 at the rim.
GROOVE_DEPTH_RATIO = 0.5            # times the bearing depth
# A circle of radius r inscribed in the groove's 90 degree V sits r * sqrt 2
# from the apex; 0.1 mm more keeps it off the flanks.
GROOVE_SEAT_CLEARANCE = 0.1         # mm

# The loop's legs leave the groove at the wheel axis height; this is the
# least depth the two legs ever have, so the path never degenerates.
DROP_MIN = 0.5                      # mm

# The click-fit detent: the top frame carries two spheres of 0.75 times the
# click-fit radius that nest in the seated bracket's sphere cuts. Along the
# release path they cross the bracket body; this is their combined volume.
DETENT_SPHERES = 2
DETENT_RADIUS_RATIO = 0.75


def detent_volume(click_fit_radius):
    r = click_fit_radius * DETENT_RADIUS_RATIO
    return DETENT_SPHERES * 4.0 / 3.0 * 3.14159265 * r ** 3


def channel_y(index, count, spacing):
    """Y of channel `index` (0 at the -Y end), centred on the frame."""
    return (index - (count - 1) / 2.0) * spacing


def slot_y(index, count, spacing):
    """Y of wall slot `index` (0 at the -Y end, `count` at the +Y end)."""
    return (index - count / 2.0) * spacing


def section_z(section, straight, connector):
    """Z of the middle of wall section 0 (upper) or 1 (lower)."""
    return -straight / 2.0 - section * (straight + connector)


def loop_radius(wheel_radius, bearing_depth, filament_radius):
    """Radius from the wheel axis to the filament centre in the groove."""
    groove_depth = bearing_depth * GROOVE_DEPTH_RATIO
    return (wheel_radius - groove_depth
            + filament_radius * sqrt(2.0) + GROOVE_SEAT_CLEARANCE)


# Measured offsets (mm). A wall rotated +90 about X has its thickness
# toward -Y from its origin, so `y0` is the wall's +Y face.
SIDEWALL_Z = -1.5        # measured: interference-free between -2.25 and -1.0
                         # debug view's Z for its rounded top to clear the
                         # top frame's slot bottom
GUIDEWALL_X = None       # set below from the config: sidewall_width / 2
