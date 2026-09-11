"""Tests for diagnostics module."""

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from custom_components.vmc_helty_flow.const import (
    CONF_EASC_ABSOLUTE_HUMIDITY,
    CONF_EASC_CONFIG,
    CONF_EASC_DEW_POINT_DELTA,
    CONF_EASC_ENABLED,
    CONF_EASC_HUMIDITY_SOURCE,
    CONF_EASC_TEMPERATURE_EXTERNAL,
    CONF_EASC_TEMPERATURE_INTERNAL,
    CONF_EASC_TEMPERATURE_SOURCE,
    EASC_SOURCE_VMC,
)
from custom_components.vmc_helty_flow.diagnostics import (
    TO_REDACT,
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
)
from custom_components.vmc_helty_flow.easc_provider import EASCDataProvider


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.port = 5001
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

    # ------------------------------------------------------------------
    # EASC diagnostics section
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_easc_section_always_present(self, mock_hass, mock_config_entry):
        """EASC section is present even when not configured."""
        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)
        assert "easc" in result

    @pytest.mark.asyncio
    async def test_easc_not_configured(self, mock_hass, mock_config_entry):
        """When no EASC config in options → configured=False, all VMC sources."""
        # mock_config_entry.options has no CONF_EASC_CONFIG
        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)
        easc = result["easc"]

        assert easc["configured"] is False
        # All sensors should default to VMC sources
        for sensor_key in ("absolute_humidity", "dew_point", "comfort_index"):
            assert easc["sensors"][sensor_key]["enabled"] is False
            assert easc["sensors"][sensor_key]["temperature_source"]["source"] == "vmc"
            assert easc["sensors"][sensor_key]["humidity_source"]["source"] == "vmc"
        assert easc["sensors"]["dew_point_delta"]["enabled"] is False

    @pytest.mark.asyncio
    async def test_easc_configured_vmc_sources(self, mock_hass, mock_config_entry):
        """When EASC configured with VMC sources → configured=True, available=True."""
        mock_config_entry.options[CONF_EASC_CONFIG] = {
            "advanced_sensors": {
                CONF_EASC_ABSOLUTE_HUMIDITY: {
                    CONF_EASC_ENABLED: True,
                    CONF_EASC_TEMPERATURE_SOURCE: EASC_SOURCE_VMC,
                    CONF_EASC_HUMIDITY_SOURCE: EASC_SOURCE_VMC,
                }
            }
        }
        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)
        easc = result["easc"]

        assert easc["configured"] is True
        ah = easc["sensors"]["absolute_humidity"]
        assert ah["enabled"] is True
        assert ah["temperature_source"] == {"source": "vmc", "available": True}
        assert ah["humidity_source"] == {"source": "vmc", "available": True}

    @pytest.mark.asyncio
    async def test_easc_external_entity_available(self, mock_hass, mock_config_entry):
        """External entity available → shows state and last_updated."""
        state = SimpleNamespace(
            state="22.5",
            last_updated=datetime(2026, 3, 27, 12, 0, 0),
        )
        mock_hass.states.get.return_value = state

        mock_config_entry.options[CONF_EASC_CONFIG] = {
            "advanced_sensors": {
                CONF_EASC_ABSOLUTE_HUMIDITY: {
                    CONF_EASC_ENABLED: True,
                    CONF_EASC_TEMPERATURE_SOURCE: "sensor.room_temp",
                    CONF_EASC_HUMIDITY_SOURCE: EASC_SOURCE_VMC,
                }
            }
        }
        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)
        t_src = result["easc"]["sensors"]["absolute_humidity"]["temperature_source"]

        assert t_src["source"] == "sensor.room_temp"
        assert t_src["available"] is True
        assert t_src["state"] == "22.5"
        assert "2026-03-27" in t_src["last_updated"]

    @pytest.mark.asyncio
    async def test_easc_external_entity_not_found(self, mock_hass, mock_config_entry):
        """External entity not in HA → available=False, reason=entity_not_found."""
        mock_hass.states.get.return_value = None

        mock_config_entry.options[CONF_EASC_CONFIG] = {
            "advanced_sensors": {
                CONF_EASC_ABSOLUTE_HUMIDITY: {
                    CONF_EASC_ENABLED: True,
                    CONF_EASC_TEMPERATURE_SOURCE: "sensor.missing",
                    CONF_EASC_HUMIDITY_SOURCE: EASC_SOURCE_VMC,
                }
            }
        }
        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)
        t_src = result["easc"]["sensors"]["absolute_humidity"]["temperature_source"]

        assert t_src["available"] is False
        assert t_src["reason"] == "entity_not_found"

    @pytest.mark.asyncio
    async def test_easc_external_entity_unavailable(self, mock_hass, mock_config_entry):
        """External entity in HA but state=unavailable → available=False."""
        state = SimpleNamespace(state="unavailable", last_updated=None)
        mock_hass.states.get.return_value = state

        mock_config_entry.options[CONF_EASC_CONFIG] = {
            "advanced_sensors": {
                CONF_EASC_ABSOLUTE_HUMIDITY: {
                    CONF_EASC_ENABLED: True,
                    CONF_EASC_TEMPERATURE_SOURCE: "sensor.broken",
                    CONF_EASC_HUMIDITY_SOURCE: EASC_SOURCE_VMC,
                }
            }
        }
        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)
        t_src = result["easc"]["sensors"]["absolute_humidity"]["temperature_source"]

        assert t_src["available"] is False
        assert t_src["reason"] == "unavailable"

    @pytest.mark.asyncio
    async def test_easc_dew_point_delta_sources(self, mock_hass, mock_config_entry):
        """DewPointDelta shows internal/external temperature sources."""
        mock_hass.states.get.return_value = None  # entities not found

        mock_config_entry.options[CONF_EASC_CONFIG] = {
            "advanced_sensors": {
                CONF_EASC_DEW_POINT_DELTA: {
                    CONF_EASC_ENABLED: True,
                    CONF_EASC_TEMPERATURE_INTERNAL: "sensor.indoor",
                    CONF_EASC_TEMPERATURE_EXTERNAL: "weather.home",
                    CONF_EASC_HUMIDITY_SOURCE: EASC_SOURCE_VMC,
                }
            }
        }
        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)
        dpd = result["easc"]["sensors"]["dew_point_delta"]

        assert dpd["enabled"] is True
        assert dpd["temperature_internal_source"]["source"] == "sensor.indoor"
        assert dpd["temperature_external_source"]["source"] == "weather.home"
        assert dpd["humidity_source"] == {"source": "vmc", "available": True}


