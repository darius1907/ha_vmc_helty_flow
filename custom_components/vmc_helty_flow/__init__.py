"""Integrazione VMC Helty Flow per Home Assistant."""

import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry

from .const import (
    DEFAULT_PORT,
    DOMAIN,
    NETWORK_INFO_UPDATE_INTERVAL,
    SENSORS_UPDATE_INTERVAL,
)
from .coordinator import VmcHeltyCoordinator
from .device_action import async_setup_device_actions
from .device_registry import async_get_or_create_device, async_remove_orphaned_devices
from .helpers import (
    tcp_send_command,
    validate_network_connectivity,
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# Definisce le platform supportate dall'integrazione
PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.LIGHT,
    Platform.BUTTON,
]

# Intervalli di aggiornamento per diversi tipi di dati
DEFAULT_SCAN_INTERVAL = timedelta(seconds=SENSORS_UPDATE_INTERVAL)
NETWORK_INFO_INTERVAL = timedelta(seconds=NETWORK_INFO_UPDATE_INTERVAL)
DEVICE_NAME_INTERVAL = timedelta(seconds=NETWORK_INFO_UPDATE_INTERVAL)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Setup services for the integration."""
    # Service schema for room volume update
    update_room_volume_schema = vol.Schema(
        {
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("room_volume"): vol.All(
                vol.Coerce(float), vol.Range(min=1.0, max=1000.0)
            ),
        }
    )

    # Service schema for network diagnostics
    network_diagnostics_schema = vol.Schema(
        {
            vol.Required("ip"): cv.string,
            vol.Optional("port", default=DEFAULT_PORT): cv.port,
        }
    )

    # Service schema for set special mode
    set_special_mode_schema = vol.Schema(
        {
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("mode"): vol.In(
                ["hyperventilation", "night_mode", "free_cooling"]
            ),
        }
    )

    async def handle_update_room_volume(call: ServiceCall) -> None:
        """Handle room volume update service call."""
        entity_id = call.data["entity_id"]
        new_volume = float(call.data["room_volume"])

        # Trova la config entry associata all'entità
        entity_registry_instance = entity_registry.async_get(hass)
        entity_entry = entity_registry_instance.async_get(entity_id)

        if not entity_entry:
            raise HomeAssistantError(f"Entity {entity_id} not found")

        config_entry = hass.config_entries.async_get_entry(entity_entry.config_entry_id)
        if not config_entry or config_entry.domain != DOMAIN:
            raise HomeAssistantError(
                f"Entity {entity_id} is not from VMC Helty Flow integration"
            )

        # Aggiorna i dati della config entry
        new_data = {**config_entry.data, "room_volume": new_volume}
        hass.config_entries.async_update_entry(config_entry, data=new_data)

        _LOGGER.info(
            "Updated room volume for %s to %.1f m³",
            config_entry.data.get("name", config_entry.data.get("ip")),
            new_volume,
        )

    async def handle_network_diagnostics(
        call: ServiceCall,
    ) -> dict[str, str | bool | int | None]:
        """Handle network diagnostics service call."""
        ip = call.data["ip"]
        port = call.data["port"]

        _LOGGER.info("Running network diagnostics for %s:%s", ip, port)

        try:
            diagnostics = await validate_network_connectivity(ip, port)
        except Exception as err:
            _LOGGER.exception("Failed to run network diagnostics for %s:%s", ip, port)
            raise HomeAssistantError(f"Network diagnostics failed: {err}") from err
        else:
            # Log the results
            _LOGGER.info(
                "Network diagnostics for %s:%s - Ping: %s, TCP: %s, Reachable: %s",
                ip,
                port,
                diagnostics.get("ping_success"),
                diagnostics.get("tcp_connection"),
                diagnostics.get("reachable"),
            )

            if diagnostics.get("error_details"):
                _LOGGER.warning(
                    "Network diagnostics errors for %s:%s - %s",
                    ip,
                    port,
                    diagnostics.get("error_details"),
                )

            return diagnostics

    async def handle_set_special_mode(call: ServiceCall) -> None:
        """Handle set special mode service call."""
        entity_id = call.data["entity_id"]
        mode = call.data["mode"]

        # Trova l'entità
        entity_registry_instance = entity_registry.async_get(hass)
        entity_entry = entity_registry_instance.async_get(entity_id)

        if not entity_entry:
            raise HomeAssistantError(f"Entity {entity_id} not found")

        config_entry = hass.config_entries.async_get_entry(entity_entry.config_entry_id)
        if not config_entry or config_entry.domain != DOMAIN:
            raise HomeAssistantError(
                f"Entity {entity_id} is not from VMC Helty Flow integration"
            )

        # Ottieni il coordinatore
        coordinator = hass.data[DOMAIN].get(config_entry.entry_id)
        if not coordinator:
            raise HomeAssistantError(f"Coordinator not found for entity {entity_id}")

        # Mapping mode to speed values come da protocollo VMC
        mode_mapping = {
            "night_mode": 5,  # 125% -> comando VMWH0000005
            "hyperventilation": 6,  # 150% -> comando VMWH0000006
            "free_cooling": 7,  # 175% -> comando VMWH0000007
        }

        if mode not in mode_mapping:
            raise HomeAssistantError(f"Invalid mode: {mode}")

        speed = mode_mapping[mode]

        try:
            # Use tcp_send_command directly
            command = f"VMWH{speed:07d}"
            result = await tcp_send_command(coordinator.ip, DEFAULT_PORT, command)

            _LOGGER.info(
                "Set special mode %s (speed %d) for %s: %s",
                mode,
                speed,
                entity_id,
                result,
            )

            # Aggiorna i dati del coordinatore
            await coordinator.async_request_refresh()

        except Exception as err:
            _LOGGER.exception(
                "Failed to set special mode %s for %s: %s", mode, entity_id, err
            )
            raise HomeAssistantError(
                f"Failed to set special mode {mode}: {err}"
            ) from err

    # Register services
    hass.services.async_register(
        DOMAIN,
        "update_room_volume",
        handle_update_room_volume,
        schema=update_room_volume_schema,
    )

    hass.services.async_register(
        DOMAIN,
        "network_diagnostics",
        handle_network_diagnostics,
        schema=network_diagnostics_schema,
        supports_response="only",
    )

    hass.services.async_register(
        DOMAIN,
        "set_special_mode",
        handle_set_special_mode,
        schema=set_special_mode_schema,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up VMC Helty Flow from a config entry."""
    # Inizializza il dominio se non esiste
    hass.data.setdefault(DOMAIN, {})

    # Setup delle device actions (solo una volta per l'integrazione)
    if not hass.data[DOMAIN].get("device_actions_setup"):
        await async_setup_device_actions(hass)
        hass.data[DOMAIN]["device_actions_setup"] = True

    # Setup del servizio per aggiornare il volume (solo una volta)
    if not hass.data[DOMAIN].get("services_setup"):
        await async_setup_services(hass)
        hass.data[DOMAIN]["services_setup"] = True

    # Crea il coordinatore per questo dispositivo
    coordinator = VmcHeltyCoordinator(hass, entry)

    # Effettua il primo fetch dei dati
    await coordinator.async_config_entry_first_refresh()

    # Registra il dispositivo nel device registry
    coordinator.device_entry = await async_get_or_create_device(hass, coordinator)

    # Aggiunge device_id per i sensori
    coordinator.device_id = (
        coordinator.device_entry.id if coordinator.device_entry else None
    )

    # Salva il coordinatore
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Avvia le piattaforme
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Registra la funzione di aggiornamento opzioni se non già registrata
    if not entry.update_listeners:
        entry.add_update_listener(async_reload_entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove the data stored for this entry
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_remove_config_entry_device(
    _hass: HomeAssistant, config_entry: ConfigEntry, device_entry
) -> bool:
    """Remove a config entry from a device."""
    # Questo metodo viene chiamato quando un dispositivo viene rimosso
    # dall'interfaccia utente
    _LOGGER.info(
        "Removing device %s from config entry %s",
        device_entry.id,
        config_entry.entry_id,
    )

    # Consenti sempre la rimozione del dispositivo
    return True


async def async_remove_entry(hass: HomeAssistant, _entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    # Rimuovi dispositivi orfani dopo la rimozione dell'entry
    await async_remove_orphaned_devices(hass)
