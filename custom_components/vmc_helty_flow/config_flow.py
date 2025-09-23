"""Config flow per l'integrazione VMC Helty Flow."""

import contextlib
import ipaddress
import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.storage import Store

from .const import DOMAIN, IP_NETWORK_PREFIX
from .helpers import discover_vmc_devices, get_device_info
from .helpers_net import (
    count_ips_in_subnet,
    parse_subnet_for_discovery,
    validate_subnet,
)

# Costanti per i limiti di validazione
MAX_PORT = 65535
MAX_TIMEOUT = 60
MAX_IPS_IN_SUBNET = 254

STORAGE_KEY = f"{DOMAIN}.devices"
STORAGE_VERSION = 1

_LOGGER = logging.getLogger(__name__)


class VmcHeltyFlowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestisce il flusso di configurazione dell'integrazione VMC Helty."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.subnet = None
        self.port = None
        self.timeout = 10
        self.discovered_devices = []
        self._store = None

        # New attributes for incremental scan
        self.scan_mode = "incremental"  # Always incremental for better UX
        self.current_ip_index = 0
        self.ip_range = []  # List of IPs to scan
        self.scan_in_progress = False
        self.found_devices_session = []  # Devices found in current session
        self.total_ips_to_scan = 0
        self.current_found_device = None
        self.pending_continue = False  # Track if continue after entry creation

    def _get_store(self) -> Store:
        """Ottieni l'istanza del store per i dispositivi."""
        if self._store is None:
            self._store = Store(self.hass, STORAGE_VERSION, STORAGE_KEY)
        return self._store

    async def _load_devices(self) -> list[dict[str, Any]]:
        """Carica la lista dei dispositivi dallo storage di Home Assistant."""
        try:
            data = await self._get_store().async_load()
        except Exception:
            return []
        else:
            devices: list[dict[str, Any]] = data.get("devices", []) if data else []
            return devices

    async def _save_devices(self, devices: list) -> None:
        """Salva la lista dei dispositivi nello storage di Home Assistant."""
        with contextlib.suppress(Exception):
            await self._get_store().async_save({"devices": devices})

    def _create_config_form(self, help_text=None):
        """Create the configuration form for subnet, port, and timeout."""
        schema = vol.Schema(
            {
                vol.Required("subnet", default="192.168.1.0/24"): str,
                vol.Required("port", default=5001): int,
                vol.Required("timeout", default=10): int,
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "help": help_text
                or (
                    "Inserisci la subnet in formato CIDR (es. 192.168.1.0/24), "
                    "la porta TCP e il timeout (secondi) per la ricerca dei "
                    "dispositivi Helty."
                )
            },
        )

    def _create_confirmation_form(self, existing_devices):
        """Create the confirmation form for new scan."""
        schema = vol.Schema({vol.Required("confirm", default=False): bool})
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "help": (
                    f"Sono già configurati {len(existing_devices)} "
                    "dispositivi. Vuoi avviare una nuova scansione?"
                )
            },
        )

    async def _handle_first_request(self, existing_devices):
        """Handle the first request without user input."""
        if existing_devices:
            return self._create_confirmation_form(existing_devices)
        return self._create_config_form()

    async def _handle_confirmation_input(self, user_input, existing_devices):
        """Handle confirmation input when devices exist."""
        if not user_input["confirm"]:
            device_list = "\n".join(
                [f"{d['name']} ({d['ip']})" for d in existing_devices]
            )
            return self.async_show_form(
                step_id="user",
                description_placeholders={
                    "help": f"Dispositivi configurati:\n{device_list}"
                },
                errors={"base": "scan_annullata"},
            )
        return self._create_config_form()

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        existing_devices = await self._load_devices()

        # Prima richiesta senza input
        if user_input is None:
            return await self._handle_first_request(existing_devices)

        # Gestione conferma se ci sono dispositivi esistenti
        if existing_devices and "confirm" in user_input:
            return await self._handle_confirmation_input(user_input, existing_devices)

        # Validazione dati di configurazione
        if "subnet" not in user_input:
            return self._create_config_form()
        # Validazione subnet/porta
        self.subnet = user_input["subnet"]
        self.port = user_input["port"]
        self.timeout = user_input.get("timeout", 10)
        self.scan_mode = "incremental"  # Always incremental
        errors = {}
        if not validate_subnet(self.subnet):
            errors["subnet"] = "subnet_non_valida"
        if not (1 <= self.port <= MAX_PORT):
            errors["port"] = "porta_non_valida"
        if not (1 <= self.timeout <= MAX_TIMEOUT):
            errors["timeout"] = "timeout_non_valido"
        ip_count = count_ips_in_subnet(self.subnet)
        if ip_count > MAX_IPS_IN_SUBNET:
            errors["subnet"] = "subnet_troppo_grande"
        if errors:
            schema = vol.Schema(
                {
                    vol.Required("subnet", default=self.subnet): str,
                    vol.Required("port", default=self.port): int,
                    vol.Required("timeout", default=self.timeout): int,
                    vol.Required("scan_mode", default=self.scan_mode): vol.In(
                        ["full", "incremental"]
                    ),
                }
            )
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors,
                description_placeholders={
                    "help": (
                        "Controlla i parametri inseriti. La subnet deve essere in "
                        "formato CIDR (es. 192.168.1.0/24) e non deve generare "
                        "più di 254 IP."
                    )
                },
            )

        # Se non ci sono errori, procedi direttamente con la discovery
        _LOGGER.info(
            "Parametri validati: subnet=%s, port=%s, timeout=%s, scan_mode=%s",
            self.subnet,
            self.port,
            self.timeout,
            self.scan_mode,
        )

        # Always use incremental scan for better UX
        return await self._start_incremental_scan()

    async def async_step_discovery(self, user_input=None):
        """Handle device discovery and selection."""
        if user_input:
            errors: dict[str, str] = {}
            return await self._handle_discovery_input(user_input, errors)

        return await self._handle_discovery_display()

    async def _handle_discovery_input(self, user_input, _errors):
        """Handle discovery step input."""
        if "selected_devices" in user_input:
            return await self._process_device_selection(user_input)

        # Se non ci sono dispositivi selezionati, torna al form
        return self._show_device_selection_form()

    async def _perform_device_discovery(self):
        """Esegue la discovery direttamente senza step intermedio."""
        _LOGGER.info("Inizio discovery diretta...")

        try:
            # Esegui la discovery con callback di progresso
            discovered_devices = await self._discover_devices_async(
                self.subnet, self.port, self.timeout
            )

            _LOGGER.info(
                "Discovery completata, trovati %d dispositivi", len(discovered_devices)
            )

            if not discovered_devices:
                # Nessun dispositivo trovato, torna alla configurazione
                schema = vol.Schema(
                    {
                        vol.Required("subnet", default=self.subnet): str,
                        vol.Required("port", default=self.port): int,
                        vol.Required("timeout", default=self.timeout): int,
                    }
                )
                return self.async_show_form(
                    step_id="user",
                    data_schema=schema,
                    errors={"base": "nessun_dispositivo_trovato"},
                    description_placeholders={
                        "help": (
                            "Nessun dispositivo VMC Helty trovato nella rete. "
                            "Verifica la subnet, porta e timeout, poi riprova."
                        )
                    },
                )

            # Salva i dispositivi scoperti
            self.discovered_devices = discovered_devices
            await self._save_devices(discovered_devices)

            # Vai direttamente al form di selezione dispositivi
            return self._show_device_selection_form()

        except Exception:
            _LOGGER.exception("Errore durante la discovery")
            schema = vol.Schema(
                {
                    vol.Required("subnet", default=self.subnet): str,
                    vol.Required("port", default=self.port): int,
                    vol.Required("timeout", default=self.timeout): int,
                }
            )
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors={"base": "errore_discovery"},
                description_placeholders={
                    "help": (
                        "Errore durante la scansione della rete. "
                        "Verifica i parametri e riprova."
                    )
                },
            )

    async def _handle_discovery_display(self):
        """Handle the display logic for discovery step."""
        # Esegui la scansione se non è già stata fatta
        if not hasattr(self, "discovered_devices") or not self.discovered_devices:
            return await self._perform_device_discovery()

        # Mostra il form di selezione dei dispositivi
        return self._show_device_selection_form()

    async def _process_device_selection(self, user_input):
        """Process the user's device selection."""
        selected_ips = user_input["selected_devices"]
        selected_devices = [
            d for d in self.discovered_devices if d["ip"] in selected_ips
        ]

        # Salva i dispositivi selezionati nello storage
        await self._save_devices(selected_devices)

        # Crea entry separate per ogni dispositivo selezionato
        entries_created = 0
        first_entry = None

        for device in selected_devices:
            # Verifica che non esista già una entry per questo dispositivo
            existing_entries = [
                entry
                for entry in self._async_current_entries()
                if entry.data.get("ip") == device["ip"]
            ]

            if not existing_entries:
                await self.async_set_unique_id(device["ip"])
                try:
                    self._abort_if_unique_id_configured()
                except Exception:
                    # Se già configurato, salta questo dispositivo
                    continue

                # Crea entry separata per ogni dispositivo
                entry = self.async_create_entry(
                    title=device["name"],
                    data={
                        "ip": device["ip"],
                        "name": device["name"],
                        "model": device.get("model", "VMC Flow"),
                        "manufacturer": device.get("manufacturer", "Helty"),
                    },
                )

                entries_created += 1
                if first_entry is None:
                    first_entry = entry

        # Se tutti i dispositivi erano già configurati
        if entries_created == 0:
            return self.async_abort(reason="all_devices_already_configured")

        # Ritorna la prima entry creata (Home Assistant gestisce le altre
        # automaticamente)
        return first_entry

    def _show_device_selection_form(self):
        """Show the device selection form."""
        devices = self.discovered_devices
        device_options = {d["ip"]: f"{d['name']} ({d['ip']})" for d in devices}

        schema = vol.Schema(
            {
                vol.Required("selected_devices"): cv.multi_select(device_options),
            }
        )

        # Calcola statistiche per il messaggio
        total_scanned = getattr(self, "total_ips_scanned", 0)
        progress_msg = (
            f"Scansione completata! Analizzati {total_scanned} indirizzi IP. "
            f"Trovati {len(devices)} dispositivi VMC Helty. "
            "Seleziona i dispositivi da aggiungere a Home Assistant:"
        )

        return self.async_show_form(
            step_id="discovery",
            data_schema=schema,
            description_placeholders={"help": progress_msg},
        )

    async def _discover_devices_async(self, subnet, port, timeout):
        """Perform device discovery with progress tracking."""
        self.subnet = subnet
        self.port = port
        self.timeout = timeout
        self.discovered_devices = []

        # Parsing subnet per determinare il range di IPs
        subnet_base = parse_subnet_for_discovery(subnet)

        # Reset progress tracking
        start_ip = 1
        end_ip = 254
        self.total_ips_scanned = end_ip - start_ip + 1

        # Usa la funzione di discovery standard per velocizzare
        _LOGGER.info("Usando discovery standard")
        return await discover_vmc_devices(
            subnet=subnet_base,
            port=self.port,
            timeout=self.timeout,
        )

    def _generate_ip_range(self, subnet: str) -> list[str]:
        """Generate list of IP addresses to scan from subnet."""
        try:
            network = ipaddress.IPv4Network(subnet, strict=False)
            # Skip network and broadcast addresses for /24 networks
            if network.prefixlen >= IP_NETWORK_PREFIX:
                return [str(ip) for ip in network.hosts()]
            # For larger networks, scan a reasonable range
            return [str(ip) for ip in list(network.hosts())[:254]]
        except ValueError:
            _LOGGER.exception("Invalid subnet format: %s", subnet)
            return []

    async def _start_incremental_scan(self) -> dict[str, Any]:
        """Start incremental device scanning."""
        _LOGGER.info("Starting incremental scan on subnet %s", self.subnet)

        # Generate IP range to scan
        self.ip_range = self._generate_ip_range(self.subnet)
        self.total_ips_to_scan = len(self.ip_range)
        self.current_ip_index = 0
        self.scan_in_progress = True
        self.found_devices_session = []

        if not self.ip_range:
            return self.async_show_form(
                step_id="user",
                errors={"subnet": "subnet_non_valida"},
                description_placeholders={
                    "help": "Impossibile generare il range di IP dalla subnet fornita."
                },
            )

        _LOGGER.info("Generated %d IPs to scan", self.total_ips_to_scan)

        # Start scanning
        return await self._scan_next_ip()

    async def _scan_next_ip(self) -> dict[str, Any] | None:
        """Scan the next IP in the range. Returns device info if found."""
        while self.current_ip_index < len(self.ip_range):
            current_ip = self.ip_range[self.current_ip_index]
            _LOGGER.debug(
                "Scanning IP %s (%d/%d)",
                current_ip,
                self.current_ip_index + 1,
                self.total_ips_to_scan,
            )

            try:
                # Try to get device info from this IP
                device_info = await get_device_info(current_ip, self.port, self.timeout)

                if device_info:
                    _LOGGER.info(
                        "Device found at %s: %s",
                        current_ip,
                        device_info.get("name", "Unknown"),
                    )
                    self.current_found_device = device_info

                    # Move to next IP for next scan
                    self.current_ip_index += 1

                    # Go to device found step
                    return await self.async_step_device_found()

            except Exception as err:
                _LOGGER.debug("No device at %s: %s", current_ip, err)

            # Move to next IP
            self.current_ip_index += 1

        # Scan completed - no more IPs to scan
        _LOGGER.info(
            "Incremental scan completed. Found %d devices.",
            len(self.found_devices_session),
        )
        return await self._finalize_incremental_scan()

    async def _finalize_incremental_scan(self) -> dict[str, Any]:
        """Finalize incremental scan and proceed to completion."""
        self.scan_in_progress = False

        if not self.found_devices_session:
            # No devices found during incremental scan
            return self.async_show_form(
                step_id="user",
                errors={"base": "nessun_dispositivo_trovato"},
                description_placeholders={
                    "help": (
                        f"Scansione completata. Nessun dispositivo VMC Helty "
                        f"trovato su {self.total_ips_to_scan} indirizzi IP."
                    )
                },
            )

        # Save found devices for reference
        self.discovered_devices = self.found_devices_session
        await self._save_devices(self.discovered_devices)

        # All devices should have been created during scan
        # Complete the flow by aborting with success message
        device_count = len(self.found_devices_session)
        return self.async_abort(
            reason="devices_configured_successfully",
            description_placeholders={
                "device_count": str(device_count),
                "help": (
                    f"Scansione completata! {device_count} dispositivo/i "
                    "VMC Helty configurato/i con successo."
                ),
            },
        )

    async def async_step_device_found(self, user_input=None):
        """Handle when a device is found during incremental scan."""
        if user_input is None:
            # Show device info and options
            device = self.current_found_device

            # Calculate progress
            # Include current device in count
            current_found_count = len(self.found_devices_session) + 1
            # Progress string without percentage (static info)
            progress_str = f"IP {self.current_ip_index} di {self.total_ips_to_scan}"

            schema = vol.Schema(
                {
                    vol.Required("action"): vol.In(
                        [
                            "add_continue",  # Add device and continue scanning
                            "skip_continue",  # Skip device and continue scanning
                            "add_stop",  # Add device and stop scanning
                            "stop_scan",  # Stop scanning without adding
                        ]
                    )
                }
            )

            return self.async_show_form(
                step_id="device_found",
                data_schema=schema,
                description_placeholders={
                    "device_name": device.get("name", "Dispositivo sconosciuto"),
                    "device_ip": device["ip"],
                    "device_model": device.get("model", "VMC Flow"),
                    "progress": progress_str,
                    "found_count": str(current_found_count),
                },
            )

        # Handle user choice
        action = user_input["action"]
        device = self.current_found_device

        if action in ["add_continue", "add_stop"]:
            # Create entry and show popup for both actions
            _LOGGER.info("Creating entry for device %s", device["ip"])

            # Check if device is already configured
            existing_entries = [
                entry
                for entry in self._async_current_entries()
                if entry.data.get("ip") == device["ip"]
            ]

            if not existing_entries:
                # Set unique ID for this device
                await self.async_set_unique_id(device["ip"])
                try:
                    self._abort_if_unique_id_configured()
                except Exception:
                    _LOGGER.warning("Device %s already configured", device["ip"])

                # Store the action for post-creation logic
                self.pending_continue = (action == "add_continue")
                
                # Create entry in this flow - this will show the popup for both actions
                return self.async_create_entry(
                    title=device["name"],
                    data={
                        "ip": device["ip"],
                        "name": device["name"],
                        "model": device.get("model", "VMC Flow"),
                        "manufacturer": device.get("manufacturer", "Helty"),
                        "port": self.port,
                        "timeout": self.timeout,
                    },
                )

            # Add to session for tracking
            self.found_devices_session.append(device)

        if action in ["add_stop", "stop_scan"]:
            # Stop scanning
            _LOGGER.info("Scan stopped by user choice: %s", action)
            return await self._finalize_incremental_scan()

        # Continue scanning
        return await self._scan_next_ip()

    async def async_step_discovered_device(self, discovery_info):
        """Handle automatic device discovery from incremental scan."""
        if not discovery_info:
            return self.async_abort(reason="invalid_discovery_info")

        # Set unique_id for this device
        await self.async_set_unique_id(discovery_info["ip"])
        self._abort_if_unique_id_configured()

        # Create entry for this device
        return self.async_create_entry(
            title=discovery_info["name"],
            data={
                "ip": discovery_info["ip"],
                "name": discovery_info["name"],
                "model": discovery_info.get("model", "VMC Flow"),
                "manufacturer": discovery_info.get("manufacturer", "Helty"),
                "port": discovery_info.get("port", 5001),
                "timeout": discovery_info.get("timeout", 10),
            },
        )

    async def async_step_import(self, import_info):
        """Handle import from configuration.yaml (se supportato)."""
        return await self.async_step_user(import_info)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return VmcHeltyOptionsFlowHandler(config_entry)


class VmcHeltyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle VMC Helty Flow options."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize VMC Helty Flow options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the VMC Helty Flow options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    "scan_interval",
                    default=self.config_entry.options.get("scan_interval", 60),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=600)),
                vol.Optional(
                    "timeout", default=self.config_entry.options.get("timeout", 10)
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
                vol.Optional(
                    "retry_attempts",
                    default=self.config_entry.options.get("retry_attempts", 3),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={
                "help": (
                    "Configura le opzioni avanzate per l'integrazione VMC Helty Flow."
                )
            },
        )
