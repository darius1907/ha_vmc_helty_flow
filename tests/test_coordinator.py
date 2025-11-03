"""Test per il modulo coordinator.py."""

from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.vmc_helty_flow.coordinator import VmcHeltyCoordinator
from custom_components.vmc_helty_flow.helpers import VMCConnectionError


@patch("custom_components.vmc_helty_flow.helpers.tcp_send_command")
class TestVmcHeltyCoordinator:
    """Test per la classe VmcHeltyCoordinator."""

    def setup_method(self, _mock_tcp):
        """Set up test fixtures."""
        self.hass = Mock(spec=HomeAssistant)
        self.hass.loop = Mock()
        self.hass.loop.time = Mock(return_value=123456.0)
        self.config_entry = Mock(spec=ConfigEntry)
        self.config_entry.data = {
            "ip": "192.168.1.100",
            "name": "Test VMC",
            "port": 5001,
            "room_volume": 60.0,
        }
        self.config_entry.title = "VMC Test Device"
        self.config_entry.options = {"scan_interval": 60}

    @patch(
        "custom_components.vmc_helty_flow.coordinator.DataUpdateCoordinator.__init__"
    )
    def test_init(self, mock_super_init, _mock_tcp):
        """Test inizializzazione del coordinator."""
        mock_super_init.return_value = None

        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)

        mock_super_init.assert_called_once()
        assert coordinator.config_entry == self.config_entry
        assert coordinator.ip == "192.168.1.100"
        assert coordinator.name == "Test VMC"
        assert coordinator.device_entry is None
        assert coordinator._consecutive_errors == 0

    @patch(
        "custom_components.vmc_helty_flow.coordinator.DataUpdateCoordinator.__init__"
    )
    @patch("custom_components.vmc_helty_flow.coordinator.tcp_send_command")
    @pytest.mark.asyncio
    async def test_update_data_successful(
        self, mock_tcp_send, mock_super_init, _mock_tcp
    ):
        """Test aggiornamento dati con successo."""
        mock_super_init.return_value = None
        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        coordinator._consecutive_errors = 0
        # Mock the missing attributes
        coordinator._update_interval = timedelta(seconds=60)
        coordinator._normal_update_interval = timedelta(seconds=60)
        coordinator.hass = self.hass

        async def tcp_response(*_args, **_kwargs):
            return "VMGO,2,1,0,0,1,0"

        mock_tcp_send.side_effect = tcp_response

        result = await coordinator._async_update_data()
        assert result["status"] == "VMGO,2,1,0,0,1,0"
        assert coordinator._consecutive_errors == 0

    @patch(
        "custom_components.vmc_helty_flow.coordinator.DataUpdateCoordinator.__init__"
    )
    @pytest.mark.asyncio
    async def test_update_data_connection_error(self, mock_super_init, mock_tcp):
        """Test aggiornamento dati con errore di connessione."""
        mock_super_init.return_value = None
        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        coordinator._consecutive_errors = 0

        mock_tcp.side_effect = VMCConnectionError("Connection failed")
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
        assert coordinator._consecutive_errors == 1

    @patch(
        "custom_components.vmc_helty_flow.coordinator.DataUpdateCoordinator.__init__"
    )
    @pytest.mark.asyncio
    async def test_update_data_multiple_errors(self, mock_super_init, mock_tcp):
        """Test aggiornamento dati con errori multipli."""
        mock_super_init.return_value = None
        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        coordinator._consecutive_errors = 0

        mock_tcp.side_effect = VMCConnectionError("Connection failed")
        # Primo errore
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
        assert coordinator._consecutive_errors == 1
        # Secondo errore
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
        assert coordinator._consecutive_errors == 2

    @patch(
        "custom_components.vmc_helty_flow.coordinator.DataUpdateCoordinator.__init__"
    )
    @patch("custom_components.vmc_helty_flow.coordinator.tcp_send_command")
    @pytest.mark.asyncio
    async def test_update_data_recovery_after_error(
        self, mock_tcp_send, mock_super_init, _mock_tcp
    ):
        """Test recupero dopo errore."""
        mock_super_init.return_value = None
        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        coordinator._consecutive_errors = 2
        # Mock the missing attributes
        coordinator._update_interval = timedelta(seconds=30)  # Recovery interval
        coordinator._normal_update_interval = timedelta(seconds=60)
        coordinator.hass = self.hass

        async def tcp_response(*_args, **_kwargs):
            return "VMGO,1,0,1,0,0,1"

        mock_tcp_send.side_effect = tcp_response

        result = await coordinator._async_update_data()
        assert result["status"] == "VMGO,1,0,1,0,0,1"
        assert coordinator._consecutive_errors == 0

    @patch(
        "custom_components.vmc_helty_flow.coordinator.DataUpdateCoordinator.__init__"
    )
    def test_coordinator_properties(self, mock_super_init, _mock_tcp):
        """Test proprietà del coordinator."""
        mock_super_init.return_value = None
        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        # Mock the missing attributes
        coordinator.hass = self.hass

        assert coordinator.hass == self.hass
        assert coordinator.config_entry == self.config_entry
        assert coordinator.ip == "192.168.1.100"
        assert coordinator.name == "Test VMC"
