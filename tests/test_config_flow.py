"""Test config flow for VMC Helty Flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.vmc_helty_flow.config_flow import (
    MAX_IPS_IN_SUBNET,
    MAX_PORT,
    MAX_TIMEOUT,
    STORAGE_KEY,
    STORAGE_VERSION,
    VmcHeltyFlowConfigFlow,
)
from custom_components.vmc_helty_flow.const import DOMAIN


class TestVmcHeltyFlowConfigFlow:
    """Test VMC Helty Flow config flow."""

    @pytest.fixture
    def mock_hass(self):
        """Mock HomeAssistant."""
        return MagicMock(spec=HomeAssistant)

    @pytest.fixture
    def config_flow(self, mock_hass):
        """Create config flow instance."""
        flow = VmcHeltyFlowConfigFlow()
        flow.hass = mock_hass
        return flow

    def test_config_flow_constants(self):
        """Test config flow constants."""
        assert MAX_PORT == 65535
        assert MAX_TIMEOUT == 60
        assert MAX_IPS_IN_SUBNET == 254
        assert f"{DOMAIN}.devices" == STORAGE_KEY
        assert STORAGE_VERSION == 1

    def test_init(self, config_flow):
        """Test config flow initialization."""
        assert config_flow.VERSION == 1
        assert config_flow.subnet is None
        assert config_flow.port is None
        assert config_flow.timeout == 10
        assert config_flow.discovered_devices == []
        assert config_flow.scan_interrupted is False
        assert config_flow.progress == 0
        assert config_flow._store is None

    def test_get_store(self, config_flow):
        """Test store getter."""
        with patch("custom_components.vmc_helty_flow.config_flow.Store") as mock_store:
            store = config_flow._get_store()
            assert store is not None
            mock_store.assert_called_once_with(
                config_flow.hass, STORAGE_VERSION, STORAGE_KEY
            )

            # Test caching
            store2 = config_flow._get_store()
            assert store is store2

    async def test_load_devices_success(self, config_flow):
        """Test successful device loading."""
        mock_store = MagicMock()
        mock_store.async_load = AsyncMock(
            return_value={"devices": [{"ip": "192.168.1.100", "name": "Test"}]}
        )

        with patch.object(config_flow, "_get_store", return_value=mock_store):
            devices = await config_flow._load_devices()
            assert devices == [{"ip": "192.168.1.100", "name": "Test"}]

    async def test_load_devices_no_data(self, config_flow):
        """Test device loading with no data."""
        mock_store = MagicMock()
        mock_store.async_load = AsyncMock(return_value=None)

        with patch.object(config_flow, "_get_store", return_value=mock_store):
            devices = await config_flow._load_devices()
            assert devices == []

    async def test_load_devices_empty_data(self, config_flow):
        """Test device loading with empty devices."""
        mock_store = MagicMock()
        mock_store.async_load = AsyncMock(return_value={})

        with patch.object(config_flow, "_get_store", return_value=mock_store):
            devices = await config_flow._load_devices()
            assert devices == []

    async def test_load_devices_exception(self, config_flow):
        """Test device loading with exception."""
        mock_store = MagicMock()
        mock_store.async_load = AsyncMock(side_effect=Exception("Load error"))

        with patch.object(config_flow, "_get_store", return_value=mock_store):
            devices = await config_flow._load_devices()
            assert devices == []

    async def test_save_devices_success(self, config_flow):
        """Test successful device saving."""
        mock_store = MagicMock()
        mock_store.async_save = AsyncMock()
        devices = [{"ip": "192.168.1.100", "name": "Test"}]

        with patch.object(config_flow, "_get_store", return_value=mock_store):
            await config_flow._save_devices(devices)
            mock_store.async_save.assert_called_once_with({"devices": devices})

    async def test_save_devices_exception(self, config_flow):
        """Test device saving with exception."""
        mock_store = MagicMock()
        mock_store.async_save = AsyncMock(side_effect=Exception("Save error"))
        devices = [{"ip": "192.168.1.100", "name": "Test"}]

        with patch.object(config_flow, "_get_store", return_value=mock_store):
            # Should not raise exception due to suppress
            await config_flow._save_devices(devices)
            mock_store.async_save.assert_called_once()

    async def test_async_step_user_no_existing_devices(self, config_flow):
        """Test user step with no existing devices."""
        with patch.object(config_flow, "_load_devices", return_value=[]):
            result = await config_flow.async_step_user()

            assert result["type"] == "form"
            assert result["step_id"] == "user"
            assert "subnet" in result["data_schema"].schema
            assert "port" in result["data_schema"].schema
            assert "timeout" in result["data_schema"].schema

    async def test_async_step_user_with_existing_devices_no_input(self, config_flow):
        """Test user step with existing devices and no input."""
        existing_devices = [{"ip": "192.168.1.100", "name": "Test"}]

        with patch.object(config_flow, "_load_devices", return_value=existing_devices):
            result = await config_flow.async_step_user()

            assert result["type"] == "form"
            assert result["step_id"] == "user"
            assert "confirm" in result["data_schema"].schema

    async def test_async_step_user_confirm_false(self, config_flow):
        """Test user step with confirm=False."""
        existing_devices = [{"ip": "192.168.1.100", "name": "Test"}]
        user_input = {"confirm": False}

        with patch.object(config_flow, "_load_devices", return_value=existing_devices):
            result = await config_flow.async_step_user(user_input)

            assert result["type"] == "form"
            assert result["step_id"] == "user"
            assert "errors" in result
            assert result["errors"]["base"] == "scan_annullata"

    async def test_async_step_user_valid_input(self, config_flow):
        """Test user step with valid input."""
        user_input = {"subnet": "192.168.1.0/24", "port": 5001, "timeout": 10}

        with (
            patch.object(config_flow, "_load_devices", return_value=[]),
            patch.object(config_flow, "async_step_discovery") as mock_discovery,
            patch(
                "custom_components.vmc_helty_flow.config_flow.validate_subnet",
                return_value=True,
            ),
            patch(
                "custom_components.vmc_helty_flow.config_flow.count_ips_in_subnet",
                return_value=254,
            ),
        ):
            await config_flow.async_step_user(user_input)

            assert config_flow.subnet == "192.168.1.0/24"
            assert config_flow.port == 5001
            assert config_flow.timeout == 10
            mock_discovery.assert_called_once()

    async def test_async_step_user_invalid_subnet(self, config_flow):
        """Test user step with invalid subnet."""
        user_input = {"subnet": "invalid_subnet", "port": 5001, "timeout": 10}

        with (
            patch.object(config_flow, "_load_devices", return_value=[]),
            patch(
                "custom_components.vmc_helty_flow.config_flow.validate_subnet",
                return_value=False,
            ),
        ):
            result = await config_flow.async_step_user(user_input)

            assert result["type"] == "form"
            assert result["errors"]["subnet"] == "subnet_non_valida"

    async def test_async_step_user_invalid_port(self, config_flow):
        """Test user step with invalid port."""
        user_input = {"subnet": "192.168.1.0/24", "port": 99999, "timeout": 10}

        with (
            patch.object(config_flow, "_load_devices", return_value=[]),
            patch(
                "custom_components.vmc_helty_flow.config_flow.validate_subnet",
                return_value=True,
            ),
        ):
            result = await config_flow.async_step_user(user_input)

            assert result["type"] == "form"
            assert result["errors"]["port"] == "porta_non_valida"

    async def test_async_step_user_invalid_timeout(self, config_flow):
        """Test user step with invalid timeout."""
        user_input = {"subnet": "192.168.1.0/24", "port": 5001, "timeout": 100}

        with (
            patch.object(config_flow, "_load_devices", return_value=[]),
            patch(
                "custom_components.vmc_helty_flow.config_flow.validate_subnet",
                return_value=True,
            ),
        ):
            result = await config_flow.async_step_user(user_input)

            assert result["type"] == "form"
            assert result["errors"]["timeout"] == "timeout_non_valido"

    async def test_async_step_user_subnet_too_large(self, config_flow):
        """Test user step with subnet too large."""
        user_input = {"subnet": "192.168.0.0/16", "port": 5001, "timeout": 10}

        with (
            patch.object(config_flow, "_load_devices", return_value=[]),
            patch(
                "custom_components.vmc_helty_flow.config_flow.validate_subnet",
                return_value=True,
            ),
            patch(
                "custom_components.vmc_helty_flow.config_flow.count_ips_in_subnet",
                return_value=65534,
            ),
        ):
            result = await config_flow.async_step_user(user_input)

            assert result["type"] == "form"
            assert result["errors"]["subnet"] == "subnet_troppo_grande"

    async def test_async_step_discovery_with_input(self, config_flow):
        """Test discovery step with user input."""
        user_input = {"selected_devices": ["192.168.1.100"]}

        with patch.object(config_flow, "_handle_discovery_input") as mock_handler:
            await config_flow.async_step_discovery(user_input)
            mock_handler.assert_called_once_with(user_input)

    async def test_async_step_discovery_without_input(self, config_flow):
        """Test discovery step without user input."""
        with patch.object(config_flow, "_handle_discovery_display") as mock_handler:
            await config_flow.async_step_discovery()
            mock_handler.assert_called_once()

    async def test_handle_discovery_input_device_selection(self, config_flow):
        """Test handling device selection."""
        user_input = {"selected_devices": ["192.168.1.100"]}

        with patch.object(config_flow, "_process_device_selection") as mock_process:
            await config_flow._handle_discovery_input(user_input)
            mock_process.assert_called_once_with(user_input)

    async def test_handle_discovery_input_interrupt_scan(self, config_flow):
        """Test handling scan interruption."""
        user_input = {"interrupt_scan": True}

        with patch.object(config_flow, "_handle_scan_interruption") as mock_handler:
            await config_flow._handle_discovery_input(user_input)
            mock_handler.assert_called_once()

    async def test_handle_discovery_display_no_devices(self, config_flow):
        """Test discovery display when no devices discovered yet."""
        # Remove the attribute to simulate not discovered yet
        if hasattr(config_flow, "discovered_devices"):
            delattr(config_flow, "discovered_devices")

        with patch.object(config_flow, "_perform_device_discovery") as mock_discovery:
            await config_flow._handle_discovery_display()
            mock_discovery.assert_called_once()

    async def test_handle_discovery_display_with_devices(self, config_flow):
        """Test discovery display when devices already discovered."""
        config_flow.discovered_devices = [{"ip": "192.168.1.100", "name": "Test"}]

        with patch.object(config_flow, "_show_device_selection_form") as mock_show:
            await config_flow._handle_discovery_display()
            mock_show.assert_called_once()

    async def test_process_device_selection_success(self, config_flow):
        """Test successful device selection processing."""
        config_flow.discovered_devices = [
            {"ip": "192.168.1.100", "name": "Test1"},
            {"ip": "192.168.1.101", "name": "Test2"},
        ]
        user_input = {"selected_devices": ["192.168.1.100"]}

        with (
            patch.object(config_flow, "_save_devices") as mock_save,
            patch.object(config_flow, "_async_current_entries", return_value=[]),
            patch.object(config_flow, "async_set_unique_id"),
            patch.object(config_flow, "_abort_if_unique_id_configured"),
            patch.object(config_flow, "async_create_entry") as mock_create,
        ):
            mock_entry = {"title": "Test1", "data": {"ip": "192.168.1.100"}}
            mock_create.return_value = mock_entry

            result = await config_flow._process_device_selection(user_input)

            mock_save.assert_called_once()
            mock_create.assert_called_once()
            assert result == mock_entry

    async def test_process_device_selection_all_configured(self, config_flow):
        """Test device selection when all devices already configured."""
        config_flow.discovered_devices = [{"ip": "192.168.1.100", "name": "Test1"}]
        user_input = {"selected_devices": ["192.168.1.100"]}

        # Mock existing entry
        existing_entry = MagicMock()
        existing_entry.data.get.return_value = "192.168.1.100"

        with (
            patch.object(config_flow, "_save_devices"),
            patch.object(
                config_flow, "_async_current_entries", return_value=[existing_entry]
            ),
            patch.object(config_flow, "async_abort") as mock_abort,
        ):
            await config_flow._process_device_selection(user_input)
            mock_abort.assert_called_once_with(reason="all_devices_already_configured")

    async def test_handle_scan_interruption(self, config_flow):
        """Test scan interruption handling via public interface."""
        with patch.object(config_flow, "async_show_form") as mock_show:
            user_input = {"interrupt_scan": True}
            await config_flow._handle_discovery_input(user_input)

            assert config_flow.scan_interrupted is True
            mock_show.assert_called_once()

    async def test_perform_device_discovery_success(self, config_flow):
        """Test successful device discovery."""
        config_flow.subnet = "192.168.1.0/24"
        config_flow.port = 5001
        config_flow.timeout = 10

        devices = [{"ip": "192.168.1.100", "name": "Test"}]

        with (
            patch.object(config_flow, "_discover_devices_async", return_value=devices),
            patch.object(config_flow, "_save_devices") as mock_save,
        ):
            result = await config_flow._perform_device_discovery()

            assert config_flow.discovered_devices == devices
            mock_save.assert_called_once_with(devices)
            assert result is None

    async def test_perform_device_discovery_no_devices(self, config_flow):
        """Test device discovery with no devices found."""
        config_flow.subnet = "192.168.1.0/24"
        config_flow.port = 5001
        config_flow.timeout = 10

        with (
            patch.object(config_flow, "_discover_devices_async", return_value=[]),
            patch.object(config_flow, "_save_devices"),
            patch.object(config_flow, "async_show_form") as mock_show,
        ):
            await config_flow._perform_device_discovery()

            mock_show.assert_called_once()
            assert "errors" in mock_show.call_args[1]

    async def test_perform_device_discovery_exception(self, config_flow):
        """Test device discovery with exception."""
        config_flow.subnet = "192.168.1.0/24"
        config_flow.port = 5001
        config_flow.timeout = 10

        with (
            patch.object(
                config_flow,
                "_discover_devices_async",
                side_effect=Exception("Discovery error"),
            ),
            patch.object(config_flow, "_save_devices"),
            patch.object(config_flow, "async_show_form") as mock_show,
        ):
            await config_flow._perform_device_discovery()

            assert config_flow.discovered_devices == []
            mock_show.assert_called_once()

    def test_show_device_selection_form(self, config_flow):
        """Test device selection form display."""
        config_flow.discovered_devices = [
            {"ip": "192.168.1.100", "name": "Test1"},
            {"ip": "192.168.1.101", "name": "Test2"},
        ]
        config_flow.total_ips_scanned = 254

        with patch.object(config_flow, "async_show_form") as mock_show:
            config_flow._show_device_selection_form()

            mock_show.assert_called_once()
            assert mock_show.call_args[1]["step_id"] == "discovery"

    def test_update_discovery_progress(self, config_flow):
        """Test discovery progress update."""
        progress_info = {
            "progress": 50,
            "current_ip": "192.168.1.100",
            "devices_found": 2,
            "scanned": 100,
            "total": 254,
        }

        config_flow._update_discovery_progress(progress_info)

        assert config_flow.progress == 50
        assert config_flow._discovery_progress["current_ip"] == "192.168.1.100"
        assert config_flow._discovery_progress["devices_found"] == 2

    async def test_discover_devices_async(self, config_flow):
        """Test async device discovery."""
        devices = [{"ip": "192.168.1.100", "name": "Test"}]

        with (
            patch(
                "custom_components.vmc_helty_flow.config_flow.parse_subnet_for_discovery",
                return_value="192.168.1",
            ),
            patch(
                "custom_components.vmc_helty_flow.config_flow.discover_vmc_devices_with_progress",
                return_value=devices,
            ),
        ):
            result = await config_flow._discover_devices_async(
                "192.168.1.0/24", 5001, 10
            )

            assert result == devices
            assert config_flow.subnet == "192.168.1.0/24"
            assert config_flow.port == 5001
            assert config_flow.timeout == 10

    async def test_async_step_import(self, config_flow):
        """Test import step."""
        import_info = {"subnet": "192.168.1.0/24"}

        with patch.object(config_flow, "async_step_user") as mock_user:
            await config_flow.async_step_import(import_info)
            mock_user.assert_called_once_with(import_info)
