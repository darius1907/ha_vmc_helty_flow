"""Test per il sensore VmcHeltyDewPointDeltaSensor."""
import math
from unittest.mock import Mock

from custom_components.vmc_helty_flow.sensor import VmcHeltyDewPointDeltaSensor


class TestVmcHeltyDewPointDeltaSensor:
    """Test class for VmcHeltyDewPointDeltaSensor."""

    def test_init(self):
        """Test inizializzazione del sensore."""
        mock_coordinator = Mock()
        mock_coordinator.ip = "192.168.1.100"
        mock_coordinator.name = "VMC Helty Test"
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        
        assert sensor._attr_unique_id == "192.168.1.100_dew_point_delta"
        assert sensor._attr_name == "VMC Helty Test Delta Punto Rugiada"
        assert sensor._attr_icon == "mdi:thermometer-water"
        assert sensor._attr_device_class == "temperature"
        assert sensor._attr_state_class == "measurement"
        assert sensor._attr_native_unit_of_measurement == "°C"

    def test_native_value_no_data(self):
        """Test valore con dati mancanti."""
        mock_coordinator = Mock()
        mock_coordinator.data = None
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        assert sensor.native_value is None

    def test_native_value_no_sensors_data(self):
        """Test valore con dati sensori mancanti."""
        mock_coordinator = Mock()
        mock_coordinator.data = {"other_key": "value"}
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        assert sensor.native_value is None

    def test_native_value_invalid_sensors_data(self):
        """Test valore con dati sensori non validi."""
        mock_coordinator = Mock()
        mock_coordinator.data = {"sensors": "INVALID_DATA"}
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        assert sensor.native_value is None

    def test_native_value_insufficient_data(self):
        """Test valore con dati insufficienti."""
        mock_coordinator = Mock()
        mock_coordinator.data = {"sensors": "VMGI,220,180,500"}  # Troppo pochi campi
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        assert sensor.native_value is None

    def test_calculation_standard_conditions(self):
        """Test calcolo delta punto di rugiada in condizioni standard."""
        mock_coordinator = Mock()
        # VMGI,220,150,500,800,0,0,0,0,0,0,150,0,0,0
        # temp_int=22.0°C, temp_ext=15.0°C, humidity=50.0%
        mock_coordinator.data = {
            "sensors": "VMGI,220,150,500,800,0,0,0,0,0,0,150,0,0,0",
        }
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        result = sensor.native_value
        
        # Verifica manuale della formula Magnus-Tetens
        temp_int, temp_ext, humidity = 22.0, 15.0, 50.0
        a, b = 17.27, 237.7
        
        # Punto di rugiada interno
        gamma_int = (a * temp_int) / (b + temp_int) + math.log(humidity / 100.0)
        dew_int = (b * gamma_int) / (a - gamma_int)
        
        # Punto di rugiada esterno
        gamma_ext = (a * temp_ext) / (b + temp_ext) + math.log(humidity / 100.0)
        dew_ext = (b * gamma_ext) / (a - gamma_ext)
        
        expected_delta = round(dew_int - dew_ext, 1)
        
        assert result is not None
        assert result == expected_delta
        assert result > 0  # Interno dovrebbe essere > esterno

    def test_calculation_same_temperatures(self):
        """Test calcolo con temperature interne ed esterne uguali."""
        mock_coordinator = Mock()
        # VMGI,200,200,600,800,0,0,0,0,0,0,150,0,0,0
        # temp_int=20.0°C, temp_ext=20.0°C, humidity=60.0%
        mock_coordinator.data = {
            "sensors": "VMGI,200,200,600,800,0,0,0,0,0,0,150,0,0,0",
        }
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        result = sensor.native_value
        
        # Con temperature uguali, i punti di rugiada dovrebbero essere uguali
        assert result is not None
        assert abs(result) < 0.1  # Dovrebbe essere circa 0

    def test_calculation_internal_colder_than_external(self):
        """Test calcolo con interno più freddo dell'esterno."""
        mock_coordinator = Mock()
        # VMGI,150,250,400,800,0,0,0,0,0,0,150,0,0,0
        # temp_int=15.0°C, temp_ext=25.0°C, humidity=40.0%
        mock_coordinator.data = {
            "sensors": "VMGI,150,250,400,800,0,0,0,0,0,0,150,0,0,0",
        }
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        result = sensor.native_value
        
        assert result is not None
        assert result < 0  # Delta dovrebbe essere negativo

    def test_calculation_zero_humidity(self):
        """Test gestione umidità zero."""
        mock_coordinator = Mock()
        mock_coordinator.data = {
            "sensors": "VMGI,220,150,0,800,0,0,0,0,0,0,150,0,0,0",
        }
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        assert sensor.native_value is None

    def test_calculation_excessive_humidity(self):
        """Test gestione umidità eccessiva."""
        mock_coordinator = Mock()
        mock_coordinator.data = {
            "sensors": "VMGI,220,150,850,800,0,0,0,0,0,0,150,0,0,0",  # 85%
        }
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        result = sensor.native_value
        
        # Dovrebbe funzionare anche con umidità alta
        assert result is not None

    def test_dew_point_calculation_function(self):
        """Test funzione di calcolo punto di rugiada."""
        mock_coordinator = Mock()
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        
        # Test con valori noti
        temp, humidity = 20.0, 60.0
        result = sensor._calculate_dew_point(temp, humidity)
        
        # Verifica manuale
        a, b = 17.27, 237.7
        gamma = (a * temp) / (b + temp) + math.log(humidity / 100.0)
        expected = (b * gamma) / (a - gamma)
        
        assert abs(result - expected) < 0.001  # Tolleranza numerica

    def test_extra_state_attributes_complete(self):
        """Test attributi aggiuntivi con dati completi."""
        mock_coordinator = Mock()
        # VMGI,220,150,500,800,0,0,0,0,0,0,150,0,0,0
        mock_coordinator.data = {
            "sensors": "VMGI,220,150,500,800,0,0,0,0,0,0,150,0,0,0",
        }
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        attributes = sensor.extra_state_attributes
        
        assert attributes is not None
        assert "risk_level" in attributes
        assert "risk_description" in attributes
        assert "recommended_action" in attributes
        assert "internal_dew_point" in attributes
        assert "external_dew_point" in attributes
        assert "internal_temperature" in attributes
        assert "external_temperature" in attributes
        assert "humidity" in attributes
        
        # Verifica valori specifici
        assert attributes["internal_temperature"] == "22.0°C"
        assert attributes["external_temperature"] == "15.0°C"
        assert attributes["humidity"] == "50.0%"

    def test_extra_state_attributes_no_data(self):
        """Test attributi aggiuntivi senza dati."""
        mock_coordinator = Mock()
        mock_coordinator.data = None
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        attributes = sensor.extra_state_attributes
        
        # Dovrebbe restituire attributi vuoti o di base
        assert attributes is not None

    def test_condensation_risk_classification(self):
        """Test classificazione del rischio di condensazione."""
        mock_coordinator = Mock()
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        
        # Test diversi livelli di rischio
        risk_cases = [
            (-3.0, "Critico"),      # Delta molto negativo
            (-1.0, "Alto"),         # Delta leggermente negativo
            (1.0, "Moderato"),      # Delta piccolo positivo
            (3.0, "Basso"),         # Delta medio positivo
            (10.0, "Sicuro"),       # Delta grande positivo
        ]
        
        for delta, expected_level in risk_cases:
            risk_info = sensor._get_condensation_risk(delta)
            assert risk_info["level"] == expected_level
            assert "description" in risk_info
            assert "action" in risk_info

    def test_invalid_data_types(self):
        """Test gestione di tipi di dati non validi."""
        mock_coordinator = Mock()
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        
        # Test con dati malformati
        mock_coordinator.data = {
            "sensors": "VMGI,invalid,150,500,800,0,0,0,0,0,0,150,0,0,0",
        }
        assert sensor.native_value is None

        # Test con temperatura esterna invalida
        mock_coordinator.data = {
            "sensors": "VMGI,220,invalid,500,800,0,0,0,0,0,0,150,0,0,0",
        }
        assert sensor.native_value is None

        # Test con umidità invalida
        mock_coordinator.data = {
            "sensors": "VMGI,220,150,invalid,800,0,0,0,0,0,0,150,0,0,0",
        }
        assert sensor.native_value is None

    def test_mathematical_consistency(self):
        """Test consistenza matematica dei calcoli."""
        mock_coordinator = Mock()
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        
        # Test che delta sia coerente con differenze di temperatura
        test_cases = [
            (25.0, 15.0, 50.0),  # Interno più caldo
            (15.0, 25.0, 50.0),  # Esterno più caldo  
            (20.0, 20.0, 60.0),  # Temperature uguali
        ]
        
        for temp_int, temp_ext, humidity in test_cases:
            temp_int_val = int(temp_int * 10)
            temp_ext_val = int(temp_ext * 10)
            humidity_val = int(humidity * 10)
            
            mock_coordinator.data = {
                "sensors": f"VMGI,{temp_int_val},{temp_ext_val},{humidity_val},800,0,0,0,0,0,0,150,0,0,0",
            }
            
            delta = sensor.native_value
            assert delta is not None
            
            # Verifica coerenza: se temp_int > temp_ext, delta dovrebbe essere > 0
            if temp_int > temp_ext:
                assert delta > 0
            elif temp_int < temp_ext:
                assert delta < 0
            else:  # temp_int == temp_ext
                assert abs(delta) < 0.1  # Dovrebbe essere circa 0

    def test_extreme_conditions(self):
        """Test comportamento in condizioni estreme."""
        mock_coordinator = Mock()
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        
        # Test temperature molto diverse
        mock_coordinator.data = {
            "sensors": "VMGI,350,50,300,800,0,0,0,0,0,0,150,0,0,0",  # 35°C vs 5°C, 30%
        }
        result_extreme = sensor.native_value
        assert result_extreme is not None
        assert result_extreme > 5.0  # Dovrebbe essere un delta grande
        
        # Test umidità molto alta
        mock_coordinator.data = {
            "sensors": "VMGI,250,200,950,800,0,0,0,0,0,0,150,0,0,0",  # 25°C vs 20°C, 95%
        }
        result_humid = sensor.native_value
        assert result_humid is not None

    def test_precision_and_rounding(self):
        """Test precisione e arrotondamento dei risultati."""
        mock_coordinator = Mock()
        # VMGI,235,187,649,800,0,0,0,0,0,0,150,0,0,0
        # temp_int=23.5°C, temp_ext=18.7°C, humidity=64.9%
        mock_coordinator.data = {
            "sensors": "VMGI,235,187,649,800,0,0,0,0,0,0,150,0,0,0",
        }
        
        sensor = VmcHeltyDewPointDeltaSensor(mock_coordinator)
        result = sensor.native_value
        
        assert result is not None
        # Verifica che il risultato sia arrotondato a 1 decimale
        assert result == round(result, 1)
        # Verifica che abbia senso dato le temperature
        assert 0 < result < 10  # Delta ragionevole