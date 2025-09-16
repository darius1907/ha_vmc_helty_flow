"""Device registry utilities for VMC Helty Flow integration."""

import logging
import re
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, MAX_UNIQUE_ID_LENGTH, MIN_UNIQUE_ID_LENGTH
from .helpers import tcp_send_command

_LOGGER = logging.getLogger(__name__)


async def async_get_or_create_device(
    hass: HomeAssistant, coordinator: DataUpdateCoordinator
) -> DeviceEntry:
    """Get o crea un device entry nel device registry."""
    device_registry_instance = device_registry.async_get(hass)

    # Recupera l'indirizzo IP dal coordinatore
    ip_address = coordinator.ip

    # Cerca di ottenere l'indirizzo MAC o un identificatore univoco
    unique_id = await async_get_device_unique_id(hass, ip_address)

    # Se non è disponibile un identificatore univoco, usa l'IP
    # (non è l'ideale, ma è meglio di niente)
    if not unique_id:
        unique_id = f"helty_flow_{ip_address.replace('.', '_')}"

    # Ottieni informazioni aggiuntive sul dispositivo
    device_info = await async_get_device_info(hass, ip_address)

    # Crea o aggiorna il device nel registry
    return device_registry_instance.async_get_or_create(
        config_entry_id=coordinator.config_entry.entry_id,
        # Usa sia MAC/identificatore univoco che IP come identificatori
        identifiers={(DOMAIN, unique_id), (DOMAIN, ip_address)},
        # Usa l'IP come connessione
        connections={("ip", ip_address)},
        name=device_info.get("name", coordinator.name),
        manufacturer="Helty",
        model=device_info.get("model", "Flow"),
        sw_version=device_info.get("sw_version"),
        hw_version=device_info.get("hw_version"),
        suggested_area=device_info.get("suggested_area"),
        configuration_url=f"http://{ip_address}:5001",
    )


async def async_get_device_unique_id(
    hass: HomeAssistant, ip_address: str
) -> str | None:
    """Ottieni un identificatore univoco per il dispositivo."""
    try:
        # Cerca di ottenere un identificatore dal dispositivo tramite protocollo
        network_info = await tcp_send_command(ip_address, 5001, "VMSL?")

        if network_info and network_info.startswith("VMSL"):
            # Prova a estrarre MAC address, serial number o altro identificatore stabile
            parts = network_info.split(",")

            # Il formato esatto dipende dal protocollo del dispositivo
            # Qui assumiamo che ci sia un MAC o un ID univoco in uno dei campi
            for part in parts:
                # Cerca un pattern che sembra un MAC address
                mac_match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", part)
                if mac_match:
                    return mac_match.group(0).replace(":", "").replace("-", "").lower()

                # Cerca un pattern che sembra un serial number
                sn_match = re.search(r"S[:/]?N[:=]?\s*([A-Za-z0-9-]+)", part)
                if sn_match:
                    return sn_match.group(1)

            # Se trovato un campo che sembra un ID univoco
            for i, part in enumerate(parts):
                if MIN_UNIQUE_ID_LENGTH <= len(
                    part
                ) <= MAX_UNIQUE_ID_LENGTH and re.match(r"^[A-Za-z0-9_-]+$", part):
                    return f"helty_{part.lower()}"

        # In alternativa, prova a ottenere il nome dispositivo come parte dell'ID
        device_name = await tcp_send_command(ip_address, 5001, "VMNM?")
        if device_name and device_name.startswith("VMNM"):
            parts = device_name.split(",")
            if len(parts) > 1 and parts[1]:
                # Normalizza il nome per l'uso come ID
                normalized_name = re.sub(r"[^a-z0-9_]", "_", parts[1].lower())
                return f"helty_{normalized_name}_{ip_address.replace('.', '_')}"
    except Exception as err:
        _LOGGER.error("Failed to get unique ID for device %s: %s", ip_address, err)
        return None
    else:
        return None


async def async_get_device_info(hass: HomeAssistant, ip_address: str) -> dict[str, Any]:
    """Ottieni informazioni dettagliate sul dispositivo."""
    device_info = {
        "model": "Flow",
        "manufacturer": "Helty",
    }

    try:
        # Ottieni nome dispositivo
        name_response = await tcp_send_command(ip_address, 5001, "VMNM?")
        if name_response and name_response.startswith("VMNM"):
            parts = name_response.split(",")
            if len(parts) > 1:
                device_info["name"] = parts[1].strip() or f"Helty Flow ({ip_address})"

        # Cerca di ottenere la versione firmware se disponibile
        version_cmd = "VMCV?"  # Comando ipotetico per la versione, da adattare
        version_response = await tcp_send_command(ip_address, 5001, version_cmd)
        if version_response and not version_response.startswith("ERROR"):
            # Estrai la versione dalla risposta se disponibile
            version_match = re.search(r"(\d+\.\d+\.\d+)", version_response)
            if version_match:
                device_info["sw_version"] = version_match.group(1)

        # Determina l'area suggerita in base al nome o altri attributi
        if "name" in device_info:
            name_lower = device_info["name"].lower()
            if any(room in name_lower for room in ["sala", "living", "soggiorno"]):
                device_info["suggested_area"] = "Soggiorno"
            elif any(room in name_lower for room in ["camera", "letto", "bedroom"]):
                device_info["suggested_area"] = "Camera da letto"
            elif any(room in name_lower for room in ["cucina", "kitchen"]):
                device_info["suggested_area"] = "Cucina"
            # Aggiungi altre stanze se necessario
    except Exception as err:
        _LOGGER.error("Error retrieving device info for %s: %s", ip_address, err)

    return device_info


async def async_remove_orphaned_devices(hass: HomeAssistant) -> None:
    """Rimuovi i dispositivi orfani quando l'integrazione viene rimossa."""
    device_registry_instance = device_registry.async_get(hass)
    entity_registry_instance = entity_registry.async_get(hass)

    # Trova tutti i dispositivi associati al dominio
    domain_devices = [
        entry
        for entry in device_registry_instance.devices.values()
        if any(ident[0] == DOMAIN for ident in entry.identifiers)
    ]

    # Ottieni tutti gli entry_id attivi
    config_entries = hass.config_entries.async_entries(DOMAIN)
    active_entry_ids = [entry.entry_id for entry in config_entries]

    # Rimuovi i dispositivi che non sono più associati a entry attivi
    for device in domain_devices:
        if not any(entry_id in active_entry_ids for entry_id in device.config_entries):
            _LOGGER.debug("Removing orphaned device: %s", device.name)
            device_registry_instance.async_remove_device(device.id)
