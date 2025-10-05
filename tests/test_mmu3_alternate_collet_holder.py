from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import pytest
from build123d import Part

from mmu3_alternate_collet_holder import (
    AlternateColletHolder,
    AlternateColletHolderConfig,
)


class TestAlternateColletHolderConfig:
    def test_config_initialization(self):
        config = AlternateColletHolderConfig()
        assert config.yaml_tree == "FilamentBracket"
        assert config.stl_folder == "NONE"
        assert config.file_prefix == ""
        assert config.file_suffix == ""

    def test_config_constants(self):
        config = AlternateColletHolderConfig()
        # Test MMU3 constants that should not be changed
        assert config.COLLET_HOLDER_REVISION == "R1"
        assert config.COLLET_HOLDER_LENGTH == 65.2
        assert config.COLLET_HOLDER_ANGLE == 10
        assert config.COLLET_HOLDER_TOP_STRAIGHT_DEPTH == 4.925
        assert config.COLLET_HOLDER_TOP_BENT_DEPTH == 16.189
        assert config.COLLET_HOLDER_WIDTH == 10.0
        assert config.COLLET_HOLDER_CHAMFER_RADIUS == 1
        assert config.COLLET_HOLDER_TUBE_DISTANCE == 14
        assert config.COLLET_HOLDER_TUBE_RADIUS == 2.125


