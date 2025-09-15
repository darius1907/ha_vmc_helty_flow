"""Tests for sensor module."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.vmc_helty_flow import sensor
from custom_components.vmc_helty_flow.const import DOMAIN
from custom_components.vmc_helty_flow.sensor import VmcHeltySensor


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "VMC Test"
    coordinator.data = {
        "sensors": "VMGI,245,205,650,450,50,75,80,90,100,1,2,3,4,1000",
        "status": "VMGO,3,1,25,0,24",
    }
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {DOMAIN: {"test_entry": "mock_coordinator"}}
    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry"
    return entry


@pytest.mark.asyncio
async def test_async_setup_entry(mock_hass, mock_config_entry, mock_coordinator):
    """Test async_setup_entry creates all expected entities."""
    # Setup coordinator in hass.data
    mock_hass.data[DOMAIN][mock_config_entry.entry_id] = mock_coordinator

    async_add_entities = MagicMock()

    await sensor.async_setup_entry(mock_hass, mock_config_entry, async_add_entities)

    # Verify async_add_entities was called with entities
    async_add_entities.assert_called_once()
    entities = async_add_entities.call_args[0][0]

    # Should have 15 entities total
    assert len(entities) == 15

    # Check some entity types
    sensor_entities = [e for e in entities if isinstance(e, VmcHeltySensor)]
    assert len(sensor_entities) >= 5  # At least the 5 main sensors


class TestVmcHeltySensor:
    """Test VmcHeltySensor class."""

    def test_init(self, mock_coordinator):
        """Test initialization."""
        sensor_entity = VmcHeltySensor(
            mock_coordinator,
            "temperature_internal",
            "Temperatura Interna",
            "°C",
            "temperature",
            "measurement",
        )

        assert sensor_entity._sensor_key == "temperature_internal"
        assert sensor_entity._attr_unique_id == "192.168.1.100_temperature_internal"
        assert sensor_entity._attr_name == "VMC Test Temperatura Interna"
        assert sensor_entity._attr_native_unit_of_measurement == "°C"
        assert sensor_entity._attr_device_class == "temperature"
        assert sensor_entity._attr_state_class == "measurement"

    def test_native_value_no_data(self, mock_coordinator):
        """Test native_value when no data."""
        mock_coordinator.data = None
        sensor_entity = VmcHeltySensor(
            mock_coordinator, "temperature_internal", "Test", "°C"
        )

        assert sensor_entity.native_value is None

    def test_native_value_no_sensors_data(self, mock_coordinator):
        """Test native_value when no sensors data."""
        mock_coordinator.data = {"status": "VMGO,3,1,25,0,24"}
        sensor_entity = VmcHeltySensor(
            mock_coordinator, "temperature_internal", "Test", "°C"
        )

        assert sensor_entity.native_value is None

    def test_native_value_invalid_sensors_data(self, mock_coordinator):
        """Test native_value with invalid sensors data."""
        mock_coordinator.data = {"sensors": "INVALID"}
        sensor_entity = VmcHeltySensor(
            mock_coordinator, "temperature_internal", "Test", "°C"
        )

        assert sensor_entity.native_value is None

    def test_native_value_short_sensors_data(self, mock_coordinator):
        """Test native_value with short sensors data."""
        mock_coordinator.data = {"sensors": "VMGI,245,205"}
        sensor_entity = VmcHeltySensor(
            mock_coordinator, "temperature_internal", "Test", "°C"
        )

        assert sensor_entity.native_value is None

    def test_native_value_temperature_internal(self, mock_coordinator):
        """Test native_value for internal temperature."""
        mock_coordinator.data = {
            "sensors": "VMGI,245,205,650,450,50,75,80,90,100,1,2,3,4,1000"
        }
        sensor_entity = VmcHeltySensor(
            mock_coordinator, "temperature_internal", "Test", "°C"
        )

        # 245 / 10 = 24.5
        assert sensor_entity.native_value == 24.5

    def test_native_value_temperature_external(self, mock_coordinator):
        """Test native_value for external temperature."""
        mock_coordinator.data = {
            "sensors": "VMGI,245,205,650,450,50,75,80,90,100,1,2,3,4,1000"
        }
        sensor_entity = VmcHeltySensor(
            mock_coordinator, "temperature_external", "Test", "°C"
        )

        # 205 / 10 = 20.5
        assert sensor_entity.native_value == 20.5

    def test_native_value_humidity(self, mock_coordinator):
        """Test native_value for humidity."""
        mock_coordinator.data = {
            "sensors": "VMGI,245,205,650,450,50,75,80,90,100,1,2,3,4,1000"
        }
        sensor_entity = VmcHeltySensor(mock_coordinator, "humidity", "Test", "%")

        # 650 / 10 = 65.0
        assert sensor_entity.native_value == 65.0

    def test_native_value_co2(self, mock_coordinator):
        """Test native_value for CO2."""
        mock_coordinator.data = {
            "sensors": "VMGI,245,205,650,450,50,75,80,90,100,1,2,3,4,1000"
        }
        sensor_entity = VmcHeltySensor(mock_coordinator, "co2", "Test", "ppm")

        # 450 (no division)
        assert sensor_entity.native_value == 450

    def test_native_value_voc(self, mock_coordinator):
        """Test native_value for VOC."""
        mock_coordinator.data = {
            "sensors": "VMGI,245,205,650,450,50,75,80,90,100,1,2,3,4,1000"
        }
        sensor_entity = VmcHeltySensor(mock_coordinator, "voc", "Test", "ppb")

        # 1000 (position 14)
        assert sensor_entity.native_value == 1000

    def test_native_value_unknown_sensor(self, mock_coordinator):
        """Test native_value for unknown sensor type."""
        mock_coordinator.data = {
            "sensors": "VMGI,245,205,650,450,50,75,80,90,100,1,2,3,4,1000"
        }
        sensor_entity = VmcHeltySensor(mock_coordinator, "unknown", "Test", "unit")

        assert sensor_entity.native_value is None

    def test_native_value_empty_values(self, mock_coordinator):
        """Test native_value with empty values in sensors data."""
        mock_coordinator.data = {
            "sensors": "VMGI,,205,650,450,50,75,80,90,100,1,2,3,4,1000"
        }
        sensor_entity = VmcHeltySensor(
            mock_coordinator, "temperature_internal", "Test", "°C"
        )

        assert sensor_entity.native_value is None

    def test_native_value_invalid_values(self, mock_coordinator):
        """Test native_value with invalid values in sensors data."""
        mock_coordinator.data = {
            "sensors": "VMGI,invalid,205,650,450,50,75,80,90,100,1,2,3,4,1000"
        }
        sensor_entity = VmcHeltySensor(
            mock_coordinator, "temperature_internal", "Test", "°C"
        )

        assert sensor_entity.native_value is None
