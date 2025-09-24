"""Tests for VMC Helty Airflow sensor."""

from unittest.mock import MagicMock

import pytest

from custom_components.vmc_helty_flow.const import AIRFLOW_MAPPING
from custom_components.vmc_helty_flow.sensor import VmcHeltyAirflowSensor


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "VMC Test"
    coordinator.data = {
        "status": "VMGO,1,1,25,0,24",
    }
    return coordinator


class TestVmcHeltyAirflowSensor:
    """Test VMC Helty Airflow sensor."""

    @pytest.fixture
    def airflow_sensor(self, mock_coordinator):
        """Create airflow sensor instance."""
        return VmcHeltyAirflowSensor(mock_coordinator)

    def test_init(self, airflow_sensor, mock_coordinator):
        """Test sensor initialization."""
        assert airflow_sensor._attr_unique_id == f"{mock_coordinator.ip}_airflow"
        assert airflow_sensor._attr_name == f"{mock_coordinator.name} Portata d'Aria"
        assert airflow_sensor._attr_native_unit_of_measurement == "m³/h"
        assert airflow_sensor._attr_device_class == "volume_flow_rate"
        assert airflow_sensor._attr_state_class == "measurement"

    def test_native_value_no_data(self, airflow_sensor, mock_coordinator):
        """Test native_value when no data."""
        mock_coordinator.data = None
        assert airflow_sensor.native_value is None

    def test_native_value_no_status(self, airflow_sensor, mock_coordinator):
        """Test native_value when no status data."""
        mock_coordinator.data = {"sensors": "test"}
        assert airflow_sensor.native_value is None

    def test_native_value_invalid_status(self, airflow_sensor, mock_coordinator):
        """Test native_value with invalid status data."""
        mock_coordinator.data = {"status": "INVALID"}
        assert airflow_sensor.native_value is None

    @pytest.mark.parametrize(
        ("fan_speed", "expected_airflow"),
        [
            (0, 0),  # Spenta
            (1, 10),  # Velocità 1
            (2, 17),  # Velocità 2
            (3, 26),  # Velocità 3
            (4, 37),  # Velocità 4
        ],
    )
    def test_native_value_normal_speeds(
        self, airflow_sensor, mock_coordinator, fan_speed, expected_airflow
    ):
        """Test native_value for normal fan speeds."""
        mock_coordinator.data = {"status": f"VMGO,{fan_speed},1,25,0,24"}
        assert airflow_sensor.native_value == expected_airflow

    def test_native_value_night_mode(self, airflow_sensor, mock_coordinator):
        """Test native_value for night mode."""
        # Night mode (fan_speed = 5) has its own mapping
        mock_coordinator.data = {
            "status": "VMGO,5,1,25,0,24"  # fan_speed = 5 = night mode
        }
        # In night mode, airflow is 7 m³/h according to AIRFLOW_MAPPING
        expected = AIRFLOW_MAPPING[5]  # 7
        assert airflow_sensor.native_value == expected

    def test_native_value_hyperventilation(self, airflow_sensor, mock_coordinator):
        """Test native_value for hyperventilation mode."""
        # Hyperventilation mode (fan_speed = 6) has higher airflow
        mock_coordinator.data = {
            "status": "VMGO,6,1,25,0,24"  # fan_speed = 6 = hyperventilation
        }
        # In hyperventilation mode, airflow is 42 m³/h according to AIRFLOW_MAPPING
        expected = AIRFLOW_MAPPING[6]  # 42
        assert airflow_sensor.native_value == expected

    def test_native_value_free_cooling(self, airflow_sensor, mock_coordinator):
        """Test native_value for free cooling mode."""
        # Free cooling mode (fan_speed = 7) uses moderate airflow
        mock_coordinator.data = {
            "status": "VMGO,7,1,25,0,24"  # fan_speed = 7 = free cooling
        }
        # In free cooling mode, airflow is 26 m³/h according to AIRFLOW_MAPPING
        expected = AIRFLOW_MAPPING[7]  # 26
        assert airflow_sensor.native_value == expected

    def test_native_value_invalid_response_parts(
        self, airflow_sensor, mock_coordinator
    ):
        """Test native_value with invalid response parts."""
        mock_coordinator.data = {"status": "VMGO"}  # Too few parts
        assert airflow_sensor.native_value is None

    def test_native_value_invalid_fan_speed(self, airflow_sensor, mock_coordinator):
        """Test native_value with invalid fan speed."""
        mock_coordinator.data = {"status": "VMGO,invalid,1,25,0,24"}
        assert airflow_sensor.native_value is None

    def test_native_value_high_fan_speed_clamped(
        self, airflow_sensor, mock_coordinator
    ):
        """Test native_value with fan speed above maximum."""
        mock_coordinator.data = {
            "status": "VMGO,10,1,25,0,24"  # Fan speed 10 (not in mapping)
        }
        # Unknown fan speeds return 0 (default value from .get())
        expected = 0
        assert airflow_sensor.native_value == expected

    def test_airflow_mapping_constants(self):
        """Test that AIRFLOW_MAPPING constants are correct."""
        assert AIRFLOW_MAPPING[0] == 0
        assert AIRFLOW_MAPPING[1] == 10
        assert AIRFLOW_MAPPING[2] == 17
        assert AIRFLOW_MAPPING[3] == 26
        assert AIRFLOW_MAPPING[4] == 37
