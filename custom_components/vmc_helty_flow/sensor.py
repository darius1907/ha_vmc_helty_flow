"""Entità sensori per VMC Helty Flow."""

import logging
import math
from datetime import datetime
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
from homeassistant.util import dt as dt_util

from . import VmcHeltyCoordinator
from .const import (
    AIR_EXCHANGE_ACCEPTABLE,
    AIR_EXCHANGE_EXCELLENT,
    AIR_EXCHANGE_GOOD,
    AIR_EXCHANGE_POOR,
    AIR_EXCHANGE_TIME_ACCEPTABLE,
    AIR_EXCHANGE_TIME_EXCELLENT,
    AIR_EXCHANGE_TIME_GOOD,
    AIRFLOW_MAPPING,
    COMFORT_HUMIDITY_ACCEPTABLE_MAX,
    COMFORT_HUMIDITY_ACCEPTABLE_MIN,
    COMFORT_HUMIDITY_MAX,
    COMFORT_HUMIDITY_OPTIMAL_MAX,
    COMFORT_HUMIDITY_OPTIMAL_MIN,
    COMFORT_HUMIDITY_REFERENCE,
    COMFORT_HUMIDITY_TOLERABLE_MAX,
    COMFORT_HUMIDITY_TOLERABLE_MIN,
    COMFORT_INDEX_ACCEPTABLE,
    COMFORT_INDEX_EXCELLENT,
    COMFORT_INDEX_GOOD,
    COMFORT_INDEX_MEDIOCRE,
    COMFORT_TEMP_ACCEPTABLE_MAX,
    COMFORT_TEMP_ACCEPTABLE_MIN,
    COMFORT_TEMP_OPTIMAL_MAX,
    COMFORT_TEMP_OPTIMAL_MIN,
    COMFORT_TEMP_REFERENCE,
    COMFORT_TEMP_TOLERABLE_MAX,
    COMFORT_TEMP_TOLERABLE_MIN,
    DAILY_AIR_CHANGES_ADEQUATE,
    DAILY_AIR_CHANGES_ADEQUATE_MIN,
    DAILY_AIR_CHANGES_EXCELLENT,
    DAILY_AIR_CHANGES_EXCELLENT_MIN,
    DAILY_AIR_CHANGES_GOOD,
    DAILY_AIR_CHANGES_GOOD_MIN,
    DAILY_AIR_CHANGES_POOR,
    DEW_POINT_ACCEPTABLE_MAX,
    DEW_POINT_ACCEPTABLE_MIN,
    DEW_POINT_COMFORTABLE_MAX,
    DEW_POINT_COMFORTABLE_MIN,
    DEW_POINT_DELTA_CRITICAL,
    DEW_POINT_DELTA_HIGH_RISK,
    DEW_POINT_DELTA_LOW_RISK,
    DEW_POINT_DELTA_MODERATE_RISK,
    DEW_POINT_DRY_MAX,
    DEW_POINT_DRY_MIN,
    DEW_POINT_GOOD_MAX,
    DEW_POINT_GOOD_MIN,
    DEW_POINT_HUMID_MAX,
    DEW_POINT_HUMID_MIN,
    DEW_POINT_VERY_DRY,
    DOMAIN,
    ENTITY_NAME_PREFIX,
    FAN_SPEED_MAX_NORMAL,
    FANSPEED_MAPPING,
    MIN_RESPONSE_PARTS,
    MIN_STATUS_PARTS,
)
from .device_info import VmcHeltyEntity
from .helpers import parse_vmsl_response, tcp_send_command

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VMC Helty sensors from config entry."""
    _LOGGER.debug(
        "Setting up VMC Helty sensors for config entry: %s", config_entry.entry_id
    )

    try:
        coordinator = hass.data[DOMAIN][config_entry.entry_id]
        _LOGGER.debug("Retrieved coordinator: %s", coordinator)
    except KeyError:
        _LOGGER.exception(
            "Coordinator not found for entry %s in hass.data[%s]",
            config_entry.entry_id,
            DOMAIN,
        )
        _LOGGER.debug(
            "Available entries in hass.data[%s]: %s",
            DOMAIN,
            list(hass.data.get(DOMAIN, {}).keys()),
        )
        return

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
        # Sensore portata d'aria
        VmcHeltyAirflowSensor(coordinator),
        # Sensori avanzati calcolati
        VmcHeltyAbsoluteHumiditySensor(coordinator),
        VmcHeltyDewPointSensor(coordinator),
        VmcHeltyDewPointDeltaSensor(coordinator),
        VmcHeltyComfortIndexSensor(coordinator),
        VmcHeltyAirExchangeTimeSensor(coordinator),
        VmcHeltyDailyAirChangesSensor(coordinator, coordinator.device_id),
        # Sensori di stato
        VmcHeltyOnOffSensor(coordinator),
        VmcHeltyLastResponseSensor(coordinator),
        VmcHeltyFilterHoursSensor(coordinator),
        # Sensori di rete
        VmcHeltyIPAddressSensor(coordinator),
        # Pulsanti e controlli di testo
        VmcHeltyResetFilterButton(coordinator),
        VmcHeltyNameText(coordinator),
        VmcHeltySSIDText(coordinator),
        VmcHeltyPasswordText(coordinator),
    ]

    _LOGGER.debug("Created %d sensor entities", len(entities))
    async_add_entities(entities)
    _LOGGER.debug("Successfully added VMC Helty sensor entities")


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
        self._attr_unique_id = f"{coordinator.name_slug}_{sensor_key}"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} {sensor_name}"
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
                "voc": (
                    11,  # VOC is at position 11 based on real data analysis
                    lambda x: int(x) if int(x) > 0 else None,  # VOC = 0 means no data
                ),
            }

            if self._sensor_key in sensor_mapping:
                index, converter = sensor_mapping[self._sensor_key]
                if parts[index]:
                    return converter(parts[index])

        except (ValueError, IndexError):
            pass

        return None


class VmcHeltyAirflowSensor(VmcHeltyEntity, SensorEntity):
    """VMC Helty airflow sensor based on fan speed."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_airflow"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Portata d'Aria"
        self._attr_native_unit_of_measurement = "m³/h"
        self._attr_device_class = SensorDeviceClass.VOLUME_FLOW_RATE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return airflow value based on fan speed."""
        if not self.coordinator.data:
            return None

        status_data = self.coordinator.data.get("status", "")
        if not status_data or not status_data.startswith("VMGO"):
            return None

        try:
            parts = status_data.split(",")
            if len(parts) < MIN_STATUS_PARTS:  # Need at least VMGO and fan_speed
                return None

            # Ottieni la velocità della ventola (posizione 1)
            fan_speed_raw = int(parts[1])

            # Mappa la velocità alla portata d'aria
            return AIRFLOW_MAPPING.get(fan_speed_raw, 0)

        except (ValueError, IndexError):
            return None


class VmcHeltyOnOffSensor(VmcHeltyEntity, BinarySensorEntity):
    """VMC Helty device online/offline sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_online"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Online"
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
        self._attr_unique_id = f"{coordinator.name_slug}_last_response"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Last Response"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Return last update time."""
        if not self.coordinator.data:
            return None

        timestamp = self.coordinator.data.get("last_update")
        if timestamp is None:
            return None

        # Converti timestamp Unix in datetime UTC
        return datetime.fromtimestamp(timestamp, tz=dt_util.UTC)


