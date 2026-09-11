"""Coordinator for VMC Helty Flow integration."""

import logging
import re
import time
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_PORT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_ROOM_VOLUME,
    DEFAULT_TIMEOUT,
    DOMAIN,
    NETWORK_INFO_UPDATE_INTERVAL,
    SENSORS_UPDATE_INTERVAL,
)
from .helpers import (
    VMCConnectionError,
    VMCTimeoutError,
    tcp_send_command,
    validate_network_connectivity,
)

_LOGGER = logging.getLogger(__name__)

NETWORK_INFO_INTERVAL = timedelta(seconds=NETWORK_INFO_UPDATE_INTERVAL)
DEVICE_NAME_INTERVAL = timedelta(seconds=NETWORK_INFO_UPDATE_INTERVAL)


class VmcHeltyCoordinator(DataUpdateCoordinator):
    """Coordinator to manage VMC Helty data updates."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator."""
        scan_interval_seconds = int(
            config_entry.options.get("scan_interval", SENSORS_UPDATE_INTERVAL)
        )
        normal_update_interval = timedelta(seconds=scan_interval_seconds)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=normal_update_interval,
            config_entry=config_entry,
        )
        self.config_entry = config_entry
        self.ip = config_entry.data["ip"]
        self.name = config_entry.data["name"]
        self.device_entry: DeviceEntry | None = None
        self.device_id: str | None = None
        self._consecutive_errors = 0
        self._max_consecutive_errors = 5
        self._error_recovery_interval = timedelta(seconds=30)
        self._normal_update_interval = normal_update_interval
        self._recovery_update_interval = timedelta(seconds=60)

        # Timestamps for smart update intervals
        self._last_network_update = 0.0
        self._last_name_update = 0.0

        # Cache for last valid data
        self._cached_data: dict[str, str | None] = {
            "name": None,
            "network": None,
        }

    @property
    def room_volume(self) -> float:
        """Return configured room volume from config entry options."""
        if self.config_entry is None:
            return DEFAULT_ROOM_VOLUME
        # Leggi solo da options (migrazione automatica gestita in __init__.py)
        room_volume = self.config_entry.options.get("room_volume", DEFAULT_ROOM_VOLUME)
        return float(room_volume)

    @property
    def timeout(self) -> int:
        """Return configured TCP timeout from config entry options."""
        if self.config_entry is None:
            return DEFAULT_TIMEOUT
        return int(self.config_entry.options.get("timeout", DEFAULT_TIMEOUT))

    @property
    def port(self) -> int:
        """Return configured TCP port from config entry data."""
        if self.config_entry is None:
            return DEFAULT_PORT
        return int(self.config_entry.data.get("port", DEFAULT_PORT))

    @property
    def retry_attempts(self) -> int:
        """Return configured number of retry attempts from config entry options."""
        if self.config_entry is None:
            return DEFAULT_RETRY_ATTEMPTS
        return int(
            self.config_entry.options.get("retry_attempts", DEFAULT_RETRY_ATTEMPTS)
        )

    @property
    def name_slug(self) -> str:
        """Return device name as a slug with vmc_helty_ prefix (safe for entity IDs)."""
        slug = re.sub(r"[^a-z0-9]+", "_", self.name.lower())
        slug = re.sub(r"^_+|_+$", "", slug)
        slug = re.sub(r"_+", "_", slug)
        if not slug:
            slug = "device"
        if not slug.startswith("vmc_helty_"):
            slug = f"vmc_helty_{slug}"
        return slug

    def _parse_filter_hours(self, status_response: str) -> int | None:
        """Parse filter hours from VMGH? response.

        Response format: VMGO,<fan_speed>,<led>,<temp>,<humidity>,<filter_hours>
        Filter hours is at position 5.
        """
        try:
            if not status_response or not status_response.startswith("VMGO"):
                return None

            parts = status_response.split(",")
            # Need 6 parts: VMGO + fan_speed + led + temp + humidity + filter_hours
            if len(parts) < 6:  # noqa: PLR2004
                return None

            return int(parts[5])
        except (ValueError, IndexError):
            return None

    async def _get_status_data(self) -> str:
        """Get device status data.

        Retries up to ``retry_attempts`` times, both on connection/timeout
        errors and on a "successful" but empty/invalid response — the VMC
        hardware sometimes closes the connection with an empty payload
        instead of raising a network-level error, which would otherwise
        bypass the retry logic in ``tcp_send_command``.
        """
        attempts = max(1, self.retry_attempts)
        status_response = ""
        last_timeout_err: VMCTimeoutError | None = None
        last_connection_err: VMCConnectionError | None = None

        for attempt in range(1, attempts + 1):
            last_timeout_err = None
            last_connection_err = None
            try:
                status_response = await tcp_send_command(
                    self.ip, self.port, "VMGH?", self.timeout
                )
            except VMCTimeoutError as err:
                last_timeout_err = err
                _LOGGER.warning(
                    "Timeout getting status from %s (tentativo %d/%d): %s",
                    self.ip,
                    attempt,
                    attempts,
                    err,
                )
            except VMCConnectionError as err:
                last_connection_err = err
                _LOGGER.warning(
                    "Connection error to %s (tentativo %d/%d): %s",
                    self.ip,
                    attempt,
                    attempts,
                    err,
                )
            else:
                if status_response and status_response.startswith("VMGO"):
                    return status_response
                _LOGGER.warning(
                    "Risposta di stato non valida da %s (tentativo %d/%d): %r",
                    self.ip,
                    attempt,
                    attempts,
                    status_response,
                )

        if last_timeout_err is not None:
            self._handle_error()
            raise UpdateFailed(
                f"Timeout communicating with {self.ip}"
            ) from last_timeout_err

        if last_connection_err is not None:
            if self._consecutive_errors == 0 or self._consecutive_errors % 5 == 0:
                try:
                    diagnostics = await validate_network_connectivity(
                        self.ip, self.port
                    )
                    _LOGGER.info(
                        "Network diagnostics for %s: ping=%s, tcp=%s, details=%s",
                        self.ip,
                        diagnostics.get("ping_success"),
                        diagnostics.get("tcp_connection"),
                        diagnostics.get("error_details"),
                    )
                except Exception as diag_err:
                    _LOGGER.debug("Unable to run network diagnostics: %s", diag_err)
            self._handle_error()
            raise UpdateFailed(
                f"Connection error to {self.ip}: {last_connection_err}"
            ) from last_connection_err

        # Nessuna eccezione, ma la risposta resta non valida dopo tutti i
        # tentativi: la gestione dell'errore/conteggio è lasciata al chiamante
        # (_async_update_data), come per il comportamento preesistente.
        return status_response

    async def _get_additional_data(self) -> dict[str, str | None]:
        """Get additional device data (sensors, name, network) with smart intervals."""
        responses: dict[str, str | None] = {}
        current_time = time.time()

        # Sensors data - always updated (every 60 seconds)
        try:
            responses["sensors"] = await tcp_send_command(
                self.ip, self.port, "VMGI?", self.timeout, self.retry_attempts
            )
        except VMCConnectionError as err:
            _LOGGER.warning("Unable to read sensors from %s: %s", self.ip, err)
            responses["sensors"] = None

        # Device name - updated every 15 minutes
        time_since_name_update = current_time - self._last_name_update
        if time_since_name_update >= DEVICE_NAME_INTERVAL.total_seconds():
            try:
                responses["name"] = await tcp_send_command(
                    self.ip, self.port, "VMNM?", self.timeout, self.retry_attempts
                )
                self._last_name_update = current_time
                if responses["name"]:
                    self._cached_data["name"] = responses["name"]
                _LOGGER.debug("Updated device name for %s", self.ip)
            except VMCConnectionError as err:
                _LOGGER.warning("Unable to read name from %s: %s", self.ip, err)
                responses["name"] = None
        else:
            responses["name"] = self._cached_data["name"]

        # Network info - updated every 15 minutes
        time_since_network_update = current_time - self._last_network_update
        if time_since_network_update >= NETWORK_INFO_INTERVAL.total_seconds():
            try:
                responses["network"] = await tcp_send_command(
                    self.ip, self.port, "VMSL?", self.timeout, self.retry_attempts
                )
                self._last_network_update = current_time
                if responses["network"]:
                    self._cached_data["network"] = responses["network"]
                _LOGGER.debug("Updated network info for %s", self.ip)
            except VMCConnectionError as err:
                _LOGGER.warning("Unable to read network info from %s: %s", self.ip, err)
                responses["network"] = None
        else:
            responses["network"] = self._cached_data["network"]

        return responses

    def _handle_successful_update(self) -> None:
        """Handle successful data update."""
        if self._consecutive_errors > 0:
            _LOGGER.info(
                "Connection restored with %s after %d consecutive errors",
                self.ip,
                self._consecutive_errors,
            )

        self._consecutive_errors = 0
        if self.update_interval != self._normal_update_interval:  # type: ignore[has-type]
            self.update_interval = self._normal_update_interval  # type: ignore[has-type]
            _LOGGER.info("Restored normal update interval for %s", self.ip)

    async def _async_update_data(self):
        """Fetch data from VMC device."""

        def _raise_update_failed(status_response: str) -> None:
            """Raise UpdateFailed after handling error."""
            self._handle_error()
            raise UpdateFailed(
                f"Device {self.ip} did not respond correctly: {status_response}"
            )

        try:
            status_response = await self._get_status_data()

            if not status_response or not status_response.startswith("VMGO"):
                _raise_update_failed(status_response)

            additional_data = await self._get_additional_data()

            self._handle_successful_update()

            # Parse filter hours from status response
            filter_hours = self._parse_filter_hours(status_response)

            data = {
                "status": status_response,
                "sensors": additional_data["sensors"],
                "name": additional_data["name"],
                "network": additional_data["network"],
                "filter_hours": filter_hours,
                "available": True,
                "last_update": time.time(),
            }

            self._maybe_update_device_name(additional_data["name"])

        except UpdateFailed:
            raise
        except Exception as err:
            self._handle_error()
            _LOGGER.exception(
                "Unexpected error during data update for %s",
                self.ip,
            )
            raise UpdateFailed(f"Error communicating with {self.ip}: {err}") from err
        else:
            return data

    def _handle_error(self):
        """Handle consecutive error count and recovery logic."""
        self._consecutive_errors += 1

        if self._consecutive_errors == 1:
            _LOGGER.warning("Communication error with %s", self.ip)
        elif self._consecutive_errors == self._max_consecutive_errors:
            _LOGGER.error(
                "Reached %d consecutive errors with %s, switching to recovery mode",
                self._max_consecutive_errors,
                self.ip,
            )
        elif self._consecutive_errors > self._max_consecutive_errors:
            _LOGGER.debug(
                "Consecutive error #%d for %s", self._consecutive_errors, self.ip
            )
        else:
            _LOGGER.info(
                "Consecutive error #%d for %s", self._consecutive_errors, self.ip
            )

        if (
            self._consecutive_errors >= self._max_consecutive_errors
            and self.update_interval != self._error_recovery_interval
        ):
            self.update_interval = self._error_recovery_interval  # type: ignore
            _LOGGER.info(
                "Changed update interval for %s to %d seconds (recovery mode)",
                self.ip,
                self._error_recovery_interval.total_seconds(),
            )

    def _maybe_update_device_name(self, name_response):
        """Update device name if needed."""
        if name_response and name_response.startswith("VMNM"):
            try:
                parts = name_response.split(",")
                if (
                    len(parts) > 1
                    and (new_name := parts[1].strip())
                    and new_name != self.name
                ):
                    _LOGGER.info(
                        "Device name changed from '%s' to '%s'",
                        self.name,
                        new_name,
                    )
                    self.name = new_name
                    if hasattr(self, "hass") and self.hass and self.config_entry:
                        new_data = {**self.config_entry.data, "name": new_name}
                        self.hass.config_entries.async_update_entry(
                            self.config_entry, data=new_data
                        )
            except Exception as err:
                _LOGGER.warning("Error updating device name: %s", err)
