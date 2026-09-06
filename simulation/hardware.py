"""The parts a maker buys, from the site's bill of materials. Defines no
node.

The bearing is an MR126 (6 mm bore, 12 mm outside, 4 mm wide). Its bore is
modelled at the upstream post diameter rather than the catalogue 6.0 mm:
the upstream bracket post is 6.1 mm, a 0.05 mm-per-side press fit into the
real bore, and adjacency discipline forbids two solids sharing volume, so
the press fit is represented as contact. This is an upstream finding, not a
change to the design.
"""

BEARING_OUTER_DIAMETER = 12.0   # mm, MR126
BEARING_WIDTH = 4.0             # mm

FILAMENT_DIAMETER = 1.75        # mm
FILAMENT_RADIUS = FILAMENT_DIAMETER / 2
