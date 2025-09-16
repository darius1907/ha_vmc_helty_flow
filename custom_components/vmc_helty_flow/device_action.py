"""Device actions for VMC Helty Flow integration."""

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .const import (
    DOMAIN,
    FAN_SPEED_OFF,
    FAN_SPEED_MAX_NORMAL,
    MAX_DEVICE_NAME_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_SSID_LENGTH,
    MIN_PASSWORD_LENGTH,
)
from .helpers import tcp_send_command

# Schema di validazione per le azioni del dispositivo
DEVICE_ACTION_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): str,
        vol.Required("action"): str,
        vol.Optional("parameters", default={}): dict,
    }
)


async def async_setup_device_actions(hass: HomeAssistant) -> None:
    """Set up device actions for VMC Helty devices."""

    async def handle_device_action(call: ServiceCall) -> None:
        """Handle device action service call."""
        device_id = call.data["device_id"]
        action = call.data["action"]
        parameters = call.data.get("parameters", {})

        # Trova il dispositivo nel registry
        device_registry = dr.async_get(hass)
        device = device_registry.async_get(device_id)

        if not device:
            raise HomeAssistantError(f"Device {device_id} not found")

        # Trova l'IP del dispositivo dalle identifiers
        ip = None
        for identifier in device.identifiers:
            if identifier[0] == DOMAIN:
                ip = identifier[1]
                break

        if not ip:
            raise HomeAssistantError(f"Cannot find IP for device {device_id}")

        # Esegue l'azione richiesta
        await _execute_device_action(ip, action, parameters)

    # Registra il servizio per le azioni del dispositivo
    hass.services.async_register(
        DOMAIN,
        "device_action",
        handle_device_action,
        schema=DEVICE_ACTION_SCHEMA,
    )


async def _execute_device_action(ip: str, action: str, parameters: dict) -> None:
    """Execute a device action."""
    actions = {
        "set_fan_speed": _set_fan_speed,
        "set_hyperventilation": _set_hyperventilation,
        "set_night_mode": _set_night_mode,
        "set_free_cooling": _set_free_cooling,
        "set_panel_led": _set_panel_led,
        "set_sensors": _set_sensors,
        "reset_filter": _reset_filter,
        "set_device_name": _set_device_name,
        "set_network_config": _set_network_config,
    }

    if action not in actions:
        raise HomeAssistantError(f"Unknown action: {action}")

    await actions[action](ip, parameters)


async def _set_fan_speed(ip: str, parameters: dict) -> None:
    """Set fan speed (0-4)."""
    speed = parameters.get("speed", 1)
    if not FAN_SPEED_OFF <= speed <= FAN_SPEED_MAX_NORMAL:
        raise HomeAssistantError("Speed must be between 0 and 4")

    response = await tcp_send_command(ip, 5001, f"VMWH000000{speed}")
    if response != "OK":
        raise HomeAssistantError(f"Failed to set fan speed: {response}")


async def _set_hyperventilation(ip: str, parameters: dict) -> None:
    """Set hyperventilation mode."""
    enable = parameters.get("enable", True)
    command = "VMWH0000005" if enable else "VMWH0000001"  # Enable or set to speed 1

    response = await tcp_send_command(ip, 5001, command)
    if response != "OK":
        raise HomeAssistantError(f"Failed to set hyperventilation: {response}")


async def _set_night_mode(ip: str, parameters: dict) -> None:
    """Set night mode."""
    enable = parameters.get("enable", True)
    command = "VMWH0000006" if enable else "VMWH0000001"  # Enable or set to speed 1

    response = await tcp_send_command(ip, 5001, command)
    if response != "OK":
        raise HomeAssistantError(f"Failed to set night mode: {response}")


async def _set_free_cooling(ip: str, parameters: dict) -> None:
    """Set free cooling mode."""
    enable = parameters.get("enable", True)
    command = "VMWH0000007" if enable else "VMWH0000001"  # Enable or set to speed 1

    response = await tcp_send_command(ip, 5001, command)
    if response != "OK":
        raise HomeAssistantError(f"Failed to set free cooling: {response}")


