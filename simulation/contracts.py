"""Test support: a whole-model interference check over exact solids.

The framework's `assertNoSolidInterference` reads every printed solid's STL
through a Manifold cache and refuses a file trimesh calls non-watertight.
Seven of the upstream parts tessellate that way (T-junctions between faces;
Manifold itself accepts them with matching volumes), so the frame and root
tests check interference pairwise on the exact solids instead, after a
bounding-box prefilter. Defines no node.
"""

import itertools

import numpy as np


def rigid_solids(node):
    """The printed solids below `node`: topmost rigid nodes."""
    if node.rigid:
        return [node]
    found = []
    for child in node.children:
        found.extend(rigid_solids(child))
    return found


def boxes_touch(a, b, margin=0.0):
    (alo, ahi), (blo, bhi) = a, b
    return bool(np.all(alo <= bhi + margin) and np.all(blo <= ahi + margin))


def candidate_pairs(solids, exclude=()):
    """Pairs of solids whose world bounding boxes overlap, minus `exclude`
    (a set of frozensets of names)."""
    bounds = {s: s.mesh.bounds for s in solids}
    pairs = []
    for a, b in itertools.combinations(solids, 2):
        if frozenset((a.name, b.name)) in exclude:
            continue
        if boxes_touch(bounds[a], bounds[b]):
            pairs.append((a, b))
    return pairs


def assert_no_interference(test, node, exclude=()):
    """Every pair of printed solids below `node` whose boxes overlap shares
    no volume (exact between exact nodes). Skips flexible leaves."""
    solids = [s for s in rigid_solids(node)]
    for a, b in candidate_pairs(solids, exclude):
        test.assertNotIntersecting(a, b)
