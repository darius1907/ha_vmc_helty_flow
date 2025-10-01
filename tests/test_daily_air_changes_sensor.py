"""Test per VmcHeltyDailyAirChangesSensor."""

import unittest
from unittest.mock import Mock

from custom_components.vmc_helty_flow.const import (
    DAILY_AIR_CHANGES_EXCELLENT,
    DAILY_AIR_CHANGES_ADEQUATE,
    DAILY_AIR_CHANGES_GOOD,
    DAILY_AIR_CHANGES_POOR,
)
from custom_components.vmc_helty_flow.sensor import VmcHeltyDailyAirChangesSensor


class TestVmcHeltyDailyAirChangesSensor(unittest.TestCase):
    """Test della classe VmcHeltyDailyAirChangesSensor."""

    # Test room volume - should match conftest.py config entry
    TEST_ROOM_VOLUME = 60.0

    def setUp(self):
        """Configura il test."""
        self.coordinator = Mock()
        self.device_id = "test_device"
        self.coordinator.name = "TestVMC"
        self.coordinator.name_slug = "vmc_helty_testvmc"
        self.coordinator.room_volume = self.TEST_ROOM_VOLUME
        self.sensor = VmcHeltyDailyAirChangesSensor(self.coordinator, self.device_id)

    def test_init(self):
        """Test di inizializzazione del sensore."""
        assert self.sensor._attr_unique_id == "vmc_helty_testvmc_daily_air_changes"
        assert self.sensor._attr_name == "VMC Helty TestVMC Daily Air Changes"
        assert self.sensor._attr_icon == "mdi:air-filter"

    def test_native_value_no_data(self):
        """Test native_value quando non ci sono dati."""
        self.coordinator.data = None
        assert self.sensor.native_value is None

    def test_native_value_no_status_data(self):
        """Test native_value quando non ci sono dati di status."""
        self.coordinator.data = {}
        assert self.sensor.native_value is None

    def test_native_value_invalid_vmgo_format(self):
        """Test native_value con formato VMGO non valido."""
        self.coordinator.data = {"status": "INVALID"}
        assert self.sensor.native_value is None

    def test_native_value_insufficient_vmgo_data(self):
        """Test native_value con dati VMGO insufficienti."""
        self.coordinator.data = {"status": "VMGO,1"}  # Only 2 parts, need at least 15
        assert self.sensor.native_value is None

    def test_calculation_fan_speed_0(self):
        """Test calcolo con velocità ventola 0 (off)."""
        self.coordinator.data = {
            "status": "VMGO,0,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        assert self.sensor.native_value == 0.0

    def test_calculation_fan_speed_1(self):
        """Test calcolo con velocità ventola 1 (10 m³/h)."""
        self.coordinator.data = {
            "status": "VMGO,1,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Portata: 10 m³/h, Ricambi/ora: 10/60 = 0.167, Ricambi/giorno: 0.167*24 = 4.0
        expected = round((10 / self.TEST_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_fan_speed_2(self):
        """Test calcolo con velocità ventola 2 (17 m³/h)."""
        self.coordinator.data = {
            "status": "VMGO,2,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Portata: 17 m³/h, Ricambi/ora: 17/60 = 0.283, Ricambi/giorno: 0.283*24 = 6.8
        expected = round((17 / self.TEST_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_fan_speed_3(self):
        """Test calcolo con velocità ventola 3 (26 m³/h)."""
        self.coordinator.data = {
            "status": "VMGO,3,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Portata: 26 m³/h, Ricambi/ora: 26/60 = 0.433, Ricambi/giorno: 0.433*24 = 10.4
        expected = round((26 / self.TEST_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_fan_speed_4(self):
        """Test calcolo con velocità ventola 4 (37 m³/h)."""
        self.coordinator.data = {
            "status": "VMGO,4,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Portata: 37 m³/h, Ricambi/ora: 37/60 = 0.617, Ricambi/giorno: 0.617*24 = 14.8
        expected = round((37 / self.TEST_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_night_mode(self):
        """Test calcolo con modalità notturna (velocità 5 -> 7 m³/h)."""
        self.coordinator.data = {
            "status": "VMGO,5,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Portata: 7 m³/h, Ricambi/ora: 7/60 = 0.117, Ricambi/giorno: 0.117*24 = 2.8
        expected = round((7 / self.TEST_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_hyperventilation(self):
        """Test calcolo con iperventilazione (velocità 6 -> 42 m³/h)."""
        self.coordinator.data = {
            "status": "VMGO,6,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Portata: 42 m³/h, Ricambi/ora: 42/60 = 0.7, Ricambi/giorno: 0.7*24 = 16.8
        expected = round((42 / self.TEST_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_free_cooling(self):
        """Test calcolo con free cooling (velocità 7 -> 26 m³/h)."""
        self.coordinator.data = {
            "status": "VMGO,7,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Portata: 26 m³/h, Ricambi/ora: 26/60 = 0.433, Ricambi/giorno: 0.433*24 = 10.4
        expected = round((26 / self.TEST_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_invalid_fan_speed(self):
        """Test calcolo con velocità ventola non valida (fallback 10 m³/h)."""
        self.coordinator.data = {
            "status": "VMGO,999,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Portata: 10 m³/h (fallback), Ricambi/ora: 10/60 = 0.167, Ricambi/giorno: 0.167*24 = 4.0
        expected = round((10 / self.TEST_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_invalid_data_types(self):
        """Test handling of invalid data types in VMGO."""
        self.coordinator.data = {"status": 123}  # Integer instead of string
        assert self.sensor.native_value is None

    def test_extra_state_attributes_no_data(self):
        """Test extra_state_attributes when no data available."""
        self.coordinator.data = None
        attrs = self.sensor.extra_state_attributes
        # When no data, should still have room_volume from coordinator
        assert "room_volume_m3" in attrs or len(attrs) == 0
        if "room_volume" in attrs:
            assert attrs["room_volume"] == self.TEST_ROOM_VOLUME

    def test_extra_state_attributes_complete(self):
        """Test extra_state_attributes with valid data."""
        self.coordinator.data = {
            "status": "VMGO,2,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        attrs = self.sensor.extra_state_attributes

        assert "air_changes_per_hour" in attrs
        assert "category" in attrs
        assert "assessment" in attrs
        assert "recommendation" in attrs
        assert "room_volume_m3" in attrs


if __name__ == "__main__":
    unittest.main()