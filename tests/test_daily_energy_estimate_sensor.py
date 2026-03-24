"""Tests for VMC Helty Daily Energy Estimate sensor."""

from unittest.mock import MagicMock

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy

from custom_components.vmc_helty_flow.const import ENTITY_NAME_PREFIX
from custom_components.vmc_helty_flow.sensor import VmcHeltyDailyEnergyEstimateSensor


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "TestVMC"
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.data = {"status": "VMGO,2,1,0,0,0"}  # Default speed 2
    return coordinator


async def test_daily_energy_sensor_init(mock_coordinator):
    """Test daily energy sensor initialization."""
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    assert sensor.unique_id == f"{mock_coordinator.name_slug}_daily_energy_estimate"
    assert (
        sensor.name
        == f"{ENTITY_NAME_PREFIX} {mock_coordinator.name} Daily Energy Estimate"
    )
    assert sensor.native_unit_of_measurement == UnitOfEnergy.WATT_HOUR
    assert sensor.device_class == SensorDeviceClass.ENERGY
    assert sensor.state_class == SensorStateClass.TOTAL
    assert sensor.icon == "mdi:lightning-bolt-circle"


async def test_daily_energy_baseline_speed_2(mock_coordinator):
    """Test daily energy estimate at baseline speed 2."""
    mock_coordinator.data = {"status": "VMGO,2,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    value = sensor.native_value
    assert value is not None
    # Baseline: 4*0 + 5*4.6 + 12*6.5 + 2*9 + 1*16.5 = 135.5 Wh
    assert value == 135.5  # Speed 2: 1.0x baseline


async def test_daily_energy_speed_0_off(mock_coordinator):
    """Test daily energy estimate when off."""
    mock_coordinator.data = {"status": "VMGO,0,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    value = sensor.native_value
    assert value is not None
    assert value == 135.5  # Returns baseline even when off


async def test_daily_energy_speed_1_lower(mock_coordinator):
    """Test daily energy estimate at speed 1 (lower consumption)."""
    mock_coordinator.data = {"status": "VMGO,1,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    value = sensor.native_value
    assert value is not None
    assert value == 135.5 * 0.9  # Speed 1: 0.9x baseline = 121.95 Wh


async def test_daily_energy_speed_3_higher(mock_coordinator):
    """Test daily energy estimate at speed 3 (higher consumption)."""
    mock_coordinator.data = {"status": "VMGO,3,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    value = sensor.native_value
    assert value is not None
    assert value == 135.5 * 1.1  # Speed 3: 1.1x baseline = 149.05 Wh


async def test_daily_energy_speed_4_highest(mock_coordinator):
    """Test daily energy estimate at speed 4 (highest normal consumption)."""
    mock_coordinator.data = {"status": "VMGO,4,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    value = sensor.native_value
    assert value is not None
    assert value == 135.5 * 1.2  # Speed 4: 1.2x baseline = 162.6 Wh


async def test_daily_energy_speed_6_night_mode(mock_coordinator):
    """Test daily energy estimate in night mode (lower consumption)."""
    mock_coordinator.data = {"status": "VMGO,6,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    value = sensor.native_value
    assert value is not None
    assert value == 135.5 * 0.8  # Night mode: 0.8x baseline = 108.4 Wh


async def test_daily_energy_speed_5_hyperventilation(mock_coordinator):
    """Test daily energy estimate in hyperventilation mode."""
    mock_coordinator.data = {"status": "VMGO,5,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    value = sensor.native_value
    assert value is not None
    assert value == 135.5 * 1.3  # Hyperventilation: 1.3x baseline = 176.15 Wh


async def test_daily_energy_speed_7_free_cooling(mock_coordinator):
    """Test daily energy estimate in free cooling mode."""
    mock_coordinator.data = {"status": "VMGO,7,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    value = sensor.native_value
    assert value is not None
    assert value == 135.5 * 1.3  # Free cooling: 1.3x baseline = 176.15 Wh


async def test_daily_energy_no_data(mock_coordinator):
    """Test daily energy sensor with no data."""
    mock_coordinator.data = None
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    assert sensor.native_value is None


async def test_daily_energy_no_status(mock_coordinator):
    """Test daily energy sensor with no status data."""
    mock_coordinator.data = {}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    assert sensor.native_value is None


async def test_daily_energy_invalid_status(mock_coordinator):
    """Test daily energy sensor with invalid status format."""
    mock_coordinator.data = {"status": "INVALID"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    assert sensor.native_value is None


async def test_daily_energy_insufficient_parts(mock_coordinator):
    """Test daily energy sensor with insufficient status parts."""
    mock_coordinator.data = {"status": "VMGO"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    assert sensor.native_value is None


async def test_daily_energy_extra_attributes(mock_coordinator):
    """Test daily energy sensor extra state attributes."""
    mock_coordinator.data = {"status": "VMGO,2,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["current_power_w"] == 6.5  # Speed 2 = 6.5W
    assert attrs["current_fan_speed"] == 2
    assert "daily_cost_eur" in attrs
    assert "monthly_energy_kwh" in attrs
    assert "yearly_energy_kwh" in attrs
    assert "yearly_cost_eur" in attrs
    assert attrs["typical_runtime_hours"] == 20


async def test_daily_energy_cost_calculations(mock_coordinator):
    """Test cost calculation attributes."""
    mock_coordinator.data = {"status": "VMGO,2,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    attrs = sensor.extra_state_attributes
    daily_energy_wh = 135.5
    daily_cost = (daily_energy_wh / 1000) * 0.25

    assert attrs["daily_cost_eur"] == round(daily_cost, 2)
    assert attrs["monthly_energy_kwh"] == round((daily_energy_wh * 30) / 1000, 1)
    assert attrs["yearly_energy_kwh"] == round((daily_energy_wh * 365) / 1000, 1)


async def test_daily_energy_all_speeds(mock_coordinator):
    """Test daily energy estimates for all valid speeds."""
    expected_multipliers = {
        0: 1.0,  # Off - baseline
        1: 0.9,  # Speed 1 - lower
        2: 1.0,  # Speed 2 - baseline
        3: 1.1,  # Speed 3 - higher
        4: 1.2,  # Speed 4 - highest
        5: 1.3,  # Hyperventilation
        6: 0.8,  # Night mode - lowest
        7: 1.3,  # Free cooling
    }

    baseline = 135.5

    for speed, multiplier in expected_multipliers.items():
        mock_coordinator.data = {"status": f"VMGO,{speed},1,0,0,0"}
        sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

        expected_value = baseline * multiplier
        assert (
            sensor.native_value == expected_value
        ), f"Speed {speed}: expected {expected_value}, got {sensor.native_value}"


async def test_daily_energy_invalid_fan_speed_value(mock_coordinator):
    """Test daily energy sensor with invalid fan speed value."""
    mock_coordinator.data = {"status": "VMGO,invalid,1,0,0,0"}
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    assert sensor.native_value is None


async def test_daily_energy_extra_attributes_no_data(mock_coordinator):
    """Test extra attributes with no data."""
    mock_coordinator.data = None
    sensor = VmcHeltyDailyEnergyEstimateSensor(mock_coordinator)

    assert sensor.extra_state_attributes is None
