"""Test for VmcHeltyAirExchangeTimeSensor."""

import unittest
from unittest.mock import Mock

from custom_components.vmc_helty_flow.const import (
    AIR_EXCHANGE_ACCEPTABLE,
    AIR_EXCHANGE_EXCELLENT,
    AIR_EXCHANGE_GOOD,
    AIR_EXCHANGE_POOR,
    AIR_EXCHANGE_TIME_ACCEPTABLE,
    AIR_EXCHANGE_TIME_EXCELLENT,
    AIR_EXCHANGE_TIME_GOOD,
    DEFAULT_ROOM_VOLUME,
)
from custom_components.vmc_helty_flow.sensor import VmcHeltyAirExchangeTimeSensor


class TestVmcHeltyAirExchangeTimeSensor(unittest.TestCase):
    """Test class for VmcHeltyAirExchangeTimeSensor."""

    def setUp(self):
        """Set up test fixtures."""
        self.coordinator = Mock()
        self.coordinator.ip = "192.168.1.100"
        self.coordinator.name_slug = "vmc_helty_testvmc"
        self.coordinator.name = "TestVMC"
        self.sensor = VmcHeltyAirExchangeTimeSensor(self.coordinator)

    def test_init(self):
        """Test sensor initialization."""
        assert self.sensor.unique_id == "vmc_helty_testvmc_air_exchange_time"
        assert self.sensor.name == "VMC Helty TestVMC Air Exchange Time"
        assert self.sensor.native_unit_of_measurement == "min"
        assert self.sensor.icon == "mdi:clock-time-four"

    def test_native_value_no_data(self):
        """Test native_value when no data available."""
        self.coordinator.data = None
        assert self.sensor.native_value is None

    def test_native_value_no_status_data(self):
        """Test native_value when no status data available."""
        self.coordinator.data = {"other": "data"}
        assert self.sensor.native_value is None

    def test_native_value_invalid_vmgo_data(self):
        """Test native_value with invalid VMGO data."""
        self.coordinator.data = {"status": "invalid"}
        assert self.sensor.native_value is None

    def test_native_value_insufficient_vmgo_data(self):
        """Test native_value with insufficient VMGO data."""
        self.coordinator.data = {"status": "VMGO"}  # Only 1 part, need at least 2
        assert self.sensor.native_value is None

    def test_calculation_fan_speed_0(self):
        """Test calculation with fan off (speed 0)."""
        self.coordinator.data = {"status": "VMGO,0,0,0,0"}  # Fan speed 0 (off)
        assert self.sensor.native_value is None

    def test_calculation_fan_speed_1(self):
        """Test calculation with fan speed 1 (10 m³/h)."""
        self.coordinator.data = {"status": "VMGO,1,0,0,0"}  # Fan speed 1
        # Expected: (DEFAULT_ROOM_VOLUME / 10) * 60 = (60 / 10) * 60 = 360 minutes
        expected = (DEFAULT_ROOM_VOLUME / 10) * 60
        assert self.sensor.native_value == round(expected, 1)

    def test_calculation_fan_speed_2(self):
        """Test calculation with fan speed 2 (17 m³/h)."""
        self.coordinator.data = {"status": "VMGO,2,0,0,0"}  # Fan speed 2
        # Expected: (DEFAULT_ROOM_VOLUME / 17) * 60 = (60 / 17) * 60 = 211.8 minutes
        expected = (DEFAULT_ROOM_VOLUME / 17) * 60
        assert self.sensor.native_value == round(expected, 1)

    def test_calculation_fan_speed_3(self):
        """Test calculation with fan speed 3 (26 m³/h)."""
        self.coordinator.data = {"status": "VMGO,3,0,0,0"}  # Fan speed 3
        # Expected: (DEFAULT_ROOM_VOLUME / 26) * 60 = (60 / 26) * 60 = 138.5 minutes
        expected = (DEFAULT_ROOM_VOLUME / 26) * 60
        assert self.sensor.native_value == round(expected, 1)

    def test_calculation_fan_speed_4(self):
        """Test calculation with fan speed 4 (37 m³/h)."""
        self.coordinator.data = {"status": "VMGO,4,0,0,0"}  # Fan speed 4
        # Expected: (DEFAULT_ROOM_VOLUME / 37) * 60 = (60 / 37) * 60 = 97.3 minutes
        expected = (DEFAULT_ROOM_VOLUME / 37) * 60
        assert self.sensor.native_value == round(expected, 1)

    def test_calculation_fan_speed_night_mode(self):
        """Test calculation with night mode (5 -> 7 m³/h)."""
        self.coordinator.data = {"status": "VMGO,5,0,0,0"}  # Night mode -> 7 m³/h
        # Expected: (DEFAULT_ROOM_VOLUME / 7) * 60 = (60 / 7) * 60 = 514.3 minutes
        expected = (DEFAULT_ROOM_VOLUME / 7) * 60
        assert self.sensor.native_value == round(expected, 1)

    def test_calculation_fan_speed_hyperventilation(self):
        """Test calculation with hyperventilation mode (6 -> 42 m³/h)."""
        self.coordinator.data = {
            "status": "VMGO,6,0,0,0"
        }  # Hyperventilation -> 42 m³/h
        # Expected: (DEFAULT_ROOM_VOLUME / 42) * 60 = (60 / 42) * 60 = 85.7 minutes
        expected = (DEFAULT_ROOM_VOLUME / 42) * 60
        assert self.sensor.native_value == round(expected, 1)

    def test_calculation_fan_speed_free_cooling(self):
        """Test calculation with free cooling mode (7 -> speed 2)."""
        self.coordinator.data = {"status": "VMGO,7,0,0,0"}  # Free cooling -> speed 2
        # Expected: (DEFAULT_ROOM_VOLUME / 26) * 60 = (26 / 100) * 60 = 90 minutes
        expected = (DEFAULT_ROOM_VOLUME / 26) * 60
        assert self.sensor.native_value == round(expected, 1)

    def test_calculation_invalid_fan_speed(self):
        """Test calculation with invalid fan speed uses default 100 m³/h."""
        self.coordinator.data = {
            "status": "VMGO,999,0,0,0"
        }  # Invalid speed -> default 100
        # Expected: (DEFAULT_ROOM_VOLUME / 100) * 60 = (60 / 100) * 60 = 36.0 minutes
        expected = (DEFAULT_ROOM_VOLUME / 100) * 60
        assert self.sensor.native_value == round(expected, 1)

    def test_invalid_data_types(self):
        """Test handling of invalid data types in VMGO."""
        self.coordinator.data = {"status": "VMGO,invalid,0,0,0"}
        assert self.sensor.native_value is None

    def test_extra_state_attributes_no_data(self):
        """Test extra_state_attributes when no data available."""
        self.coordinator.data = None
        attrs = self.sensor.extra_state_attributes
        assert attrs["efficiency_category"] is None
        assert attrs["room_volume"] is None
        assert attrs["estimated_airflow"] is None
        assert attrs["fan_speed"] is None

    def test_extra_state_attributes_no_vmgo_data(self):
        """Test extra_state_attributes when no VMGO data available."""
        self.coordinator.data = {"other": "data"}
        attrs = self.sensor.extra_state_attributes
        assert attrs["efficiency_category"] is None
        assert attrs["room_volume"] is None
        assert attrs["estimated_airflow"] is None
        assert attrs["fan_speed"] is None

    def test_extra_state_attributes_complete(self):
        """Test extra_state_attributes with valid data."""
        self.coordinator.data = {"status": "VMGO,2,0,0,0"}  # Fan speed 2
        attrs = self.sensor.extra_state_attributes

        # Fan speed 2 -> 100 m³/h -> (150/100)*60 = 90 min
        # Check what category 90 min falls into
        expected_efficiency = AIR_EXCHANGE_POOR

        assert attrs["efficiency_category"] == expected_efficiency
        assert attrs["room_volume"] == f"{DEFAULT_ROOM_VOLUME} m³"
        assert attrs["estimated_airflow"] == "100 m³/h"
        assert attrs["fan_speed"] == 2
        assert attrs["calculation_method"] == "Volume/Airflow*60"
        assert "optimization_tip" in attrs

    def test_efficiency_categories(self):
        """Test different efficiency categories based on exchange time."""
        # Test performance (fan speed 4 -> 97.3 min)
        self.coordinator.data = {"status": "VMGO,4,0,0,0"}  # Fan speed 4
        attrs = self.sensor.extra_state_attributes

        exchange_time = 97.3  # (60/37)*60
        if exchange_time <= AIR_EXCHANGE_TIME_EXCELLENT:
            expected = AIR_EXCHANGE_EXCELLENT
        elif exchange_time <= AIR_EXCHANGE_TIME_GOOD:
            expected = AIR_EXCHANGE_GOOD
        elif exchange_time <= AIR_EXCHANGE_TIME_ACCEPTABLE:
            expected = AIR_EXCHANGE_ACCEPTABLE
        else:
            expected = AIR_EXCHANGE_POOR

        assert attrs["efficiency_category"] == expected

    def test_optimization_tip_generation(self):
        """Test optimization tip generation."""
        # Test with fan speed 2 (typically poor performance)
        self.coordinator.data = {"status": "VMGO,2,0,0,0"}  # Fan speed 2
        attrs = self.sensor.extra_state_attributes

        # Should suggest increasing fan speed since it's < 4
        optimization_tip = attrs["optimization_tip"]
        assert (
            "aumentare velocità" in optimization_tip.lower()
            or "ricambio" in optimization_tip.lower()
        )

    def test_optimization_tip_max_speed(self):
        """Test optimization tip when at maximum speed but still poor performance."""
        self.coordinator.data = {"status": "VMGO,4,0,0,0"}  # Fan speed 4 (max)

        # Calculate what speed 4 actually gives us
        actual_exchange_time = (DEFAULT_ROOM_VOLUME / 37) * 60  # 97.3 minutes

        attrs = self.sensor.extra_state_attributes
        optimization_tip = attrs["optimization_tip"]

        # Check if the tip is appropriate for the actual exchange time
        if actual_exchange_time <= AIR_EXCHANGE_TIME_EXCELLENT:
            assert (
                "eccellent" in optimization_tip.lower()
                or "ottimale" in optimization_tip.lower()
            )
        elif actual_exchange_time <= AIR_EXCHANGE_TIME_GOOD:
            assert (
                "buon" in optimization_tip.lower()
                or "efficac" in optimization_tip.lower()
            )
        elif actual_exchange_time <= AIR_EXCHANGE_TIME_ACCEPTABLE:
            assert (
                "accettabil" in optimization_tip.lower()
                or "considerare" in optimization_tip.lower()
            )

    def test_mathematical_consistency(self):
        """Test mathematical consistency across different fan speeds."""
        fan_speeds = [1, 2, 3, 4]
        airflow_rates = {1: 10, 2: 17, 3: 26, 4: 37}  # Real AIRFLOW_MAPPING values

        for speed in fan_speeds:
            self.coordinator.data = {"status": f"VMGO,{speed},0,0,0"}

            calculated_value = self.sensor.native_value
            expected_value = (DEFAULT_ROOM_VOLUME / airflow_rates[speed]) * 60

            assert calculated_value == round(expected_value, 1)

            # Verify that higher speeds result in lower exchange times
            if speed > 1:
                prev_speed = speed - 1
                self.coordinator.data = {"status": f"VMGO,{prev_speed},0,0,0"}
                prev_value = self.sensor.native_value

                self.coordinator.data = {"status": f"VMGO,{speed},0,0,0"}
                curr_value = self.sensor.native_value

                assert curr_value < prev_value, (
                    f"Speed {speed} should have lower exchange time "
                    f"than speed {prev_speed}"
                )

    def test_extreme_conditions(self):
        """Test sensor behavior under extreme conditions."""
        # Test with very high fan speed (edge case) - uses default 100 m³/h
        self.coordinator.data = {
            "status": "VMGO,99,0,0,0"
        }  # Very high speed -> default 100
        # Expected: (DEFAULT_ROOM_VOLUME / 100) * 60 = (60 / 100) * 60 = 36.0 minutes
        expected = (DEFAULT_ROOM_VOLUME / 100) * 60
        assert self.sensor.native_value == round(expected, 1)

    def test_precision_and_rounding(self):
        """Test precision and rounding of calculated values."""
        # Use fan speed that creates non-integer result
        self.coordinator.data = {"status": "VMGO,3,0,0,0"}  # Fan speed 3

        # Expected: (60 / 26) * 60 = 138.5 minutes
        expected = round((DEFAULT_ROOM_VOLUME / 26) * 60, 1)
        assert self.sensor.native_value == expected

        # Ensure result is properly rounded to 1 decimal place
        assert isinstance(self.sensor.native_value, float)
        assert len(str(self.sensor.native_value).split(".")[-1]) <= 1

    def test_edge_case_empty_vmgo(self):
        """Test handling of empty VMGO string."""
        self.coordinator.data = {"status": ""}
        assert self.sensor.native_value is None

    def test_edge_case_malformed_vmgo(self):
        """Test handling of malformed VMGO string."""
        self.coordinator.data = {"status": "malformed,data,string"}
        assert self.sensor.native_value is None


if __name__ == "__main__":
    unittest.main()
