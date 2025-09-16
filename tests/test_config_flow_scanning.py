"""Test per il nuovo step scanning del config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.vmc_helty_flow.config_flow import VmcHeltyFlowConfigFlow
from custom_components.vmc_helty_flow.const import DOMAIN


def mock_vmc_device():
    """Mock device for testing."""
    return {
        "ip": "192.168.1.100",
        "model": "Helty Flow Elite",
        "version": "1.2.3",
        "mac": "AA:BB:CC:DD:EE:FF",
        "product_code": "HFE200",
        "serial_number": "TEST12345",
        "network_password": "password123",
    }


class TestConfigFlowScanning:
    """Test del nuovo step scanning del config flow."""

    async def test_scanning_step_initial_form(self, hass: HomeAssistant):
        """Test che lo step scanning mostri il form iniziale."""
        flow = VmcHeltyFlowConfigFlow()
        flow.hass = hass
        flow.subnet = "192.168.1"
        flow.port = 5001
        flow.timeout = 10

        # Test che il form iniziale venga mostrato
        result = await flow.async_step_scanning()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "scanning"
        assert "subnet" in result["description_placeholders"]
        assert result["description_placeholders"]["subnet"] == "192.168.1"
        assert result["description_placeholders"]["port"] == "5001"

    @patch(
        "custom_components.vmc_helty_flow.config_flow.discover_vmc_devices_with_progress"
    )
    async def test_scanning_step_with_devices_found(
        self, mock_discover, hass: HomeAssistant, mock_vmc_device
    ):
        """Test dello step scanning quando vengono trovati dispositivi."""
        mock_discover.return_value = [mock_vmc_device]

        flow = VmcHeltyFlowConfigFlow()
        flow.hass = hass
        flow.subnet = "192.168.1"
        flow.port = 5001
        flow.timeout = 10

        # Simula il submit del form
        result = await flow.async_step_scanning(user_input={})

        # Dovrebbe procedere al discovery_results step
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "discovery_results"

        # Verifica che i dispositivi siano stati memorizzati
        assert flow.discovered_devices == [mock_vmc_device]

        # Verifica che discover sia stato chiamato con i parametri corretti
        mock_discover.assert_called_once_with("192.168.1", 5001, 10)

    @patch(
        "custom_components.vmc_helty_flow.config_flow.discover_vmc_devices_with_progress"
    )
    async def test_scanning_step_no_devices_found(
        self, mock_discover, hass: HomeAssistant
    ):
        """Test dello step scanning quando non vengono trovati dispositivi."""
        mock_discover.return_value = []

        flow = VmcHeltyFlowConfigFlow()
        flow.hass = hass
        flow.subnet = "192.168.1"
        flow.port = 5001
        flow.timeout = 10

        # Simula il submit del form
        result = await flow.async_step_scanning(user_input={})

        # Dovrebbe mostrare un errore e rimanere sullo stesso step
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "scanning"
        assert "nessun_dispositivo_trovato" in result["errors"]["base"]

    @patch(
        "custom_components.vmc_helty_flow.config_flow.discover_vmc_devices_with_progress"
    )
    async def test_scanning_step_discovery_error(
        self, mock_discover, hass: HomeAssistant
    ):
        """Test dello step scanning quando si verifica un errore durante la discovery."""
        mock_discover.side_effect = Exception("Connection error")

        flow = VmcHeltyFlowConfigFlow()
        flow.hass = hass
        flow.subnet = "192.168.1"
        flow.port = 5001
        flow.timeout = 10

        # Simula il submit del form
        result = await flow.async_step_scanning(user_input={})

        # Dovrebbe mostrare un errore
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "scanning"
        assert "errore_discovery" in result["errors"]["base"]

    async def test_handle_discovery_input_calls_scanning(self, hass: HomeAssistant):
        """Test che _handle_discovery_input reindirizza allo step scanning."""
        flow = VmcHeltyFlowConfigFlow()
        flow.hass = hass
        flow.subnet = "192.168.1"
        flow.port = 5001
        flow.timeout = 10

        errors = {}
        result = await flow._handle_discovery_input({}, errors)

        # Dovrebbe reindirizzare allo step scanning
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "scanning"

    async def test_full_flow_with_scanning_step(
        self, hass: HomeAssistant, mock_vmc_device
    ):
        """Test del flusso completo incluso il nuovo step scanning."""

        with patch(
            "custom_components.vmc_helty_flow.config_flow.discover_vmc_devices_with_progress"
        ) as mock_discover:
            mock_discover.return_value = [mock_vmc_device]

            # Inizio config flow
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "user"

            # Submit parametri di configurazione
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"subnet": "192.168.1.0/24", "port": 5001, "timeout": 10},
            )

            # Dovrebbe mostrare lo step scanning
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "scanning"

            # Submit del form scanning
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"], user_input={}
            )

            # Dovrebbe procedere al discovery_results
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "discovery_results"
