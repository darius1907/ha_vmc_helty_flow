"""Platform setup for button entities."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device_info import VmcHeltyEntity
from .helpers import tcp_send_command


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VMC Helty buttons from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        VmcHeltyResetFilterButton(coordinator),
    ]

    async_add_entities(entities)


class VmcHeltyResetFilterButton(VmcHeltyEntity, ButtonEntity):
    """VMC Helty reset filter button."""

    def __init__(self, coordinator):
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_reset_filter"
        self._attr_name = f"{coordinator.name} Reset Filter"
        self._attr_icon = "mdi:air-filter"

    async def async_press(self) -> None:
        """Reset filter counter."""
        response = await tcp_send_command(self.coordinator.ip, 5001, "VMWH0417744")
        if response == "OK":
            await self.coordinator.async_request_refresh()
