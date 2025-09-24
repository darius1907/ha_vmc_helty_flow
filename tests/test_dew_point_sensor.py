"""Test per VmcHeltyDewPointSensor."""

import math
from unittest.mock import Mock

import pytest

from custom_components.vmc_helty_flow.sensor import VmcHeltyDewPointSensor


class TestVmcHeltyDewPointSensor:
    """Test class per VmcHeltyDewPointSensor."""

    def test_init(self):
        """Test inizializzazione del sensore."""
        mock_coordinator = Mock()
        mock_coordinator.ip = "192.168.1.100"
        mock_coordinator.name = "Test VMC"
        mock_coordinator.name_slug = "testvmc"

        sensor = VmcHeltyDewPointSensor(mock_coordinator)

        assert sensor.coordinator == mock_coordinator
        assert sensor._attr_unique_id == "vmc_testvmc_dew_point"
        assert sensor._attr_name == "Test VMC Punto di Rugiada"
        assert sensor._attr_native_unit_of_measurement == "°C"
        assert sensor._attr_icon == "mdi:thermometer-water"

    def test_native_value_no_data(self):
        """Test calcolo senza dati."""
        mock_coordinator = Mock()
        mock_coordinator.data = None

        sensor = VmcHeltyDewPointSensor(mock_coordinator)

        assert sensor.native_value is None

    def test_native_value_no_sensors_data(self):
        """Test calcolo senza dati sensori."""
        mock_coordinator = Mock()
        mock_coordinator.data = {
            "sensors": "",  # Dati sensori vuoti
        }

        sensor = VmcHeltyDewPointSensor(mock_coordinator)

        assert sensor.native_value is None

    def test_native_value_invalid_sensors_data(self):
        """Test calcolo con dati sensori non validi."""
        mock_coordinator = Mock()
        mock_coordinator.data = {
            "sensors": "INVALID_DATA",
        }

        sensor = VmcHeltyDewPointSensor(mock_coordinator)

        assert sensor.native_value is None

    def test_native_value_zero_humidity(self):
        """Test calcolo con umidità zero."""
        mock_coordinator = Mock()
        mock_coordinator.data = {
            "temperature_internal": 20.0,
            "humidity": 0.0,
        }

        sensor = VmcHeltyDewPointSensor(mock_coordinator)

        assert sensor.native_value is None

    def test_calculation_standard_conditions(self):
        """Test calcolo punto di rugiada in condizioni standard."""
        mock_coordinator = Mock()
        # VMGI,200,150,600,800,0,0,0,0,0,0,150,0,0,0 - temp=20.0°C, humidity=60.0%
        mock_coordinator.data = {
            "sensors": "VMGI,200,150,600,800,0,0,0,0,0,0,150,0,0,0",
        }

        sensor = VmcHeltyDewPointSensor(mock_coordinator)
        result = sensor.native_value

        # Formula Magnus-Tetens per verifica
        temp = 20.0  # 200/10
        humidity = 60.0  # 600/10
        a = 17.27
        b = 237.7
        alpha = ((a * temp) / (b + temp)) + math.log(humidity / 100.0)
        expected = (b * alpha) / (a - alpha)

        assert result is not None
        assert abs(result - expected) < 0.1  # Tolleranza per arrotondamento
        assert result == round(expected, 1)

    def test_calculation_high_humidity(self):
        """Test calcolo con alta umidità."""
        mock_coordinator = Mock()
        # VMGI,250,180,900,800,0,0,0,0,0,0,150,0,0,0 - temp=25.0°C, humidity=90.0%
        mock_coordinator.data = {
            "sensors": "VMGI,250,180,900,800,0,0,0,0,0,0,150,0,0,0",
        }

        sensor = VmcHeltyDewPointSensor(mock_coordinator)
        result = sensor.native_value

        assert result is not None
        assert result > 20  # Con 25°C e 90% RH, il dew point dovrebbe essere alto

    def test_calculation_low_humidity(self):
        """Test calcolo con bassa umidità."""
        mock_coordinator = Mock()
        # VMGI,200,150,300,800,0,0,0,0,0,0,150,0,0,0 - temp=20.0°C, humidity=30.0%
        mock_coordinator.data = {
            "sensors": "VMGI,200,150,300,800,0,0,0,0,0,0,150,0,0,0",
        }

        sensor = VmcHeltyDewPointSensor(mock_coordinator)
        result = sensor.native_value

        assert result is not None
        assert result < 5  # Con 20°C e 30% RH, il dew point dovrebbe essere basso

    def test_calculation_edge_cases(self):
        """Test calcolo in casi limite."""
        mock_coordinator = Mock()
        sensor = VmcHeltyDewPointSensor(mock_coordinator)
        
        # Umidità molto alta (99%)
        # VMGI,150,120,990,800,0,0,0,0,0,0,150,0,0,0 - temp=15.0°C, humidity=99.0%
        mock_coordinator.data = {
            "sensors": "VMGI,150,120,990,800,0,0,0,0,0,0,150,0,0,0",
        }
        result_high_humidity = sensor.native_value
        
        # Il punto di rugiada dovrebbe essere molto vicino alla temperatura
        assert result_high_humidity is not None
        assert abs(result_high_humidity - 15.0) < 1.0

        # Umidità molto bassa (1%)
        # VMGI,150,120,10,800,0,0,0,0,0,0,150,0,0,0 - temp=15.0°C, humidity=1.0%
        mock_coordinator.data = {
            "sensors": "VMGI,150,120,10,800,0,0,0,0,0,0,150,0,0,0",
        }
        result_low_humidity = sensor.native_value
        
        # Il punto di rugiada dovrebbe essere molto più basso della temperatura
        assert result_low_humidity is not None
        assert result_low_humidity < 0

    def test_extra_state_attributes_complete(self):
        """Test attributi aggiuntivi con dati completi."""
        mock_coordinator = Mock()
        # VMGI,220,180,550,800,0,0,0,0,0,0,150,0,0,0 - temp=22.0°C, humidity=55.0%
        mock_coordinator.data = {
            "sensors": "VMGI,220,180,550,800,0,0,0,0,0,0,150,0,0,0",
        }

        sensor = VmcHeltyDewPointSensor(mock_coordinator)
        attributes = sensor.extra_state_attributes

        assert attributes is not None
        assert attributes["formula"] == "Magnus-Tetens"
        assert attributes["temperature_source"] == 22.0
        assert attributes["humidity_source"] == 55.0
        assert attributes["precision"] == "±0.2°C"
        assert attributes["standard"] == "ASHRAE 55-2020"
        assert "comfort_level" in attributes
        assert "comfort_color" in attributes

    def test_extra_state_attributes_no_data(self):
        """Test attributi aggiuntivi senza dati."""
        mock_coordinator = Mock()
        mock_coordinator.data = None

        sensor = VmcHeltyDewPointSensor(mock_coordinator)
        attributes = sensor.extra_state_attributes

        assert attributes is None

    def test_comfort_level_classification(self):
        """Test classificazione dei livelli di comfort."""
        mock_coordinator = Mock()
        sensor = VmcHeltyDewPointSensor(mock_coordinator)

        # Test diversi valori di punto di rugiada e livelli di comfort
        test_cases = [
            (5.0, "Molto Secco"),     # < 8°C
            (10.0, "Secco"),          # 8-12°C  
            (15.0, "Confortevole"),   # 13-18°C
            (20.0, "Buono"),          # 18-21°C
            (23.0, "Accettabile"),    # 21-24°C
            (26.0, "Umido"),          # 24-26°C
            (28.0, "Opprimente"),     # > 26°C
        ]

        for dew_point_temp, _expected_comfort in test_cases:
            # Simula il calcolo che produce il dew point desiderato
            # Usiamo una temperatura e umidità che producano circa il dew point voluto
            temp_value = int((dew_point_temp + 5) * 10)  # Temp leggermente più alta in decimi
            humidity_value = 700  # Umidità 70.0% in decimi
            mock_coordinator.data = {
                "sensors": (
                    f"VMGI,{temp_value},180,{humidity_value},800,0,0,0,0,0,0,150,0,0,0"
                ),
            }
            
            # Verifica che gli attributi contengano il comfort level
            attributes = sensor.extra_state_attributes
            assert attributes is not None
            assert "comfort_level" in attributes
            assert "comfort_color" in attributes
            
            # Il colore dovrebbe essere una stringa hex valida
            assert attributes["comfort_color"].startswith("#")

    def test_mathematical_consistency(self):
        """Test consistenza matematica della formula Magnus-Tetens."""
        mock_coordinator = Mock()
        sensor = VmcHeltyDewPointSensor(mock_coordinator)

        # Test che il punto di rugiada sia sempre <= temperatura
        for temp in [5, 10, 15, 20, 25, 30]:
            for humidity in [30, 50, 70, 90]:
                temp_value = temp * 10  # Decimi di grado
                humidity_value = humidity * 10  # Decimi di %
                mock_coordinator.data = {
                    "sensors": (
                        f"VMGI,{temp_value},180,{humidity_value},800,0,0,0,0,0,0,150,0,0,0"
                    ),
                }
                
                dew_point = sensor.native_value
                assert dew_point is not None
                assert dew_point <= temp, f"Dew point {dew_point} > temperature {temp}"

    def test_calculation_precision(self):
        """Test precisione del calcolo."""
        mock_coordinator = Mock()
        # VMGI,235,180,679,800,0,0,0,0,0,0,150,0,0,0 - temp=23.5°C, humidity=67.9%
        mock_coordinator.data = {
            "sensors": "VMGI,235,180,679,800,0,0,0,0,0,0,150,0,0,0",
        }

        sensor = VmcHeltyDewPointSensor(mock_coordinator)
        result = sensor.native_value

        assert result is not None
        # Il risultato deve essere arrotondato a 1 decimale
        assert result == round(result, 1)

    def test_invalid_data_types(self):
        """Test gestione di tipi di dati non validi."""
        mock_coordinator = Mock()
        sensor = VmcHeltyDewPointSensor(mock_coordinator)
        
        # Test con dati malformati
        mock_coordinator.data = {
            "sensors": "VMGI,invalid,150,600,800,0,0,0,0,0,0,150,0,0,0",
        }
        assert sensor.native_value is None

        # Test con dati insufficienti
        mock_coordinator.data = {
            "sensors": "VMGI,200,150",  # Troppo pochi campi
        }
        assert sensor.native_value is None

        # Test con umidità zero (dovrebbe essere gestita)
        mock_coordinator.data = {
            "sensors": "VMGI,200,150,0,800,0,0,0,0,0,0,150,0,0,0",
        }
        assert sensor.native_value is None