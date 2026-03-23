"""Tests for VMC Helty Power sensor."""

from unittest.mock import MagicMock

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from custom_components.vmc_helty_flow.const import ENTITY_NAME_PREFIX, POWER_MAPPING
from custom_components.vmc_helty_flow.sensor import VmcHeltyPowerSensor


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "TestVMC"
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.data = {"status": "VMGO,0,1,0,0,0"}
    return coordinator


async def test_power_sensor_init(mock_coordinator):
    """Test power sensor initialization."""
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.unique_id == f"{mock_coordinator.name_slug}_power"
    assert sensor.name == f"{ENTITY_NAME_PREFIX} {mock_coordinator.name} Power"
    assert sensor.native_unit_of_measurement == "W"
    assert sensor.device_class == SensorDeviceClass.POWER
    assert sensor.state_class == SensorStateClass.MEASUREMENT
    assert sensor.icon == "mdi:flash"


async def test_power_sensor_speed_0_off(mock_coordinator):
    """Test power sensor with speed 0 (off)."""
    mock_coordinator.data = {"status": "VMGO,0,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value == 0


async def test_power_sensor_speed_1(mock_coordinator):
    """Test power sensor with speed 1."""
    mock_coordinator.data = {"status": "VMGO,1,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value == 10


async def test_power_sensor_speed_2(mock_coordinator):
    """Test power sensor with speed 2."""
    mock_coordinator.data = {"status": "VMGO,2,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value == 20


async def test_power_sensor_speed_3(mock_coordinator):
    """Test power sensor with speed 3."""
    mock_coordinator.data = {"status": "VMGO,3,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value == 35


async def test_power_sensor_speed_4(mock_coordinator):
    """Test power sensor with speed 4."""
    mock_coordinator.data = {"status": "VMGO,4,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value == 50


async def test_power_sensor_speed_5_hyperventilation(mock_coordinator):
    """Test power sensor with speed 5 (hyperventilation)."""
    mock_coordinator.data = {"status": "VMGO,5,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value == 55


async def test_power_sensor_speed_6_night_mode(mock_coordinator):
    """Test power sensor with speed 6 (night mode)."""
    mock_coordinator.data = {"status": "VMGO,6,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value == 5


async def test_power_sensor_speed_7_free_cooling(mock_coordinator):
    """Test power sensor with speed 7 (free cooling)."""
    mock_coordinator.data = {"status": "VMGO,7,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value == 35


async def test_power_sensor_no_data(mock_coordinator):
    """Test power sensor with no data."""
    mock_coordinator.data = None
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value is None


async def test_power_sensor_no_status(mock_coordinator):
    """Test power sensor with no status data."""
    mock_coordinator.data = {}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value is None


async def test_power_sensor_invalid_status(mock_coordinator):
    """Test power sensor with invalid status format."""
    mock_coordinator.data = {"status": "INVALID"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value is None


async def test_power_sensor_insufficient_parts(mock_coordinator):
    """Test power sensor with insufficient status parts."""
    mock_coordinator.data = {"status": "VMGO"}  # Missing fan speed part
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value is None


async def test_power_sensor_extra_attributes(mock_coordinator):
    """Test power sensor extra state attributes."""
    mock_coordinator.data = {"status": "VMGO,3,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["fan_speed"] == 3
    assert attrs["airflow_m3h"] == 26  # From AIRFLOW_MAPPING
    assert attrs["efficiency_m3h_per_watt"] == round(26 / 35, 2)
    assert "power_mapping" in attrs


async def test_power_sensor_efficiency_at_speed_0(mock_coordinator):
    """Test efficiency calculation at speed 0 (division by zero protection)."""
    mock_coordinator.data = {"status": "VMGO,0,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["efficiency_m3h_per_watt"] == 0


async def test_power_sensor_all_speeds_mapped(mock_coordinator):
    """Test that all speeds have valid power mapping."""
    for speed in range(8):  # 0-7
        mock_coordinator.data = {"status": f"VMGO,{speed},1,0,0,0"}
        sensor = VmcHeltyPowerSensor(mock_coordinator)

        power = sensor.native_value
        assert power is not None
        assert power >= 0
        assert power == POWER_MAPPING[speed]


async def test_power_sensor_invalid_fan_speed_value(mock_coordinator):
    """Test power sensor with invalid fan speed value."""
    mock_coordinator.data = {"status": "VMGO,invalid,1,0,0,0"}
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.native_value is None


async def test_power_sensor_extra_attributes_no_data(mock_coordinator):
    """Test extra attributes with no data."""
    mock_coordinator.data = None
    sensor = VmcHeltyPowerSensor(mock_coordinator)

    assert sensor.extra_state_attributes is None
