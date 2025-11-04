"""Entità Switch per modalità speciali VMC Helty Flow."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ENTITY_NAME_PREFIX, PART_INDEX_PANEL_LED, PART_INDEX_SENSORS
from .device_info import VmcHeltyEntity
from .helpers import tcp_send_command

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VMC Helty switches from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        # Modalità speciali
        VmcHeltyModeSwitch(coordinator, "hyperventilation", "Iperventilazione"),
        VmcHeltyModeSwitch(coordinator, "night", "Modalità Notte"),
        VmcHeltyModeSwitch(coordinator, "free_cooling", "Free Cooling"),
        # Altri switch
        VmcHeltyPanelLedSwitch(coordinator),
        VmcHeltySensorsSwitch(coordinator),
    ]

    async_add_entities(entities)


MODES = {
    "hyperventilation": {
        "cmd": "VMWH0000005",
        "fan_value": 6,
        "name": "Iperventilazione",
    },
    "night": {"cmd": "VMWH0000006", "fan_value": 5, "name": "Modalità Notte"},
    "free_cooling": {"cmd": "VMWH0000007", "fan_value": 7, "name": "Free Cooling"},
}


class VmcHeltyModeSwitch(VmcHeltyEntity, SwitchEntity):
    """VMC Helty special mode switch."""

    def __init__(self, coordinator, mode_key, mode_name):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._mode_key = mode_key
        self._attr_unique_id = f"{coordinator.name_slug}_{mode_key}"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} {mode_name}"
        self._attr_icon = self._get_mode_icon(mode_key)

    def _get_mode_icon(self, mode_key):
        """Get icon for mode."""
        icons = {
            "hyperventilation": "mdi:fan-plus",
            "night": "mdi:weather-night",
            "free_cooling": "mdi:snowflake",
        }
        return icons.get(mode_key, "mdi:toggle-switch")

    @property
    def is_on(self) -> bool:
        """Return True if mode is active."""
        if not self.coordinator.data:
            return False

        status = self.coordinator.data.get("status", "")
        if status and status.startswith("VMGO"):
            try:
                parts = status.split(",")
                fan_speed = int(parts[1]) if len(parts) > 1 else 0
                return fan_speed == MODES[self._mode_key]["fan_value"]
            except (ValueError, IndexError):
                return False
        return False

    async def async_turn_on(self, **_kwargs) -> None:
        """Turn on the mode."""
        response = await tcp_send_command(
            str(self.coordinator.ip), 5001, str(MODES[self._mode_key]["cmd"])
        )
        if response == "OK":
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_kwargs) -> None:
        """Turn off the mode (set to manual speed 1)."""
        # Disattiva la modalità speciale impostando velocità manuale 1
        response = await tcp_send_command(str(self.coordinator.ip), 5001, "VMWH0000001")
        if response == "OK":
            await self.coordinator.async_request_refresh()


class VmcHeltyPanelLedSwitch(VmcHeltyEntity, SwitchEntity):
    """VMC Helty panel LED switch."""

    def __init__(self, coordinator):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_panel_led"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Panel LED"
        self._attr_icon = "mdi:led-on"

    @property
    def is_on(self) -> bool:
        """Return True if panel LED is on."""
        if not self.coordinator.data:
            return False

        status = self.coordinator.data.get("status", "")
        if status and status.startswith("VMGO"):
            try:
                parts = status.split(",")
                return bool(
                    parts[PART_INDEX_PANEL_LED] == "00010"
                    if len(parts) > PART_INDEX_PANEL_LED
                    else False
                )
            except (ValueError, IndexError):
                return False
        return False

    async def async_turn_on(self, **_kwargs) -> None:
        """Turn on panel LED."""
        _LOGGER.debug(
            "Panel LED Switch: Sending turn_on command VMWH0100010 to %s",
            self.coordinator.ip,
        )
        response = await tcp_send_command(str(self.coordinator.ip), 5001, "VMWH0100010")
        _LOGGER.debug("Panel LED Switch: Turn_on response: %s", response)
        if response == "OK":
            _LOGGER.debug(
                "Panel LED Switch: Turn_on successful, requesting coordinator refresh"
            )
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Panel LED Switch: Turn_on failed, response: %s", response)

    async def async_turn_off(self, **_kwargs) -> None:
        """Turn off panel LED."""
        _LOGGER.debug(
            "Panel LED Switch: Sending turn_off command VMWH0100000 to %s",
            self.coordinator.ip,
        )
        response = await tcp_send_command(str(self.coordinator.ip), 5001, "VMWH0100000")
        _LOGGER.debug("Panel LED Switch: Turn_off response: %s", response)
        if response == "OK":
            _LOGGER.debug(
                "Panel LED Switch: Turn_off successful, requesting coordinator refresh"
            )
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Panel LED Switch: Turn_off failed, response: %s", response)


class VmcHeltySensorsSwitch(VmcHeltyEntity, SwitchEntity):
    """VMC Helty sensors activation switch."""

    def __init__(self, coordinator):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_sensors"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Sensors"
        self._attr_icon = "mdi:eye"

    @property
    def is_on(self) -> bool:
        """Return True if sensors are active."""
        if not self.coordinator.data:
            return True  # Default active

        status = self.coordinator.data.get("status", "")
        if status and status.startswith("VMGO"):
            try:
                parts = status.split(",")
                # Sensori attivi se il valore è 0, inattivi se 1
                return bool(
                    parts[PART_INDEX_SENSORS] == "00000"
                    if len(parts) > PART_INDEX_SENSORS
                    else True
                )
            except (ValueError, IndexError):
                return True
        return True

    async def async_turn_on(self, **_kwargs) -> None:
        """Turn on sensors."""
        response = await tcp_send_command(str(self.coordinator.ip), 5001, "VMWH0300000")
        if response == "OK":
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_kwargs) -> None:
        """Turn off sensors."""
        response = await tcp_send_command(str(self.coordinator.ip), 5001, "VMWH0300002")
        if response == "OK":
            await self.coordinator.async_request_refresh()
