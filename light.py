from homeassistant.components.light import LightEntity
from .const import DOMAIN, DEFAULT_PORT
from .helpers import tcp_send_command

class VmcHeltyLight(LightEntity):
    def __init__(self, ip, name):
        self._ip = ip
        self._name = name
        self._is_on = False
        self._available = True

    @property
    def name(self):
        return f"{self._name} Luce"

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
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMLT1")
        if response == "OK":
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMLT0")
        if response == "OK":
            self._is_on = False
            self.async_write_ha_state()

    async def async_update(self):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMLT?")
        if response and response.startswith("VMLT"):
            self._is_on = response.split()[1] == "1"
            self._available = True
        else:
            self._available = False