async def _set_panel_led(ip: str, parameters: dict) -> None:
    """Set panel LED state."""
    enable = parameters.get("enable", True)
    command = "VMWH0100010" if enable else "VMWH0100000"

    response = await tcp_send_command(ip, 5001, command)
    if response != "OK":
        raise HomeAssistantError(f"Failed to set panel LED: {response}")


async def _set_sensors(ip: str, parameters: dict) -> None:
    """Set sensors state."""
    enable = parameters.get("enable", True)
    command = "VMWH0300000" if enable else "VMWH0300002"

    response = await tcp_send_command(ip, 5001, command)
    if response != "OK":
        raise HomeAssistantError(f"Failed to set sensors: {response}")


async def _reset_filter(ip: str, _parameters: dict) -> None:
    """Reset filter counter."""
    response = await tcp_send_command(ip, 5001, "VMWH0417744")
    if response != "OK":
        raise HomeAssistantError(f"Failed to reset filter: {response}")


async def _set_device_name(ip: str, parameters: dict) -> None:
    """Set device name."""
    name = parameters.get("name", "")
    if not name or len(name) > MAX_DEVICE_NAME_LENGTH:
        raise HomeAssistantError("Name must be between 1 and 32 characters")

    # Rimuove caratteri non ASCII e spazi
    safe_name = "".join(c for c in name if c.isalnum() or c == "_")

    response = await tcp_send_command(ip, 5001, f"VMNM {safe_name}")
    if response != "OK":
        raise HomeAssistantError(f"Failed to set device name: {response}")


async def _set_network_config(ip: str, parameters: dict) -> None:
    """Set network configuration (SSID and password)."""
    ssid = parameters.get("ssid", "")
    password = parameters.get("password", "")

    if not ssid or len(ssid) > MAX_SSID_LENGTH:
        raise HomeAssistantError("SSID must be between 1 and 32 characters")

    if not password or len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        raise HomeAssistantError("Password must be between 8 and 32 characters")

    # Formatta il comando con padding
    ssid_padded = ssid.ljust(32, "*")
    password_padded = password.ljust(32, "*")

    response = await tcp_send_command(ip, 5001, f"VMSL {ssid_padded}{password_padded}")
    if response != "OK":
        raise HomeAssistantError(f"Failed to set network config: {response}")


# Azioni disponibili per ogni dispositivo VMC
DEVICE_ACTIONS = {
    "set_fan_speed": {
        "name": "Set Fan Speed",
        "parameters": {
            "speed": {"type": "integer", "min": FAN_SPEED_OFF, "max": FAN_SPEED_MAX_NORMAL, "required": True}
        },
    },
    "set_hyperventilation": {
        "name": "Set Hyperventilation Mode",
        "parameters": {"enable": {"type": "boolean", "required": True}},
    },
    "set_night_mode": {
        "name": "Set Night Mode",
        "parameters": {"enable": {"type": "boolean", "required": True}},
    },
    "set_free_cooling": {
        "name": "Set Free Cooling Mode",
        "parameters": {"enable": {"type": "boolean", "required": True}},
    },
    "set_panel_led": {
        "name": "Set Panel LED",
        "parameters": {"enable": {"type": "boolean", "required": True}},
    },
    "set_sensors": {
        "name": "Set Sensors State",
        "parameters": {"enable": {"type": "boolean", "required": True}},
    },
    "reset_filter": {"name": "Reset Filter Counter", "parameters": {}},
    "set_device_name": {
        "name": "Set Device Name",
        "parameters": {"name": {"type": "string", "max_length": 32, "required": True}},
    },
    "set_network_config": {
        "name": "Set Network Configuration",
        "parameters": {
            "ssid": {"type": "string", "max_length": 32, "required": True},
            "password": {
                "type": "string",
                "min_length": 8,
                "max_length": 32,
                "required": True,
            },
        },
    },
}