class TestEascProviderDebugLogging:
    """Tests for EASC-008 debug logging in EASCDataProvider."""

    def _make_coordinator(self, t_int=215, t_ext=80, hum=550):
        coordinator = MagicMock()
        coordinator.data = {
            "sensors": f"VMGI,{t_int},{t_ext},{hum},400,0,0,0,0,0,0,0,0,0,0"
        }
        return coordinator

    def test_vmc_temperature_logs_debug(self):
        """get_temperature(VMC) emits a DEBUG log."""
        coordinator = self._make_coordinator()
        provider = EASCDataProvider(MagicMock(), coordinator)

        with patch(
            "custom_components.vmc_helty_flow.easc_provider._LOGGER"
        ) as mock_log:
            provider.get_temperature(EASC_SOURCE_VMC)
            mock_log.debug.assert_called_once()
            call_msg = mock_log.debug.call_args[0][0]
            assert "vmc" in call_msg

    def test_entity_temperature_logs_debug_on_success(self):
        """get_temperature(entity) emits DEBUG on successful read."""
        hass = MagicMock()
        hass.states.get.return_value = SimpleNamespace(
            state="22.5", attributes={"unit_of_measurement": "°C"}
        )
        coordinator = self._make_coordinator()
        provider = EASCDataProvider(hass, coordinator)

        with patch(
            "custom_components.vmc_helty_flow.easc_provider._LOGGER"
        ) as mock_log:
            provider.get_temperature("sensor.room")
            mock_log.debug.assert_called_once()
            mock_log.warning.assert_not_called()

    def test_entity_temperature_logs_warning_and_fallback_debug_on_fail(self):
        """get_temperature(unavailable entity) logs warning + fallback debug."""
        hass = MagicMock()
        hass.states.get.return_value = None  # entity missing
        coordinator = self._make_coordinator()
        provider = EASCDataProvider(hass, coordinator)

        with patch(
            "custom_components.vmc_helty_flow.easc_provider._LOGGER"
        ) as mock_log:
            provider.get_temperature("sensor.missing")
            mock_log.warning.assert_called_once()
            mock_log.debug.assert_called_once()
            debug_msg = mock_log.debug.call_args[0][0]
            assert "fallback" in debug_msg

    def test_humidity_logs_debug_vmc(self):
        """get_humidity(VMC) emits a DEBUG log."""
        coordinator = self._make_coordinator()
        provider = EASCDataProvider(MagicMock(), coordinator)

        with patch(
            "custom_components.vmc_helty_flow.easc_provider._LOGGER"
        ) as mock_log:
            provider.get_humidity(EASC_SOURCE_VMC)
            mock_log.debug.assert_called_once()
            call_msg = mock_log.debug.call_args[0][0]
            assert "humidity" in call_msg
