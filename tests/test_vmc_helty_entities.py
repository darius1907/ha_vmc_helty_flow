"""Test entità VMC Helty."""

from unittest.mock import Mock

import pytest

from custom_components.vmc_helty_flow.fan import VmcHeltyFan
from custom_components.vmc_helty_flow.light import VmcHeltyLight, VmcHeltyLightTimer
from custom_components.vmc_helty_flow.sensor import (
    VmcHeltyFilterHoursSensor,
    VmcHeltyIPAddressSensor,
    VmcHeltyLastResponseSensor,
    VmcHeltyNameText,
    VmcHeltyNetworkPasswordSensor,
    VmcHeltyNetworkSSIDSensor,
    VmcHeltyOnOffSensor,
    VmcHeltyPasswordText,
    VmcHeltyResetFilterButton,
    VmcHeltySensor,
    VmcHeltySSIDText,
)
from custom_components.vmc_helty_flow.switch import (
    VmcHeltyModeSwitch,
    VmcHeltyPanelLedSwitch,
    VmcHeltySensorsSwitch,
)

# Test constants
IP = "192.168.1.100"
NAME = "TestVMC"
SSID = "TestSSID"
PASSWORD = "TestPass"


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator for testing."""
    coordinator = Mock()
    coordinator.ip = IP
    coordinator.name = NAME
    coordinator.data = {}
    coordinator.config_entry = Mock()
    coordinator.config_entry.entry_id = "test_entry"
    return coordinator


@pytest.mark.parametrize(
    ("entity_cls", "args"),
    [
        (VmcHeltyFan, []),
        (VmcHeltySensor, ["temperature_internal", "Temperatura Interna", "°C"]),
        (VmcHeltySensor, ["temperature_external", "Temperatura Esterna", "°C"]),
        (VmcHeltySensor, ["humidity", "Umidità", "%"]),
        (VmcHeltySensor, ["co2", "CO2", "ppm"]),
        (VmcHeltySensor, ["voc", "VOC", "ppm"]),
        (VmcHeltyModeSwitch, ["hyperventilation", "Iperventilazione"]),
        (VmcHeltyModeSwitch, ["night", "Modalità Notte"]),
        (VmcHeltyModeSwitch, ["free_cooling", "Free Cooling"]),
        (VmcHeltyPanelLedSwitch, []),
        (VmcHeltySensorsSwitch, []),
        (VmcHeltyLight, []),
        (VmcHeltyLightTimer, []),
        (VmcHeltyOnOffSensor, []),
        (VmcHeltyResetFilterButton, []),
        (VmcHeltyNameText, []),
        (VmcHeltySSIDText, []),
        (VmcHeltyPasswordText, []),
        (VmcHeltyIPAddressSensor, []),
        (VmcHeltyLastResponseSensor, []),
        (VmcHeltyFilterHoursSensor, []),
        (VmcHeltyNetworkSSIDSensor, []),
        (VmcHeltyNetworkPasswordSensor, []),
    ],
)
def test_entity_instantiation(entity_cls, args, mock_coordinator):
    """Test that entities can be instantiated with proper arguments."""
    # Pass coordinator as first argument, then any additional args
    entity = entity_cls(mock_coordinator, *args)
    assert entity is not None

    # Basic checks that should work for all entities
    if hasattr(entity, "unique_id"):
        assert entity.unique_id is not None
    if hasattr(entity, "name"):
        assert entity.name is not None


import pytest

from custom_components.vmc_helty_flow.fan import VmcHeltyFan
from custom_components.vmc_helty_flow.light import VmcHeltyLight, VmcHeltyLightTimer
from custom_components.vmc_helty_flow.sensor import (
    VmcHeltyFilterHoursSensor,
    VmcHeltyIPAddressSensor,
    VmcHeltyLastResponseSensor,
    VmcHeltyNameText,
    VmcHeltyNetworkPasswordSensor,
    VmcHeltyNetworkSSIDSensor,
    VmcHeltyOnOffSensor,
    VmcHeltyPasswordText,
    VmcHeltyResetFilterButton,
    VmcHeltySensor,
    VmcHeltySSIDText,
)
from custom_components.vmc_helty_flow.switch import (
    VmcHeltyModeSwitch,
    VmcHeltyPanelLedSwitch,
    VmcHeltySensorsSwitch,
)

IP = "192.168.1.100"
NAME = "TestVMC"
SSID = "TestSSID"
PASSWORD = "TestPass"
MASK = "255.255.255.0"
GATEWAY = "192.168.1.1"


@pytest.mark.parametrize(
    ("entity_cls", "additional_args"),
    [
        (VmcHeltyFan, []),
        (VmcHeltySensor, ["temp_in", "Temperatura Interna", "°C"]),
        (VmcHeltySensor, ["temp_out", "Temperatura Esterna", "°C"]),
        (VmcHeltySensor, ["humidity", "Umidità", "%"]),
        (VmcHeltySensor, ["co2", "CO2", "ppm"]),
        (VmcHeltySensor, ["voc", "VOC", "ppb"]),
        (VmcHeltyModeSwitch, ["hyperventilation", "Hyperventilation"]),
        (VmcHeltyModeSwitch, ["night", "Night"]),
        (VmcHeltyModeSwitch, ["free_cooling", "Free Cooling"]),
        (VmcHeltyPanelLedSwitch, []),
        (VmcHeltySensorsSwitch, []),
        (VmcHeltyLight, []),
        (VmcHeltyLightTimer, []),
        (VmcHeltyOnOffSensor, []),
        (VmcHeltyResetFilterButton, []),
        (VmcHeltyNameText, []),
        (VmcHeltySSIDText, []),
        (VmcHeltyPasswordText, []),
        (VmcHeltyIPAddressSensor, []),
        (VmcHeltyLastResponseSensor, []),
        (VmcHeltyFilterHoursSensor, []),
        (VmcHeltyNetworkSSIDSensor, []),
        (VmcHeltyNetworkPasswordSensor, []),
    ],
)
def test_entity_instantiation(entity_cls, additional_args):
    # Create mock coordinator
    mock_coordinator = Mock()
    mock_coordinator.ip = IP
    mock_coordinator.config_entry = Mock()
    mock_coordinator.config_entry.entry_id = "test_entry"

    # Create entity with coordinator and any additional args
    entity = entity_cls(mock_coordinator, *additional_args)
    assert entity is not None
    assert hasattr(entity, "coordinator")
    # Ulteriori test specifici possono essere aggiunti qui
