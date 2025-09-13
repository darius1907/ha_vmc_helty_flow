"""
Entità Fan per VMC Helty Flow
"""
from typing import Optional, Dict, Any, List

from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device_info import VmcHeltyEntity
from .helpers import tcp_send_command, VMCConnectionError


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VMC Helty fan from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([VmcHeltyFan(coordinator)])


class VmcHeltyFan(VmcHeltyEntity, FanEntity):
    """VMC Helty Fan entity."""

    def __init__(self, coordinator):
        """Initialize the fan."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_fan"
        self._attr_name = f"{coordinator.name} Fan"
        self._attr_speed_count = 4  # 4 velocità (1-4)
        self._attr_supported_features = 0  # Nessuna feature speciale per ora

    @property
    def is_on(self) -> bool:
        """Return True if fan is on."""
        if not self.coordinator.data:
            return False

        # Parsa lo stato dalla risposta VMGH
        status = self.coordinator.data.get("status", "")
        if status and status.startswith("VMGO"):
            try:
                parts = status.split(",")
                fan_speed = int(parts[1]) if len(parts) > 1 else 0
                # Velocità 0 = off, 1-4 = on, 5-7 = modalità speciali (considerare come on)
                return fan_speed > 0
            except (ValueError, IndexError):
                return False
        return False

    @property
    def percentage(self) -> int:
        """Return current speed percentage."""
        if not self.coordinator.data:
            return 0

        status = self.coordinator.data.get("status", "")
        if status and status.startswith("VMGO"):
            try:
                parts = status.split(",")
                fan_speed = int(parts[1]) if len(parts) > 1 else 0

                # Gestione modalità speciali
                if fan_speed == 5:  # Modalità notte -> velocità 1
                    return 25
                elif fan_speed == 6:  # Iperventilazione -> velocità 4
                    return 100
                elif fan_speed == 7:  # Free cooling -> velocità 0
                    return 0
                else:  # Velocità normale 0-4
                    return min(fan_speed * 25, 100)
            except (ValueError, IndexError):
                return 0
        return 0

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}

        status = self.coordinator.data.get("status", "")
        attributes = {}

        if status and status.startswith("VMGO"):
            try:
                parts = status.split(",")
                fan_speed = int(parts[1]) if len(parts) > 1 else 0

                # Modalità speciali
                attributes["night_mode"] = fan_speed == 5
                attributes["hyperventilation"] = fan_speed == 6
                attributes["free_cooling"] = fan_speed == 7
                attributes["manual_speed"] = fan_speed if 0 <= fan_speed <= 4 else None

                # Altri stati dal dispositivo
                if len(parts) > 2:
                    attributes["panel_led"] = parts[2] == "1" if len(parts) > 2 else False
                if len(parts) > 4:
                    attributes["sensors_active"] = parts[4] == "0" if len(parts) > 4 else True

            except (ValueError, IndexError):
                pass

        return attributes

    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed by percentage."""
        if percentage == 0:
            speed = 0
        else:
            # Converte percentuale in velocità (1-4)
            speed = max(1, min(4, round(percentage / 25)))

        try:
            response = await tcp_send_command(
                self.coordinator.ip, 5001, f"VMWH000000{speed}"
            )
            if response == "OK":
                # Forza aggiornamento del coordinatore
                await self.coordinator.async_request_refresh()
        except VMCConnectionError as err:
            self._attr_available = False
            raise err
        except Exception as err:
            self._attr_available = False
            raise err

    async def async_turn_on(
        self,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Turn on the fan."""
        if percentage is None:
            percentage = 25  # Default alla velocità minima
        await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        await self.async_set_percentage(0)
