"""
Entità Number per timer luci VMC Helty Flow
"""
from homeassistant.components.number import NumberEntity
from .const import DOMAIN, DEFAULT_PORT
from .helpers import tcp_send_command

class VmcHeltyLightTimer(NumberEntity):
    def __init__(self, ip, name):
        self._ip = ip
        self._name = name
        self._timer = 0
        self._available = True

    @property
    def name(self):
        return f"{self._name} Timer Luci"

    @property
    def native_value(self):
        return self._timer

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

    @property
    def native_min_value(self):
        return 0

    @property
    def native_max_value(self):
        return 300

    @property
    def native_step(self):
        return 5

    async def async_set_native_value(self, value):
        value = int(value)
        value = min(300, max(0, value))
        response = await tcp_send_command(self._ip, DEFAULT_PORT, f"VMWH0300{value:03d}")
        if response == "OK":
            self._timer = value
            self.async_write_ha_state()

    async def async_update(self):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMGH?")
        if response and response.startswith("VMGO"):
            parts = response.split(",")
            try:
                self._timer = int(parts[14])  # 15° campo: timer luci
                self._available = True
            except Exception:
                self._available = False
        else:
            self._available = False
