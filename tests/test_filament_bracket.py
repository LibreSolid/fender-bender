from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
import pytest
from filament_channels import FilamentChannels
from filament_bracket import FilamentBracket
from bender_config import BenderConfig
from filament_bracket_config import FilamentBracketConfig
from dataclasses import fields, field, MISSING


class TestFilamentBracket:
    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/filament_bracket.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))

    def test_complete_connector_set(self, complete_connector_config_yaml):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("filament_bracket.save_screenshot"),
        ):
            bender_config = BenderConfig(complete_connector_config_yaml)
            bracket = FilamentBracket(bender_config.filament_bracket_config())
            bracket.compile()
            bracket.display()
            bracket.export_stls()
            bracket._config.stl_folder = "c:/temp"
            bracket.export_stls()

    def test_bracket_block(self):
        bender_config = BenderConfig()
        bracket = FilamentBracket(bender_config.filament_bracket_config())
        block = bracket.bottom_bracket_block()
        assert block is not None
        assert block.volume > 0
        assert block.bounding_box().size.X == pytest.approx(106.20623590190772)

    def test_straight_filament_path(self):
        channels = FilamentChannels()
        block = channels.straight_filament_block_solid()
        assert block is not None
        assert block.is_valid
        path = channels.straight_filament_path_cut()
        assert path is not None
        assert block.is_valid

    def test_curved_filament_path(self):
        channels = FilamentChannels()
        block = channels.curved_filament_block_solid()
        assert block is not None
        assert block.is_valid
        path = channels.curved_filament_path_cut()
        assert path is not None
        assert block.is_valid

    def test_initialized_load_from_bender_config(self, bender_config_yaml_threaded):
        bender_config = BenderConfig(bender_config_yaml_threaded)
        channels = FilamentChannels(bender_config.filament_bracket_config())
        assert channels._config.connector.thread_angle == 30

    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/filament_bracket.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))

    def test_channels_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/filament_channels.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))

    def test_curved_filament_block_solid_with_twist_snap_extension(self):
        """Test curved filament block solid with twist snap extension enabled"""
        bender_config = BenderConfig()
        config = bender_config.filament_bracket_config()
        # Enable twist snap extension
        config.connector.twist_snap_extension = True

        channels = FilamentChannels(config)
        block = channels.curved_filament_block_solid()

        assert block is not None
        assert block.is_valid
        assert block.volume > 0
        assert block.label == "curved filament path"

    def test_curved_filament_block_solid_without_top_exit_fillet(self):
        """Test curved filament block solid with top_exit_fillet=False"""
        channels = FilamentChannels()
        block = channels.curved_filament_block_solid(top_exit_fillet=False)

        assert block is not None
        assert block.is_valid
        assert block.volume > 0
        assert block.label == "curved filament path"

    def test_curved_filament_block_solid_twist_snap_and_no_top_fillet(self):
        """Test curved filament block solid with both twist snap extension and no top exit fillet"""
        bender_config = BenderConfig()
        config = bender_config.filament_bracket_config()
        # Enable twist snap extension
        config.connector.twist_snap_extension = True

        channels = FilamentChannels(config)
        block = channels.curved_filament_block_solid(top_exit_fillet=False)

        assert block is not None
        assert block.is_valid
        assert block.volume > 0
        assert block.label == "curved filament path"

    def test_straight_filament_block_complete_mode(self):
        """Test straight filament block with COMPLETE channel mode (covers lines 255-256)"""
        from filament_channels import ChannelMode

        channels = FilamentChannels()
        channels.channel_mode = ChannelMode.COMPLETE
        block = channels.straight_filament_block()

        assert block is not None
        assert block.is_valid
        assert block.volume > 0
        assert block.label == "filament path"

    def test_straight_filament_block_with_twist_snap_extension(self):
        """Test straight filament block with twist snap extension"""
        from filament_channels import ChannelMode

        bender_config = BenderConfig()
        config = bender_config.filament_bracket_config()
        config.connector.twist_snap_extension = True

        channels = FilamentChannels(config)
        channels.channel_mode = ChannelMode.COMPLETE
        block = channels.straight_filament_block()

        assert block is not None
        assert block.is_valid
        assert block.volume > 0
        assert block.label == "filament path"

    def test_straight_filament_block_solid_mode(self):
        """Test straight filament block with SOLID channel mode"""
        from filament_channels import ChannelMode

        channels = FilamentChannels()
        channels.channel_mode = ChannelMode.SOLID
        block = channels.straight_filament_block()

        assert block is not None
        assert block.is_valid
        assert block.volume > 0
        assert block.label == "filament path"

    def test_curved_filament_block_complete_mode(self):
        """Test curved filament block with COMPLETE channel mode"""
        from filament_channels import ChannelMode

        channels = FilamentChannels()
        channels.channel_mode = ChannelMode.COMPLETE
        block = channels.curved_filament_block()

        assert block is not None
        assert block.is_valid
        assert block.volume > 0
        assert block.label == "filament path"

    def test_curved_filament_block_solid_mode(self):
        """Test curved filament block with SOLID channel mode"""
        from filament_channels import ChannelMode

        channels = FilamentChannels()
        channels.channel_mode = ChannelMode.SOLID
        block = channels.curved_filament_block()

        assert block is not None
        assert block.is_valid
        assert block.volume > 0
        assert block.label == "filament path"

    def test_compile_method_lean_forward(self):
        """Test compile method with LEAN_FORWARD configuration"""
        from filament_channels import ChannelMode
        from filament_bracket_config import ChannelPairDirection

        bender_config = BenderConfig()
        config = bender_config.filament_bracket_config()
        config.channel_pair_direction = ChannelPairDirection.LEAN_FORWARD

        channels = FilamentChannels(config)
        channels.channel_mode = ChannelMode.COMPLETE
        channels.compile()

        assert len(channels.parts) == 1
        assert channels.parts[0].part.label == "filament channels"

    def test_compile_method_lean_reverse(self):
        """Test compile method with LEAN_REVERSE configuration"""
        from filament_channels import ChannelMode
        from filament_bracket_config import ChannelPairDirection

        bender_config = BenderConfig()
        config = bender_config.filament_bracket_config()
        config.channel_pair_direction = ChannelPairDirection.LEAN_REVERSE

        channels = FilamentChannels(config)
        channels.channel_mode = ChannelMode.COMPLETE
        channels.compile()

        assert len(channels.parts) == 1
        assert channels.parts[0].part.label == "filament channels"

    def test_compile_method_straight(self):
        """Test compile method with STRAIGHT configuration"""
        from filament_channels import ChannelMode
        from filament_bracket_config import ChannelPairDirection

        bender_config = BenderConfig()
        config = bender_config.filament_bracket_config()
        config.channel_pair_direction = ChannelPairDirection.STRAIGHT

        channels = FilamentChannels(config)
        channels.channel_mode = ChannelMode.COMPLETE
        channels.compile()

        assert len(channels.parts) == 1
        assert channels.parts[0].part.label == "filament channels"

    def test_compile_method_cut_path_mode(self):
        """Test compile method with CUT_PATH channel mode"""
        from filament_channels import ChannelMode

        channels = FilamentChannels()
        channels.channel_mode = ChannelMode.CUT_PATH
        channels.compile()

        assert len(channels.parts) == 1
        assert channels.parts[0].part.label == "filament channels"

    def test_connector_threads_function(self):
        """Test the standalone connector_threads function"""
        from filament_channels import connector_threads

        bender_config = BenderConfig()
        config = bender_config.filament_bracket_config()

        threads = connector_threads(config.connector)

        assert threads is not None
        assert threads.is_valid
        assert threads.volume > 0


