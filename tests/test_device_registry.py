"""Test per il modulo device_registry."""

from unittest.mock import Mock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.vmc_helty_flow.const import DOMAIN
from custom_components.vmc_helty_flow.device_registry import (
    async_get_or_create_device,
    async_remove_orphaned_devices,
)


class TestAsyncGetOrCreateDevice:
    """Test class per async_get_or_create_device."""

    def setup_method(self):
        """Setup per ogni test."""
        self.hass = Mock(spec=HomeAssistant)
        self.coordinator = Mock()
        self.coordinator.ip = "192.168.1.100"
        self.coordinator.name = "Test Device"
        self.coordinator.config_entry.entry_id = "test_entry_id"

    @pytest.mark.asyncio
    async def test_create_new_device(self):
        """Test creazione nuovo dispositivo."""
        mock_device_registry = Mock()
        mock_device = Mock(id="new_device")
        mock_device_registry.async_get_or_create = Mock(return_value=mock_device)

        with (
            patch(
                "custom_components.vmc_helty_flow.device_registry.device_registry.async_get",
                return_value=mock_device_registry,
            ),
            patch(
                "custom_components.vmc_helty_flow.device_registry.async_get_device_unique_id",
                return_value="unique_mac_123",
            ) as mock_unique_id,
            patch(
                "custom_components.vmc_helty_flow.device_registry.async_get_device_info",
                return_value={"name": "Test Device", "model": "Flow"},
            ) as mock_device_info,
        ):
            result = await async_get_or_create_device(self.hass, self.coordinator)

            assert result.id == "new_device"
            mock_unique_id.assert_called_once_with(self.hass, "192.168.1.100")
            mock_device_info.assert_called_once_with(self.hass, "192.168.1.100")

            # Verifica che async_get_or_create sia stato chiamato
            mock_device_registry.async_get_or_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_existing_device(self):
        """Test recupero dispositivo esistente."""
        existing_device = Mock(id="existing_device")
        mock_device_registry = Mock()
        mock_device_registry.async_get_or_create = Mock(return_value=existing_device)

        with (
            patch(
                "custom_components.vmc_helty_flow.device_registry.device_registry.async_get",
                return_value=mock_device_registry,
            ),
            patch(
                "custom_components.vmc_helty_flow.device_registry.async_get_device_unique_id",
                return_value="unique_mac_123",
            ),
            patch(
                "custom_components.vmc_helty_flow.device_registry.async_get_device_info",
                return_value={"name": "Existing Device", "model": "Flow"},
            ),
        ):
            result = await async_get_or_create_device(self.hass, self.coordinator)

            assert result == existing_device

    @pytest.mark.asyncio
    async def test_device_creation_with_fallback_unique_id(self):
        """Test creazione dispositivo quando il MAC non è disponibile."""
        mock_device_registry = Mock()
        mock_device = Mock(id="test_device")
        mock_device_registry.async_get_or_create = Mock(return_value=mock_device)

        with (
            patch(
                "custom_components.vmc_helty_flow.device_registry.device_registry.async_get",
                return_value=mock_device_registry,
            ),
            patch(
                "custom_components.vmc_helty_flow.device_registry.async_get_device_unique_id",
                return_value=None,  # Simula MAC non disponibile
            ),
            patch(
                "custom_components.vmc_helty_flow.device_registry.async_get_device_info",
                return_value={"name": "Device Name", "model": "Flow"},
            ),
        ):
            await async_get_or_create_device(self.hass, self.coordinator)

            # Verifica che sia stato usato il fallback IP-based ID
            call_args = mock_device_registry.async_get_or_create.call_args
            identifiers = call_args[1]["identifiers"]
            assert (DOMAIN, "helty_flow_192_168_1_100") in identifiers


