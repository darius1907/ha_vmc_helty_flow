"""
Entità Light per livello luci VMC Helty Flow
"""
from homeassistant.components.light import LightEntity
from .const import DOMAIN, DEFAULT_PORT
from .helpers import tcp_send_command

class VmcHeltyLight(LightEntity):
    def __init__(self, ip, name):
        self._ip = ip
        self._name = name
        self._brightness = 0
        self._available = True

    @property
    def name(self):
        return f"{self._name} Luci"

    @property
    def brightness(self):
        return int(self._brightness * 2.55)  # Home Assistant usa 0-255

    @property
    def is_on(self):
        return self._brightness > 0

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
        brightness = kwargs.get("brightness", 255)
        level = round(brightness / 2.55)
        # Arrotonda a step di 25
        level = min(100, max(0, 25 * round(level / 25)))
        response = await tcp_send_command(self._ip, DEFAULT_PORT, f"VMWH02000{level:02d}")
        if response == "OK":
            self._brightness = level
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMWH0200000")
        if response == "OK":
            self._brightness = 0
            self.async_write_ha_state()

    async def async_update(self):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMGH?")
        if response and response.startswith("VMGO"):
            parts = response.split(",")
            try:
                self._brightness = int(parts[10])  # 11° campo: livello luci
                self._available = True
            except Exception:
                self._available = False
        else:
            self._available = False
