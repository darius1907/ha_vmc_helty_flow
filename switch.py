"""
Entità Switch per modalità speciali VMC Helty Flow
"""
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN, DEFAULT_PORT
from .helpers import tcp_send_command

MODES = {
    "hyperventilation": {"cmd": "VMWH0000005", "fan_value": 6, "name": "Iperventilazione"},
    "night": {"cmd": "VMWH0000006", "fan_value": 5, "name": "Modalità Notte"},
    "free_cooling": {"cmd": "VMWH0000007", "fan_value": 7, "name": "Free Cooling"}
}

class VmcHeltyModeSwitch(SwitchEntity):
    def __init__(self, ip, name, mode_key):
        self._ip = ip
        self._name = name
        self._mode_key = mode_key
        self._is_on = False
        self._available = True

    @property
    def name(self):
        return f"{self._name} {MODES[self._mode_key]['name']}"

    @property
    def is_on(self):
        return self._is_on

    @property
    def available(self):
        return self._available

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._ip)},
            "name": self._name,
            "manufacturer": "Helty",
            "model": "VMC Flow",
            "sw_version": "1.0"
        }

    async def async_turn_on(self, **kwargs):
        cmd = MODES[self._mode_key]["cmd"]
        response = await tcp_send_command(self._ip, DEFAULT_PORT, cmd)
        if response == "OK":
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        # Disattivare la modalità speciale: imposto la ventola su manuale (es. livello 1)
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMWH0000001")
        if response == "OK":
            self._is_on = False
            self.async_write_ha_state()

    async def async_update(self):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMGH?")
        if response and response.startswith("VMGO"):
            parts = response.split(",")
            try:
                fan_value = int(parts[1])
                self._is_on = fan_value == MODES[self._mode_key]["fan_value"]
                self._available = True
            except Exception:
                self._available = False
        else:
            self._available = False

class VmcHeltyPanelLedSwitch(SwitchEntity):
    def __init__(self, ip, name):
        self._ip = ip
        self._name = name
        self._is_on = False
        self._available = True

    @property
    def name(self):
        return f"{self._name} LED Pannello"

    @property
    def is_on(self):
        return self._is_on

    @property
    def available(self):
        return self._available

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._ip)},
            "name": self._name,
            "manufacturer": "Helty",
            "model": "VMC Flow",
            "sw_version": "1.0"
        }

    async def async_turn_on(self, **kwargs):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMWH0100010")
        if response == "OK":
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMWH0100000")
        if response == "OK":
            self._is_on = False
            self.async_write_ha_state()

    async def async_update(self):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMGH?")
        if response and response.startswith("VMGO"):
            parts = response.split(",")
            try:
                self._is_on = int(parts[1]) == 1  # 2° campo: LED pannello
                self._available = True
            except Exception:
                self._available = False
        else:
            self._available = False
