"""
Entità Fan per VMC Helty Flow
"""
from homeassistant.components.fan import FanEntity
from .const import DOMAIN, DEFAULT_PORT
from .helpers import tcp_send_command

class VmcHeltyFan(FanEntity):
    def __init__(self, ip, name):
        self._ip = ip
        self._name = name
        self._speed = 0
        self._available = True
        self._night_mode = False
        self._hyperventilation = False
        self._free_cooling = False

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._speed > 0

    @property
    def available(self):
        return self._available

    @property
    def percentage(self):
        return int(self._speed * 25)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._ip)},
            "name": self._name,
            "manufacturer": "Helty",
            "model": "VMC Flow",
            "sw_version": "1.0"
        }

    async def async_set_percentage(self, percentage):
        speed = round(percentage / 25)
        response = await tcp_send_command(self._ip, DEFAULT_PORT, f"VMWH000000{speed}")
        if response == "OK":
            self._speed = speed
            self.async_write_ha_state()

    async def async_update(self):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMGH?")
        if response and response.startswith("VMGO"):
            parts = response.split(",")
            try:
                speed_raw = int(parts[1])
                # Gestione modalità speciali
                if speed_raw == 5:
                    self._speed = 1
                    self._night_mode = True
                    self._hyperventilation = False
                    self._free_cooling = False
                elif speed_raw == 6:
                    self._speed = 4
                    self._night_mode = False
                    self._hyperventilation = True
                    self._free_cooling = False
                elif speed_raw == 7:
                    self._speed = 0
                    self._night_mode = False
                    self._hyperventilation = False
                    self._free_cooling = True
                else:
                    self._speed = speed_raw
                    self._night_mode = False
                    self._hyperventilation = False
                    self._free_cooling = False
                self._available = True
            except Exception:
                self._available = False
        else:
            self._available = False

    @property
    def extra_state_attributes(self):
        return {
            "night_mode": getattr(self, "_night_mode", False),
            "hyperventilation": getattr(self, "_hyperventilation", False),
            "free_cooling": getattr(self, "_free_cooling", False)
        }
