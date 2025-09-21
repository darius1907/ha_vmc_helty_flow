"""Diagnostics support for VMC Helty Flow integration."""

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DIAG_LIGHTS_LEVEL_INDEX,
    DIAG_LIGHTS_TIMER_INDEX,
    DIAG_PANEL_LED_INDEX,
    DIAG_SENSORS_INDEX,
    DOMAIN,
)

# Campi sensibili da oscurare nei diagnostics
TO_REDACT = {
    "password",
    "network_password",
    "wifi_password",
    "ssid",
    "network_ssid",
    "wifi_ssid",
    "host",
    "ip",
    "mac",
    "serial_number",
    "unique_id",
    "username",
    "credentials",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Raccoglie i dati diagnostici
    diagnostics_data = {
        "config_entry": {
            "title": config_entry.title,
            "domain": config_entry.domain,
            "version": config_entry.version,
            "data": async_redact_data(config_entry.data, TO_REDACT),
            "options": async_redact_data(config_entry.options, TO_REDACT),
            "source": config_entry.source,
            # Il unique_id è considerato sensibile quindi oscurato
            "unique_id": config_entry.unique_id and "**REDACTED**",
        },
        "coordinator": {
            "ip": async_redact_data({"ip": coordinator.ip}, TO_REDACT)["ip"],
            "name": coordinator.name,
            "last_update_success": coordinator.last_update_success,
            "last_update": coordinator.last_update,
            "update_interval": coordinator.update_interval.total_seconds(),
            "data": async_redact_data(coordinator.data or {}, TO_REDACT),
        },
        "device_info": {
            "available": coordinator.last_update_success,
            "model": config_entry.data.get("model", "Unknown"),
            "manufacturer": config_entry.data.get("manufacturer", "Helty"),
        },
    }

    # Aggiunge statistiche aggiuntive se disponibili
    if coordinator.data:
        try:
            status = coordinator.data.get("status", "")
            if status and status.startswith("VMGO"):
                parts = status.split(",")
                diagnostics_data["device_status"] = {
                    "fan_speed_raw": parts[1] if len(parts) > 1 else "unknown",
                    "panel_led_raw": (
                        parts[DIAG_PANEL_LED_INDEX]
                        if len(parts) > DIAG_PANEL_LED_INDEX
                        else "unknown"
                    ),
                    "sensors_raw": (
                        parts[DIAG_SENSORS_INDEX]
                        if len(parts) > DIAG_SENSORS_INDEX
                        else "unknown"
                    ),
                    "lights_level_raw": (
                        parts[DIAG_LIGHTS_LEVEL_INDEX]
                        if len(parts) > DIAG_LIGHTS_LEVEL_INDEX
                        else "unknown"
                    ),
                    "lights_timer_raw": (
                        parts[DIAG_LIGHTS_TIMER_INDEX]
                        if len(parts) > DIAG_LIGHTS_TIMER_INDEX
                        else "unknown"
                    ),
                    "response_parts_count": len(parts),
                    # Non includere la risposta completa nei diagnostici,
                    # solo i valori rilevanti
                    "full_response": "**REDACTED**",
                }
        except Exception:
            diagnostics_data["device_status"] = {"parsing_error": True}

    return diagnostics_data


async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry, _device
) -> dict:
    """Return diagnostics for a device entry."""
    return await async_get_config_entry_diagnostics(hass, config_entry)
