"""Tests for switch module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.vmc_helty_flow import switch
from custom_components.vmc_helty_flow.const import DOMAIN
from custom_components.vmc_helty_flow.switch import (
    MODES,
    VmcHeltyModeSwitch,
    VmcHeltyPanelLedSwitch,
    VmcHeltySensorsSwitch,
)


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "VMC Test"
    coordinator.data = {
        "status": "VMGO,3,1,25,0,24",
        "temperature": 22.5,
    }
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {DOMAIN: {"test_entry": "mock_coordinator"}}
    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry"
    return entry


@pytest.mark.asyncio
async def test_async_setup_entry(mock_hass, mock_config_entry, mock_coordinator):
    """Test async_setup_entry creates all expected entities."""
    # Setup coordinator in hass.data
    mock_hass.data[DOMAIN][mock_config_entry.entry_id] = mock_coordinator

    async_add_entities = MagicMock()

    await switch.async_setup_entry(mock_hass, mock_config_entry, async_add_entities)

    # Verify async_add_entities was called with entities
    async_add_entities.assert_called_once()
    entities = async_add_entities.call_args[0][0]

    # Should have 5 entities: 3 mode switches + 2 other switches
    assert len(entities) == 5

    # Check entity types
    mode_switches = [e for e in entities if isinstance(e, VmcHeltyModeSwitch)]
    panel_switches = [e for e in entities if isinstance(e, VmcHeltyPanelLedSwitch)]
    sensor_switches = [e for e in entities if isinstance(e, VmcHeltySensorsSwitch)]

    assert len(mode_switches) == 3
    assert len(panel_switches) == 1
    assert len(sensor_switches) == 1


def test_modes_constant():
    """Test MODES constant has expected structure."""
    assert "hyperventilation" in MODES
    assert "night" in MODES
    assert "free_cooling" in MODES

    for _mode_key, mode_data in MODES.items():
        assert "cmd" in mode_data
        assert "fan_value" in mode_data
        assert "name" in mode_data
        assert isinstance(mode_data["fan_value"], int)
        assert isinstance(mode_data["cmd"], str)


class TestVmcHeltyModeSwitch:
    """Test VmcHeltyModeSwitch class."""

    def test_init(self, mock_coordinator):
        """Test initialization."""
        mock_coordinator.name_slug = "vmc_helty_testvmc"
        switch_entity = VmcHeltyModeSwitch(
            mock_coordinator, "hyperventilation", "Iperventilazione"
        )

        assert switch_entity._mode_key == "hyperventilation"
        expected_id = "vmc_helty_testvmc_hyperventilation"
        assert switch_entity._attr_unique_id == expected_id
        expected_name = f"VMC Helty {mock_coordinator.name} Iperventilazione"
        assert switch_entity._attr_name == expected_name
        assert switch_entity._attr_icon == "mdi:fan-plus"

    def test_get_mode_icon(self, mock_coordinator):
        """Test _get_mode_icon method."""
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        assert switch_entity._get_mode_icon("hyperventilation") == "mdi:fan-plus"
        assert switch_entity._get_mode_icon("night") == "mdi:weather-night"
        assert switch_entity._get_mode_icon("free_cooling") == "mdi:snowflake"
        assert switch_entity._get_mode_icon("unknown") == "mdi:toggle-switch"

    def test_is_on_no_data(self, mock_coordinator):
        """Test is_on property when no data."""
        mock_coordinator.data = None
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        assert switch_entity.is_on is False

    def test_is_on_hyperventilation_active(self, mock_coordinator):
        """Test is_on property when hyperventilation is active."""
        # fan_value 6 = hyperventilation
        mock_coordinator.data = {"status": "VMGO,6,1,25,0,24"}
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        assert switch_entity.is_on is True

    def test_is_on_hyperventilation_inactive(self, mock_coordinator):
        """Test is_on property when hyperventilation is inactive."""
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24"}  # fan_value 3, not 6
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        assert switch_entity.is_on is False

    def test_is_on_night_active(self, mock_coordinator):
        """Test is_on property when night mode is active."""
        mock_coordinator.data = {"status": "VMGO,5,1,25,0,24"}  # fan_value 5 = night
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "night", "Test")

        assert switch_entity.is_on is True

    def test_is_on_invalid_status(self, mock_coordinator):
        """Test is_on property with invalid status."""
        mock_coordinator.data = {"status": "INVALID"}
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        assert switch_entity.is_on is False

    def test_is_on_malformed_status(self, mock_coordinator):
        """Test is_on property with malformed status."""
        mock_coordinator.data = {"status": "VMGO,invalid,1,25,0,24"}
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        assert switch_entity.is_on is False

    def test_is_on_short_status(self, mock_coordinator):
        """Test is_on property with short status."""
        mock_coordinator.data = {"status": "VMGO"}
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        assert switch_entity.is_on is False

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_on_success(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with successful command."""
        mock_tcp_send.return_value = "OK"
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        await switch_entity.async_turn_on()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH0000005")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_on_failure(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with failed command."""
        mock_tcp_send.return_value = "ERROR"
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        await switch_entity.async_turn_on()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH0000005")
        # Should not refresh on non-OK response
        mock_coordinator.async_request_refresh.assert_not_called()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_on_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        with pytest.raises(Exception, match="Connection error"):
            await switch_entity.async_turn_on()

        mock_coordinator.async_request_refresh.assert_not_called()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_off_success(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_off with successful command."""
        mock_tcp_send.return_value = "OK"
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        await switch_entity.async_turn_off()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH0000001")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_off_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_off with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        switch_entity = VmcHeltyModeSwitch(mock_coordinator, "hyperventilation", "Test")

        with pytest.raises(Exception, match="Connection error"):
            await switch_entity.async_turn_off()


class TestVmcHeltyPanelLedSwitch:
    """Test VmcHeltyPanelLedSwitch class."""

    def test_init(self, mock_coordinator):
        """Test initialization."""
        mock_coordinator.name_slug = "vmc_helty_testvmc"
        switch_entity = VmcHeltyPanelLedSwitch(mock_coordinator)

        expected_id = "vmc_helty_testvmc_panel_led"
        assert switch_entity._attr_unique_id == expected_id
        expected_name = f"VMC Helty {mock_coordinator.name} Panel LED"
        assert switch_entity._attr_name == expected_name
        assert switch_entity._attr_icon == "mdi:led-on"

    def test_is_on_no_data(self, mock_coordinator):
        """Test is_on property when no data."""
        mock_coordinator.data = None
        switch_entity = VmcHeltyPanelLedSwitch(mock_coordinator)

        assert switch_entity.is_on is False

    def test_is_on_led_active(self, mock_coordinator):
        """Test is_on property when LED is active."""
        # LED on (position 2 = "1")
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24"}
        switch_entity = VmcHeltyPanelLedSwitch(mock_coordinator)

        assert switch_entity.is_on is True

    def test_is_on_led_inactive(self, mock_coordinator):
        """Test is_on property when LED is inactive."""
        # LED off (position 2 = "0")
        mock_coordinator.data = {"status": "VMGO,3,0,25,0,24"}
        switch_entity = VmcHeltyPanelLedSwitch(mock_coordinator)

        assert switch_entity.is_on is False

    def test_is_on_invalid_status(self, mock_coordinator):
        """Test is_on property with invalid status."""
        mock_coordinator.data = {"status": "INVALID"}
        switch_entity = VmcHeltyPanelLedSwitch(mock_coordinator)

        assert switch_entity.is_on is False

    def test_is_on_short_status(self, mock_coordinator):
        """Test is_on property with short status."""
        mock_coordinator.data = {"status": "VMGO,3"}
        switch_entity = VmcHeltyPanelLedSwitch(mock_coordinator)

        assert switch_entity.is_on is False

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_on_success(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with successful command."""
        mock_tcp_send.return_value = "OK"
        switch_entity = VmcHeltyPanelLedSwitch(mock_coordinator)

        await switch_entity.async_turn_on()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH0100010")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_off_success(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_off with successful command."""
        mock_tcp_send.return_value = "OK"
        switch_entity = VmcHeltyPanelLedSwitch(mock_coordinator)

        await switch_entity.async_turn_off()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH0100000")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_on_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        switch_entity = VmcHeltyPanelLedSwitch(mock_coordinator)

        with pytest.raises(Exception, match="Connection error"):
            await switch_entity.async_turn_on()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_off_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_off with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        switch_entity = VmcHeltyPanelLedSwitch(mock_coordinator)

        with pytest.raises(Exception, match="Connection error"):
            await switch_entity.async_turn_off()


class TestVmcHeltySensorsSwitch:
    """Test VmcHeltySensorsSwitch class."""

    def test_init(self, mock_coordinator):
        """Test initialization."""
        mock_coordinator.name_slug = "vmc_helty_testvmc"
        switch_entity = VmcHeltySensorsSwitch(mock_coordinator)

        expected_id = "vmc_helty_testvmc_sensors"
        assert switch_entity._attr_unique_id == expected_id
        expected_name = f"VMC Helty {mock_coordinator.name} Sensors"
        assert switch_entity._attr_name == expected_name
        assert switch_entity._attr_icon == "mdi:eye"

    def test_is_on_no_data(self, mock_coordinator):
        """Test is_on property when no data (default True)."""
        mock_coordinator.data = None
        switch_entity = VmcHeltySensorsSwitch(mock_coordinator)

        assert switch_entity.is_on is True

    def test_is_on_sensors_active(self, mock_coordinator):
        """Test is_on property when sensors are active."""
        # Sensors active (position 4 = "0")
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24"}
        switch_entity = VmcHeltySensorsSwitch(mock_coordinator)

        assert switch_entity.is_on is True

    def test_is_on_sensors_inactive(self, mock_coordinator):
        """Test is_on property when sensors are inactive."""
        # Sensors inactive (position 4 = "1")
        mock_coordinator.data = {"status": "VMGO,3,1,25,1,24"}
        switch_entity = VmcHeltySensorsSwitch(mock_coordinator)

        assert switch_entity.is_on is False

    def test_is_on_invalid_status(self, mock_coordinator):
        """Test is_on property with invalid status (default True)."""
        mock_coordinator.data = {"status": "INVALID"}
        switch_entity = VmcHeltySensorsSwitch(mock_coordinator)

        assert switch_entity.is_on is True

    def test_is_on_short_status(self, mock_coordinator):
        """Test is_on property with short status (default True)."""
        mock_coordinator.data = {"status": "VMGO,3,1,25"}
        switch_entity = VmcHeltySensorsSwitch(mock_coordinator)

        assert switch_entity.is_on is True

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_on_success(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with successful command."""
        mock_tcp_send.return_value = "OK"
        switch_entity = VmcHeltySensorsSwitch(mock_coordinator)

        await switch_entity.async_turn_on()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH0300000")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_off_success(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_off with successful command."""
        mock_tcp_send.return_value = "OK"
        switch_entity = VmcHeltySensorsSwitch(mock_coordinator)

        await switch_entity.async_turn_off()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH0300002")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_on_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        switch_entity = VmcHeltySensorsSwitch(mock_coordinator)

        with pytest.raises(Exception, match="Connection error"):
            await switch_entity.async_turn_on()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.switch.tcp_send_command")
    async def test_async_turn_off_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_off with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        switch_entity = VmcHeltySensorsSwitch(mock_coordinator)

        with pytest.raises(Exception, match="Connection error"):
            await switch_entity.async_turn_off()
