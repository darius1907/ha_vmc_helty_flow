"""Test delle entità VMC Helty Flow."""

from unittest.mock import Mock

from custom_components.vmc_helty_flow.fan import VmcHeltyFan

IP = "192.168.1.100"
NAME = "TestVMC"


def test_vmc_helty_fan_creation():
    """Test creazione entità fan."""
    # Mock del coordinator
    coordinator = Mock()
    coordinator.ip = IP
    coordinator.name = NAME
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.data = {"status": "VMGO,1,1,12345"}

    fan = VmcHeltyFan(coordinator)

    assert fan._attr_unique_id == "vmc_helty_testvmc"
    assert fan._attr_name == "VMC Helty TestVMC"


def test_fan_percentage_calculation():
    """Test calcolo percentuale ventola."""
    coordinator = Mock()
    coordinator.ip = IP
    coordinator.name = NAME
    coordinator.data = {"status": "VMGO,2,1,12345"}

    fan = VmcHeltyFan(coordinator)

    # Test con velocità 2 (dovrebbe essere 50%)
    assert fan.percentage == 50


def test_fan_is_on():
    """Test stato accensione ventola."""
    coordinator = Mock()
    coordinator.ip = IP
    coordinator.name = NAME
    coordinator.data = {"status": "VMGO,1,1,12345"}

    fan = VmcHeltyFan(coordinator)

    # Con velocità 1, la ventola dovrebbe essere accesa
    assert fan.is_on is True
