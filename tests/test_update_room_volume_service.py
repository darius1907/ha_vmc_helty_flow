"""Test update room volume service."""

import pytest
from unittest.mock import MagicMock

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.vmc_helty_flow import async_setup_volume_service
from custom_components.vmc_helty_flow.const import DOMAIN


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()
    hass.helpers = MagicMock()
    hass.config_entries = MagicMock()
    return hass


@pytest.fixture
def mock_entity_registry():
    """Create a mock entity registry."""
    registry = MagicMock()
    return registry


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    config_entry = MagicMock(spec=ConfigEntry)
    config_entry.domain = DOMAIN
    config_entry.data = {
        "ip": "192.168.1.100",
        "name": "Test VMC",
        "room_volume": 60.0,
    }
    return config_entry


@pytest.fixture
def mock_entity_entry():
    """Create a mock entity entry."""
    entity_entry = MagicMock()
    entity_entry.config_entry_id = "test_config_entry_id"
    return entity_entry


class TestUpdateRoomVolumeService:
    """Test class for update room volume service."""

    async def test_async_setup_volume_service_registers_service(self, mock_hass):
        """Test that service setup registers the service correctly."""
        await async_setup_volume_service(mock_hass)

        # Verify service was registered
        mock_hass.services.async_register.assert_called_once()
        call_args = mock_hass.services.async_register.call_args
        
        assert call_args[0][0] == DOMAIN  # domain
        assert call_args[0][1] == "update_room_volume"  # service name
        assert callable(call_args[0][2])  # handler function
        assert "schema" in call_args[1]  # schema in kwargs

    async def test_handle_update_room_volume_success(
        self, mock_hass, mock_entity_registry, mock_config_entry, mock_entity_entry
    ):
        """Test successful room volume update."""
        # Setup mocks
        mock_hass.helpers.entity_registry.async_get.return_value = mock_entity_registry
        mock_entity_registry.async_get.return_value = mock_entity_entry
        mock_hass.config_entries.async_get_entry.return_value = mock_config_entry
        mock_hass.config_entries.async_update_entry = MagicMock()

        # Setup service
        await async_setup_volume_service(mock_hass)
        
        # Get the registered handler
        handler = mock_hass.services.async_register.call_args[0][2]
        
        # Create service call mock
        service_call = MagicMock()
        service_call.data = {
            "entity_id": "fan.test_vmc",
            "room_volume": 85.5
        }

        # Call the handler
        await handler(service_call)

        # Verify config entry was updated
        mock_hass.config_entries.async_update_entry.assert_called_once()
        call_args = mock_hass.config_entries.async_update_entry.call_args
        assert call_args[0][0] == mock_config_entry  # config entry
        assert call_args[1]["data"]["room_volume"] == 85.5  # new volume

    async def test_handle_update_room_volume_entity_not_found(
        self, mock_hass, mock_entity_registry
    ):
        """Test handling when entity is not found."""
        # Setup mocks
        mock_hass.helpers.entity_registry.async_get.return_value = mock_entity_registry
        mock_entity_registry.async_get.return_value = None  # Entity not found

        # Setup service
        await async_setup_volume_service(mock_hass)
        
        # Get the registered handler
        handler = mock_hass.services.async_register.call_args[0][2]
        
        # Create service call mock
        service_call = MagicMock()
        service_call.data = {
            "entity_id": "fan.nonexistent",
            "room_volume": 85.5
        }

        # Verify exception is raised
        with pytest.raises(HomeAssistantError, match="Entity fan.nonexistent not found"):
            await handler(service_call)

    async def test_handle_update_room_volume_wrong_domain(
        self, mock_hass, mock_entity_registry, mock_entity_entry
    ):
        """Test handling when entity is from wrong domain."""
        # Setup mocks
        mock_hass.helpers.entity_registry.async_get.return_value = mock_entity_registry
        mock_entity_registry.async_get.return_value = mock_entity_entry
        
        # Wrong domain config entry
        wrong_config_entry = MagicMock(spec=ConfigEntry)
        wrong_config_entry.domain = "other_domain"
        mock_hass.config_entries.async_get_entry.return_value = wrong_config_entry

        # Setup service
        await async_setup_volume_service(mock_hass)
        
        # Get the registered handler
        handler = mock_hass.services.async_register.call_args[0][2]
        
        # Create service call mock
        service_call = MagicMock()
        service_call.data = {
            "entity_id": "fan.wrong_domain",
            "room_volume": 85.5
        }

        # Verify exception is raised
        with pytest.raises(HomeAssistantError, match="is not from VMC Helty Flow integration"):
            await handler(service_call)

    async def test_handle_update_room_volume_config_entry_not_found(
        self, mock_hass, mock_entity_registry, mock_entity_entry
    ):
        """Test handling when config entry is not found."""
        # Setup mocks
        mock_hass.helpers.entity_registry.async_get.return_value = mock_entity_registry
        mock_entity_registry.async_get.return_value = mock_entity_entry
        mock_hass.config_entries.async_get_entry.return_value = None  # Not found

        # Setup service
        await async_setup_volume_service(mock_hass)
        
        # Get the registered handler
        handler = mock_hass.services.async_register.call_args[0][2]
        
        # Create service call mock
        service_call = MagicMock()
        service_call.data = {
            "entity_id": "fan.test_vmc",
            "room_volume": 85.5
        }

        # Verify exception is raised
        with pytest.raises(HomeAssistantError, match="is not from VMC Helty Flow integration"):
            await handler(service_call)


if __name__ == "__main__":
    pytest.main([__file__])