"""Tests for button module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.vmc_helty_flow import button
from custom_components.vmc_helty_flow.button import VmcHeltyResetFilterButton
from custom_components.vmc_helty_flow.const import DOMAIN


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "VMC Test"
    coordinator.data = {"status": "VMGO,3,1,25,0,24"}
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

    await button.async_setup_entry(mock_hass, mock_config_entry, async_add_entities)

    # Verify async_add_entities was called with entities
    async_add_entities.assert_called_once()
    entities = async_add_entities.call_args[0][0]

    # Should have 1 entity: reset filter button
    assert len(entities) == 1

    # Check entity type
    assert isinstance(entities[0], VmcHeltyResetFilterButton)


class TestVmcHeltyResetFilterButton:
    """Test VmcHeltyResetFilterButton class."""

    def test_init(self, mock_coordinator):
        """Test initialization."""
        button_entity = VmcHeltyResetFilterButton(mock_coordinator)

        assert button_entity._attr_unique_id == "192.168.1.100_reset_filter"
        assert button_entity._attr_name == "VMC Test Reset Filter"
        assert button_entity._attr_icon == "mdi:air-filter"

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.button.tcp_send_command")
    async def test_async_press_success(self, mock_tcp_send, mock_coordinator):
        """Test async_press with successful command."""
        mock_tcp_send.return_value = "OK"
        button_entity = VmcHeltyResetFilterButton(mock_coordinator)

        await button_entity.async_press()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH0417744")
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.button.tcp_send_command")
    async def test_async_press_failure(self, mock_tcp_send, mock_coordinator):
        """Test async_press with failed command."""
        mock_tcp_send.return_value = "ERROR"
        button_entity = VmcHeltyResetFilterButton(mock_coordinator)

        await button_entity.async_press()

        mock_tcp_send.assert_called_once_with("192.168.1.100", 5001, "VMWH0417744")
        # Should not refresh on non-OK response
        mock_coordinator.async_request_refresh.assert_not_called()

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.button.tcp_send_command")
    async def test_async_press_exception(self, mock_tcp_send, mock_coordinator):
        """Test async_press with exception."""
        mock_tcp_send.side_effect = Exception("Connection error")
        button_entity = VmcHeltyResetFilterButton(mock_coordinator)

        with pytest.raises(Exception, match="Connection error"):
            await button_entity.async_press()

        mock_coordinator.async_request_refresh.assert_not_called()
