"""Test incremental scan functionality in config flow."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.vmc_helty_flow.config_flow import VmcHeltyFlowConfigFlow
from custom_components.vmc_helty_flow.const import DOMAIN


class TestIncrementalScan:
    """Test incremental scan functionality."""

    @pytest.fixture
    def mock_config_flow(self):
        """Create a mocked config flow for testing."""
        flow = VmcHeltyFlowConfigFlow()
        flow.hass = MagicMock()
        flow.hass.config_entries = MagicMock()
        flow.hass.config_entries.async_get_entry = MagicMock(return_value=None)
        return flow

    @pytest.fixture
    def mock_device_data(self):
        """Mock device data for testing."""
        return {
            "ip": "192.168.1.100",
            "name": "VMC Test Device",
            "model": "VMC Flow Pro",
            "manufacturer": "Helty",
        }

    async def test_scan_mode_selection_incremental(self, mock_config_flow):
        """Test selection of incremental scan mode."""
        # Setup
        with patch.object(mock_config_flow, '_load_devices', return_value=[]):
            user_input = {
                "subnet": "192.168.1.0/24",
                "port": 5001,
                "timeout": 10,
                "scan_mode": "incremental"
            }
            
            with patch.object(mock_config_flow, '_start_incremental_scan') as mock_start:
                mock_start.return_value = {"type": FlowResultType.FORM, "step_id": "device_found"}
                
                # Execute
                result = await mock_config_flow.async_step_user(user_input)
                
                # Verify
                assert mock_config_flow.scan_mode == "incremental"
                mock_start.assert_called_once()

    async def test_scan_mode_selection_full(self, mock_config_flow):
        """Test selection of full scan mode (default)."""
        # Setup
        with patch.object(mock_config_flow, '_load_devices', return_value=[]):
            user_input = {
                "subnet": "192.168.1.0/24",
                "port": 5001,
                "timeout": 10,
                "scan_mode": "full"
            }
            
            with patch.object(mock_config_flow, '_perform_device_discovery') as mock_full:
                mock_full.return_value = {"type": FlowResultType.FORM, "step_id": "discovery"}
                
                # Execute
                result = await mock_config_flow.async_step_user(user_input)
                
                # Verify
                assert mock_config_flow.scan_mode == "full"
                mock_full.assert_called_once()

    async def test_generate_ip_range(self, mock_config_flow):
        """Test IP range generation for incremental scan."""
        # Test /24 subnet
        ip_list = mock_config_flow._generate_ip_range("192.168.1.0/24")
        assert len(ip_list) == 254  # Exclude network and broadcast
        assert "192.168.1.1" in ip_list
        assert "192.168.1.254" in ip_list
        assert "192.168.1.0" not in ip_list  # Network address excluded
        assert "192.168.1.255" not in ip_list  # Broadcast address excluded

        # Test invalid subnet
        ip_list = mock_config_flow._generate_ip_range("invalid.subnet")
        assert ip_list == []

    async def test_start_incremental_scan_initialization(self, mock_config_flow):
        """Test incremental scan initialization."""
        # Setup
        mock_config_flow.subnet = "192.168.1.0/24"
        mock_config_flow.port = 5001
        mock_config_flow.timeout = 10
        
        with patch.object(mock_config_flow, '_scan_next_ip') as mock_scan_next:
            mock_scan_next.return_value = {"type": FlowResultType.FORM, "step_id": "device_found"}
            
            # Execute
            result = await mock_config_flow._start_incremental_scan()
            
            # Verify initialization
            assert mock_config_flow.scan_in_progress is True
            assert mock_config_flow.current_ip_index == 0
            assert mock_config_flow.total_ips_to_scan == 254
            assert mock_config_flow.found_devices_session == []
            assert len(mock_config_flow.ip_range) == 254
            mock_scan_next.assert_called_once()

    async def test_start_incremental_scan_invalid_subnet(self, mock_config_flow):
        """Test incremental scan with invalid subnet."""
        # Setup
        mock_config_flow.subnet = "invalid.subnet"
        
        # Execute
        result = await mock_config_flow._start_incremental_scan()
        
        # Verify error handling
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"]["subnet"] == "subnet_non_valida"

    async def test_scan_next_ip_device_found(self, mock_config_flow, mock_device_data):
        """Test scanning next IP when device is found."""
        # Setup
        mock_config_flow.ip_range = ["192.168.1.100", "192.168.1.101"]
        mock_config_flow.current_ip_index = 0
        mock_config_flow.total_ips_to_scan = 2
        mock_config_flow.port = 5001
        mock_config_flow.timeout = 10

        with patch('custom_components.vmc_helty_flow.config_flow.get_device_info') as mock_get_device:
            mock_get_device.return_value = mock_device_data

            with patch.object(mock_config_flow, 'async_step_device_found') as mock_device_found:
                mock_device_found.return_value = {"type": FlowResultType.FORM, "step_id": "device_found"}

                # Execute
                result = await mock_config_flow._scan_next_ip()

                # Verify
                assert mock_config_flow.current_ip_index == 1  # Moved to next IP
                assert mock_config_flow.current_found_device == mock_device_data
                mock_get_device.assert_called_once_with("192.168.1.100", 5001, 10)
                mock_device_found.assert_called_once()

    async def test_scan_next_ip_no_device_found(self, mock_config_flow):
        """Test scanning next IP when no device is found."""
        # Setup
        mock_config_flow.ip_range = ["192.168.1.100"]
        mock_config_flow.current_ip_index = 0
        mock_config_flow.total_ips_to_scan = 1
        mock_config_flow.found_devices_session = []
        
        with patch('custom_components.vmc_helty_flow.helpers.get_device_info') as mock_get_device:
            mock_get_device.return_value = None  # No device found
            
            with patch.object(mock_config_flow, '_finalize_incremental_scan') as mock_finalize:
                mock_finalize.return_value = {"type": FlowResultType.FORM, "step_id": "user"}
                
                # Execute
                result = await mock_config_flow._scan_next_ip()
                
                # Verify scan completed
                assert mock_config_flow.current_ip_index == 1
                mock_finalize.assert_called_once()

    async def test_scan_next_ip_scan_completed(self, mock_config_flow):
        """Test scan completion when all IPs are scanned."""
        # Setup - already at end of IP range
        mock_config_flow.ip_range = ["192.168.1.100"]
        mock_config_flow.current_ip_index = 1  # Beyond range
        mock_config_flow.total_ips_to_scan = 1
        mock_config_flow.found_devices_session = []
        
        with patch.object(mock_config_flow, '_finalize_incremental_scan') as mock_finalize:
            mock_finalize.return_value = {"type": FlowResultType.FORM, "step_id": "user"}
            
            # Execute
            result = await mock_config_flow._scan_next_ip()
            
            # Verify
            mock_finalize.assert_called_once()

    async def test_device_found_step_display(self, mock_config_flow, mock_device_data):
        """Test device found step display."""
        # Setup
        mock_config_flow.current_found_device = mock_device_data
        mock_config_flow.current_ip_index = 50
        mock_config_flow.total_ips_to_scan = 254
        mock_config_flow.found_devices_session = []
        
        # Execute
        result = await mock_config_flow.async_step_device_found()
        
        # Verify
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "device_found"
        assert "action" in result["data_schema"].schema
        
        # Check placeholders
        placeholders = result["description_placeholders"]
        assert placeholders["device_name"] == "VMC Test Device"
        assert placeholders["device_ip"] == "192.168.1.100"
        assert placeholders["device_model"] == "VMC Flow Pro"
        assert "50/254" in placeholders["progress"]
        assert placeholders["found_count"] == "1"  # Include current device in count

    async def test_device_found_step_display_with_existing_devices(self, mock_config_flow, mock_device_data):
        """Test device found step display when other devices already found."""
        # Setup - simulate 2 devices already found
        mock_config_flow.current_found_device = mock_device_data
        mock_config_flow.current_ip_index = 100
        mock_config_flow.total_ips_to_scan = 254
        mock_config_flow.found_devices_session = [
            {"ip": "192.168.1.101", "name": "Device 1"},
            {"ip": "192.168.1.102", "name": "Device 2"}
        ]

        # Execute
        result = await mock_config_flow.async_step_device_found()

        # Verify
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "device_found"

        # Check that found_count includes current device (2 existing + 1 current = 3)
        placeholders = result["description_placeholders"]
        assert placeholders["found_count"] == "3"

    async def test_device_found_action_add_continue(self, mock_config_flow, mock_device_data):
        """Test add device and continue action."""
        # Setup
        mock_config_flow.current_found_device = mock_device_data
        mock_config_flow.found_devices_session = []
        
        user_input = {"action": "add_continue"}
        
        with patch.object(mock_config_flow, '_scan_next_ip') as mock_scan_next:
            mock_scan_next.return_value = {"type": FlowResultType.FORM, "step_id": "device_found"}
            
            # Execute
            result = await mock_config_flow.async_step_device_found(user_input)
            
            # Verify device was added
            assert len(mock_config_flow.found_devices_session) == 1
            assert mock_config_flow.found_devices_session[0] == mock_device_data
            mock_scan_next.assert_called_once()

    async def test_device_found_action_skip_continue(self, mock_config_flow, mock_device_data):
        """Test skip device and continue action."""
        # Setup
        mock_config_flow.current_found_device = mock_device_data
        mock_config_flow.found_devices_session = []
        
        user_input = {"action": "skip_continue"}
        
        with patch.object(mock_config_flow, '_scan_next_ip') as mock_scan_next:
            mock_scan_next.return_value = {"type": FlowResultType.FORM, "step_id": "device_found"}
            
            # Execute
            result = await mock_config_flow.async_step_device_found(user_input)
            
            # Verify device was NOT added
            assert len(mock_config_flow.found_devices_session) == 0
            mock_scan_next.assert_called_once()

    async def test_device_found_action_add_stop(self, mock_config_flow, mock_device_data):
        """Test add device and stop scanning action."""
        # Setup
        mock_config_flow.current_found_device = mock_device_data
        mock_config_flow.found_devices_session = []
        
        user_input = {"action": "add_stop"}
        
        with patch.object(mock_config_flow, '_finalize_incremental_scan') as mock_finalize:
            mock_finalize.return_value = {"type": FlowResultType.CREATE_ENTRY}
            
            # Execute
            result = await mock_config_flow.async_step_device_found(user_input)
            
            # Verify device was added and scan stopped
            assert len(mock_config_flow.found_devices_session) == 1
            assert mock_config_flow.found_devices_session[0] == mock_device_data
            mock_finalize.assert_called_once()

    async def test_device_found_action_stop_scan(self, mock_config_flow, mock_device_data):
        """Test stop scanning without adding device action."""
        # Setup
        mock_config_flow.current_found_device = mock_device_data
        mock_config_flow.found_devices_session = []
        
        user_input = {"action": "stop_scan"}
        
        with patch.object(mock_config_flow, '_finalize_incremental_scan') as mock_finalize:
            mock_finalize.return_value = {"type": FlowResultType.FORM, "step_id": "user"}
            
            # Execute
            result = await mock_config_flow.async_step_device_found(user_input)
            
            # Verify device was NOT added and scan stopped
            assert len(mock_config_flow.found_devices_session) == 0
            mock_finalize.assert_called_once()

    async def test_finalize_incremental_scan_no_devices(self, mock_config_flow):
        """Test finalization when no devices found."""
        # Setup
        mock_config_flow.found_devices_session = []
        mock_config_flow.total_ips_to_scan = 254
        
        # Execute
        result = await mock_config_flow._finalize_incremental_scan()
        
        # Verify
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"]["base"] == "nessun_dispositivo_trovato"
        assert mock_config_flow.scan_in_progress is False

    async def test_finalize_incremental_scan_single_device(self, mock_config_flow, mock_device_data):
        """Test finalization with single device found."""
        # Setup
        mock_config_flow.found_devices_session = [mock_device_data]
        mock_config_flow.port = 5001
        mock_config_flow.timeout = 10
        
        with patch.object(mock_config_flow, '_save_devices') as mock_save:
            with patch.object(mock_config_flow, 'async_create_entry') as mock_create:
                mock_create.return_value = {"type": FlowResultType.CREATE_ENTRY}
                
                # Execute
                result = await mock_config_flow._finalize_incremental_scan()
                
                # Verify
                assert mock_config_flow.scan_in_progress is False
                assert mock_config_flow.discovered_devices == [mock_device_data]
                mock_save.assert_called_once_with([mock_device_data])
                mock_create.assert_called_once()

    async def test_finalize_incremental_scan_multiple_devices(self, mock_config_flow):
        """Test finalization with multiple devices found."""
        # Setup
        devices = [
            {"ip": "192.168.1.100", "name": "Device 1"},
            {"ip": "192.168.1.101", "name": "Device 2"}
        ]
        mock_config_flow.found_devices_session = devices
        
        with patch.object(mock_config_flow, '_save_devices') as mock_save:
            with patch.object(mock_config_flow, '_show_device_selection_form') as mock_show_form:
                mock_show_form.return_value = {"type": FlowResultType.FORM, "step_id": "discovery"}
                
                # Execute
                result = await mock_config_flow._finalize_incremental_scan()
                
                # Verify
                assert mock_config_flow.scan_in_progress is False
                assert mock_config_flow.discovered_devices == devices
                mock_save.assert_called_once_with(devices)
                mock_show_form.assert_called_once()

    async def test_create_entries_for_devices_single(self, mock_config_flow, mock_device_data):
        """Test creating entry for single device."""
        # Setup
        mock_config_flow.port = 5001
        mock_config_flow.timeout = 10
        
        with patch.object(mock_config_flow, 'async_create_entry') as mock_create:
            mock_create.return_value = {"type": FlowResultType.CREATE_ENTRY}
            
            # Execute
            result = await mock_config_flow._create_entries_for_devices([mock_device_data])
            
            # Verify
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            assert call_args[1]["title"] == "VMC Test Device"
            assert call_args[1]["data"]["ip"] == "192.168.1.100"

    async def test_create_entries_for_devices_multiple(self, mock_config_flow):
        """Test creating entries for multiple devices."""
        # Setup
        devices = [
            {"ip": "192.168.1.100", "name": "Device 1"},
            {"ip": "192.168.1.101", "name": "Device 2"}
        ]
        
        with patch.object(mock_config_flow, '_show_device_selection_form') as mock_show_form:
            mock_show_form.return_value = {"type": FlowResultType.FORM, "step_id": "discovery"}
            
            # Execute
            result = await mock_config_flow._create_entries_for_devices(devices)
            
            # Verify
            mock_show_form.assert_called_once()

    async def test_incremental_scan_with_network_error(self, mock_config_flow):
        """Test incremental scan handling network errors gracefully."""
        # Setup
        mock_config_flow.ip_range = ["192.168.1.100"]
        mock_config_flow.current_ip_index = 0
        mock_config_flow.total_ips_to_scan = 1
        mock_config_flow.found_devices_session = []
        
        with patch('custom_components.vmc_helty_flow.helpers.get_device_info') as mock_get_device:
            mock_get_device.side_effect = Exception("Network error")
            
            with patch.object(mock_config_flow, '_finalize_incremental_scan') as mock_finalize:
                mock_finalize.return_value = {"type": FlowResultType.FORM, "step_id": "user"}
                
                # Execute
                result = await mock_config_flow._scan_next_ip()
                
                # Verify scan continues despite error
                assert mock_config_flow.current_ip_index == 1
                mock_finalize.assert_called_once()