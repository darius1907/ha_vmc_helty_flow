"""Tests for light module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.light import ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.vmc_helty_flow import light
from custom_components.vmc_helty_flow.const import DOMAIN
from custom_components.vmc_helty_flow.light import VmcHeltyLight, VmcHeltyLightTimer


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "TestVMC"
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.data = {
        "status": "VMGO,3,1,25,0,24,0,0,0,0,0,75,0,0,0,300",
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

    await light.async_setup_entry(mock_hass, mock_config_entry, async_add_entities)

    # Verify async_add_entities was called with entities
    async_add_entities.assert_called_once()
    entities = async_add_entities.call_args[0][0]

    # Should have 2 entities: light and light timer
    assert len(entities) == 2

    # Check entity types
    light_entities = [e for e in entities if isinstance(e, VmcHeltyLight)]
    timer_entities = [e for e in entities if isinstance(e, VmcHeltyLightTimer)]

    assert len(light_entities) == 1
    assert len(timer_entities) == 1


class TestVmcHeltyLight:
    """Test VmcHeltyLight class."""

    def test_init(self, mock_coordinator):
        """Test initialization."""
        light_entity = VmcHeltyLight(mock_coordinator)

        assert light_entity._attr_unique_id == "vmc_helty_testvmc_light"
        assert light_entity._attr_name == f"VMC Helty {mock_coordinator.name} Light"
        assert light_entity._attr_color_mode == ColorMode.BRIGHTNESS
        assert light_entity._attr_supported_color_modes == {ColorMode.BRIGHTNESS}

    def test_brightness_no_data(self, mock_coordinator):
        """Test brightness property when no data."""
        mock_coordinator.data = None
        light_entity = VmcHeltyLight(mock_coordinator)

        assert light_entity.brightness == 0

    def test_brightness_with_data(self, mock_coordinator):
        """Test brightness property with valid data."""
        # Light level 75 in position 11 -> 75 * 2.55 = 191.25 -> 191
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24,0,0,0,0,0,75,0,0,0,300"}
        light_entity = VmcHeltyLight(mock_coordinator)

        assert light_entity.brightness == 191

    def test_brightness_zero(self, mock_coordinator):
        """Test brightness property when light level is 0."""
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24,0,0,0,0,0,0,0,0,0,300"}
        light_entity = VmcHeltyLight(mock_coordinator)

        assert light_entity.brightness == 0

    def test_brightness_invalid_status(self, mock_coordinator):
        """Test brightness property with invalid status."""
        mock_coordinator.data = {"status": "INVALID"}
        light_entity = VmcHeltyLight(mock_coordinator)

        assert light_entity.brightness == 0

    def test_brightness_short_status(self, mock_coordinator):
        """Test brightness property with short status."""
        mock_coordinator.data = {"status": "VMGO,3,1,25"}
        light_entity = VmcHeltyLight(mock_coordinator)

        assert light_entity.brightness == 0

    def test_brightness_malformed_status(self, mock_coordinator):
        """Test brightness property with malformed data."""
        mock_coordinator.data = {
            "status": "VMGO,3,1,25,0,24,0,0,0,0,0,invalid,0,0,0,300"
        }
        light_entity = VmcHeltyLight(mock_coordinator)

        assert light_entity.brightness == 0

    def test_is_on_with_brightness(self, mock_coordinator):
        """Test is_on property when light has brightness."""
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24,0,0,0,0,0,50,0,0,0,300"}
        light_entity = VmcHeltyLight(mock_coordinator)

        assert light_entity.is_on is True

    def test_is_on_no_brightness(self, mock_coordinator):
        """Test is_on property when light has no brightness."""
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24,0,0,0,0,0,0,0,0,0,300"}
        light_entity = VmcHeltyLight(mock_coordinator)

        assert light_entity.is_on is False

    def test_is_on_no_data(self, mock_coordinator):
        """Test is_on property when no data."""
        mock_coordinator.data = None
        light_entity = VmcHeltyLight(mock_coordinator)

        assert light_entity.is_on is False

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_on_default_brightness(
        self, mock_tcp_send, mock_coordinator
    ):
        """Test async_turn_on with default brightness."""
        mock_tcp_send.return_value = "OK"
        light_entity = VmcHeltyLight(mock_coordinator)

        await light_entity.async_turn_on()

        # Default brightness 255 -> 100 (rounded to 25 step) -> VMWH06100000
        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH06100000")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_on_with_brightness(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with specific brightness."""
        mock_tcp_send.return_value = "OK"
        light_entity = VmcHeltyLight(mock_coordinator)

        # Brightness 128 -> ~50 -> rounded to 50
        await light_entity.async_turn_on(brightness=128)

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH06050000")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_on_low_brightness(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with low brightness."""
        mock_tcp_send.return_value = "OK"
        light_entity = VmcHeltyLight(mock_coordinator)

        # Brightness 32 -> ~12.5 -> rounded to 0
        await light_entity.async_turn_on(brightness=32)

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH06000000")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_on_mid_brightness(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with mid brightness."""
        mock_tcp_send.return_value = "OK"
        light_entity = VmcHeltyLight(mock_coordinator)

        # Brightness 191 -> ~75 -> rounded to 75
        await light_entity.async_turn_on(brightness=191)

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH06075000")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_on_failure(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with failed command."""
        mock_tcp_send.return_value = "ERROR"
        light_entity = VmcHeltyLight(mock_coordinator)

        await light_entity.async_turn_on()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH06100000")
        # Should not refresh on non-OK response
        mock_coordinator.async_request_refresh.assert_not_called()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_on_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        light_entity = VmcHeltyLight(mock_coordinator)

        with pytest.raises(Exception, match="Connection error"):
            await light_entity.async_turn_on()

        mock_coordinator.async_request_refresh.assert_not_called()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_off_success(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_off with successful command."""
        mock_tcp_send.return_value = "OK"
        light_entity = VmcHeltyLight(mock_coordinator)

        await light_entity.async_turn_off()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH0600000")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_off_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_off with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        light_entity = VmcHeltyLight(mock_coordinator)

        with pytest.raises(Exception, match="Connection error"):
            await light_entity.async_turn_off()


class TestVmcHeltyLightTimer:
    """Test VmcHeltyLightTimer class."""

    def test_init(self, mock_coordinator):
        """Test initialization."""
        timer_entity = VmcHeltyLightTimer(mock_coordinator)
        expected_id = "vmc_helty_testvmc_light_timer"
        assert timer_entity._attr_unique_id == expected_id
        assert (
            timer_entity._attr_name == f"VMC Helty {mock_coordinator.name} Light Timer"
        )
        assert timer_entity._attr_icon == "mdi:timer"

    def test_extra_state_attributes_no_data(self, mock_coordinator):
        """Test extra_state_attributes when no data."""
        mock_coordinator.data = None
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        assert timer_entity.extra_state_attributes == {}

    def test_extra_state_attributes_with_data(self, mock_coordinator):
        """Test extra_state_attributes with valid data."""
        # Timer value 300 in position 15
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24,0,0,0,0,0,75,0,0,0,300"}
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        assert timer_entity.extra_state_attributes == {"timer_seconds": 300}

    def test_extra_state_attributes_zero_timer(self, mock_coordinator):
        """Test extra_state_attributes when timer is 0."""
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24,0,0,0,0,0,75,0,0,0,0"}
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        assert timer_entity.extra_state_attributes == {"timer_seconds": 0}

    def test_extra_state_attributes_invalid_status(self, mock_coordinator):
        """Test extra_state_attributes with invalid status."""
        mock_coordinator.data = {"status": "INVALID"}
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        assert timer_entity.extra_state_attributes == {}

    def test_extra_state_attributes_short_status(self, mock_coordinator):
        """Test extra_state_attributes with short status."""
        mock_coordinator.data = {"status": "VMGO,3,1,25"}
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        assert timer_entity.extra_state_attributes == {"timer_seconds": 0}

    def test_extra_state_attributes_malformed_status(self, mock_coordinator):
        """Test extra_state_attributes with malformed data."""
        mock_coordinator.data = {
            "status": "VMGO,3,1,25,0,24,0,0,0,0,0,75,0,0,0,invalid"
        }
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        assert timer_entity.extra_state_attributes == {}

    def test_is_on_with_timer(self, mock_coordinator):
        """Test is_on property when timer is active."""
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24,0,0,0,0,0,75,0,0,0,300"}
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        assert timer_entity.is_on is True

    def test_is_on_no_timer(self, mock_coordinator):
        """Test is_on property when timer is not active."""
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24,0,0,0,0,0,75,0,0,0,0"}
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        assert timer_entity.is_on is False

    def test_is_on_no_data(self, mock_coordinator):
        """Test is_on property when no data."""
        mock_coordinator.data = None
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        assert timer_entity.is_on is False

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_on_success(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with successful command."""
        mock_tcp_send.return_value = "OK"
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        await timer_entity.async_turn_on()

        # Default timer 300 seconds
        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH1400300")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_on_failure(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with failed command."""
        mock_tcp_send.return_value = "ERROR"
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        await timer_entity.async_turn_on()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH1400300")
        # Should not refresh on non-OK response
        mock_coordinator.async_request_refresh.assert_not_called()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_on_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_on with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        with pytest.raises(Exception, match="Connection error"):
            await timer_entity.async_turn_on()

        mock_coordinator.async_request_refresh.assert_not_called()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_off_success(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_off with successful command."""
        mock_tcp_send.return_value = "OK"
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        await timer_entity.async_turn_off()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH1400000")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.light.tcp_send_command")
    async def test_async_turn_off_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_turn_off with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        timer_entity = VmcHeltyLightTimer(mock_coordinator)

        with pytest.raises(Exception, match="Connection error"):
            await timer_entity.async_turn_off()
