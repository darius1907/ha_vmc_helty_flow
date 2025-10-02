
# pylint: disable=protected-access
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from homeassistant.core import HomeAssistant
from custom_components.vmc_helty_flow.config_flow import (
    MAX_IPS_IN_SUBNET,
    MAX_PORT,
    MAX_TIMEOUT,
    VmcHeltyFlowConfigFlow,
)
from custom_components.vmc_helty_flow.const import DEFAULT_ROOM_VOLUME, DOMAIN


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
        # Storage constants removed - now using config entries registry

    def test_init(self, config_flow):
        """Test config flow initialization."""
        assert config_flow.VERSION == 1
        assert config_flow.subnet is None
        assert config_flow.port is None
        assert config_flow.timeout == 10
        assert config_flow.discovered_devices == []
        # Storage system removed - now using config entries registry directly

    def test_get_configured_devices_empty(self, config_flow):
        """Test getting configured devices with no entries."""
        config_flow._async_current_entries = MagicMock(return_value=[])
        devices = config_flow._get_configured_devices()
        assert devices == []

    def test_get_configured_devices_with_entries(self, config_flow):
        """Test getting configured devices with existing entries."""
        mock_entry = MagicMock()
        mock_entry.domain = DOMAIN
        mock_entry.entry_id = "test_id"
        mock_entry.title = "Test VMC"
        mock_entry.data = {
            "ip": "192.168.1.100",
            "name": "Test Device",
            "model": "VMC Flow",
            "manufacturer": "Helty",
        }
        mock_entry.state.name = "loaded"

        config_flow._async_current_entries = MagicMock(return_value=[mock_entry])
        devices = config_flow._get_configured_devices()

        assert len(devices) == 1
        assert devices[0]["ip"] == "192.168.1.100"
        assert devices[0]["name"] == "Test Device"
        assert devices[0]["entry_id"] == "test_id"

    async def test_load_devices_uses_registry(self, config_flow):
        """Test that _load_devices now uses registry via _get_configured_devices."""
        mock_devices = [{"ip": "192.168.1.100", "name": "Test"}]

        with patch.object(
            config_flow, "_get_configured_devices", return_value=mock_devices
        ):
            devices = await config_flow._load_devices()
            assert devices == mock_devices

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
        """Test user step with valid input - starts incremental scan."""
        user_input = {"subnet": "192.168.1.0/24", "port": 5001, "timeout": 10}

        with (
            patch.object(config_flow, "_load_devices", return_value=[]),
            patch.object(
                config_flow,
                "_scan_next_ip",
                return_value={"type": "form", "step_id": "scanning"},
            ) as mock_scan,
            patch(
                "custom_components.vmc_helty_flow.config_flow.validate_subnet",
                return_value=True,
            ),
            patch(
                "custom_components.vmc_helty_flow.config_flow.count_ips_in_subnet",
                return_value=254,
            ),
        ):
            result = await config_flow.async_step_user(user_input)

            assert config_flow.subnet == "192.168.1.0/24"
            assert config_flow.port == 5001
            assert config_flow.timeout == 10
            assert config_flow.scan_in_progress is True

            # Con la nuova logica incrementale, dovrebbe iniziare la scansione
            mock_scan.assert_called_once()

            # Verifica che venga mostrata la form di scansione incrementale
            assert result["type"] == "form"

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

    # Legacy test removed - method no longer exists

    # Legacy test removed - method no longer exists

    # Legacy test removed - method no longer exists

    # Legacy test removed - method no longer exists

    # Legacy test removed - method no longer exists

    # Legacy test removed - method no longer exists

    # Legacy test removed - method no longer exists

    async def test_async_step_device_found_add_and_configure(self, config_flow):
        """Test device found step with add and configure action."""
        config_flow.current_found_device = {"ip": "192.168.1.100", "name": "Test1"}
        user_input = {"action": "add_and_configure"}

        with (
            patch.object(config_flow, "_async_current_entries", return_value=[]),
            patch.object(config_flow, "async_step_room_config") as mock_room_config,
        ):
            mock_result = {"type": "form", "step_id": "room_config"}
            mock_room_config.return_value = mock_result

            result = await config_flow.async_step_device_found(user_input)

            mock_room_config.assert_called_once()
            assert result == mock_result

    async def test_async_step_device_found_add_and_stop(self, config_flow):
        """Test device found step with add and stop action now goes to room config."""
        config_flow.current_found_device = {"ip": "192.168.1.100", "name": "Test1"}
        user_input = {"action": "add_and_stop"}

        with (
            patch.object(config_flow, "_async_current_entries", return_value=[]),
            patch.object(
                config_flow, "async_step_room_config"
            ) as mock_room_config,
        ):
            mock_room_config.return_value = {
                "type": "form",
                "step_id": "room_config",
            }

            result = await config_flow.async_step_device_found(user_input)

            # Verify that it goes to room configuration step
            mock_room_config.assert_called_once()
            assert result["type"] == "form"
            assert result["step_id"] == "room_config"

            # Verify that stop flag is set
            assert config_flow._stop_after_current is True

    async def test_async_step_device_found_skip_continue(self, config_flow):
        """Test device found step with skip and continue action."""
        config_flow.current_found_device = {"ip": "192.168.1.100", "name": "Test1"}
        user_input = {"action": "skip_continue"}

        with patch.object(config_flow, "_scan_next_ip") as mock_scan:
            mock_result = {"type": "form", "step_id": "device_found"}
            mock_scan.return_value = mock_result

            result = await config_flow.async_step_device_found(user_input)

            mock_scan.assert_called_once()
            assert result == mock_result

    async def test_async_step_room_config_success_manual_volume(self, config_flow):
        """Test successful room configuration step with manual volume input."""
        config_flow.current_found_device = {"ip": "192.168.1.100", "name": "Test1"}
        config_flow._continue_after_room_config = True  # Set flag to continue scan
        user_input = {
            "input_method": "manual",
            "room_volume": 120
        }

        with (
            patch.object(config_flow, "_async_current_entries", return_value=[]),
            patch.object(config_flow, "async_set_unique_id"),
            patch.object(config_flow, "_abort_if_unique_id_configured"),
            patch.object(
                config_flow.hass.config_entries.flow,
                "async_init",
                new_callable=AsyncMock,
            ) as mock_async_init,
            patch.object(
                config_flow, "_scan_next_ip", new_callable=AsyncMock
            ) as mock_scan_next,
        ):
            expected_data = {
                "ip": "192.168.1.100",
                "name": "Test1",
                "model": "VMC Flow",
                "manufacturer": "Helty",
                "port": 5001,
                "timeout": 10,
                "room_volume": 120.0
            }
            mock_scan_next.return_value = {
                "type": "form",
                "step_id": "scanning"
            }

            result = await config_flow.async_step_room_config(user_input)

            mock_async_init.assert_called_once_with(
                DOMAIN,
                context={"source": "discovered_device"},
                data=expected_data,
            )
            mock_scan_next.assert_called_once()
            assert result["type"] == "form"
            # Flag should be reset
            assert config_flow._continue_after_room_config is False

    async def test_async_step_room_config_success_calculated_volume(self, config_flow):
        """Test successful room configuration step with calculated volume."""
        config_flow.current_found_device = {"ip": "192.168.1.100", "name": "Test1"}
        config_flow._continue_after_room_config = True  # Set flag to continue scan
        user_input = {
            "input_method": "calculate",
            "length": 5.0,
            "width": 4.0,
            "height": 3.0
        }

        with (
            patch.object(config_flow, "_async_current_entries", return_value=[]),
            patch.object(config_flow, "async_set_unique_id"),
            patch.object(config_flow, "_abort_if_unique_id_configured"),
            patch.object(
                config_flow.hass.config_entries.flow,
                "async_init",
                new_callable=AsyncMock,
            ) as mock_async_init,
            patch.object(
                config_flow, "_scan_next_ip", new_callable=AsyncMock
            ) as mock_scan_next,
        ):
            expected_data = {
                "ip": "192.168.1.100",
                "name": "Test1",
                "model": "VMC Flow",
                "manufacturer": "Helty",
                "port": 5001,
                "timeout": 10,
                "room_volume": DEFAULT_ROOM_VOLUME  # 5.0 * 4.0 * 3.0 = 60.0
            }
            mock_scan_next.return_value = {
                "type": "form",
                "step_id": "scanning"
            }

            result = await config_flow.async_step_room_config(user_input)

            mock_async_init.assert_called_once_with(
                DOMAIN,
                context={"source": "discovered_device"},
                data=expected_data,
            )
            mock_scan_next.assert_called_once()
            assert result["type"] == "form"
            # Flag should be reset
            assert config_flow._continue_after_room_config is False

    async def test_async_step_room_config_no_input(self, config_flow):
        """Test room configuration step without input shows form."""
        config_flow.current_found_device = {"ip": "192.168.1.100", "name": "Test1"}

        result = await config_flow.async_step_room_config()

        assert result["type"] == "form"
        assert result["step_id"] == "room_config"
        schema_keys = list(result["data_schema"].schema.keys())
        schema_key_names = [str(key) for key in schema_keys]

        # Verifica che tutti i campi necessari siano presenti
        assert any("input_method" in key_name for key_name in schema_key_names)
        assert any("room_volume" in key_name for key_name in schema_key_names)
        assert any("length" in key_name for key_name in schema_key_names)
        assert any("width" in key_name for key_name in schema_key_names)
        assert any("height" in key_name for key_name in schema_key_names)

    # Legacy test removed - method no longer exists

    async def test_discover_devices_async(self, config_flow):
        """Test async device discovery."""
        devices = [{"ip": "192.168.1.100", "name": "Test"}]

        with (
            patch(
                "custom_components.vmc_helty_flow.config_flow.parse_subnet_for_discovery",
                return_value="192.168.1",
            ),
            patch(
                "custom_components.vmc_helty_flow.config_flow.discover_vmc_devices",
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

    async def test_complete_flow_no_loop(self, config_flow):
        """Test complete flow from confirmation to incremental scan without loops."""
        # Setup: existing devices in registry
        existing_devices = [{"name": "Test Device", "ip": "192.168.1.100"}]

        with patch.object(
            config_flow, "_get_configured_devices", return_value=existing_devices
        ):
            # Step 1: First request - should show confirmation form
            result1 = await config_flow.async_step_user(None)
            assert result1["type"] == "form"
            assert result1["step_id"] == "user"
            assert "confirm" in str(result1["data_schema"])
            assert "subnet" not in str(result1["data_schema"])

            # Step 2: User confirms new scan - should show config form
            result2 = await config_flow.async_step_user({"confirm": True})
            assert result2["type"] == "form"
            assert result2["step_id"] == "user"
            assert "subnet" in str(result2["data_schema"])
            assert "port" in str(result2["data_schema"])
            assert "timeout" in str(result2["data_schema"])
            assert "confirm" not in str(result2["data_schema"])

            # Step 3: User inputs valid config - should start incremental scan
            with patch.object(config_flow, "_scan_next_ip") as mock_scan:
                mock_scan.return_value = {"type": "form", "step_id": "scanning"}
                await config_flow.async_step_user(
                    {"subnet": "192.168.1.0/24", "port": 5001, "timeout": 10}
                )
                mock_scan.assert_called_once()
                assert config_flow.scan_in_progress is True

            # Verify flow state is set correctly
            assert config_flow.subnet == "192.168.1.0/24"
            assert config_flow.port == 5001
            assert config_flow.timeout == 10

    async def test_incremental_scan_device_found(self, config_flow):
        """Test incremental scan when device is found."""
        # Setup flow state
        config_flow.scan_in_progress = True
        config_flow.current_found_device = {
            "ip": "192.168.1.100",
            "name": "VMC Test Device",
            "model": "Test Model",
        }
        config_flow.current_ip_index = 5
        config_flow.total_ips_to_scan = 254
        config_flow.found_devices_session = []

        # Test the device_found step
        result = await config_flow.async_step_device_found(None)

        assert result["type"] == "form"
        assert result["step_id"] == "device_found"
        assert "action" in str(result["data_schema"])
        assert "VMC Test Device" in result["description_placeholders"]["device_name"]
        assert "192.168.1.100" in result["description_placeholders"]["device_ip"]

    async def test_incremental_scan_add_continue(self, config_flow):
        """Test adding device and continuing scan."""
        # Setup flow state
        config_flow.scan_in_progress = True
        config_flow.current_found_device = {
            "ip": "192.168.1.100",
            "name": "VMC Test Device",
        }
        config_flow.found_devices_session = []
        config_flow.port = 5001
        config_flow.timeout = 10

        with (
            patch.object(config_flow, "_async_current_entries", return_value=[]),
            patch.object(config_flow, "async_step_room_config") as mock_room_config,
        ):
            mock_result = {"type": "form", "step_id": "room_config"}
            mock_room_config.return_value = mock_result

            result = await config_flow.async_step_device_found(
                {"action": "add_and_configure"}
            )

            # Should go to room configuration
            mock_room_config.assert_called_once()
            assert result == mock_result

    async def test_incremental_scan_add_stop(self, config_flow):
        """Test adding device and stopping scan now goes to room config first."""
        # Setup flow state
        config_flow.scan_in_progress = True
        config_flow.current_found_device = {
            "ip": "192.168.1.100",
            "name": "VMC Test Device",
        }
        config_flow.found_devices_session = []
        config_flow.port = 5001
        config_flow.timeout = 10

        with (
            patch.object(config_flow, "_async_current_entries", return_value=[]),
            patch.object(
                config_flow, "async_step_room_config"
            ) as mock_room_config,
        ):
            mock_result = {"type": "form", "step_id": "room_config"}
            mock_room_config.return_value = mock_result

            result = await config_flow.async_step_device_found(
                {"action": "add_and_stop"}
            )

            # Should go to room configuration step
            mock_room_config.assert_called_once()
            assert result["type"] == "form"
            assert result["step_id"] == "room_config"

            # Stop flag should be set
            assert config_flow._stop_after_current is True

    async def test_room_config_with_stop_flag(self, config_flow):
        """Test room config step when _stop_after_current flag is set."""
        # Setup flow state
        config_flow.current_found_device = {
            "ip": "192.168.1.100",
            "name": "VMC Test Device",
        }
        config_flow._stop_after_current = True
        config_flow.found_devices_session = []

        with (
            patch.object(config_flow, "_async_current_entries", return_value=[]),
            patch.object(config_flow, "async_set_unique_id"),
            patch.object(config_flow, "_abort_if_unique_id_configured"),
            patch.object(
                config_flow.hass.config_entries.flow,
                "async_init",
                new_callable=AsyncMock,
            ) as mock_async_init,
            patch.object(
                config_flow, "_finalize_incremental_scan", new_callable=AsyncMock
            ) as mock_finalize,
        ):
            expected_data = {
                "ip": "192.168.1.100",
                "name": "VMC Test Device",
                "model": "VMC Flow",
                "manufacturer": "Helty",
                "port": 5001,
                "timeout": 10,
                "room_volume": 45.0,  # User configured volume
            }
            mock_finalize.return_value = {
                "type": "create_entry",
                "title": "Scan completed",
                "data": {},
            }

            user_input = {"input_method": "manual", "room_volume": 45.0}
            result = await config_flow.async_step_room_config(user_input)

            mock_async_init.assert_called_once_with(
                DOMAIN,
                context={"source": "discovered_device"},
                data=expected_data,
            )
            mock_finalize.assert_called_once()
            assert result["type"] == "create_entry"
            # Flag should be reset after use
            assert config_flow._stop_after_current is False
            # Device should be added to session (twice)
            assert len(config_flow.found_devices_session) >= 1

    async def test_async_step_discovered_device_with_custom_volume(self, config_flow):
        """Test discovered_device step uses volume from discovery_info."""
        discovery_info = {
            "ip": "192.168.1.100",
            "name": "Test Device",
            "model": "VMC Flow",
            "manufacturer": "Helty",
            "port": 5001,
            "timeout": 10,
            "room_volume": 85.5,  # Custom volume
        }

        with (
            patch.object(config_flow, "_async_current_entries", return_value=[]),
            patch.object(config_flow, "async_set_unique_id"),
            patch.object(config_flow, "_abort_if_unique_id_configured"),
            patch.object(config_flow, "async_create_entry") as mock_create_entry,
        ):
            mock_create_entry.return_value = {
                "type": "create_entry",
                "title": "Test Device",
                "data": discovery_info,
            }

            result = await config_flow.async_step_discovered_device(discovery_info)

            # Verify that create_entry was called with custom volume
            mock_create_entry.assert_called_once_with(
                title="Test Device",
                data={
                    "ip": "192.168.1.100",
                    "name": "Test Device",
                    "model": "VMC Flow",
                    "manufacturer": "Helty",
                    "port": 5001,
                    "timeout": 10,
                    "room_volume": 85.5,  # Should use the custom volume
                }
            )

            assert result["type"] == "create_entry"

    async def test_async_step_discovered_device_default_volume(self, config_flow):
        """Test discovered_device step uses default volume when not provided."""
        discovery_info = {
            "ip": "192.168.1.100",
            "name": "Test Device",
            "model": "VMC Flow",
            "manufacturer": "Helty",
            "port": 5001,
            "timeout": 10,
            # No room_volume provided
        }

        with (
            patch.object(config_flow, "_async_current_entries", return_value=[]),
            patch.object(config_flow, "async_set_unique_id"),
            patch.object(config_flow, "_abort_if_unique_id_configured"),
            patch.object(config_flow, "async_create_entry") as mock_create_entry,
        ):
            mock_create_entry.return_value = {
                "type": "create_entry",
                "title": "Test Device",
                "data": discovery_info,
            }

            result = await config_flow.async_step_discovered_device(discovery_info)

            # Verify that create_entry was called with default volume
            mock_create_entry.assert_called_once_with(
                title="Test Device",
                data={
                    "ip": "192.168.1.100",
                    "name": "Test Device",
                    "model": "VMC Flow",
                    "manufacturer": "Helty",
                    "port": 5001,
                    "timeout": 10,
                    "room_volume": DEFAULT_ROOM_VOLUME,  # Should use default volume
                }
            )

            assert result["type"] == "create_entry"
