"""Entità sensori per VMC Helty Flow."""

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.button import ButtonEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MIN_RESPONSE_PARTS
from .device_info import VmcHeltyEntity
from .helpers import parse_vmsl_response, tcp_send_command


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VMC Helty sensors from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        # Sensori ambientali
        VmcHeltySensor(
            coordinator,
            "temperature_internal",
            "Temperatura Interna",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        VmcHeltySensor(
            coordinator,
            "temperature_external",
            "Temperatura Esterna",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        VmcHeltySensor(
            coordinator,
            "humidity",
            "Umidità",
            PERCENTAGE,
            SensorDeviceClass.HUMIDITY,
            SensorStateClass.MEASUREMENT,
        ),
        VmcHeltySensor(
            coordinator,
            "co2",
            "CO2",
            CONCENTRATION_PARTS_PER_MILLION,
            SensorDeviceClass.CO2,
            SensorStateClass.MEASUREMENT,
        ),
        VmcHeltySensor(
            coordinator,
            "voc",
            "VOC",
            "ppb",
            None,
            SensorStateClass.MEASUREMENT,
        ),
        # Sensori di stato
        VmcHeltyOnOffSensor(coordinator),
        VmcHeltyLastResponseSensor(coordinator),
        VmcHeltyFilterHoursSensor(coordinator),
        # Sensori di rete
        VmcHeltyIPAddressSensor(coordinator),
        VmcHeltyNetworkSSIDSensor(coordinator),
        VmcHeltyNetworkPasswordSensor(coordinator),
        # Pulsanti e controlli di testo
        VmcHeltyResetFilterButton(coordinator),
        VmcHeltyNameText(coordinator),
        VmcHeltySSIDText(coordinator),
        VmcHeltyPasswordText(coordinator),
    ]

    async_add_entities(entities)


class VmcHeltySensor(VmcHeltyEntity, SensorEntity):
    """VMC Helty environmental sensor."""

    def __init__(
        self,
        coordinator,
        sensor_key,
        sensor_name,
        unit,
        device_class=None,
        state_class=None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_unique_id = f"{coordinator.ip}_{sensor_key}"
        self._attr_name = f"{coordinator.name} {sensor_name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self) -> Any | None:
        """Return the sensor value."""
        if not self.coordinator.data:
            return None

        sensors_data = self.coordinator.data.get("sensors", "")
        if not sensors_data or not sensors_data.startswith("VMGI"):
            return None

        try:
            parts = sensors_data.split(",")
            if len(parts) < MIN_RESPONSE_PARTS:
                return None

            # Mapping dei sensori con logica unificata
            sensor_mapping = {
                "temperature_internal": (1, lambda x: float(x) / 10),
                "temperature_external": (2, lambda x: float(x) / 10),
                "humidity": (3, lambda x: float(x) / 10),
                "co2": (4, lambda x: int(x)),
                "voc": (14, lambda x: int(x)),
            }

            if self._sensor_key in sensor_mapping:
                index, converter = sensor_mapping[self._sensor_key]
                if parts[index]:
                    return converter(parts[index])

        except (ValueError, IndexError):
            pass

        return None


class VmcHeltyOnOffSensor(VmcHeltyEntity, BinarySensorEntity):
    """VMC Helty device online/offline sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_online"
        self._attr_name = f"{coordinator.name} Online"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool:
        """Return True if device is online."""
        return self.coordinator.data and self.coordinator.data.get("available", False)


class VmcHeltyLastResponseSensor(VmcHeltyEntity, SensorEntity):
    """VMC Helty last response timestamp sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_last_response"
        self._attr_name = f"{coordinator.name} Last Response"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> float | None:
        """Return last update time."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("last_update")


class VmcHeltyFilterHoursSensor(VmcHeltyEntity, SensorEntity):
    """VMC Helty filter hours sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_filter_hours"
        self._attr_name = f"{coordinator.name} Filter Hours"
        self._attr_native_unit_of_measurement = UnitOfTime.HOURS
        self._attr_icon = "mdi:air-filter"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> int | None:
        """Return filter hours from device status."""
        if not self.coordinator.data:
            return None

        # Il contatore filtro potrebbe essere nei dati di stato - da implementare
        # Per ora restituisce un valore placeholder
        return 0


class VmcHeltyIPAddressSensor(VmcHeltyEntity, SensorEntity):
    """VMC Helty IP address sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_ip_address"
        self._attr_name = f"{coordinator.name} IP Address"
        self._attr_icon = "mdi:ip-network"

    @property
    def native_value(self) -> str:
        """Return device IP address."""
        return self.coordinator.ip


class VmcHeltyNetworkSSIDSensor(VmcHeltyEntity, SensorEntity):
    """VMC Helty network SSID sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_network_ssid"
        self._attr_name = f"{coordinator.name} Network SSID"
        self._attr_icon = "mdi:wifi"

    @property
    def native_value(self) -> str | None:
        """Return network SSID."""
        if not self.coordinator.data:
            return None

        network_data = self.coordinator.data.get("network", "")
        if network_data:
            ssid, _ = parse_vmsl_response(network_data)
            return ssid
        return None


class VmcHeltyNetworkPasswordSensor(VmcHeltyEntity, SensorEntity):
    """VMC Helty network password sensor (masked)."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_network_password"
        self._attr_name = f"{coordinator.name} Network Password"
        self._attr_icon = "mdi:lock"

    @property
    def native_value(self) -> str | None:
        """Return masked network password."""
        if not self.coordinator.data:
            return None

        network_data = self.coordinator.data.get("network", "")
        if network_data:
            _, password = parse_vmsl_response(network_data)
            return "*" * len(password) if password else None
        return None


class VmcHeltyResetFilterButton(VmcHeltyEntity, ButtonEntity):
    """VMC Helty reset filter button."""

    def __init__(self, coordinator):
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_reset_filter"
        self._attr_name = f"{coordinator.name} Reset Filter"
        self._attr_icon = "mdi:air-filter"

    async def async_press(self) -> None:
        """Reset filter counter."""
        response = await tcp_send_command(self.coordinator.ip, 5001, "VMWH0417744")
        if response == "OK":
            await self.coordinator.async_request_refresh()


class VmcHeltyNameText(VmcHeltyEntity, TextEntity):
    """VMC Helty device name text entity."""

    def __init__(self, coordinator):
        """Initialize the text entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_device_name"
        self._attr_name = f"{coordinator.name} Device Name"
        self._attr_icon = "mdi:rename-box"

    @property
    def native_value(self) -> str | None:
        """Return current device name."""
        if not self.coordinator.data:
            return None

        name_data = self.coordinator.data.get("name", "")
        if name_data and name_data.startswith("VMNM"):
            return name_data[4:].strip()
        return self.coordinator.name

    async def async_set_value(self, value: str) -> None:
        """Set new device name."""
        response = await tcp_send_command(self.coordinator.ip, 5001, f"VMNM {value}")
        if response == "OK":
            await self.coordinator.async_request_refresh()


class VmcHeltySSIDText(VmcHeltyEntity, TextEntity):
    """VMC Helty WiFi SSID text entity."""

    def __init__(self, coordinator):
        """Initialize the text entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_wifi_ssid"
        self._attr_name = f"{coordinator.name} WiFi SSID"
        self._attr_icon = "mdi:wifi"

    @property
    def native_value(self) -> str | None:
        """Return current WiFi SSID."""
        if not self.coordinator.data:
            return None

        network_data = self.coordinator.data.get("network", "")
        if network_data:
            ssid, _ = parse_vmsl_response(network_data)
            return ssid
        return None

    async def async_set_value(self, value: str) -> None:
        """Set new WiFi SSID (requires password)."""
        # Per sicurezza, questa operazione richiede anche la password
        # Implementazione da completare con form di conferma


class VmcHeltyPasswordText(VmcHeltyEntity, TextEntity):
    """VMC Helty WiFi password text entity."""

    def __init__(self, coordinator):
        """Initialize the text entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.ip}_wifi_password"
        self._attr_name = f"{coordinator.name} WiFi Password"
        self._attr_icon = "mdi:lock"
        self._attr_mode = "password"

    @property
    def native_value(self) -> str | None:
        """Return masked password."""
        if not self.coordinator.data:
            return None

        network_data = self.coordinator.data.get("network", "")
        if network_data:
            _, password = parse_vmsl_response(network_data)
            return "*" * len(password) if password else None
        return None

    async def async_set_value(self, value: str) -> None:
        """Set new WiFi password."""
        # Implementazione da completare con validazione sicurezza