class TestFilamentBracketConfig:

    def test_detault_config(self):
        config = FilamentBracketConfig()
        config.bracket_height = 1000
        assert config.bracket_height == 1000
        config._default_config()
        assert config.bracket_height == pytest.approx(43.5)

    def test_yaml_config(self, filament_bracket_config_yaml):
        config = FilamentBracketConfig(filament_bracket_config_yaml)
        assert config.bracket_height == pytest.approx(43.5)

    def test_yaml_with_dict_config(self, filament_bracket_config_yaml_with_dict):
        config = FilamentBracketConfig(filament_bracket_config_yaml_with_dict)
        assert config.lock_pin.pin_length == pytest.approx(123)

    def test_dict_kwargs(self, filament_bracket_config_yaml_with_dict):
        config = FilamentBracketConfig(
            lock_pin={
                "stl_folder": "NONE",
                "pin_length": 123,
                "tolerance": 0.1,
                "height": 4,
                "tie_loop": True,
            }
        )
        assert config.lock_pin.pin_length == pytest.approx(123)

    def test_default_config_field_without_default(self):
        """Test that _default_config raises ValueError when a field has no default"""
        config = FilamentBracketConfig()

        original_fields = fields(config)

        mock_field = field()
        mock_field.name = "mock_field"
        mock_field.default = MISSING
        mock_field.default_factory = MISSING

        modified_fields = list(original_fields) + [mock_field]

        with patch("filament_bracket_config.fields", return_value=modified_fields):
            with pytest.raises(
                ValueError, match="Field mock_field has no default value"
            ):
                config._default_config()