class VmcHeltyFilterHoursSensor(VmcHeltyEntity, SensorEntity):
    """VMC Helty filter hours sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_filter_hours"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Filter Hours"
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
        self._attr_unique_id = f"{coordinator.name_slug}_ip_address"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} IP Address"
        self._attr_icon = "mdi:ip-network"

    @property
    def native_value(self) -> str:
        """Return device IP address."""
        return self.coordinator.ip


class VmcHeltyResetFilterButton(VmcHeltyEntity, ButtonEntity):
    """VMC Helty reset filter button."""

    def __init__(self, coordinator):
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_reset_filter"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Reset Filter"
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
        self._attr_unique_id = f"{coordinator.name_slug}_device_name"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Device Name"
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
        self._attr_unique_id = f"{coordinator.name_slug}_wifi_ssid"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} WiFi SSID"
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
        self._attr_unique_id = f"{coordinator.name_slug}_wifi_password"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} WiFi Password"
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


class VmcHeltyAbsoluteHumiditySensor(VmcHeltyEntity, SensorEntity):
    """VMC Helty absolute humidity sensor using Magnus-Tetens formula."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_absolute_humidity"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Umidità Assoluta"
        self._attr_native_unit_of_measurement = "g/m³"
        self._attr_device_class = None  # No device class for absolute humidity
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:water-percent"

    @property
    def native_value(self) -> float | None:
        """Calculate absolute humidity using Magnus-Tetens formula."""
        if not self.coordinator.data:
            return None

        try:
            # Ottieni i dati dei sensori dalla stringa VMGI
            sensors_data = self.coordinator.data.get("sensors", "")
            if not sensors_data or not sensors_data.startswith("VMGI"):
                return None

            parts = sensors_data.split(",")
            if (
                len(parts) < MIN_RESPONSE_PARTS
            ):  # Serve almeno temp_int, temp_ext, humidity, co2
                return None

            # Estrai temperatura interna (pos 1) e umidità (pos 3)
            temp_internal = float(parts[1]) / 10  # Decimi di °C
            humidity = float(parts[3]) / 10  # Decimi di %

            if temp_internal is None or humidity is None:
                return None

            # Formula Magnus-Tetens per umidità assoluta
            # Costanti per acqua
            a = 17.27
            b = 237.7

            # Pressione vapore saturo (hPa) - formula Magnus-Tetens
            es = 6.112 * math.exp((a * temp_internal) / (b + temp_internal))

            # Pressione vapore reale (hPa)
            e = (humidity / 100.0) * es

            # Umidità assoluta (g/m³) usando formula termodinamica
            # Formula: AH = (e * molar_mass) / (gas_constant * temp_kelvin)
            molar_mass = 18.016  # g/mol (peso molecolare acqua)
            gas_constant = 0.08314  # L·hPa/(mol·K)
            temp_kelvin = temp_internal + 273.15  # K

            abs_humidity = (e * molar_mass) / (gas_constant * temp_kelvin)

            return round(abs_humidity, 2)

        except (ValueError, TypeError, ZeroDivisionError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra attributes."""
        if not self.coordinator.data:
            return None

        # Ottieni i dati dei sensori dalla stringa VMGI
        sensors_data = self.coordinator.data.get("sensors", "")
        if not sensors_data or not sensors_data.startswith("VMGI"):
            return None

        try:
            parts = sensors_data.split(",")
            if len(parts) < MIN_RESPONSE_PARTS:
                return None

            temp_internal = float(parts[1]) / 10  # Decimi di °C
            humidity = float(parts[3]) / 10  # Decimi di %

            return {
                "formula": "Magnus-Tetens",
                "temperature_source": f"{temp_internal}°C",
                "humidity_source": f"{humidity}%",
                "precision": "±0.1 g/m³",
                "valid_range": "-40°C to +50°C",
            }
        except (ValueError, IndexError):
            return None


class VmcHeltyDewPointSensor(VmcHeltyEntity, SensorEntity):
    """VMC Helty dew point sensor using Magnus-Tetens formula."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_dew_point"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Punto di Rugiada"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:thermometer-water"

    @property
    def native_value(self) -> float | None:
        """Calculate dew point using Magnus-Tetens formula."""
        if not self.coordinator.data:
            return None

        try:
            # Ottieni i dati dei sensori dalla stringa VMGI
            sensors_data = self.coordinator.data.get("sensors", "")
            if not sensors_data or not sensors_data.startswith("VMGI"):
                return None

            parts = sensors_data.split(",")
            if len(parts) < MIN_RESPONSE_PARTS:
                return None

            # Estrai temperatura interna (pos 1) e umidità (pos 3)
            temp_internal = float(parts[1]) / 10  # Decimi di °C
            humidity = float(parts[3]) / 10  # Decimi di %

            if temp_internal is None or humidity is None or humidity <= 0:
                return None

            # Formula Magnus-Tetens per punto di rugiada
            # Costanti per acqua
            a = 17.27
            b = 237.7

            # Calcolo intermedio
            alpha = ((a * temp_internal) / (b + temp_internal)) + math.log(
                humidity / 100.0
            )

            # Punto di rugiada
            dew_point = (b * alpha) / (a - alpha)

            return round(dew_point, 1)

        except (ValueError, TypeError, ZeroDivisionError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra attributes."""
        if not self.coordinator.data:
            return None

        # Ottieni i dati dei sensori dalla stringa VMGI
        sensors_data = self.coordinator.data.get("sensors", "")
        if not sensors_data or not sensors_data.startswith("VMGI"):
            return None

        try:
            parts = sensors_data.split(",")
            if len(parts) < MIN_RESPONSE_PARTS:
                return None

            temp_internal = float(parts[1]) / 10  # Decimi di °C
            humidity = float(parts[3]) / 10  # Decimi di %
        except (ValueError, IndexError):
            return None

        # Calcola anche il comfort level basato sul punto di rugiada
        dew_point = self.native_value
        comfort_level = "Unknown"
        comfort_color = "#9e9e9e"

        if dew_point is not None:
            if dew_point < DEW_POINT_VERY_DRY:
                comfort_level = "Molto Secco"
                comfort_color = "#ff6b47"
            elif DEW_POINT_DRY_MIN <= dew_point < DEW_POINT_DRY_MAX:
                comfort_level = "Secco"
                comfort_color = "#ffeb3b"
            elif DEW_POINT_COMFORTABLE_MIN <= dew_point < DEW_POINT_COMFORTABLE_MAX:
                comfort_level = "Confortevole"
                comfort_color = "#4caf50"
            elif DEW_POINT_GOOD_MIN <= dew_point < DEW_POINT_GOOD_MAX:
                comfort_level = "Buono"
                comfort_color = "#8bc34a"
            elif DEW_POINT_ACCEPTABLE_MIN <= dew_point < DEW_POINT_ACCEPTABLE_MAX:
                comfort_level = "Accettabile"
                comfort_color = "#ffeb3b"
            elif DEW_POINT_HUMID_MIN <= dew_point < DEW_POINT_HUMID_MAX:
                comfort_level = "Umido"
                comfort_color = "#ff9800"
            else:
                comfort_level = "Oppressivo"
                comfort_color = "#f44336"

        return {
            "formula": "Magnus-Tetens",
            "temperature_source": temp_internal,
            "humidity_source": humidity,
            "precision": "±0.2°C",
            "comfort_level": comfort_level,
            "comfort_color": comfort_color,
            "standard": "ASHRAE 55-2020",
        }


class VmcHeltyComfortIndexSensor(VmcHeltyEntity, SensorEntity):
    """Indice di comfort igrometrico basato su temperatura e umidità."""

    def __init__(self, coordinator: VmcHeltyCoordinator) -> None:
        super().__init__(coordinator, "comfort_index")
        self._attr_name = (
            f"{ENTITY_NAME_PREFIX} {coordinator.name} Indice Comfort Igrometrico"
        )
        self._attr_unique_id = f"{coordinator.name_slug}_comfort_index"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:account-check"

    @property
    def native_value(self) -> int | None:
        """Calcola l'indice di comfort come percentuale (0-100%)."""
        if not self.coordinator.data:
            return None

        try:
            # Ottieni i dati dei sensori dalla stringa VMGI
            sensors_data = self.coordinator.data.get("sensors", "")
            if not sensors_data or not sensors_data.startswith("VMGI"):
                return None

            parts = sensors_data.split(",")
            if len(parts) < MIN_RESPONSE_PARTS:
                return None

            # Estrai temperatura interna (pos 1) e umidità (pos 3)
            temp = float(parts[1]) / 10  # Decimi di °C
            humidity = float(parts[3]) / 10  # Decimi di %

            if humidity <= 0 or humidity > COMFORT_HUMIDITY_MAX:
                return None

            # Indice basato su temperature e umidità ottimali
            temp_comfort = self._calculate_temperature_comfort(temp)
            humidity_comfort = self._calculate_humidity_comfort(humidity)

            # Combina i due fattori con peso bilanciato
            comfort_index = (temp_comfort * 0.6 + humidity_comfort * 0.4) * 100

            return round(comfort_index)

        except (ValueError, TypeError, ZeroDivisionError):
            return None

    def _calculate_temperature_comfort(self, temp: float) -> float:
        """Calcola il comfort termico (0.0-1.0)."""
        # Range ottimale
        if COMFORT_TEMP_OPTIMAL_MIN <= temp <= COMFORT_TEMP_OPTIMAL_MAX:
            return 1.0
        # Range accettabile con degradazione lineare
        if COMFORT_TEMP_ACCEPTABLE_MIN <= temp < COMFORT_TEMP_OPTIMAL_MIN:
            return 0.5 + (temp - COMFORT_TEMP_ACCEPTABLE_MIN) * 0.25  # da 0.5 a 1.0
        if COMFORT_TEMP_OPTIMAL_MAX < temp <= COMFORT_TEMP_ACCEPTABLE_MAX:
            return 1.0 - (temp - COMFORT_TEMP_OPTIMAL_MAX) * 0.25  # da 1.0 a 0.5
        # Range sopportabile con ulteriore degradazione
        if COMFORT_TEMP_TOLERABLE_MIN <= temp < COMFORT_TEMP_ACCEPTABLE_MIN:
            return 0.2 + (temp - COMFORT_TEMP_TOLERABLE_MIN) * 0.15  # da 0.2 a 0.5
        if COMFORT_TEMP_ACCEPTABLE_MAX < temp <= COMFORT_TEMP_TOLERABLE_MAX:
            return 0.5 - (temp - COMFORT_TEMP_ACCEPTABLE_MAX) * 0.15  # da 0.5 a 0.2
        # Fuori range accettabile
        return max(0.0, 0.2 - abs(temp - COMFORT_TEMP_REFERENCE) * 0.02)

    def _calculate_humidity_comfort(self, humidity: float) -> float:
        """Calcola il comfort igrometrico (0.0-1.0)."""
        # Range ottimale
        if COMFORT_HUMIDITY_OPTIMAL_MIN <= humidity <= COMFORT_HUMIDITY_OPTIMAL_MAX:
            return 1.0
        # Range accettabile con degradazione lineare
        if COMFORT_HUMIDITY_ACCEPTABLE_MIN <= humidity < COMFORT_HUMIDITY_OPTIMAL_MIN:
            return (
                0.5 + (humidity - COMFORT_HUMIDITY_ACCEPTABLE_MIN) * 0.05
            )  # da 0.5 a 1.0
        if COMFORT_HUMIDITY_OPTIMAL_MAX < humidity <= COMFORT_HUMIDITY_ACCEPTABLE_MAX:
            return (
                1.0 - (humidity - COMFORT_HUMIDITY_OPTIMAL_MAX) * 0.05
            )  # da 1.0 a 0.5
        # Range sopportabile con ulteriore degradazione
        if COMFORT_HUMIDITY_TOLERABLE_MIN <= humidity < COMFORT_HUMIDITY_ACCEPTABLE_MIN:
            return (
                0.2 + (humidity - COMFORT_HUMIDITY_TOLERABLE_MIN) * 0.06
            )  # da 0.2 a 0.5
        if COMFORT_HUMIDITY_ACCEPTABLE_MAX < humidity <= COMFORT_HUMIDITY_TOLERABLE_MAX:
            return (
                0.5 - (humidity - COMFORT_HUMIDITY_ACCEPTABLE_MAX) * 0.03
            )  # da 0.5 a 0.2
        # Fuori range accettabile
        return max(0.0, 0.2 - abs(humidity - COMFORT_HUMIDITY_REFERENCE) * 0.005)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Attributi aggiuntivi con dettagli del comfort."""
        attributes = super().extra_state_attributes or {}

        if not self.coordinator.data:
            return attributes

        try:
            # Ottieni i dati dei sensori dalla stringa VMGI
            sensors_data = self.coordinator.data.get("sensors", "")
            if not sensors_data or not sensors_data.startswith("VMGI"):
                return attributes

            parts = sensors_data.split(",")
            if len(parts) < MIN_RESPONSE_PARTS:
                return attributes

            # Estrai temperatura interna (pos 1) e umidità (pos 3)
            temp = float(parts[1]) / 10  # Decimi di °C
            humidity = float(parts[3]) / 10  # Decimi di %

            temp_comfort = self._calculate_temperature_comfort(temp)
            humidity_comfort = self._calculate_humidity_comfort(humidity)

            comfort_value = self.native_value
            if comfort_value is not None:
                # Classificazione livello comfort
                if comfort_value >= COMFORT_INDEX_EXCELLENT:
                    comfort_category = "Eccellente"
                elif comfort_value >= COMFORT_INDEX_GOOD:
                    comfort_category = "Buono"
                elif comfort_value >= COMFORT_INDEX_ACCEPTABLE:
                    comfort_category = "Accettabile"
                elif comfort_value >= COMFORT_INDEX_MEDIOCRE:
                    comfort_category = "Mediocre"
                else:
                    comfort_category = "Scarso"

                attributes.update(
                    {
                        "comfort_category": comfort_category,
                        "temperature_comfort": f"{temp_comfort:.2f}",
                        "humidity_comfort": f"{humidity_comfort:.2f}",
                        "optimal_temperature": "20-24°C",
                        "optimal_humidity": "40-60%",
                        "current_temperature": f"{temp}°C",
                        "current_humidity": f"{humidity}%",
                    }
                )

        except (ValueError, TypeError, ZeroDivisionError):
            pass

        return attributes


class VmcHeltyDewPointDeltaSensor(VmcHeltyEntity, SensorEntity):
    """Sensore Delta Punto di Rugiada per controllo condensazione."""

    def __init__(self, coordinator):
        """Inizializza il sensore."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_dew_point_delta"
        self._attr_name = (
            f"{ENTITY_NAME_PREFIX} {coordinator.name} Delta Punto di Rugiada"
        )
        self._attr_icon = "mdi:thermometer-water"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def native_value(self) -> float | None:
        """Calcola il delta punto di rugiada (interno - esterno)."""
        if not self.coordinator.data:
            return None

        try:
            # Ottieni i dati dei sensori dalla stringa VMGI
            sensors_data = self.coordinator.data.get("sensors", "")
            if not sensors_data or not sensors_data.startswith("VMGI"):
                return None

            parts = sensors_data.split(",")
            if len(parts) < MIN_RESPONSE_PARTS:
                return None

            # Estrai temperature e umidità
            temp_internal = float(parts[1]) / 10  # Decimi di °C (pos 1)
            temp_external = float(parts[2]) / 10  # Decimi di °C (pos 2)
            humidity = float(parts[3]) / 10  # Decimi di % (pos 3)

            if humidity <= 0 or humidity > COMFORT_HUMIDITY_MAX:
                return None

            # Calcola i punti di rugiada interno ed esterno
            internal_dew_point = self._calculate_dew_point(temp_internal, humidity)
            external_dew_point = self._calculate_dew_point(temp_external, humidity)

            delta = internal_dew_point - external_dew_point

            return round(delta, 1)

        except (ValueError, TypeError, ZeroDivisionError):
            return None

    def _calculate_dew_point(self, temperature: float, humidity: float) -> float:
        """Calcola il punto di rugiada usando la formula Magnus-Tetens."""
        # Costanti Magnus-Tetens per acqua
        a = 17.27
        b = 237.7

        # Calcola il punto di rugiada
        gamma = (a * temperature) / (b + temperature) + math.log(humidity / 100.0)
        return (b * gamma) / (a - gamma)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Attributi aggiuntivi con informazioni sul rischio condensazione."""
        attributes = super().extra_state_attributes or {}

        if not self.coordinator.data:
            return attributes

        try:
            # Ottieni i dati dei sensori dalla stringa VMGI
            sensors_data = self.coordinator.data.get("sensors", "")
            if not sensors_data or not sensors_data.startswith("VMGI"):
                return attributes

            parts = sensors_data.split(",")
            if len(parts) < MIN_RESPONSE_PARTS:
                return attributes

            delta_value = self.native_value
            if delta_value is not None:
                # Classificazione del rischio di condensazione
                risk_info = self._get_condensation_risk(delta_value)

                # Estrai dati dalla stringa VMGI
                temp_internal = float(parts[1]) / 10  # Decimi di °C (pos 1)
                temp_external = float(parts[2]) / 10  # Decimi di °C (pos 2)
                humidity = float(parts[3]) / 10  # Decimi di % (pos 3)

                internal_dew_point = self._calculate_dew_point(temp_internal, humidity)
                external_dew_point = self._calculate_dew_point(temp_external, humidity)

                attributes.update(
                    {
                        "risk_level": risk_info["level"],
                        "risk_description": risk_info["description"],
                        "recommended_action": risk_info["action"],
                        "internal_dew_point": f"{internal_dew_point:.1f}°C",
                        "external_dew_point": f"{external_dew_point:.1f}°C",
                        "internal_temperature": f"{temp_internal}°C",
                        "external_temperature": f"{temp_external}°C",
                        "humidity": f"{humidity}%",
                    }
                )

        except (ValueError, TypeError, ZeroDivisionError):
            pass

        return attributes

    def _get_condensation_risk(self, delta: float) -> dict[str, str]:
        """Determina il livello di rischio condensazione basato sul delta."""
        if delta <= DEW_POINT_DELTA_CRITICAL:
            return {
                "level": "Critico",
                "description": "Rischio condensazione molto alto",
                "action": "Aumentare ventilazione immediatamente",
            }

        if delta <= DEW_POINT_DELTA_HIGH_RISK:
            return {
                "level": "Alto",
                "description": "Rischio condensazione alto",
                "action": "Aumentare ventilazione e ridurre umidità",
            }

        if delta <= DEW_POINT_DELTA_MODERATE_RISK:
            return {
                "level": "Moderato",
                "description": "Rischio condensazione moderato",
                "action": "Monitorare e considerare ventilazione",
            }

        if delta <= DEW_POINT_DELTA_LOW_RISK:
            return {
                "level": "Basso",
                "description": "Rischio condensazione basso",
                "action": "Condizioni sotto controllo",
            }

        return {
            "level": "Sicuro",
            "description": "Nessun rischio condensazione",
            "action": "Condizioni ottimali",
        }


class VmcHeltyAirExchangeTimeSensor(VmcHeltyEntity, SensorEntity):
    """Air Exchange Time Sensor - calcola il tempo necessario per ricambio aria."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_air_exchange_time"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Air Exchange Time"
        self._attr_native_unit_of_measurement = "min"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:clock-time-four"

    @property
    def native_value(self) -> float | None:
        """Return the current air exchange time in minutes."""
        if not self.coordinator.data:
            return None

        # Usa il parsing VMGO per ottenere la velocità ventola
        status_data = self.coordinator.data.get("status", "")
        if not status_data or not status_data.startswith("VMGO"):
            return None

        parts = status_data.split(",")
        if len(parts) < MIN_RESPONSE_PARTS:  # Need at least 15 parts for VMGO
            return None

        try:
            # Velocità ventola dalla posizione 1 del VMGO
            fan_speed = int(parts[1])

            if fan_speed == 0:
                return None  # Ventilazione spenta

            # Calcola portata aria stimata in m³/h basata sulla velocità
            airflow = AIRFLOW_MAPPING.get(
                fan_speed, 10
            )  # Default 10 m³/h se non riconosciuto

            # Volume ambiente dalla configurazione del dispositivo
            room_volume = self.coordinator.room_volume  # m³

            # Calcola tempo di ricambio: Volume / Portata * 60 (per convertire in minuti)
            exchange_time = (room_volume / airflow) * 60

            return round(exchange_time, 1)

        except (ValueError, IndexError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, any] | None:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {
                "efficiency_category": None,
                "room_volume": None,
                "estimated_airflow": None,
                "fan_speed": None,
            }

        # Usa il parsing VMGO per ottenere la velocità ventola
        status_data = self.coordinator.data.get("status", "")
        if not status_data or not status_data.startswith("VMGO"):
            return {
                "efficiency_category": None,
                "room_volume": None,
                "estimated_airflow": None,
                "fan_speed": None,
            }

        parts = status_data.split(",")
        if len(parts) < MIN_STATUS_PARTS:
            return {
                "efficiency_category": None,
                "room_volume": None,
                "estimated_airflow": None,
                "fan_speed": None,
            }

        try:
            # Velocità ventola dalla posizione 1 del VMGO
            actual_speed = int(parts[1])

            airflow = AIRFLOW_MAPPING.get(actual_speed, 0)

            # Determina categoria efficienza
            exchange_time = self.native_value
            if exchange_time is None:
                efficiency_category = None
            elif exchange_time <= AIR_EXCHANGE_TIME_EXCELLENT:
                efficiency_category = AIR_EXCHANGE_EXCELLENT
            elif exchange_time <= AIR_EXCHANGE_TIME_GOOD:
                efficiency_category = AIR_EXCHANGE_GOOD
            elif exchange_time <= AIR_EXCHANGE_TIME_ACCEPTABLE:
                efficiency_category = AIR_EXCHANGE_ACCEPTABLE
            else:
                efficiency_category = AIR_EXCHANGE_POOR

            return {
                "efficiency_category": efficiency_category,
                "room_volume": f"{self.coordinator.room_volume} m³",
                "estimated_airflow": f"{airflow} m³/h",
                "fan_speed": FANSPEED_MAPPING.get(actual_speed, 0),
                "raw_fan_speed": actual_speed,
                "calculation_method": "Volume/Airflow*60",
                "optimization_tip": self._get_optimization_tip(
                    exchange_time, actual_speed
                ),
            }

        except (ValueError, IndexError, TypeError):
            return {
                "efficiency_category": None,
                "room_volume": None,
                "estimated_airflow": None,
                "fan_speed": None,
            }

    def _get_optimization_tip(self, exchange_time: float | None, fan_speed: int) -> str:
        """Get optimization tip based on current performance."""
        if exchange_time is None:
            return "Ventilazione non attiva"

        if exchange_time <= AIR_EXCHANGE_TIME_EXCELLENT:
            return "Prestazioni eccellenti, ricambio aria ottimale"
        if exchange_time <= AIR_EXCHANGE_TIME_GOOD:
            return "Buone prestazioni, ricambio efficace"
        if exchange_time <= AIR_EXCHANGE_TIME_ACCEPTABLE:
            return "Prestazioni accettabili, considerare aumento velocità"
        if fan_speed < FAN_SPEED_MAX_NORMAL:
            return f"Ricambio lento, aumentare velocità da {fan_speed} per migliorare"
        return "Ricambio lento anche a velocità massima, verificare impianto"


class VmcHeltyDailyAirChangesSensor(VmcHeltyEntity, SensorEntity):
    """Sensore per ricambi d'aria giornalieri basato sulla velocità della ventola."""

    def __init__(self, coordinator: VmcHeltyCoordinator, device_id: str) -> None:
        """Inizializza il sensore dei ricambi d'aria giornalieri."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.name_slug}_daily_air_changes"
        self._attr_name = f"{ENTITY_NAME_PREFIX} {coordinator.name} Daily Air Changes"
        self._attr_icon = "mdi:air-filter"
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "changes/day"

    @property
    def native_value(self) -> float | None:
        """Ritorna il numero di ricambi d'aria in 24 ore."""
        if not self.coordinator.data:
            return None

        # Usa il parsing VMGO per ottenere la velocità ventola
        status_data = self.coordinator.data.get("status", "")
        if (
            not status_data
            or not isinstance(status_data, str)
            or not status_data.startswith("VMGO")
        ):
            return None

        parts = status_data.split(",")
        # Per dati VMGO, servono almeno 15 parti
        if len(parts) < MIN_RESPONSE_PARTS:
            return None

        try:
            # Velocità ventola dalla posizione 1 del VMGO (0-7 = velocità/modalità)
            fan_speed_raw = int(parts[1])

            # Calcola portata aria stimata in m³/h basata sulla velocità
            airflow_rate = AIRFLOW_MAPPING.get(fan_speed_raw, 10)  # Default 10 m³/h

            # Volume ambiente dalla configurazione del dispositivo
            room_volume = self.coordinator.room_volume  # m³

            # Calcola ricambi d'aria per ora
            air_changes_per_hour = airflow_rate / room_volume

            # Calcola ricambi d'aria per 24 ore
            daily_air_changes = air_changes_per_hour * 24

            return round(daily_air_changes, 1)

        except (ValueError, IndexError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Ritorna attributi aggiuntivi del sensore."""
        # Livello Ricambi d'aria/h (ACH)	Applicazioni tipiche
        # Poor < 3 ACH	Ventilazione scarsa, rischio aria viziata in stanze chiuse.
        # Adequate 3 - 6 ACH Sufficiente per stanze residenziali, uffici standard.
        # Good 6 - 12 ACH Buona qualità, adatta a scuole, palestre, sale riunioni.
        # Excellent > 12 ACH Elevata, tipica di ospedali, laboratori, cucine prof.
        attributes = {}

        daily_changes = self.native_value
        if daily_changes is not None:
            # Classifica efficacia ricambi
            if daily_changes >= DAILY_AIR_CHANGES_EXCELLENT_MIN:
                category = DAILY_AIR_CHANGES_EXCELLENT
                assessment = "Ricambio d'aria ottimale"
            elif daily_changes >= DAILY_AIR_CHANGES_GOOD_MIN:
                category = DAILY_AIR_CHANGES_GOOD
                assessment = "Ricambio d'aria buono"
            elif daily_changes >= DAILY_AIR_CHANGES_ADEQUATE_MIN:
                category = DAILY_AIR_CHANGES_ADEQUATE
                assessment = "Ricambio d'aria adeguato"
            else:
                category = DAILY_AIR_CHANGES_POOR
                assessment = "Ricambio d'aria insufficiente"

            attributes.update(
                {
                    "category": category,
                    "assessment": assessment,
                    "air_changes_per_hour": round(daily_changes / 24, 2),
                    "room_volume_m3": self.coordinator.room_volume,
                    "recommendation": self._get_recommendation(daily_changes),
                }
            )

        return attributes

    def _get_recommendation(self, daily_changes: float) -> str:
        """Genera raccomandazioni basate sui ricambi d'aria giornalieri."""
        if daily_changes >= DAILY_AIR_CHANGES_EXCELLENT_MIN:
            return "Ricambio d'aria eccellente, continua così"
        if daily_changes >= DAILY_AIR_CHANGES_GOOD_MIN:
            return "Ricambio d'aria buono, eventualmente aumenta ventilazione nelle ore di punta"
        if daily_changes >= DAILY_AIR_CHANGES_ADEQUATE_MIN:
            return "Ricambio adeguato, considera di aumentare la velocità ventola"
        if not self.coordinator.data:
            return "Nessun dato disponibile"

        status_data = self.coordinator.data.get("status", "")
        if status_data and status_data.startswith("VMGO"):
            try:
                parts = status_data.split(",")
                if len(parts) >= MIN_RESPONSE_PARTS:
                    fan_speed_raw = int(parts[1])
                    # Decodifica modalità speciali
                    fan_speed = FANSPEED_MAPPING.get(fan_speed_raw, 1)

                    if fan_speed < FAN_SPEED_MAX_NORMAL:
                        return f"Ricambio insufficiente, aumentare velocità da {fan_speed} a 3-4"
                    return "Ricambio insufficiente anche a velocità massima, verificare impianto"
            except (ValueError, IndexError):
                pass
        return "Errore nel calcolo, verificare stato ventola"
