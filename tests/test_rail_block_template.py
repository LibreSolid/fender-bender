from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from rail_block import rail_block_template
from build123d import Part
import pytest


class TestRailBlockTemplate:
    def test_rail_block_template(self):
        rail_block = rail_block_template(
            width=10, length=20, depth=10, radius=1, inset=0.2, rail_width=1
        )
        assert rail_block.is_valid()
        assert isinstance(rail_block, Part)
        assert rail_block.bounding_box().size.X == pytest.approx(24.8)
        assert rail_block.bounding_box().size.Y == pytest.approx(9.8)
        assert rail_block.bounding_box().size.Z == pytest.approx(10.8)

    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader("__main__", "src/rail_block.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))
