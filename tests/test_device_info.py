"""Test per il modulo device_info."""

from unittest.mock import Mock

from custom_components.vmc_helty_flow.const import DOMAIN
from custom_components.vmc_helty_flow.device_info import VmcHeltyEntity


class TestVmcHeltyEntity:
    """Test per la classe VmcHeltyEntity."""

    def test_init_with_config_entry(self):
        """Test inizializzazione con config_entry."""
        # Crea mock coordinator con config_entry
        coordinator = Mock()
        coordinator.config_entry.entry_id = "test_entry_123"
        coordinator.ip = "192.168.1.100"
        coordinator.name = "Test VMC"

        entity = VmcHeltyEntity(coordinator)

        assert entity.coordinator == coordinator
        assert entity._device_info == {}
        assert entity._attr_should_poll is False
        expected_unique_id = "test_entry_123_VmcHeltyEntity"
        assert entity._attr_unique_id == expected_unique_id

    def test_init_without_config_entry(self):
        """Test inizializzazione senza config_entry."""
        # Crea mock coordinator senza config_entry
        coordinator = Mock(spec=["ip", "name"])
        coordinator.ip = "192.168.1.100"
        coordinator.name = "Test VMC"

        entity = VmcHeltyEntity(coordinator)

        assert entity.coordinator == coordinator
        assert entity._device_info == {}
        assert entity._attr_should_poll is False
        expected_unique_id = "192.168.1.100_VmcHeltyEntity"
        assert entity._attr_unique_id == expected_unique_id

    def test_init_with_device_info(self):
        """Test inizializzazione con device_info personalizzato."""
        coordinator = Mock(spec=["ip", "name"])
        coordinator.ip = "192.168.1.100"
        coordinator.name = "Test VMC"

        device_info = {
            "manufacturer": "Custom Manufacturer",
            "model": "Custom Model",
            "sw_version": "1.2.3",
        }

        entity = VmcHeltyEntity(coordinator, device_info)

        assert entity._device_info == device_info

    def test_device_info_default_values(self):
        """Test device_info con valori predefiniti."""
        coordinator = Mock(spec=["ip", "name"])
        coordinator.ip = "192.168.1.100"
        coordinator.name = "Test VMC"

        entity = VmcHeltyEntity(coordinator)
        device_info = entity.device_info

        assert isinstance(device_info, dict)
        assert device_info["identifiers"] == {
            (DOMAIN, "helty_flow_192_168_1_100"),
            (DOMAIN, "192.168.1.100"),
        }
        assert device_info["connections"] == {("ip", "192.168.1.100")}
        assert device_info["name"] == "Test VMC"
        assert device_info["manufacturer"] == "Helty"
        assert device_info["model"] == "VMC Flow"
        assert device_info["configuration_url"] == "http://192.168.1.100:5001"

    def test_device_info_custom_values(self):
        """Test device_info con valori personalizzati."""
        coordinator = Mock(spec=["ip", "name"])
        coordinator.ip = "192.168.1.200"
        coordinator.name = "Custom VMC"

        custom_device_info = {
            "unique_id": "custom_unique_id",
            "manufacturer": "Custom Manufacturer",
            "model": "Custom Model V2",
            "sw_version": "2.1.0",
            "hw_version": "HW_v1.5",
            "suggested_area": "Basement",
        }

        entity = VmcHeltyEntity(coordinator, custom_device_info)
        device_info = entity.device_info

        assert isinstance(device_info, dict)
        assert device_info["identifiers"] == {
            (DOMAIN, "custom_unique_id"),
            (DOMAIN, "192.168.1.200"),
        }
        assert device_info["connections"] == {("ip", "192.168.1.200")}
        assert device_info["name"] == "Custom VMC"
        assert device_info["manufacturer"] == "Custom Manufacturer"
        assert device_info["model"] == "Custom Model V2"
        assert device_info["sw_version"] == "2.1.0"
        assert device_info["hw_version"] == "HW_v1.5"
        assert device_info["suggested_area"] == "Basement"
        assert device_info["configuration_url"] == "http://192.168.1.200:5001"

    def test_device_info_partial_custom_values(self):
        """Test device_info con alcuni valori personalizzati."""
        coordinator = Mock(spec=["ip", "name"])
        coordinator.ip = "192.168.1.150"
        coordinator.name = "Partial VMC"

        partial_device_info = {
            "manufacturer": "Custom Manufacturer",
            "sw_version": "1.0.5",
        }

        entity = VmcHeltyEntity(coordinator, partial_device_info)
        device_info = entity.device_info

        # Verifica che i valori personalizzati siano usati
        assert device_info["manufacturer"] == "Custom Manufacturer"
        assert device_info["sw_version"] == "1.0.5"

        # Verifica che i valori predefiniti siano usati per gli altri
        assert device_info["model"] == "VMC Flow"
        assert device_info["hw_version"] is None
        assert device_info["suggested_area"] is None

    def test_unique_id_generation_ip_with_dots(self):
        """Test generazione unique_id con IP contenente punti."""
        coordinator = Mock(spec=["ip", "name"])
        coordinator.ip = "192.168.1.255"
        coordinator.name = "Test VMC"

        entity = VmcHeltyEntity(coordinator)
        device_info = entity.device_info

        # Verifica che i punti nell'IP siano sostituiti con underscore
        expected_unique_id = "helty_flow_192_168_1_255"
        assert (DOMAIN, expected_unique_id) in device_info["identifiers"]

    def test_device_info_domain_constant(self):
        """Test che device_info usi la costante DOMAIN corretta."""
        coordinator = Mock(spec=["ip", "name"])
        coordinator.ip = "192.168.1.100"
        coordinator.name = "Test VMC"

        entity = VmcHeltyEntity(coordinator)
        device_info = entity.device_info

        # Verifica che tutti gli identificatori usino la costante DOMAIN
        for identifier in device_info["identifiers"]:
            assert identifier[0] == DOMAIN
            assert identifier[0] == "vmc_helty_flow"

    def test_entity_inheritance(self):
        """Test che VmcHeltyEntity erediti correttamente da Entity."""
        coordinator = Mock(spec=["ip", "name"])
        coordinator.ip = "192.168.1.100"
        coordinator.name = "Test VMC"

        entity = VmcHeltyEntity(coordinator)

        # Verifica attributi Entity
        assert hasattr(entity, "_attr_should_poll")
        assert hasattr(entity, "_attr_unique_id")
        assert hasattr(entity, "device_info")

    def test_coordinator_reference(self):
        """Test che il riferimento al coordinator sia mantenuto."""
        coordinator = Mock(spec=["ip", "name"])
        coordinator.ip = "192.168.1.100"
        coordinator.name = "Test VMC"

        entity = VmcHeltyEntity(coordinator)

        # Verifica che il coordinator sia mantenuto correttamente
        assert entity.coordinator is coordinator
        assert entity.coordinator.ip == "192.168.1.100"
        assert entity.coordinator.name == "Test VMC"
