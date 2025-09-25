"""Device info utilities for VMC Helty Flow integration."""

import logging

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class VmcHeltyEntity(Entity):
    """Base class for VMC Helty entities."""

    def __init__(self, coordinator, device_info=None):
        """Initialize VMC Helty entity."""
        self.coordinator = coordinator
        # Ensure device_info is always a dict
        if isinstance(device_info, dict):
            self._device_info = device_info
        else:
            self._device_info = {}
        self._attr_should_poll = False

        # Specifica l'attributo unique_id
        # Il coordinator deve avere un attributo config_entry
        if hasattr(coordinator, "config_entry"):
            self._attr_unique_id = (
                f"{coordinator.config_entry.entry_id}_{self.__class__.__name__}"
            )
        else:
            self._attr_unique_id = f"{coordinator.ip}_{self.__class__.__name__}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Ottieni l'identificatore univoco o usa l'IP
        unique_id = (
            self._device_info.get("unique_id")
            or f"vmc_helty_{self.coordinator.ip.replace('.', '_')}"
        )

        return DeviceInfo(
            identifiers={(DOMAIN, unique_id), (DOMAIN, self.coordinator.ip)},
            connections={("ip", self.coordinator.ip)},
            name=self.coordinator.name,
            manufacturer=self._device_info.get("manufacturer", "Helty"),
            model=self._device_info.get("model", "VMC Flow"),
            sw_version=self._device_info.get("sw_version"),
            hw_version=self._device_info.get("hw_version"),
            configuration_url=f"http://{self.coordinator.ip}:5001",
            suggested_area=self._device_info.get("suggested_area"),
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """Connect to dispatcher when added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def name_by_user(self) -> str | None:
        """Return the user-defined name if set."""
        if hasattr(self.coordinator, "config_entry"):
            return self.coordinator.config_entry.title
        return None
