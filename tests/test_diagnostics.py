"""Tests for diagnostics module."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from custom_components.vmc_helty_flow.diagnostics import (
    TO_REDACT,
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
)


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "VMC Test"
    coordinator.last_update_success = True
    coordinator.last_update = datetime(2023, 1, 1, 12, 0, 0)
    coordinator.update_interval = timedelta(seconds=30)
    coordinator.data = {
        "status": "VMGO,3,1,25,0,24,20,30,40,50,60,70,80,90,100,110,120"
    }
    return coordinator


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.title = "VMC Test Device"
    entry.domain = "vmc_helty_flow"
    entry.version = 1
    entry.data = {
        "host": "192.168.1.100",
        "password": "secret123",
        "model": "Flow",
        "manufacturer": "Helty",
    }
    entry.options = {
        "scan_interval": 30,
        "wifi_ssid": "TestNetwork",
        "wifi_password": "wifipass",
    }
    entry.source = "user"
    entry.unique_id = "unique_test_id"
    entry.entry_id = "test_entry"
    return entry


@pytest.fixture
def mock_hass(mock_coordinator, mock_config_entry):
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {"vmc_helty_flow": {mock_config_entry.entry_id: mock_coordinator}}
    return hass


class TestDiagnostics:
    """Test diagnostics functions."""

    def test_to_redact_constants(self):
        """Test TO_REDACT contains expected sensitive fields."""
        expected_fields = {
            "password",
            "network_password",
            "wifi_password",
            "ssid",
            "network_ssid",
            "wifi_ssid",
            "host",
            "ip",
            "mac",
            "serial_number",
            "unique_id",
            "username",
            "credentials",
        }
        assert expected_fields == TO_REDACT

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics_complete(
        self, mock_hass, mock_config_entry
    ):
        """Test diagnostics with complete data."""
        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # Check config_entry section
        assert result["config_entry"]["title"] == "VMC Test Device"
        assert result["config_entry"]["domain"] == "vmc_helty_flow"
        assert result["config_entry"]["version"] == 1
        assert result["config_entry"]["source"] == "user"
        assert result["config_entry"]["unique_id"] == "**REDACTED**"

        # Check that sensitive data is redacted
        assert result["config_entry"]["data"]["password"] == "**REDACTED**"
        assert result["config_entry"]["data"]["host"] == "**REDACTED**"
        assert result["config_entry"]["data"]["model"] == "Flow"
        assert result["config_entry"]["data"]["manufacturer"] == "Helty"

        assert result["config_entry"]["options"]["wifi_ssid"] == "**REDACTED**"
        assert result["config_entry"]["options"]["wifi_password"] == "**REDACTED**"
        assert result["config_entry"]["options"]["scan_interval"] == 30

        # Check coordinator section
        assert result["coordinator"]["ip"] == "**REDACTED**"
        assert result["coordinator"]["name"] == "VMC Test"
        assert result["coordinator"]["last_update_success"] is True
        assert result["coordinator"]["update_interval"] == 30.0

        # Check device_info section
        assert result["device_info"]["available"] is True
        assert result["device_info"]["model"] == "Flow"
        assert result["device_info"]["manufacturer"] == "Helty"

        # Check device_status section
        assert result["device_status"]["fan_speed_raw"] == "3"
        assert result["device_status"]["panel_led_raw"] == "1"
        assert result["device_status"]["sensors_raw"] == "0"
        assert result["device_status"]["lights_level_raw"] == "70"
        assert result["device_status"]["lights_timer_raw"] == "110"
        assert result["device_status"]["response_parts_count"] == 17
        assert result["device_status"]["full_response"] == "**REDACTED**"

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics_no_coordinator_data(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Test diagnostics when coordinator has no data."""
        mock_coordinator.data = None

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # Should still have basic sections
        assert "config_entry" in result
        assert "coordinator" in result
        assert "device_info" in result

        # Should not have device_status section
        assert "device_status" not in result

        # Coordinator data should be empty dict after redaction
        assert result["coordinator"]["data"] == {}

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics_empty_coordinator_data(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Test diagnostics when coordinator has empty data."""
        mock_coordinator.data = {}

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # Should have basic sections
        assert "config_entry" in result
        assert "coordinator" in result
        assert "device_info" in result

        # Should not have device_status section
        assert "device_status" not in result

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics_invalid_status(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Test diagnostics with invalid status format."""
        mock_coordinator.data = {"status": "VMGO,INVALID"}

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # Should have device_status with limited data
        assert result["device_status"]["fan_speed_raw"] == "INVALID"
        assert result["device_status"]["panel_led_raw"] == "unknown"
        assert result["device_status"]["sensors_raw"] == "unknown"
        assert result["device_status"]["response_parts_count"] == 2

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics_short_status(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Test diagnostics with short status response."""
        mock_coordinator.data = {"status": "VMGO,1,2"}

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # Should handle short responses gracefully
        assert result["device_status"]["fan_speed_raw"] == "1"
        assert result["device_status"]["panel_led_raw"] == "2"
        assert result["device_status"]["sensors_raw"] == "unknown"
        assert result["device_status"]["lights_level_raw"] == "unknown"
        assert result["device_status"]["lights_timer_raw"] == "unknown"
        assert result["device_status"]["response_parts_count"] == 3

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics_non_vmgo_status(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Test diagnostics with non-VMGO status."""
        mock_coordinator.data = {"status": "ERROR,something,else"}

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # Should not have device_status section for non-VMGO responses
        assert "device_status" not in result

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics_status_parsing_error(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Test diagnostics when status parsing raises exception."""
        # Create data that will cause an exception during parsing
        mock_coordinator.data = {"status": MagicMock()}
        mock_coordinator.data["status"].startswith.side_effect = Exception(
            "Parse error"
        )

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # Should have device_status with parsing_error flag
        assert result["device_status"]["parsing_error"] is True

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics_no_unique_id(
        self, mock_hass, mock_config_entry
    ):
        """Test diagnostics when config entry has no unique_id."""
        mock_config_entry.unique_id = None

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # Should handle None unique_id gracefully
        assert result["config_entry"]["unique_id"] is None

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics_missing_model_manufacturer(
        self, mock_hass, mock_config_entry
    ):
        """Test diagnostics when model/manufacturer are missing from config."""
        mock_config_entry.data = {
            "host": "192.168.1.100",
            "password": "secret123",
        }

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # Should use default values
        assert result["device_info"]["model"] == "Unknown"
        assert result["device_info"]["manufacturer"] == "Helty"

    @pytest.mark.asyncio
    async def test_async_get_device_diagnostics(self, mock_hass, mock_config_entry):
        """Test device diagnostics returns same as config entry diagnostics."""
        mock_device = MagicMock()

        config_result = await async_get_config_entry_diagnostics(
            mock_hass, mock_config_entry
        )
        device_result = await async_get_device_diagnostics(
            mock_hass, mock_config_entry, mock_device
        )

        # Should be identical
        assert device_result == config_result
