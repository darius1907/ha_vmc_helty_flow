"""Integrazione VMC Helty Flow per Home Assistant."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_PORT, DOMAIN
from .device_action import async_setup_device_actions
from .device_registry import async_get_or_create_device, async_remove_orphaned_devices
from .helpers import (
    VMCConnectionError,
    VMCTimeoutError,
    tcp_send_command,
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# Definisce le platform supportate dall'integrazione
PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.LIGHT,
    Platform.BUTTON,
    Platform.TEXT,
]

# Intervallo di aggiornamento predefinito
DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)


class VmcHeltyCoordinator(DataUpdateCoordinator):
    """Coordinatore per gestire gli aggiornamenti dei dati VMC Helty."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.config_entry = config_entry
        self.ip = config_entry.data["ip"]
        self.name = config_entry.data["name"]
        self.device_entry = None
        self._consecutive_errors = 0
        self._max_consecutive_errors = 5
        self._error_recovery_interval = timedelta(seconds=30)
        self._normal_update_interval = DEFAULT_SCAN_INTERVAL
        self._recovery_update_interval = timedelta(seconds=60)

    async def _get_status_data(self) -> str:
        """Get device status data."""
        try:
            return await tcp_send_command(self.ip, DEFAULT_PORT, "VMGH?")
        except VMCTimeoutError as err:
            _LOGGER.warning(
                "Timeout durante l'acquisizione dello stato da %s: %s", self.ip, err
            )
            self._handle_error()
            raise UpdateFailed(
                f"Timeout durante la comunicazione con {self.ip}"
            ) from err
        except VMCConnectionError as err:
            _LOGGER.exception("Errore di connessione a %s", self.ip)
            self._handle_error()
            raise UpdateFailed(f"Errore di connessione a {self.ip}: {err}") from err

    async def _get_additional_data(self) -> dict[str, str | None]:
        """Get additional device data (sensors, name, network)."""
        responses = {}

        # Sensors data
        try:
            responses["sensors"] = await tcp_send_command(
                self.ip, DEFAULT_PORT, "VMGI?"
            )
        except VMCConnectionError as err:
            _LOGGER.warning("Impossibile leggere i sensori da %s: %s", self.ip, err)
            responses["sensors"] = None

        # Device name
        try:
            responses["name"] = await tcp_send_command(self.ip, DEFAULT_PORT, "VMNM?")
        except VMCConnectionError as err:
            _LOGGER.warning("Impossibile leggere il nome da %s: %s", self.ip, err)
            responses["name"] = None

        # Network info
        try:
            responses["network"] = await tcp_send_command(
                self.ip, DEFAULT_PORT, "VMSL?"
            )
        except VMCConnectionError as err:
            _LOGGER.warning(
                "Impossibile leggere le info di rete da %s: %s", self.ip, err
            )
            responses["network"] = None

        return responses

    def _handle_successful_update(self) -> None:
        """Handle successful data update."""
        if self._consecutive_errors > 0:
            _LOGGER.info(
                "Ripristinata connessione con %s dopo %d errori consecutivi",
                self.ip,
                self._consecutive_errors,
            )

        self._consecutive_errors = 0
        # Ripristina l'intervallo normale se eravamo in modalità recovery
        if self.update_interval != self._normal_update_interval:
            self.update_interval = self._normal_update_interval
            _LOGGER.info(
                "Ripristinato intervallo normale di aggiornamento per %s", self.ip
            )

    async def _async_update_data(self):
        """Fetch data from VMC device."""

        def _raise_update_failed(status_response: str) -> None:
            """Raise UpdateFailed after handling error."""
            self._handle_error()
            raise UpdateFailed(
                f"Dispositivo {self.ip} non risponde correttamente: "
                f"{status_response}"
            )

        try:
            # Ottiene lo stato del dispositivo
            status_response = await self._get_status_data()

            if not status_response or not status_response.startswith("VMGO"):
                _raise_update_failed(status_response)

            # Ottieni dati aggiuntivi
            additional_data = await self._get_additional_data()

            # Aggiornamento riuscito
            self._handle_successful_update()

            data = {
                "status": status_response,
                "sensors": additional_data["sensors"],
                "name": additional_data["name"],
                "network": additional_data["network"],
                "available": True,
                "last_update": self.hass.loop.time(),
            }

            # Aggiorna il nome del dispositivo se necessario
            self._maybe_update_device_name(additional_data["name"])

        except UpdateFailed:
            # Rilancia le eccezioni UpdateFailed per gestione errori a monte
            raise
        except Exception as err:
            self._handle_error()
            _LOGGER.exception(
                "Errore imprevisto durante l'aggiornamento dei dati per %s",
                self.ip,
            )
            raise UpdateFailed(
                f"Errore durante la comunicazione con {self.ip}: {err}"
            ) from err
        else:
            return data

    def _handle_error(self):
        """Gestisce l'incremento degli errori consecutivi e la logica di ripristino."""
        self._consecutive_errors += 1

        # Log appropriato in base al numero di errori
        if self._consecutive_errors == 1:
            _LOGGER.warning("Errore di comunicazione con %s", self.ip)
        elif self._consecutive_errors == self._max_consecutive_errors:
            _LOGGER.error(
                "Raggiunto il limite di %d errori consecutivi con %s, "
                "passando alla modalità di ripristino",
                self._max_consecutive_errors,
                self.ip,
            )
        elif self._consecutive_errors > self._max_consecutive_errors:
            _LOGGER.debug(
                "Errore consecutivo #%d per %s", self._consecutive_errors, self.ip
            )
        else:
            _LOGGER.info(
                "Errore consecutivo #%d per %s", self._consecutive_errors, self.ip
            )

        # Se abbiamo raggiunto il limite, passa alla modalità di ripristino
        if (
            self._consecutive_errors >= self._max_consecutive_errors
            and self.update_interval != self._error_recovery_interval
        ):
            self.update_interval = self._error_recovery_interval
            _LOGGER.info(
                "Modificato intervallo di aggiornamento per %s a %d secondi "
                "(modalità ripristino)",
                self.ip,
                self._error_recovery_interval.total_seconds(),
            )

    def _maybe_update_device_name(self, name_response):
        """Aggiorna il nome del dispositivo se necessario."""
        if name_response and name_response.startswith("VMNM"):
            try:
                parts = name_response.split(",")
                if len(parts) > 1 and parts[1].strip():
                    new_name = parts[1].strip()
                    # Verifica se il nome è cambiato
                    if new_name != self.name:
                        _LOGGER.info(
                            "Nome dispositivo cambiato da '%s' a '%s'",
                            self.name,
                            new_name,
                        )
                        self.name = new_name
                        # Se siamo in Home Assistant, aggiorna il titolo
                        # del config entry
                        if hasattr(self, "hass") and self.hass:
                            new_data = {**self.config_entry.data, "name": new_name}
                            self.hass.config_entries.async_update_entry(
                                self.config_entry, data=new_data
                            )
            except Exception as err:
                _LOGGER.warning(
                    "Errore durante l'aggiornamento del nome dispositivo: %s", err
                )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up VMC Helty Flow from a config entry."""
    # Inizializza il dominio se non esiste
    hass.data.setdefault(DOMAIN, {})

    # Setup delle device actions (solo una volta per l'integrazione)
    if not hass.data[DOMAIN].get("device_actions_setup"):
        await async_setup_device_actions(hass)
        hass.data[DOMAIN]["device_actions_setup"] = True

    # Crea il coordinatore per questo dispositivo
    coordinator = VmcHeltyCoordinator(hass, entry)

    # Effettua il primo fetch dei dati
    await coordinator.async_config_entry_first_refresh()

    # Registra il dispositivo nel device registry
    coordinator.device_entry = await async_get_or_create_device(hass, coordinator)

    # Salva il coordinatore
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Avvia le piattaforme
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Registra la funzione di aggiornamento opzioni se non già registrata
    if not entry.update_listeners:
        entry.add_update_listener(async_reload_entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove the data stored for this entry
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_remove_config_entry_device(
    _hass: HomeAssistant, config_entry: ConfigEntry, device_entry
) -> bool:
    """Remove a config entry from a device."""
    # Questo metodo viene chiamato quando un dispositivo viene rimosso
    # dall'interfaccia utente
    _LOGGER.info(
        "Removing device %s from config entry %s",
        device_entry.id,
        config_entry.entry_id,
    )

    # Consenti sempre la rimozione del dispositivo
    return True


async def async_remove_entry(hass: HomeAssistant, _entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    # Rimuovi dispositivi orfani dopo la rimozione dell'entry
    await async_remove_orphaned_devices(hass)
