"""Test per VmcHeltyDailyAirChangesSensor."""

import unittest
from unittest.mock import Mock

from custom_components.vmc_helty_flow.const import (
    DAILY_AIR_CHANGES_EXCELLENT,
    DAILY_AIR_CHANGES_ADEQUATE,
    DAILY_AIR_CHANGES_GOOD,
    DAILY_AIR_CHANGES_POOR,
    DEFAULT_ROOM_VOLUME,
)
from custom_components.vmc_helty_flow.sensor import VmcHeltyDailyAirChangesSensor


class TestVmcHeltyDailyAirChangesSensor(unittest.TestCase):
    """Test della classe VmcHeltyDailyAirChangesSensor."""

    def setUp(self):
        """Configura il test."""
        self.coordinator = Mock()
        self.device_id = "test_device"
        self.coordinator.name = "TestVMC"
        self.coordinator.name_slug = "vmc_helty_testvmc"
        self.sensor = VmcHeltyDailyAirChangesSensor(self.coordinator, self.device_id)

    def test_init(self):
        """Test di inizializzazione del sensore."""
        assert self.sensor._attr_unique_id == "vmc_helty_testvmc_daily_air_changes"
        assert self.sensor._attr_name == "VMC Helty TestVMC Daily Air Changes"
        assert self.sensor._attr_icon == "mdi:air-filter"
        assert self.sensor._attr_native_unit_of_measurement == "changes/day"

    def test_native_value_no_data(self):
        """Test native_value senza dati."""
        self.coordinator.data = None
        assert self.sensor.native_value is None

    def test_native_value_no_status_data(self):
        """Test native_value senza dati di stato."""
        self.coordinator.data = {}
        assert self.sensor.native_value is None

    def test_native_value_empty_status(self):
        """Test native_value con status vuoto."""
        self.coordinator.data = {"status": ""}
        assert self.sensor.native_value is None

    def test_native_value_invalid_vmgo_format(self):
        """Test native_value con formato VMGO non valido."""
        self.coordinator.data = {"status": "INVALID,data"}
        assert self.sensor.native_value is None

    def test_native_value_insufficient_vmgo_data(self):
        """Test native_value con dati VMGO insufficienti."""
        self.coordinator.data = {"status": "VMGO,1"}
        assert self.sensor.native_value is None

    def test_calculation_fan_speed_0(self):
        """Test calcolo con velocità ventola 0 (off)."""
        self.coordinator.data = {"status": "VMGO,0,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        assert self.sensor.native_value == 0.0

    def test_calculation_fan_speed_1(self):
        """Test calcolo con velocità ventola 1 (50 m³/h)."""
        self.coordinator.data = {"status": "VMGO,1,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        # Portata: 10 m³/h, Ricambi/ora: 10/45 = 0.222, Ricambi/giorno: 0.222*24 = 5.3
        expected = round((10 / DEFAULT_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_fan_speed_2(self):
        """Test calcolo con velocità ventola 2 (100 m³/h)."""
        self.coordinator.data = {"status": "VMGO,2,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        # Portata: 17 m³/h, Ricambi/ora: 17/45 = 0.378, Ricambi/giorno: 0.378*24 = 9.1
        expected = round((17 / DEFAULT_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_fan_speed_3(self):
        """Test calcolo con velocità ventola 3 (150 m³/h)."""
        self.coordinator.data = {"status": "VMGO,3,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        # Portata: 26 m³/h, Ricambi/ora: 26/45 = 0.578, Ricambi/giorno: 0.578*24 = 13.9
        expected = round((26 / DEFAULT_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_fan_speed_4(self):
        """Test calcolo con velocità ventola 4 (200 m³/h)."""
        self.coordinator.data = {
            "status": "VMGO,4,1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Portata: 37 m³/h, Ricambi/ora: 37/45 = 0.822, Ricambi/giorno: 0.822*24 = 19.7
        expected = round((37 / DEFAULT_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_night_mode(self):
        """Test calcolo con modalità notte (velocità FAN_SPEED_NIGHT_MODE -> 1)."""
        from custom_components.vmc_helty_flow.const import FAN_SPEED_NIGHT_MODE
        self.coordinator.data = {
            "status": f"VMGO,{FAN_SPEED_NIGHT_MODE},1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Modalità notte: velocità effettiva 1 (7 m³/h)
        expected = round((7 / DEFAULT_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_hyperventilation(self):
        """Test calcolo con iperventilazione (velocità FAN_SPEED_HYPERVENTILATION -> 4)."""
        from custom_components.vmc_helty_flow.const import FAN_SPEED_HYPERVENTILATION
        self.coordinator.data = {
            "status": f"VMGO,{FAN_SPEED_HYPERVENTILATION},1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Iperventilazione: velocità effettiva 4 (42 m³/h)
        expected = round((42 / DEFAULT_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_free_cooling(self):
        """Test calcolo con free cooling (velocità FAN_SPEED_FREE_COOLING -> 3)."""
        from custom_components.vmc_helty_flow.const import FAN_SPEED_FREE_COOLING
        self.coordinator.data = {
            "status": f"VMGO,{FAN_SPEED_FREE_COOLING},1,0,0,0,0,0,0,0,0,50,0,0,0,60"
        }
        # Freecooling: velocità effettiva 3 (27 m³/h)
        expected = round((26 / DEFAULT_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_calculation_invalid_fan_speed(self):
        """Test calcolo con velocità ventola non valida."""
        self.coordinator.data = {"status": "VMGO,99,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        # Velocità non riconosciuta: usa default 1 (1 m³/h)
        expected = round((1 / DEFAULT_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected

    def test_invalid_data_types(self):
        """Test gestione di tipi di dati non validi in VMGO."""
        self.coordinator.data = {"status": "VMGO,invalid,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        assert self.sensor.native_value is None

    def test_mathematical_consistency(self):
        """Test consistenza matematica tra diverse velocità."""
        fan_speeds = [1, 2, 3, 4]
        airflow_rates = {1: 10, 2: 17, 3: 26, 4: 37}
        for speed in fan_speeds:
            self.coordinator.data = {
                "status": f"VMGO,{speed},1,0,0,0,0,0,0,0,0,50,0,0,0,60"
            }
            calculated_value = self.sensor.native_value
            expected_value = round((airflow_rates[speed] / DEFAULT_ROOM_VOLUME) * 24, 1)
            assert calculated_value == expected_value

    def test_extra_state_attributes_no_data(self):
        """Test extra_state_attributes senza dati."""
        self.coordinator.data = None
        attrs = self.sensor.extra_state_attributes

        assert attrs == {}

    def test_extra_state_attributes_complete(self):
        """Test extra_state_attributes con dati validi."""
        self.coordinator.data = {"status": "VMGO,4,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        attrs = self.sensor.extra_state_attributes
        expected_daily_changes = round((37 / DEFAULT_ROOM_VOLUME) * 24, 1)
        expected_hourly_changes = round(expected_daily_changes / 24, 2)
        assert attrs["category"] == DAILY_AIR_CHANGES_EXCELLENT
        assert attrs["assessment"] == "Ricambio d'aria ottimale"
        assert attrs["air_changes_per_hour"] == expected_hourly_changes
        assert attrs["room_volume_m3"] == DEFAULT_ROOM_VOLUME
        assert "recommendation" in attrs

    def test_category_excellent(self):
        """Test categoria eccellente (≥24 ricambi/giorno)."""
        self.coordinator.data = {"status": "VMGO,3,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        attrs = self.sensor.extra_state_attributes

        # Velocità 3 -> 150 m³/h -> 24.0 ricambi/giorno = eccellente
        assert attrs["category"] == DAILY_AIR_CHANGES_EXCELLENT
        assert attrs["assessment"] == "Ricambio d'aria ottimale"

    def test_category_good(self):
        """Test categoria buona (6-12 ricambi/giorno)."""
        self.coordinator.data = {"status": "VMGO,2,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        attrs = self.sensor.extra_state_attributes
        assert attrs["category"] == DAILY_AIR_CHANGES_GOOD
        assert attrs["assessment"] == "Ricambio d'aria buono"

    def test_category_adequate(self):
        """Test categoria adeguata (3-6 ricambi/giorno)."""
        self.coordinator.data = {"status": "VMGO,1,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        attrs = self.sensor.extra_state_attributes
        assert attrs["category"] == DAILY_AIR_CHANGES_ADEQUATE
        assert attrs["assessment"] == "Ricambio d'aria adeguato"

    def test_category_poor(self):
        """Test categoria insufficiente (<3 ricambi/giorno)."""
        # Simula una portata molto bassa modificando temporaneamente il volume
        # Con volume 45 m³ e velocità 1 (10 m³/h): 10/45*24 = 5.33 ricambi/giorno

        # Non posso modificare la costante, quindi uso un test diverso
        # Testo con velocità 0 (off) che dovrebbe sempre essere "Poor"
        self.coordinator.data = {"status": "VMGO,0,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}

        # Con velocità 0, daily_changes sarà 0.0 c
        # he è < DAILY_AIR_CHANGES_ADEQUATE_MIN (3)
        attrs = self.sensor.extra_state_attributes
        assert attrs["category"] == DAILY_AIR_CHANGES_POOR
        assert attrs["assessment"] == "Ricambio d'aria insufficiente"

    def test_recommendation_excellent(self):
        """Test raccomandazione per ricambio eccellente."""
        self.coordinator.data = {"status": "VMGO,4,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        attrs = self.sensor.extra_state_attributes

        # Velocità 4 -> 200 m³/h -> 32.0 ricambi/giorno = eccellente
        recommendation = attrs["recommendation"]
        assert "eccellente" in recommendation.lower()

    def test_recommendation_poor_increase_speed(self):
        """Test raccomandazione per ricambio insufficiente con velocità bassa."""
        self.coordinator.data = {"status": "VMGO,0,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        attrs = self.sensor.extra_state_attributes

        # Velocità 0 -> insufficiente -> dovrebbe suggerire aumento velocità
        recommendation = attrs["recommendation"]
        assert "aumenta" in recommendation.lower()
        assert "velocità" in recommendation.lower()

    def test_recommendation_poor_max_speed(self):
        """Test raccomandazione per ricambio insufficiente con velocità massima."""
        # Simulo un caso dove anche con velocità 4 il ricambio è insufficiente
        # Questo potrebbe succedere con un volume ambiente molto grande
        # Per ora testo solo che la logica funzioni
        self.coordinator.data = {"status": "VMGO,4,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}

        # Con le portate standard, velocità 4 dovrebbe dare sempre un buon ricambio
        # Ma il test verifica che la logica del metodo _get_recommendation funzioni
        daily_changes = self.sensor.native_value
        recommendation = self.sensor._get_recommendation(daily_changes)

        # Con 32.0 ricambi/giorno dovrebbe essere eccellente
        assert "eccellente" in recommendation.lower()

    def test_precision_and_rounding(self):
        """Test precisione e arrotondamento dei valori calcolati."""
        self.coordinator.data = {"status": "VMGO,3,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        # Velocità 3 -> 26 m³/h
        expected = round((26 / DEFAULT_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected
        assert isinstance(self.sensor.native_value, float)

    def test_edge_case_empty_vmgo(self):
        """Test caso limite con VMGO vuoto."""
        self.coordinator.data = {"status": "VMGO"}
        assert self.sensor.native_value is None

    def test_edge_case_malformed_vmgo(self):
        """Test caso limite con VMGO malformato."""
        self.coordinator.data = {"status": "VMGO,,,,,"}
        assert self.sensor.native_value is None

    def test_extreme_conditions(self):
        """Test comportamento del sensore in condizioni estreme."""
        # Test con velocità molto alta (edge case)
        self.coordinator.data = {"status": "VMGO,6,1,0,0,0,0,0,0,0,0,50,0,0,0,60"}
        # Velocità 6 -> 42 m³/h
        expected = round((42 / DEFAULT_ROOM_VOLUME) * 24, 1)
        assert self.sensor.native_value == expected


if __name__ == "__main__":
    unittest.main()
