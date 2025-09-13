import pytest
from fan import VmcHeltyFan
from sensor import (
    VmcHeltySensor, VmcHeltyOnOffSensor, VmcHeltyResetFilterButton, VmcHeltyNameText,
    VmcHeltySSIDText, VmcHeltyPasswordText, VmcHeltyIPAddressSensor, VmcHeltySubnetMaskSensor,
    VmcHeltyGatewaySensor, VmcHeltyLastResponseSensor, VmcHeltyFilterHoursSensor,
    VmcHeltyNetworkSSIDSensor, VmcHeltyNetworkPasswordSensor
)
from switch import VmcHeltyModeSwitch, VmcHeltyPanelLedSwitch, VmcHeltySensorsSwitch
from light import VmcHeltyLight
from light_timer import VmcHeltyLightTimer
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


IP = "192.168.1.100"
NAME = "TestVMC"
SSID = "TestSSID"
PASSWORD = "TestPass"
MASK = "255.255.255.0"
GATEWAY = "192.168.1.1"


@pytest.mark.parametrize("entity_cls, args", [
    (VmcHeltyFan, [IP, NAME]),
    (VmcHeltySensor, [IP, NAME, "Temperatura Interna"]),
    (VmcHeltySensor, [IP, NAME, "Temperatura Esterna"]),
    (VmcHeltySensor, [IP, NAME, "Umidità"]),
    (VmcHeltySensor, [IP, NAME, "CO2"]),
    (VmcHeltySensor, [IP, NAME, "VOC"]),
    (VmcHeltyModeSwitch, [IP, NAME, "hyperventilation"]),
    (VmcHeltyModeSwitch, [IP, NAME, "night"]),
    (VmcHeltyModeSwitch, [IP, NAME, "free_cooling"]),
    (VmcHeltyPanelLedSwitch, [IP, NAME]),
    (VmcHeltySensorsSwitch, [IP, NAME]),
    (VmcHeltyLight, [IP, NAME]),
    (VmcHeltyLightTimer, [IP, NAME]),
    (VmcHeltyOnOffSensor, [IP, NAME]),
    (VmcHeltyResetFilterButton, [IP, NAME]),
    (VmcHeltyNameText, [IP, NAME]),
    (VmcHeltySSIDText, [IP, NAME, SSID]),
    (VmcHeltyPasswordText, [IP, NAME, PASSWORD]),
    (VmcHeltyIPAddressSensor, [IP, NAME]),
    (VmcHeltySubnetMaskSensor, [IP, NAME, MASK]),
    (VmcHeltyGatewaySensor, [IP, NAME, GATEWAY]),
    (VmcHeltyLastResponseSensor, [IP, NAME]),
    (VmcHeltyFilterHoursSensor, [IP, NAME]),
    (VmcHeltyNetworkSSIDSensor, [IP, NAME, SSID]),
    (VmcHeltyNetworkPasswordSensor, [IP, NAME, PASSWORD]),
])
def test_entity_instantiation(entity_cls, args):
    entity = entity_cls(*args)
    assert entity is not None
    assert hasattr(entity, "name") or hasattr(entity, "_name")
    assert hasattr(entity, "ip") or hasattr(entity, "_ip")
    # Ulteriori test specifici possono essere aggiunti qui
