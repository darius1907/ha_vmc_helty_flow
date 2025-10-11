"""Test degli intervalli di aggiornamento differenziati."""

import time
from unittest.mock import Mock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.vmc_helty_flow.const import (
    NETWORK_INFO_UPDATE_INTERVAL,
    SENSORS_UPDATE_INTERVAL,
)
from custom_components.vmc_helty_flow.coordinator import VmcHeltyCoordinator
from custom_components.vmc_helty_flow.helpers import VMCConnectionError


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.loop = Mock()
    hass.loop.time = Mock(return_value=123456.0)
    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    config_entry = Mock(spec=ConfigEntry)
    config_entry.data = {
        "ip": "192.168.1.100",
        "name": "Test VMC",
    }
    config_entry.options = {"scan_interval": 60}
    return config_entry


@pytest.fixture
def coordinator(mock_hass, mock_config_entry):
    """Crea un coordinatore mock per i test."""
    with patch(
        "custom_components.vmc_helty_flow.coordinator.DataUpdateCoordinator.__init__"
    ) as mock_super_init:
        mock_super_init.return_value = None
        coord = VmcHeltyCoordinator(mock_hass, mock_config_entry)
        coord.hass = mock_hass
        return coord


class TestUpdateIntervals:
    """Test per gli intervalli di aggiornamento differenziati."""

    @pytest.mark.asyncio
    async def test_sensors_always_updated(self, coordinator):
        """Test che i sensori vengano sempre aggiornati."""
        sensors_response = (
            "VMGI,00251,00254,00510,00510,16384,05839,00249,"
            "00112,04354,00140,00203,00249,00510,00000,00001"
        )

        with patch(
            "custom_components.vmc_helty_flow.coordinator.tcp_send_command"
        ) as mock_tcp:
            mock_tcp.return_value = sensors_response

            result = await coordinator._get_additional_data()

            # I sensori devono essere sempre aggiornati
            assert result["sensors"] is not None
            assert result["sensors"].startswith("VMGI")

    @pytest.mark.asyncio
    async def test_network_info_cached_when_not_time(self, coordinator):
        """Test cache quando non è ora di aggiornare."""
        current_time = time.time()

        # Simula che l'ultimo aggiornamento sia avvenuto poco fa
        coordinator._last_name_update = current_time - 60  # 1 minuto fa
        coordinator._last_network_update = current_time - 60  # 1 minuto fa
        coordinator._cached_data = {
            "name": "VMNM cached_device",
            "network": "cached_network_data",
        }

        sensors_response = (
            "VMGI,00251,00254,00510,00510,16384,05839,00249,"
            "00112,04354,00140,00203,00249,00510,00000,00001"
        )

        with patch(
            "custom_components.vmc_helty_flow.coordinator.tcp_send_command"
        ) as mock_tcp:
            mock_tcp.return_value = sensors_response

            with patch("time.time", return_value=current_time):
                result = await coordinator._get_additional_data()

                # Solo i sensori dovrebbero essere aggiornati
                assert result["sensors"] is not None
                assert result["name"] == "VMNM cached_device"  # Dalla cache
                assert result["network"] == "cached_network_data"  # Dalla cache

                # tcp_send_command chiamato solo per i sensori
                assert mock_tcp.call_count == 1
                mock_tcp.assert_called_with(coordinator.ip, 5001, "VMGI?")

    @pytest.mark.asyncio
    async def test_network_info_updated_after_interval(self, coordinator):
        """Test aggiornamento dopo l'intervallo."""
        current_time = time.time()

        # Simula che l'ultimo aggiornamento sia avvenuto più dell'intervallo fa
        old_time = current_time - NETWORK_INFO_UPDATE_INTERVAL - 10
        coordinator._last_name_update = old_time
        coordinator._last_network_update = old_time

        responses = [
            (
                "VMGI,00251,00254,00510,00510,16384,05839,00249,"
                "00112,04354,00140,00203,00249,00510,00000,00001"
            ),
            "VMNM new_device",
            "new_network_data",
        ]

        with patch(
            "custom_components.vmc_helty_flow.coordinator.tcp_send_command"
        ) as mock_tcp:
            mock_tcp.side_effect = responses

            with patch("time.time", return_value=current_time):
                result = await coordinator._get_additional_data()

                # Tutto dovrebbe essere aggiornato
                assert result["sensors"] is not None
                assert result["name"] == "VMNM new_device"  # Nuovo valore
                assert result["network"] == "new_network_data"  # Nuovo valore

                # tcp_send_command chiamato per tutti e 3 i comandi
                assert mock_tcp.call_count == 3

                # Verifica che la cache sia stata aggiornata
                assert coordinator._cached_data["name"] == "VMNM new_device"
                assert coordinator._cached_data["network"] == "new_network_data"

    @pytest.mark.asyncio
    async def test_cache_not_updated_on_error(self, coordinator):
        """Test che la cache non venga aggiornata se il comando fallisce."""
        current_time = time.time()
        old_cached_name = "VMNM old_cached"
        old_cached_network = "old_cached_network"

        coordinator._cached_data = {
            "name": old_cached_name,
            "network": old_cached_network,
        }

        responses = [
            (
                "VMGI,00251,00254,00510,00510,16384,05839,00249,"
                "00112,04354,00140,00203,00249,00510,00000,00001"
            ),
            VMCConnectionError("Error getting name"),
            VMCConnectionError("Error getting network"),
        ]

        with patch(
            "custom_components.vmc_helty_flow.helpers.tcp_send_command"
        ) as mock_tcp:
            mock_tcp.side_effect = responses

            with patch("time.time", return_value=current_time):
                await coordinator._get_additional_data()

                # La cache non dovrebbe essere cambiata
                assert coordinator._cached_data["name"] == old_cached_name
                assert coordinator._cached_data["network"] == old_cached_network

    def test_update_intervals_constants(self):
        """Test che le costanti degli intervalli siano configurate correttamente."""
        assert SENSORS_UPDATE_INTERVAL == 180  # 3 minuti
        assert NETWORK_INFO_UPDATE_INTERVAL == 900  # 15 minuti
