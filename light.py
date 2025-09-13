"""
Entità Light per livello luci VMC Helty Flow
"""
from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device_info import VmcHeltyEntity
from .helpers import tcp_send_command


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VMC Helty lights from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        VmcHeltyLight(coordinator),
        VmcHeltyLightTimer(coordinator),
    ]

    async_add_entities(entities)


class VmcHeltyLight(VmcHeltyEntity, LightEntity):
    """VMC Helty light entity for brightness control."""

    def __init__(self, coordinator):
        """Initialize the light."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_light"
        self._attr_name = f"{coordinator.name} Light"
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    @property
    def brightness(self) -> int | None:
        """Return current brightness (0-255)."""
        if not self.coordinator.data:
            return 0

        status = self.coordinator.data.get("status", "")
        if status and status.startswith("VMGO"):
            try:
                parts = status.split(",")
                # Il livello luci è nella posizione 11 (0-100)
                light_level = int(parts[11]) if len(parts) > 11 else 0
                # Converti da 0-100 a 0-255
                return int(light_level * 2.55)
            except (ValueError, IndexError):
                return 0
        return 0

    @property
    def is_on(self) -> bool:
        """Return True if light is on."""
        return (self.brightness or 0) > 0

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the light."""
        brightness = kwargs.get("brightness", 255)
        # Converti da 0-255 a 0-100 con step di 25
        light_level = max(0, min(100, int(brightness / 2.55)))
        # Arrotonda ai livelli supportati (0, 25, 50, 75, 100)
        light_level = round(light_level / 25) * 25

        try:
            # Il comando per impostare le luci non è specificato nei requirements
            # Placeholder per il comando - da implementare quando disponibile
            response = await tcp_send_command(
                self.coordinator.ip, 5001, f"VMWL{light_level:03d}"
            )
            if response == "OK":
                await self.coordinator.async_request_refresh()
        except Exception as err:
            raise err

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the light."""
        try:
            response = await tcp_send_command(
                self.coordinator.ip, 5001, "VMWL000"
            )
            if response == "OK":
                await self.coordinator.async_request_refresh()
        except Exception as err:
            raise err


class VmcHeltyLightTimer(VmcHeltyEntity, LightEntity):
    """VMC Helty light timer entity."""

    def __init__(self, coordinator):
        """Initialize the light timer."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_light_timer"
        self._attr_name = f"{coordinator.name} Light Timer"
        self._attr_icon = "mdi:timer"

    @property
    def extra_state_attributes(self):
        """Return timer value in seconds."""
        if not self.coordinator.data:
            return {}

        status = self.coordinator.data.get("status", "")
        if status and status.startswith("VMGO"):
            try:
                parts = status.split(",")
                # Il timer luci è nella posizione 15 (in secondi)
                timer_seconds = int(parts[15]) if len(parts) > 15 else 0
                return {"timer_seconds": timer_seconds}
            except (ValueError, IndexError):
                return {}
        return {}

    @property
    def is_on(self) -> bool:
        """Return True if timer is active."""
        attributes = self.extra_state_attributes
        return attributes.get("timer_seconds", 0) > 0

    async def async_turn_on(self, **kwargs) -> None:
        """Set light timer (default 300 seconds)."""
        timer_seconds = 300  # Default 5 minuti

        try:
            # Comando placeholder per impostare timer - da implementare
            response = await tcp_send_command(
                self.coordinator.ip, 5001, f"VMWT{timer_seconds:03d}"
            )
            if response == "OK":
                await self.coordinator.async_request_refresh()
        except Exception as err:
            raise err

    async def async_turn_off(self, **kwargs) -> None:
        """Disable light timer."""
        try:
            response = await tcp_send_command(
                self.coordinator.ip, 5001, "VMWT000"
            )
            if response == "OK":
                await self.coordinator.async_request_refresh()
        except Exception as err:
            raise err
