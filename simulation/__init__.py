"""The solid-node simulation of one Fender-Bender filament buffer.

The upstream part generators live in ``src/`` as flat modules, the way the
upstream build and tests import them, so this package puts that directory
on the import path before any node module imports a part class. Nothing in
``src/`` is edited or redesigned here: this package places, repeats, colours
and drives what the upstream classes return.
"""

import sys
from pathlib import Path

_UPSTREAM = Path(__file__).resolve().parent.parent / "src"
if str(_UPSTREAM) not in sys.path:
    sys.path.insert(0, str(_UPSTREAM))
