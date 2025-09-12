"""
Entità sensori per VMC Helty Flow
"""
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.components.text import TextEntity
from .const import DOMAIN, DEFAULT_PORT
from .helpers import tcp_send_command

class VmcHeltySensor(SensorEntity):
    def __init__(self, ip, name, sensor_type):
        self._ip = ip
        self._name = name
        self._sensor_type = sensor_type
        self._state = None
        self._available = True

    @property
    def name(self):
        return f"{self._name} {self._sensor_type}"

    @property
    def native_value(self):
        return self._state

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

    async def async_update(self):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMGI?")
        if response and response.startswith("VMGI"):
            parts = response.split()
            try:
                if self._sensor_type == "Temperatura Interna":
                    self._state = float(parts[1]) / 10
                elif self._sensor_type == "Temperatura Esterna":
                    self._state = float(parts[2]) / 10
                elif self._sensor_type == "Umidità":
                    self._state = int(parts[3])
                elif self._sensor_type == "CO2":
                    self._state = int(parts[4])
                elif self._sensor_type == "VOC":
                    self._state = int(parts[5])
                self._available = True
            except Exception:
                self._available = False
        else:
            self._available = False

class VmcHeltyOnOffSensor(BinarySensorEntity):
    def __init__(self, ip, name):
        self._ip = ip
        self._name = name
        self._is_on = None
        self._available = True

    @property
    def name(self):
        return f"{self._name} On/Off"

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

    async def async_update(self):
        response = await tcp_send_command(self._ip, DEFAULT_PORT, "VMST?")
        if response and response.startswith("VMST"):
            self._is_on = response.split()[1] == "ON"
            self._available = True
        else:
            self._available = False

class VmcHeltyResetFilterButton(ButtonEntity):
    def __init__(self, ip, name):
        self._ip = ip
        self._name = name

    @property
    def name(self):
        return f"{self._name} Reset Filtro"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._ip)},
            "name": self._name,
            "manufacturer": "Helty",
            "model": "VMC Flow",
            "sw_version": "1.0"
        }

    async def async_press(self):
        await tcp_send_command(self._ip, DEFAULT_PORT, "VMRF")

class VmcHeltyNameText(TextEntity):
    def __init__(self, ip, name):
        self._ip = ip
        self._name = name
        self._value = name

    @property
    def name(self):
        return f"{self._name} Impostazione Nome"

    @property
    def value(self):
        return self._value

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._ip)},
            "name": self._name,
            "manufacturer": "Helty",
            "model": "VMC Flow",
            "sw_version": "1.0"
        }

    async def async_set_value(self, value: str):
        await tcp_send_command(self._ip, DEFAULT_PORT, f"VMNM {value}")
        self._value = value
