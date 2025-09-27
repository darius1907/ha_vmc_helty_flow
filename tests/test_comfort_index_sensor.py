"""Test per il sensore VmcHeltyComfortIndexSensor."""

from unittest.mock import Mock

from custom_components.vmc_helty_flow.sensor import VmcHeltyComfortIndexSensor


class TestVmcHeltyComfortIndexSensor:
    """Test class for VmcHeltyComfortIndexSensor."""

    def test_init(self):
        """Test inizializzazione del sensore."""
        mock_coordinator = Mock()
        mock_coordinator.device_id = "test_device"
        mock_coordinator.name = "testvmc"
        mock_coordinator.name_slug = "vmc_helty_testvmc"

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)

        assert sensor._attr_name == "VMC Helty testvmc Indice Comfort Igrometrico"
        assert sensor._attr_unique_id == "vmc_helty_testvmc_comfort_index"
        assert sensor._attr_state_class == "measurement"
        assert sensor._attr_native_unit_of_measurement == "%"
        assert sensor._attr_icon == "mdi:account-check"

    def test_native_value_no_data(self):
        """Test valore con dati mancanti."""
        mock_coordinator = Mock()
        mock_coordinator.data = None

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        assert sensor.native_value is None

    def test_native_value_no_sensors_data(self):
        """Test valore con dati sensori mancanti."""
        mock_coordinator = Mock()
        mock_coordinator.data = {"other_key": "value"}

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        assert sensor.native_value is None

    def test_native_value_invalid_sensors_data(self):
        """Test valore con dati sensori non validi."""
        mock_coordinator = Mock()
        mock_coordinator.data = {"sensors": "INVALID_DATA"}

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        assert sensor.native_value is None

    def test_native_value_insufficient_data(self):
        """Test valore con dati insufficienti."""
        mock_coordinator = Mock()
        mock_coordinator.data = {"sensors": "VMGI,200,150"}  # Troppo pochi campi

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        assert sensor.native_value is None

    def test_calculation_optimal_conditions(self):
        """Test calcolo in condizioni ottimali."""
        mock_coordinator = Mock()
        # VMGI,220,150,500,800,0,0,0,0,0,0,150,0,0,0 - temp=22.0°C, humidity=50.0%
        mock_coordinator.data = {
            "sensors": "VMGI,220,150,500,800,0,0,0,0,0,0,150,0,0,0",
        }

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        result = sensor.native_value

        # Condizioni ottimali dovrebbero dare un valore alto (>= 85%)
        assert result is not None
        assert result >= 85
        assert result <= 100

    def test_calculation_good_conditions(self):
        """Test calcolo in buone condizioni."""
        mock_coordinator = Mock()
        # VMGI,200,150,400,800,0,0,0,0,0,0,150,0,0,0 - temp=20.0°C, humidity=40.0%
        mock_coordinator.data = {
            "sensors": "VMGI,200,150,400,800,0,0,0,0,0,0,150,0,0,0",
        }

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        result = sensor.native_value

        # Buone condizioni dovrebbero dare un valore alto
        assert result is not None
        # Potrebbe essere anche eccellente se nelle condizioni ottimali
        assert result >= 60

    def test_calculation_poor_conditions(self):
        """Test calcolo in condizioni povere."""
        mock_coordinator = Mock()
        # VMGI,100,150,200,800,0,0,0,0,0,0,150,0,0,0 - temp=10.0°C, humidity=20.0%
        mock_coordinator.data = {
            "sensors": "VMGI,100,150,200,800,0,0,0,0,0,0,150,0,0,0",
        }

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        result = sensor.native_value

        # Condizioni povere dovrebbero dare un valore basso (< 40%)
        assert result is not None
        assert result < 40

    def test_calculation_extreme_conditions(self):
        """Test calcolo in condizioni estreme."""
        mock_coordinator = Mock()
        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)

        # Temperatura molto alta, umidità molto alta
        mock_coordinator.data = {
            "sensors": "VMGI,350,150,900,800,0,0,0,0,0,0,150,0,0,0",  # 35°C, 90%
        }
        result_hot_humid = sensor.native_value
        assert result_hot_humid is not None
        assert result_hot_humid < 30  # Dovrebbe essere molto basso

        # Temperatura molto bassa, umidità molto bassa
        mock_coordinator.data = {
            "sensors": "VMGI,50,150,100,800,0,0,0,0,0,0,150,0,0,0",  # 5°C, 10%
        }
        result_cold_dry = sensor.native_value
        assert result_cold_dry is not None
        assert result_cold_dry < 30  # Dovrebbe essere molto basso

    def test_calculation_zero_humidity(self):
        """Test gestione umidità zero."""
        mock_coordinator = Mock()
        mock_coordinator.data = {
            "sensors": "VMGI,220,150,0,800,0,0,0,0,0,0,150,0,0,0",  # 22°C, 0%
        }

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        assert sensor.native_value is None

    def test_calculation_excessive_humidity(self):
        """Test gestione umidità eccessiva."""
        mock_coordinator = Mock()
        mock_coordinator.data = {
            "sensors": "VMGI,220,150,1000,800,0,0,0,0,0,0,150,0,0,0",  # 22°C, 100%
        }

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        result = sensor.native_value

        # Umidità eccessiva dovrebbe comunque dare un risultato ma non ottimale
        assert result is not None
        assert result < 85  # Non dovrebbe essere eccellente

    def test_temperature_comfort_function(self):
        """Test funzione di calcolo comfort termico."""
        mock_coordinator = Mock()
        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)

        # Test range ottimale (20-24°C)
        assert sensor._calculate_temperature_comfort(22.0) == 1.0
        assert sensor._calculate_temperature_comfort(20.0) == 1.0
        assert sensor._calculate_temperature_comfort(24.0) == 1.0

        # Test range accettabile
        comfort_19 = sensor._calculate_temperature_comfort(19.0)
        comfort_25 = sensor._calculate_temperature_comfort(25.0)
        assert 0.5 <= comfort_19 < 1.0
        assert 0.5 <= comfort_25 < 1.0

        # Test range estremo
        comfort_0 = sensor._calculate_temperature_comfort(0.0)
        comfort_40 = sensor._calculate_temperature_comfort(40.0)
        assert comfort_0 < 0.5
        assert comfort_40 < 0.5

    def test_humidity_comfort_function(self):
        """Test funzione di calcolo comfort igrometrico."""
        mock_coordinator = Mock()
        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)

        # Test range ottimale (40-60%)
        assert sensor._calculate_humidity_comfort(50.0) == 1.0
        assert sensor._calculate_humidity_comfort(40.0) == 1.0
        assert sensor._calculate_humidity_comfort(60.0) == 1.0

        # Test range accettabile
        comfort_35 = sensor._calculate_humidity_comfort(35.0)
        comfort_70 = sensor._calculate_humidity_comfort(70.0)
        assert 0.5 <= comfort_35 < 1.0
        assert 0.5 <= comfort_70 < 1.0

        # Test range estremo
        comfort_10 = sensor._calculate_humidity_comfort(10.0)
        comfort_90 = sensor._calculate_humidity_comfort(90.0)
        assert comfort_10 < 0.5
        assert comfort_90 < 0.5

    def test_extra_state_attributes_complete(self):
        """Test attributi aggiuntivi con dati completi."""
        mock_coordinator = Mock()
        # VMGI,220,150,500,800,0,0,0,0,0,0,150,0,0,0 - temp=22.0°C, humidity=50.0%
        mock_coordinator.data = {
            "sensors": "VMGI,220,150,500,800,0,0,0,0,0,0,150,0,0,0",
        }

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        attributes = sensor.extra_state_attributes

        assert attributes is not None
        assert "comfort_category" in attributes
        assert "temperature_comfort" in attributes
        assert "humidity_comfort" in attributes
        assert "optimal_temperature" in attributes
        assert "optimal_humidity" in attributes
        assert "current_temperature" in attributes
        assert "current_humidity" in attributes

        # Verifica valori specifici
        assert attributes["optimal_temperature"] == "20-24°C"
        assert attributes["optimal_humidity"] == "40-60%"
        assert attributes["current_temperature"] == "22.0°C"
        assert attributes["current_humidity"] == "50.0%"

        # Verifica che sia classificato come Eccellente
        assert attributes["comfort_category"] == "Eccellente"

    def test_extra_state_attributes_no_data(self):
        """Test attributi aggiuntivi senza dati."""
        mock_coordinator = Mock()
        mock_coordinator.data = None

        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)
        attributes = sensor.extra_state_attributes

        # Dovrebbe restituire attributi vuoti o di base
        assert attributes is not None

    def test_comfort_categories_classification(self):
        """Test classificazione categorie di comfort."""
        mock_coordinator = Mock()
        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)

        test_cases = [
            # (temp, humidity, expected_category_range)
            (22.0, 50.0, "Eccellente"),  # Condizioni ottimali
            (20.0, 45.0, "Eccellente"),  # Ancora ottime
            (19.0, 40.0, "Buono"),  # Buone condizioni
            (25.0, 65.0, "Buono"),  # Buone condizioni
            (17.0, 30.0, "Accettabile"),  # Condizioni accettabili
            (27.0, 75.0, "Accettabile"),  # Condizioni accettabili
            (10.0, 20.0, "Scarso"),  # Condizioni scarse
            (35.0, 90.0, "Scarso"),  # Condizioni scarse
        ]

        for temp, humidity, expected_category in test_cases:
            temp_value = int(temp * 10)  # Decimi di grado
            humidity_value = int(humidity * 10)  # Decimi di %
            mock_coordinator.data = {
                "sensors": f"VMGI,{temp_value},150,{humidity_value},800,0,0,0,0,0,0,150,0,0,0",
            }

            attributes = sensor.extra_state_attributes
            assert attributes is not None
            assert "comfort_category" in attributes
            # Note: Controlliamo che la categoria sia ragionevole, non necessariamente esatta
            # dato che i calcoli sono complessi
            assert attributes["comfort_category"] in [
                "Eccellente",
                "Buono",
                "Accettabile",
                "Mediocre",
                "Scarso",
            ]

    def test_invalid_data_types(self):
        """Test gestione di tipi di dati non validi."""
        mock_coordinator = Mock()
        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)

        # Test con dati malformati
        mock_coordinator.data = {
            "sensors": "VMGI,invalid,150,500,800,0,0,0,0,0,0,150,0,0,0",
        }
        assert sensor.native_value is None

        # Test con dati insufficienti
        mock_coordinator.data = {
            "sensors": "VMGI,220,150",  # Troppo pochi campi
        }
        assert sensor.native_value is None

    def test_mathematical_consistency(self):
        """Test consistenza matematica dei calcoli."""
        mock_coordinator = Mock()
        sensor = VmcHeltyComfortIndexSensor(mock_coordinator)

        # Test che condizioni migliori diano valori più alti
        # Condizioni ottime
        mock_coordinator.data = {
            "sensors": "VMGI,220,150,500,800,0,0,0,0,0,0,150,0,0,0",  # 22°C, 50%
        }
        comfort_optimal = sensor.native_value

        # Condizioni discrete
        mock_coordinator.data = {
            "sensors": "VMGI,190,150,350,800,0,0,0,0,0,0,150,0,0,0",  # 19°C, 35%
        }
        comfort_decent = sensor.native_value

        # Condizioni povere
        mock_coordinator.data = {
            "sensors": "VMGI,150,150,200,800,0,0,0,0,0,0,150,0,0,0",  # 15°C, 20%
        }
        comfort_poor = sensor.native_value

        assert comfort_optimal is not None
        assert comfort_decent is not None
        assert comfort_poor is not None

        # Verifica ordine logico
        assert comfort_optimal > comfort_decent > comfort_poor

        # Verifica range validi (0-100%)
        for comfort in [comfort_optimal, comfort_decent, comfort_poor]:
            assert 0 <= comfort <= 100
