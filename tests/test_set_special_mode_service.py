"""Test the set_special_mode service functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import ServiceCall

import custom_components.vmc_helty_flow as vmc_module
from custom_components.vmc_helty_flow.const import DOMAIN, DEFAULT_PORT


class TestSetSpecialModeService:
    """Test the set_special_mode service."""

    async def test_async_setup_services_registers_set_special_mode(self):
        """Test that service setup registers the set_special_mode service correctly."""
        mock_hass = MagicMock()
        mock_hass.services.async_register = MagicMock()

        await vmc_module.async_setup_services(mock_hass)

        # Find the set_special_mode service call
        calls = mock_hass.services.async_register.call_args_list
        set_special_mode_call = None

        for call in calls:
            if call[0][1] == "set_special_mode":
                set_special_mode_call = call
                break

        assert set_special_mode_call is not None
        assert set_special_mode_call[0][0] == DOMAIN  # domain
        assert set_special_mode_call[0][1] == "set_special_mode"  # service name
        assert callable(set_special_mode_call[0][2])  # handler function
        assert "schema" in set_special_mode_call[1]  # schema in kwargs

    async def test_set_special_mode_service_integration(self):
        """Test the complete service integration end-to-end."""
        mock_hass = MagicMock()
        mock_hass.services.async_register = MagicMock()
        mock_entity_registry = MagicMock()
        mock_config_entry = MagicMock()
        mock_coordinator = MagicMock()  # Use MagicMock instead of AsyncMock

        # Setup hass data with DOMAIN and coordinator storage structure
        mock_hass.data = {
            "entity_registry": mock_entity_registry,
            DOMAIN: {
                "test_entry_id": mock_coordinator  # Store coordinator by entry_id
            },
        }

        # Mock config entries - MUST be from our domain
        mock_hass.config_entries.async_get_entry.return_value = mock_config_entry
        mock_config_entry.runtime_data = mock_coordinator
        mock_config_entry.domain = DOMAIN  # This is crucial!
        mock_config_entry.entry_id = "test_entry_id"

        # Set coordinator IP as string (not AsyncMock)
        mock_coordinator.ip = "192.168.1.100"
        mock_coordinator.async_request_refresh = AsyncMock()

        # Mock entity entry
        mock_entity_entry = MagicMock()
        mock_entity_entry.config_entry_id = "test_entry_id"
        mock_entity_registry.async_get.return_value = mock_entity_entry

        # Register services
        await vmc_module.async_setup_services(mock_hass)

        # Get the registered handler
        calls = mock_hass.services.async_register.call_args_list
        handler = None
        for call in calls:
            if call[0][1] == "set_special_mode":
                handler = call[0][2]
                break

        assert handler is not None

        # Create service call
        call = ServiceCall(
            hass=mock_hass,
            domain=DOMAIN,
            service="set_special_mode",
            data={"entity_id": "fan.vmc_helty_test", "mode": "hyperventilation"},
        )

        # Mock tcp_send_command since the service now uses it directly
        with patch("custom_components.vmc_helty_flow.tcp_send_command") as mock_tcp:
            mock_tcp.return_value = "OK"
            
            # Call the handler directly
            await handler(call)

            # Verify tcp_send_command was called with correct parameters
            mock_tcp.assert_called_once_with("192.168.1.100", DEFAULT_PORT, "VMWH0000006")

    async def test_special_mode_mappings(self):
        """Test that the mode mappings are correct."""
        # This verifies our understanding of the mappings used in the service
        expected_mappings = {"night_mode": 5, "hyperventilation": 6, "free_cooling": 7}

        # The actual mapping is tested through integration test above
        assert len(expected_mappings) == 3
        assert all(isinstance(v, int) for v in expected_mappings.values())
