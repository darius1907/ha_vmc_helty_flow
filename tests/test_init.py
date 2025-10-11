"""Test per il modulo __init__."""

from datetime import timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.const import Platform

from custom_components.vmc_helty_flow import (
    DEFAULT_SCAN_INTERVAL,
    PLATFORMS,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.vmc_helty_flow.const import DOMAIN


class TestConstants:
    """Test per le costanti del modulo."""

    def test_platforms_constant(self):
        """Test che la costante PLATFORMS sia corretta."""
        expected_platforms = [
            Platform.FAN,
            Platform.SENSOR,
            Platform.SWITCH,
            Platform.LIGHT,
            Platform.BUTTON,
        ]
        assert expected_platforms == PLATFORMS
        assert len(PLATFORMS) == 5

    def test_default_scan_interval_constant(self):
        """Test che la costante DEFAULT_SCAN_INTERVAL sia corretta."""
        assert timedelta(seconds=180) == DEFAULT_SCAN_INTERVAL
        assert isinstance(DEFAULT_SCAN_INTERVAL, timedelta)


class TestAsyncSetupEntry:
    """Test per la funzione async_setup_entry."""

    @pytest.mark.asyncio
    async def test_setup_entry_successful(self):
        """Test setup entry con successo."""
        hass = Mock()
        hass.data = {}
        config_entry = Mock()
        config_entry.data = {"ip": "192.168.1.100", "name": "Test VMC"}
        config_entry.options = {"scan_interval": 60}
        config_entry.entry_id = "test_entry"

        with (
            patch(
                "custom_components.vmc_helty_flow.async_get_or_create_device"
            ) as mock_device,
            patch(
                "custom_components.vmc_helty_flow.async_setup_device_actions"
            ) as mock_actions,
            patch(
                "custom_components.vmc_helty_flow.VmcHeltyCoordinator"
            ) as mock_coordinator_class,
            patch.object(
                hass.config_entries, "async_forward_entry_setups", new=AsyncMock()
            ) as mock_forward,
        ):
            mock_device.return_value = Mock()
            mock_coordinator = Mock()
            mock_coordinator.async_config_entry_first_refresh = AsyncMock()
            mock_coordinator_class.return_value = mock_coordinator
            mock_forward.return_value = None

            result = await async_setup_entry(hass, config_entry)

            assert result is True
            assert DOMAIN in hass.data
            assert "test_entry" in hass.data[DOMAIN]
            mock_device.assert_called_once()
            mock_actions.assert_called_once()
            mock_forward.assert_called_once_with(config_entry, PLATFORMS)

    @pytest.mark.asyncio
    async def test_setup_entry_device_creation_error(self):
        """Test setup entry con errore nella creazione del dispositivo."""
        hass = Mock()
        hass.data = {}
        config_entry = Mock()
        config_entry.data = {"ip": "192.168.1.100", "name": "Test VMC"}
        config_entry.options = {"scan_interval": 60}
        config_entry.entry_id = "test_entry"

        with (
            patch(
                "custom_components.vmc_helty_flow.VmcHeltyCoordinator"
            ) as mock_coordinator_class,
            patch(
                "custom_components.vmc_helty_flow.async_get_or_create_device"
            ) as mock_device,
        ):
            # Setup coordinator mock
            mock_coordinator = Mock()
            mock_coordinator.async_config_entry_first_refresh = AsyncMock()
            mock_coordinator_class.return_value = mock_coordinator

            # Make device creation fail
            mock_device.side_effect = Exception("Device creation failed")

            # This should raise the exception, not return False
            with pytest.raises(Exception, match="Device creation failed"):
                await async_setup_entry(hass, config_entry)


class TestAsyncUnloadEntry:
    """Test per la funzione async_unload_entry."""

    @pytest.mark.asyncio
    async def test_unload_entry_successful(self):
        """Test unload entry con successo."""
        hass = Mock()
        hass.data = {DOMAIN: {"test_entry": Mock()}}
        config_entry = Mock()
        config_entry.entry_id = "test_entry"

        with patch.object(
            hass.config_entries, "async_unload_platforms", new=AsyncMock()
        ) as mock_unload:
            mock_unload.return_value = True

            result = await async_unload_entry(hass, config_entry)

            assert result is True
            assert "test_entry" not in hass.data[DOMAIN]
            mock_unload.assert_called_once_with(config_entry, PLATFORMS)

    @pytest.mark.asyncio
    async def test_unload_entry_platform_unload_failure(self):
        """Test unload entry con fallimento nell'unload delle platform."""
        hass = Mock()
        hass.data = {DOMAIN: {"test_entry": Mock()}}
        config_entry = Mock()
        config_entry.entry_id = "test_entry"

        with patch.object(
            hass.config_entries, "async_unload_platforms", new=AsyncMock()
        ) as mock_unload:
            mock_unload.return_value = False

            result = await async_unload_entry(hass, config_entry)

            assert result is False
            # I dati dovrebbero rimanere in caso di fallimento
            assert "test_entry" in hass.data[DOMAIN]
