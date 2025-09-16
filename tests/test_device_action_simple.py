"""Test device actions for VMC Helty Flow."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.vmc_helty_flow.const import DOMAIN
from custom_components.vmc_helty_flow.device_action import (
    DEVICE_ACTION_SCHEMA,
    DEVICE_ACTIONS,
    _execute_device_action,
    _reset_filter,
    _set_device_name,
    _set_fan_speed,
    _set_free_cooling,
    _set_hyperventilation,
    _set_network_config,
    _set_night_mode,
    _set_panel_led,
    _set_sensors,
    async_setup_device_actions,
)


class TestDeviceActionSchema:
    """Test device action schema validation."""

    def test_schema_valid_data(self):
        """Test schema with valid data."""
        data = {
            "device_id": "test_device",
            "action": "set_fan_speed",
            "parameters": {"speed": 2},
        }
        result = DEVICE_ACTION_SCHEMA(data)
        assert result == data

    def test_schema_missing_optional_parameters(self):
        """Test schema with missing optional parameters."""
        data = {"device_id": "test_device", "action": "set_fan_speed"}
        result = DEVICE_ACTION_SCHEMA(data)
        assert result["parameters"] == {}


class TestDeviceActions:
    """Test device actions constants."""

    def test_device_actions_defined(self):
        """Test that all device actions are properly defined."""
        expected_actions = [
            "set_fan_speed",
            "set_hyperventilation",
            "set_night_mode",
            "set_free_cooling",
            "set_panel_led",
            "set_sensors",
            "reset_filter",
            "set_device_name",
            "set_network_config",
        ]

        for action in expected_actions:
            assert action in DEVICE_ACTIONS
            assert "name" in DEVICE_ACTIONS[action]
            assert "parameters" in DEVICE_ACTIONS[action]


class TestAsyncSetupDeviceActions:
    """Test async_setup_device_actions function."""

    @pytest.fixture
    def mock_hass(self):
        """Create a mock HomeAssistant instance."""
        hass = MagicMock(spec=HomeAssistant)
        hass.services = MagicMock()
        return hass

    async def test_setup_device_actions(self, mock_hass):
        """Test setting up device actions."""
        await async_setup_device_actions(mock_hass)

        # Check that the service was registered
        assert mock_hass.services.async_register.called
        call_args = mock_hass.services.async_register.call_args
        assert call_args[0][0] == DOMAIN
        assert call_args[0][1] == "device_action"
        assert callable(call_args[0][2])  # Handler function
        assert call_args[1]["schema"] == DEVICE_ACTION_SCHEMA


class TestExecuteDeviceAction:
    """Test _execute_device_action function."""

    @patch("custom_components.vmc_helty_flow.device_action._set_fan_speed")
    async def test_execute_valid_action(self, mock_set_fan_speed):
        """Test executing a valid action."""
        await _execute_device_action("192.168.1.100", "set_fan_speed", {"speed": 2})
        mock_set_fan_speed.assert_called_once_with("192.168.1.100", {"speed": 2})

    async def test_execute_invalid_action(self):
        """Test executing an invalid action."""
        with pytest.raises(HomeAssistantError, match="Unknown action: invalid_action"):
            await _execute_device_action("192.168.1.100", "invalid_action", {})


class TestSetFanSpeed:
    """Test _set_fan_speed function."""

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_fan_speed_success(self, mock_tcp):
        """Test successful fan speed setting."""
        mock_tcp.return_value = "OK"

        await _set_fan_speed("192.168.1.100", {"speed": 2})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0000002")

    async def test_set_fan_speed_invalid_speed_high(self):
        """Test fan speed setting with invalid high speed."""
        with pytest.raises(HomeAssistantError, match="Speed must be between 0 and 4"):
            await _set_fan_speed("192.168.1.100", {"speed": 5})

    async def test_set_fan_speed_invalid_speed_negative(self):
        """Test fan speed setting with invalid negative speed."""
        with pytest.raises(HomeAssistantError, match="Speed must be between 0 and 4"):
            await _set_fan_speed("192.168.1.100", {"speed": -1})

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_fan_speed_failure(self, mock_tcp):
        """Test fan speed setting failure."""
        mock_tcp.return_value = "ERROR"

        with pytest.raises(HomeAssistantError, match="Failed to set fan speed: ERROR"):
            await _set_fan_speed("192.168.1.100", {"speed": 2})

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_fan_speed_default_value(self, mock_tcp):
        """Test fan speed setting with default value."""
        mock_tcp.return_value = "OK"

        await _set_fan_speed("192.168.1.100", {})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0000001")


class TestSetHyperventilation:
    """Test _set_hyperventilation function."""

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_hyperventilation_enable(self, mock_tcp):
        """Test enabling hyperventilation."""
        mock_tcp.return_value = "OK"

        await _set_hyperventilation("192.168.1.100", {"enable": True})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0000005")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_hyperventilation_disable(self, mock_tcp):
        """Test disabling hyperventilation."""
        mock_tcp.return_value = "OK"

        await _set_hyperventilation("192.168.1.100", {"enable": False})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0000001")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_hyperventilation_default(self, mock_tcp):
        """Test hyperventilation with default value."""
        mock_tcp.return_value = "OK"

        await _set_hyperventilation("192.168.1.100", {})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0000005")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_hyperventilation_failure(self, mock_tcp):
        """Test hyperventilation setting failure."""
        mock_tcp.return_value = "ERROR"

        with pytest.raises(
            HomeAssistantError, match="Failed to set hyperventilation: ERROR"
        ):
            await _set_hyperventilation("192.168.1.100", {"enable": True})


class TestSetNightMode:
    """Test _set_night_mode function."""

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_night_mode_enable(self, mock_tcp):
        """Test enabling night mode."""
        mock_tcp.return_value = "OK"

        await _set_night_mode("192.168.1.100", {"enable": True})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0000006")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_night_mode_disable(self, mock_tcp):
        """Test disabling night mode."""
        mock_tcp.return_value = "OK"

        await _set_night_mode("192.168.1.100", {"enable": False})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0000001")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_night_mode_failure(self, mock_tcp):
        """Test night mode setting failure."""
        mock_tcp.return_value = "ERROR"

        with pytest.raises(HomeAssistantError, match="Failed to set night mode: ERROR"):
            await _set_night_mode("192.168.1.100", {"enable": True})


class TestSetFreeCooling:
    """Test _set_free_cooling function."""

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_free_cooling_enable(self, mock_tcp):
        """Test enabling free cooling."""
        mock_tcp.return_value = "OK"

        await _set_free_cooling("192.168.1.100", {"enable": True})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0000007")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_free_cooling_disable(self, mock_tcp):
        """Test disabling free cooling."""
        mock_tcp.return_value = "OK"

        await _set_free_cooling("192.168.1.100", {"enable": False})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0000001")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_free_cooling_failure(self, mock_tcp):
        """Test free cooling setting failure."""
        mock_tcp.return_value = "ERROR"

        with pytest.raises(
            HomeAssistantError, match="Failed to set free cooling: ERROR"
        ):
            await _set_free_cooling("192.168.1.100", {"enable": True})


class TestSetPanelLed:
    """Test _set_panel_led function."""

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_panel_led_enable(self, mock_tcp):
        """Test enabling panel LED."""
        mock_tcp.return_value = "OK"

        await _set_panel_led("192.168.1.100", {"enable": True})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0100010")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_panel_led_disable(self, mock_tcp):
        """Test disabling panel LED."""
        mock_tcp.return_value = "OK"

        await _set_panel_led("192.168.1.100", {"enable": False})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0100000")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_panel_led_failure(self, mock_tcp):
        """Test panel LED setting failure."""
        mock_tcp.return_value = "ERROR"

        with pytest.raises(HomeAssistantError, match="Failed to set panel LED: ERROR"):
            await _set_panel_led("192.168.1.100", {"enable": True})


class TestSetSensors:
    """Test _set_sensors function."""

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_sensors_enable(self, mock_tcp):
        """Test enabling sensors."""
        mock_tcp.return_value = "OK"

        await _set_sensors("192.168.1.100", {"enable": True})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0300000")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_sensors_disable(self, mock_tcp):
        """Test disabling sensors."""
        mock_tcp.return_value = "OK"

        await _set_sensors("192.168.1.100", {"enable": False})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0300002")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_sensors_failure(self, mock_tcp):
        """Test sensors setting failure."""
        mock_tcp.return_value = "ERROR"

        with pytest.raises(HomeAssistantError, match="Failed to set sensors: ERROR"):
            await _set_sensors("192.168.1.100", {"enable": True})


class TestResetFilter:
    """Test _reset_filter function."""

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_reset_filter_success(self, mock_tcp):
        """Test successful filter reset."""
        mock_tcp.return_value = "OK"

        await _reset_filter("192.168.1.100", {})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMWH0417744")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_reset_filter_failure(self, mock_tcp):
        """Test filter reset failure."""
        mock_tcp.return_value = "ERROR"

        with pytest.raises(HomeAssistantError, match="Failed to reset filter: ERROR"):
            await _reset_filter("192.168.1.100", {})


class TestSetDeviceName:
    """Test _set_device_name function."""

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_device_name_success(self, mock_tcp):
        """Test successful device name setting."""
        mock_tcp.return_value = "OK"

        await _set_device_name("192.168.1.100", {"name": "Test_Device"})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMNM Test_Device")

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_device_name_with_special_chars(self, mock_tcp):
        """Test device name setting with special characters."""
        mock_tcp.return_value = "OK"

        await _set_device_name("192.168.1.100", {"name": "Test Device@#$%"})

        mock_tcp.assert_called_once_with("192.168.1.100", 5001, "VMNM TestDevice")

    async def test_set_device_name_empty(self):
        """Test device name setting with empty name."""
        with pytest.raises(
            HomeAssistantError, match="Name must be between 1 and 32 characters"
        ):
            await _set_device_name("192.168.1.100", {"name": ""})

    async def test_set_device_name_too_long(self):
        """Test device name setting with too long name."""
        long_name = "a" * 33
        with pytest.raises(
            HomeAssistantError, match="Name must be between 1 and 32 characters"
        ):
            await _set_device_name("192.168.1.100", {"name": long_name})

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_device_name_failure(self, mock_tcp):
        """Test device name setting failure."""
        mock_tcp.return_value = "ERROR"

        with pytest.raises(
            HomeAssistantError, match="Failed to set device name: ERROR"
        ):
            await _set_device_name("192.168.1.100", {"name": "Test"})


class TestSetNetworkConfig:
    """Test _set_network_config function."""

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_network_config_success(self, mock_tcp):
        """Test successful network configuration."""
        mock_tcp.return_value = "OK"

        await _set_network_config(
            "192.168.1.100", {"ssid": "TestWiFi", "password": "password123"}
        )

        expected_command = (
            "VMSL TestWiFi************************password123*********************"
        )
        mock_tcp.assert_called_once_with("192.168.1.100", 5001, expected_command)

    async def test_set_network_config_empty_ssid(self):
        """Test network config with empty SSID."""
        with pytest.raises(
            HomeAssistantError, match="SSID must be between 1 and 32 characters"
        ):
            await _set_network_config(
                "192.168.1.100", {"ssid": "", "password": "password123"}
            )

    async def test_set_network_config_long_ssid(self):
        """Test network config with too long SSID."""
        long_ssid = "a" * 33
        with pytest.raises(
            HomeAssistantError, match="SSID must be between 1 and 32 characters"
        ):
            await _set_network_config(
                "192.168.1.100", {"ssid": long_ssid, "password": "password123"}
            )

    async def test_set_network_config_empty_password(self):
        """Test network config with empty password."""
        with pytest.raises(
            HomeAssistantError, match="Password must be between 8 and 32 characters"
        ):
            await _set_network_config(
                "192.168.1.100", {"ssid": "TestWiFi", "password": ""}
            )

    async def test_set_network_config_short_password(self):
        """Test network config with too short password."""
        with pytest.raises(
            HomeAssistantError, match="Password must be between 8 and 32 characters"
        ):
            await _set_network_config(
                "192.168.1.100", {"ssid": "TestWiFi", "password": "short"}
            )

    async def test_set_network_config_long_password(self):
        """Test network config with too long password."""
        long_password = "a" * 33
        with pytest.raises(
            HomeAssistantError, match="Password must be between 8 and 32 characters"
        ):
            await _set_network_config(
                "192.168.1.100", {"ssid": "TestWiFi", "password": long_password}
            )

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_network_config_failure(self, mock_tcp):
        """Test network config setting failure."""
        mock_tcp.return_value = "ERROR"

        with pytest.raises(
            HomeAssistantError, match="Failed to set network config: ERROR"
        ):
            await _set_network_config(
                "192.168.1.100", {"ssid": "TestWiFi", "password": "password123"}
            )

    @patch("custom_components.vmc_helty_flow.device_action.tcp_send_command")
    async def test_set_network_config_exact_length(self, mock_tcp):
        """Test network config with exact max length."""
        mock_tcp.return_value = "OK"

        ssid_32 = "a" * 32
        password_32 = "b" * 32

        await _set_network_config(
            "192.168.1.100", {"ssid": ssid_32, "password": password_32}
        )

        expected_command = f"VMSL {ssid_32}{password_32}"
        mock_tcp.assert_called_once_with("192.168.1.100", 5001, expected_command)