class TestAsyncRemoveOrphanedDevices:
    """Test class per async_remove_orphaned_devices."""

    def setup_method(self):
        """Setup per ogni test."""
        self.hass = Mock(spec=HomeAssistant)
        self.hass.data = {}

    @pytest.mark.asyncio
    async def test_remove_orphaned_devices_no_devices(self):
        """Test rimozione dispositivi orfani quando non ce ne sono."""
        mock_device_registry = Mock()
        mock_device_registry.devices = {}

        with (
            patch(
                "custom_components.vmc_helty_flow.device_registry.device_registry.async_get",
                return_value=mock_device_registry,
            ),
            patch(
                "custom_components.vmc_helty_flow.device_registry.entity_registry.async_get"
            ) as mock_entity_registry,
        ):
            mock_entity_registry.return_value = Mock()
            mock_config_entries = Mock()
            mock_config_entries.async_entries.return_value = []
            self.hass.config_entries = mock_config_entries

            # Non dovrebbe sollevare eccezioni
            await async_remove_orphaned_devices(self.hass)

    @pytest.mark.asyncio
    async def test_remove_orphaned_devices_with_orphans(self):
        """Test rimozione dispositivi orfani quando ce ne sono."""
        # Dispositivo con config entry inesistente
        orphaned_device = Mock()
        orphaned_device.id = "orphan_1"
        orphaned_device.config_entries = {"missing_entry"}
        orphaned_device.identifiers = {(DOMAIN, "orphan_device")}
        orphaned_device.name = "Orphaned Device"

        # Dispositivo valido
        valid_device = Mock()
        valid_device.id = "valid_1"
        valid_device.config_entries = {"valid_entry"}
        valid_device.identifiers = {(DOMAIN, "valid_device")}

        mock_device_registry = Mock()
        mock_device_registry.devices = {
            "orphan_1": orphaned_device,
            "valid_1": valid_device,
        }
        mock_device_registry.async_remove_device = Mock()

        # Mock config entries - solo valid_entry esiste
        mock_entry = Mock()
        mock_entry.entry_id = "valid_entry"
        mock_config_entries = Mock()
        mock_config_entries.async_entries.return_value = [mock_entry]
        self.hass.config_entries = mock_config_entries

        with (
            patch(
                "custom_components.vmc_helty_flow.device_registry.device_registry.async_get",
                return_value=mock_device_registry,
            ),
            patch(
                "custom_components.vmc_helty_flow.device_registry.entity_registry.async_get"
            ) as mock_entity_registry,
        ):
            mock_entity_registry.return_value = Mock()
            await async_remove_orphaned_devices(self.hass)

            # Verifica che solo il dispositivo orfano sia stato rimosso
            mock_device_registry.async_remove_device.assert_called_once_with("orphan_1")

    @pytest.mark.asyncio
    async def test_remove_orphaned_devices_with_domain_filter(self):
        """Test rimozione dispositivi orfani solo per il dominio VMC."""
        # Dispositivo VMC orfano
        vmc_orphaned_device = Mock()
        vmc_orphaned_device.id = "vmc_orphan"
        vmc_orphaned_device.config_entries = {"missing_vmc_entry"}
        vmc_orphaned_device.identifiers = {(DOMAIN, "vmc_device")}

        # Dispositivo di altro dominio orfano (non dovrebbe essere rimosso)
        other_orphaned_device = Mock()
        other_orphaned_device.id = "other_orphan"
        other_orphaned_device.config_entries = {"missing_other_entry"}
        other_orphaned_device.identifiers = {("other_domain", "other_device")}

        mock_device_registry = Mock()
        mock_device_registry.devices = {
            "vmc_orphan": vmc_orphaned_device,
            "other_orphan": other_orphaned_device,
        }
        mock_device_registry.async_remove_device = Mock()

        # Nessun config entry attivo
        mock_config_entries = Mock()
        mock_config_entries.async_entries.return_value = []
        self.hass.config_entries = mock_config_entries

        with (
            patch(
                "custom_components.vmc_helty_flow.device_registry.device_registry.async_get",
                return_value=mock_device_registry,
            ),
            patch(
                "custom_components.vmc_helty_flow.device_registry.entity_registry.async_get"
            ) as mock_entity_registry,
        ):
            mock_entity_registry.return_value = Mock()
            await async_remove_orphaned_devices(self.hass)

            # Verifica che solo il dispositivo VMC sia stato rimosso
            mock_device_registry.async_remove_device.assert_called_once_with(
                "vmc_orphan"
            )

    @pytest.mark.asyncio
    async def test_remove_orphaned_devices_exception_handling(self):
        """Test che le eccezioni durante la rimozione vengano propagate."""
        orphaned_device = Mock()
        orphaned_device.id = "orphan_1"
        orphaned_device.config_entries = {"missing_entry"}
        orphaned_device.identifiers = {(DOMAIN, "orphan_device")}
        orphaned_device.name = "Orphaned Device"

        mock_device_registry = Mock()
        mock_device_registry.devices = {"orphan_1": orphaned_device}
        mock_device_registry.async_remove_device = Mock(
            side_effect=Exception("Removal failed")
        )

        mock_config_entries = Mock()
        mock_config_entries.async_entries.return_value = []
        self.hass.config_entries = mock_config_entries

        with (
            patch(
                "custom_components.vmc_helty_flow.device_registry.device_registry.async_get",
                return_value=mock_device_registry,
            ),
            patch(
                "custom_components.vmc_helty_flow.device_registry.entity_registry.async_get"
            ) as mock_entity_registry,
        ):
            mock_entity_registry.return_value = Mock()
            # L'eccezione dovrebbe essere propagata
            with pytest.raises(Exception, match="Removal failed"):
                await async_remove_orphaned_devices(self.hass)

            # Verifica che la rimozione sia stata tentata
            mock_device_registry.async_remove_device.assert_called_once_with("orphan_1")