class TestAlternateColletHolder:
    def test_initialization(self):
        mmu = AlternateColletHolder()
        assert isinstance(mmu._config, AlternateColletHolderConfig)
        assert mmu._config is not None

    def test_screwcut_component(self):
        mmu = AlternateColletHolder()
        screwcut = mmu._screwcut()
        assert isinstance(screwcut, Part)
        assert screwcut.is_valid()
        assert screwcut.label == "screw cut"
        # Check approximate dimensions - the total height is 110 (from -55 to +55)
        assert screwcut.bounding_box().size.Z == pytest.approx(110)

    def test_tube_channel_component(self):
        mmu = AlternateColletHolder()
        channel = mmu._tube_channel()
        assert isinstance(channel, Part)
        assert channel.is_valid()
        assert channel.label == "tube channel"
        # Verify the channel has positive volume
        assert channel.volume > 0

    def test_collet_holder(self):
        mmu = AlternateColletHolder()
        holder = mmu.collet_holder()
        assert isinstance(holder, Part)
        assert holder.is_valid()
        assert holder.label == "New Collet Holder"
        # Check approximate dimensions based on config values
        bbox = holder.bounding_box()
        assert bbox.size.X == pytest.approx(mmu._config.COLLET_HOLDER_LENGTH, abs=1)
        assert bbox.size.Y > 0  # Should have positive Y dimension
        assert bbox.size.Z > 0  # Should have positive Z dimension
        # Verify it has positive volume
        assert holder.volume > 0

    def test_compile(self):
        mmu = AlternateColletHolder()
        mmu.compile()
        assert len(mmu.parts) == 1
        assert mmu.parts[0].part.is_valid()
        assert mmu.parts[0].file_name_base == "mmu3_alternate_collet_holder"

    def test_compile_with_stl_folder(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            mmu = AlternateColletHolder()
            mmu._config.stl_folder = "stl/"
            mmu.compile()
            mmu.display()
            mmu.export_stls()
            assert len(mmu.parts) == 1
            assert mmu.parts[0].part.is_valid()

    def test_none_stl_folder(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            mmu = AlternateColletHolder()
            mmu._config.stl_folder = "NONE"
            mmu.compile()
            mmu.export_stls()
            assert len(mmu.parts) == 1

    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/mmu3_alternate_collet_holder.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))

    def test_config_modification(self):
        mmu = AlternateColletHolder()
        original_length = mmu._config.COLLET_HOLDER_LENGTH
        # Test that we can modify config (though normally constants shouldn't change)
        mmu._config.COLLET_HOLDER_LENGTH = 70.0
        assert mmu._config.COLLET_HOLDER_LENGTH == 70.0
        # Reset for other tests
        mmu._config.COLLET_HOLDER_LENGTH = original_length

    def test_collet_holder_with_modified_config(self):
        mmu = AlternateColletHolder()
        # Test with slightly modified tube radius to ensure parts respond to config changes
        original_radius = mmu._config.COLLET_HOLDER_TUBE_RADIUS
        mmu._config.COLLET_HOLDER_TUBE_RADIUS = 2.5

        holder = mmu.collet_holder()
        assert isinstance(holder, Part)
        assert holder.is_valid()

        # Reset config
        mmu._config.COLLET_HOLDER_TUBE_RADIUS = original_radius

    def test_part_color_and_labeling(self):
        mmu = AlternateColletHolder()
        holder = mmu.collet_holder()
        # Check color by comparison with expected blue color
        from build123d import Color

        expected_blue = Color("blue")
        assert str(holder.color) == str(expected_blue)
        assert holder.label == "New Collet Holder"

    def test_geometric_constraints(self):
        """Test that the generated parts meet basic geometric constraints"""
        mmu = AlternateColletHolder()
        holder = mmu.collet_holder()

        # The part should have reasonable dimensions
        bbox = holder.bounding_box()
        assert bbox.size.X > 60  # Should be close to COLLET_HOLDER_LENGTH (65.2)
        assert bbox.size.Y > 5  # Should be reasonable width
        assert bbox.size.Z > 15  # Should have sufficient height for angled portion

        # Volume should be positive and reasonable
        assert holder.volume > 1000  # Should have substantial volume

    def test_config_parameter_effects(self):
        """Test that changing config parameters affects the output"""
        mmu = AlternateColletHolder()

        # Store original values
        original_radius = mmu._config.COLLET_HOLDER_TUBE_RADIUS

        # Generate with original config
        holder1 = mmu.collet_holder()

        # Modify tube radius for comparison
        mmu._config.COLLET_HOLDER_TUBE_RADIUS = 2.5
        holder2 = mmu.collet_holder()

        # Restore original value
        mmu._config.COLLET_HOLDER_TUBE_RADIUS = original_radius

        # Both should be valid but different
        assert holder1.is_valid()
        assert holder2.is_valid()
        # They should have different volumes due to different tube cuts
        assert abs(holder1.volume - holder2.volume) > 0.1

    def test_component_integration(self):
        """Test that internal components integrate properly"""
        mmu = AlternateColletHolder()

        # Test individual components
        screwcut = mmu._screwcut()
        channel = mmu._tube_channel()
        holder = mmu.collet_holder()

        # All components should be valid
        assert screwcut.is_valid()
        assert channel.is_valid()
        assert holder.is_valid()

        # The holder should be larger than individual cuts
        assert holder.volume > screwcut.volume
        assert holder.volume > channel.volume

    def test_multiple_instances(self):
        """Test creating multiple instances works correctly"""
        # Store original value to restore later
        mmu = AlternateColletHolder()
        original_distance = mmu._config.COLLET_HOLDER_TUBE_DISTANCE

        holders = []

        # Create holders with different tube distances sequentially
        for distance in [12, 14, 16]:
            mmu._config.COLLET_HOLDER_TUBE_DISTANCE = distance
            holders.append(mmu.collet_holder())

        # Restore original value
        mmu._config.COLLET_HOLDER_TUBE_DISTANCE = original_distance

        # All should be valid
        for holder in holders:
            assert holder.is_valid()

        # All holders should have positive volume
        for holder in holders:
            assert holder.volume > 1000

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        mmu = AlternateColletHolder()

        # Test with minimum reasonable values
        mmu._config.COLLET_HOLDER_TUBE_RADIUS = 0.5
        mmu._config.COLLET_HOLDER_WIDTH = 5.0

        holder = mmu.collet_holder()
        assert holder.is_valid()
        assert holder.volume > 0

        # Test components still work with modified config
        screwcut = mmu._screwcut()
        channel = mmu._tube_channel()
        assert screwcut.is_valid()
        assert channel.is_valid()

    def test_revision_marking(self):
        """Test that revision marking is properly embedded"""
        mmu = AlternateColletHolder()
        holder = mmu.collet_holder()

        # The holder should be valid and contain the revision marking
        assert holder.is_valid()
        # The revision constant should match what's in the config
        assert mmu._config.COLLET_HOLDER_REVISION == "R1"

        # Test with different revision
        mmu._config.COLLET_HOLDER_REVISION = "R2"
        holder_r2 = mmu.collet_holder()
        assert holder_r2.is_valid()

    def test_shared_config_behavior(self):
        """Test the shared config behavior works as designed"""
        # Create multiple instances
        instances = [AlternateColletHolder() for _ in range(3)]

        # Store original values
        original_length = instances[0]._config.COLLET_HOLDER_LENGTH
        original_folder = instances[0]._config.stl_folder

        # All instances should share the same config object
        for i, mmu in enumerate(instances[1:], 1):
            assert mmu._config is instances[0]._config

        # Modify config through one instance
        instances[0]._config.COLLET_HOLDER_LENGTH = 70.0
        instances[0]._config.stl_folder = "test_shared"

        # All instances should see the change
        for mmu in instances:
            assert mmu._config.COLLET_HOLDER_LENGTH == 70.0
            assert mmu._config.stl_folder == "test_shared"

        # Compile all - they should all work
        for mmu in instances:
            mmu.compile()
            assert len(mmu.parts) == 1
            assert mmu.parts[0].part.is_valid()

        # Restore original values
        instances[0]._config.COLLET_HOLDER_LENGTH = original_length
        instances[0]._config.stl_folder = original_folder
