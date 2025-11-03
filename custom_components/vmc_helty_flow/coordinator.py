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
    DEFAULT_ROOM_VOLUME,
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

DEFAULT_SCAN_INTERVAL = timedelta(seconds=SENSORS_UPDATE_INTERVAL)
NETWORK_INFO_INTERVAL = timedelta(seconds=NETWORK_INFO_UPDATE_INTERVAL)
DEVICE_NAME_INTERVAL = timedelta(seconds=NETWORK_INFO_UPDATE_INTERVAL)


class VmcHeltyCoordinator(DataUpdateCoordinator):
    """Coordinator to manage VMC Helty data updates."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=config_entry,
        )
        self.config_entry = config_entry
        self.ip = config_entry.data["ip"]
        self.name = config_entry.data["name"]
        self.device_entry: DeviceEntry | None = None
        self._consecutive_errors = 0
        self._max_consecutive_errors = 5
        self._error_recovery_interval = timedelta(seconds=30)
        self._normal_update_interval = DEFAULT_SCAN_INTERVAL
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
        """Return configured room volume from config entry."""
        if self.config_entry is None:
            return DEFAULT_ROOM_VOLUME
        room_volume = self.config_entry.data.get("room_volume")
        if room_volume is None:
            room_volume = self.config_entry.options.get(
                "room_volume", DEFAULT_ROOM_VOLUME
            )
        return float(room_volume or DEFAULT_ROOM_VOLUME)

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

    async def _get_status_data(self) -> str:
        """Get device status data."""
        try:
            return await tcp_send_command(self.ip, DEFAULT_PORT, "VMGH?")
        except VMCTimeoutError as err:
            _LOGGER.warning("Timeout getting status from %s: %s", self.ip, err)
            self._handle_error()
            raise UpdateFailed(f"Timeout communicating with {self.ip}") from err
        except VMCConnectionError as err:
            _LOGGER.exception("Connection error to %s", self.ip)
            if self._consecutive_errors == 0 or self._consecutive_errors % 5 == 0:
                try:
                    diagnostics = await validate_network_connectivity(
                        self.ip, DEFAULT_PORT
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
            raise UpdateFailed(f"Connection error to {self.ip}: {err}") from err

    async def _get_additional_data(self) -> dict[str, str | None]:
        """Get additional device data (sensors, name, network) with smart intervals."""
        responses: dict[str, str | None] = {}
        current_time = time.time()

        # Sensors data - always updated (every 60 seconds)
        try:
            responses["sensors"] = await tcp_send_command(
                self.ip, DEFAULT_PORT, "VMGI?"
            )
        except VMCConnectionError as err:
            _LOGGER.warning("Unable to read sensors from %s: %s", self.ip, err)
            responses["sensors"] = None

        # Device name - updated every 15 minutes
        time_since_name_update = current_time - self._last_name_update
        if time_since_name_update >= DEVICE_NAME_INTERVAL.total_seconds():
            try:
                responses["name"] = await tcp_send_command(
                    self.ip, DEFAULT_PORT, "VMNM?"
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
                    self.ip, DEFAULT_PORT, "VMSL?"
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
        if self.update_interval != self._normal_update_interval:
            self.update_interval = self._normal_update_interval
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

            data = {
                "status": status_response,
                "sensors": additional_data["sensors"],
                "name": additional_data["name"],
                "network": additional_data["network"],
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
            self.update_interval = self._error_recovery_interval
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
