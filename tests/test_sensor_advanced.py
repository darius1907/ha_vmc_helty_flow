"""Test absolute humidity sensor."""

from unittest.mock import MagicMock
import pytest
from custom_components.vmc_helty_flow.sensor import VmcHeltyAbsoluteHumiditySensor


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator for testing."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "VMC Test"
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.data = {
        "sensors": "VMGI,245,205,650,450,50,75,80,90,100,1,2,3,4,1000",
        "status": "VMGO,3,1,25,0,24",
        "temperature_internal": 24.5,  # 245 / 10
        "humidity": 65.0,  # dal protocollo
    }
    return coordinator


class TestVmcHeltyAbsoluteHumiditySensor:
    """Test absolute humidity sensor."""

    @pytest.fixture
    def sensor(self, mock_coordinator):
        """Create sensor instance."""
        mock_coordinator.name_slug = "vmc_helty_testvmc"
        return VmcHeltyAbsoluteHumiditySensor(mock_coordinator)

    def test_init(self, sensor):
        """Test sensor initialization."""
        assert sensor._attr_unique_id == "vmc_helty_testvmc_absolute_humidity"
        assert sensor._attr_name == "VMC Helty VMC Test Umidità Assoluta"
        assert sensor._attr_native_unit_of_measurement == "g/m³"
        assert sensor._attr_device_class is None
        assert sensor._attr_state_class == "measurement"
        assert sensor._attr_icon == "mdi:water-percent"

    def test_native_value_no_data(self, sensor, mock_coordinator):
        """Test with no data."""
        mock_coordinator.data = None
        assert sensor.native_value is None

    def test_native_value_no_temperature(self, sensor, mock_coordinator):
        """Test with missing temperature data."""
        mock_coordinator.data = {"humidity": 65.0}
        assert sensor.native_value is None

    def test_native_value_no_humidity(self, sensor, mock_coordinator):
        """Test with missing humidity data."""
        mock_coordinator.data = {"temperature_internal": 24.5}
        assert sensor.native_value is None

    def test_calculation(self, mock_coordinator):
        """Test absolute humidity calculation with real values."""
        # Simula dati reali del sensore VMC nel formato originale
        # VMGI,225,183,650,850,50,75,80,90,100,1,120,3,4,1000
        # temp_int: 225 (22.5°C), humidity: 650 (65.0%)
        mock_coordinator.data = {
            "sensors": "VMGI,225,183,650,850,50,75,80,90,100,1,120,3,4,1000"
        }
        
        sensor = VmcHeltyAbsoluteHumiditySensor(mock_coordinator)
        result = sensor.native_value
        
        # Il sensore deve prima estrarre i valori dalla stringa sensors
        # poi calcolare l'umidità assoluta
        # Per T=22.5°C, RH=65.0% => ~12.96 g/m³ (formula Magnus-Tetens)
        assert result is not None
        assert isinstance(result, float)
        assert abs(result - 12.96) < 0.1  # ±0.1 g/m³

    def test_native_value_zero_humidity(self, sensor, mock_coordinator):
        """Test with zero humidity."""
        # VMGI,245,205,000,450,50,75,80,90,100,1,2,3,4,1000
        # temp_int: 245 (24.5°C), humidity: 000 (0.0%)
        mock_coordinator.data = {
            "sensors": "VMGI,245,205,000,450,50,75,80,90,100,1,2,3,4,1000"
        }
        value = sensor.native_value
        assert value is not None
        assert value == 0.0  # Zero humidity should give zero absolute humidity

    def test_native_value_edge_cases(self, sensor, mock_coordinator):
        """Test edge cases."""
        # Temperatura molto bassa
        # VMGI,-100,205,500,450,50,75,80,90,100,1,2,3,4,1000
        # temp_int: -100 (-10.0°C), humidity: 500 (50.0%)
        mock_coordinator.data = {
            "sensors": "VMGI,-100,205,500,450,50,75,80,90,100,1,2,3,4,1000"
        }
        value = sensor.native_value
        assert value is not None
        assert value > 0
        
        # Umidità molto alta
        # VMGI,250,205,990,450,50,75,80,90,100,1,2,3,4,1000
        # temp_int: 250 (25.0°C), humidity: 990 (99.0%)
        mock_coordinator.data = {
            "sensors": "VMGI,250,205,990,450,50,75,80,90,100,1,2,3,4,1000"
        }
        value = sensor.native_value
        assert value is not None
        assert value > 0

    def test_native_value_invalid_data(self, sensor, mock_coordinator):
        """Test with invalid data types."""
        # Dati sensori con valori invalidi
        mock_coordinator.data = {
            "sensors": "VMGI,invalid,205,650,450,50,75,80,90,100,1,2,3,4,1000"
        }
        assert sensor.native_value is None
        
        mock_coordinator.data = {
            "sensors": "VMGI,245,205,invalid,450,50,75,80,90,100,1,2,3,4,1000"
        }
        assert sensor.native_value is None
