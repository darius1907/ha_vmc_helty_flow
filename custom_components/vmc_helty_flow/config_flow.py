"""Config flow per l'integrazione VMC Helty Flow."""

import contextlib

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .helpers import (
    count_ips_in_subnet,
    discover_vmc_devices_with_progress,
    parse_subnet_for_discovery,
    validate_subnet,
)

# Costanti per i limiti di validazione
MAX_PORT = 65535
MAX_TIMEOUT = 60
MAX_IPS_IN_SUBNET = 254

STORAGE_KEY = f"{DOMAIN}.devices"
STORAGE_VERSION = 1


class VmcHeltyFlowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestisce il flusso di configurazione dell'integrazione VMC Helty."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.subnet = None
        self.port = None
        self.timeout = 10
        self.discovered_devices = []
        self.scan_interrupted = False
        self.progress = 0
        self._store = None

    def _get_store(self) -> Store:
        """Get the storage instance."""
        if self._store is None:
            self._store = Store(self.hass, STORAGE_VERSION, STORAGE_KEY)
        return self._store

    async def _load_devices(self) -> list:
        """Carica la lista dei dispositivi dallo storage di Home Assistant."""
        try:
            data = await self._get_store().async_load()
            return data.get("devices", []) if data else []
        except Exception:
            return []

    async def _save_devices(self, devices: list) -> None:
        """Salva la lista dei dispositivi nello storage di Home Assistant."""
        with contextlib.suppress(Exception):
            await self._get_store().async_save({"devices": devices})

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        existing_devices = await self._load_devices()
        if existing_devices:
            if user_input is None or user_input.get("confirm") is None:
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
        # Se confermato o nessun dispositivo, chiedi subnet, porta e timeout
        if user_input is None or user_input.get("subnet") is None:
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
                    "help": (
                        "Inserisci la subnet in formato CIDR (es. 192.168.1.0/24), "
                        "la porta TCP e il timeout (secondi) per la ricerca dei "
                        "dispositivi Helty."
                    )
                },
            )
        # Validazione subnet/porta
        self.subnet = user_input["subnet"]
        self.port = user_input["port"]
        self.timeout = user_input.get("timeout", 10)
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
        return await self.async_step_discovery()

    async def async_step_discovery(self, user_input=None):
        """Handle device discovery and selection."""
        if user_input:
            return await self._handle_discovery_input(user_input)

        return await self._handle_discovery_display()

    async def _handle_discovery_input(self, user_input):
        """Handle user input in discovery step."""
        # Se l'utente ha selezionato i dispositivi
        if user_input.get("selected_devices"):
            return await self._process_device_selection(user_input)

        # Se c'è una richiesta di interruzione scansione
        if user_input.get("interrupt_scan"):
            return self._handle_scan_interruption()

        return await self._handle_discovery_display()

    async def _handle_discovery_display(self):
        """Handle the display logic for discovery step."""
        # Esegui la scansione se non è già stata fatta
        if not hasattr(self, "discovered_devices"):
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

    def _handle_scan_interruption(self):
        """Handle scan interruption request."""
        self.scan_interrupted = True
        return self.async_show_form(
            step_id="user",
            errors={"base": "scan_interrotta"},
            description_placeholders={
                "help": "Scansione interrotta. Modifica i parametri se necessario."
            },
        )

    async def _perform_device_discovery(self):
        """Perform device discovery."""
        errors = {}
        self.scan_interrupted = False
        devices = []

        try:
            # Avvia la scansione con indicatore di progresso
            devices = await self._discover_devices_async(
                self.subnet, self.port, self.timeout
            )
            self.discovered_devices = devices
        except Exception:
            errors["base"] = "discovery_failed"
            self.discovered_devices = []

        await self._save_devices(devices)

        # Se nessun dispositivo trovato, riproponi configurazione
        if not devices or len(devices) == 0:
            errors["base"] = errors.get("base") or "no_devices_found"
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
                errors=errors,
                description_placeholders={
                    "help": "Nessun dispositivo trovato. "
                    "Modifica la configurazione e riprova."
                },
            )

        return None

    def _show_device_selection_form(self):
        """Show the device selection form."""
        # Mostra il form di selezione dei dispositivi
        devices = self.discovered_devices
        device_options = {d["ip"]: f"{d['name']} ({d['ip']})" for d in devices}
        schema = vol.Schema(
            {
                vol.Required("selected_devices"): cv.multi_select(device_options),
                vol.Optional("interrupt_scan", default=False): bool,
            }
        )

        # Calcola statistiche per il messaggio
        total_scanned = getattr(self, "total_ips_scanned", 0)
        progress_msg = f"Scansione completata ({total_scanned} IP scansionati). "
        progress_msg += f"Trovati {len(devices)} dispositivi. "
        progress_msg += "Seleziona i dispositivi da configurare:"

        return self.async_show_form(
            step_id="discovery",
            data_schema=schema,
            description_placeholders={"help": progress_msg},
        )

    def _update_discovery_progress(self, progress_info):
        """Update discovery progress for UI feedback."""
        self.progress = progress_info.get("progress", 0)
        # Store current progress information for the UI
        self._discovery_progress = {
            "current_ip": progress_info.get("current_ip", ""),
            "devices_found": progress_info.get("devices_found", 0),
            "scanned": progress_info.get("scanned", 0),
            "total": progress_info.get("total", 0),
            "progress": self.progress,
        }

    async def _discover_devices_async(self, subnet, port, timeout):
        """Perform device discovery with progress tracking."""
        self.subnet = subnet
        self.port = port
        self.timeout = timeout
        self.discovered_devices = []
        self._discovery_progress = {}

        # Parsing subnet per determinare il range di IPs
        subnet_base = parse_subnet_for_discovery(subnet)

        # Reset progress tracking
        start_ip = 1
        end_ip = 254
        self.total_ips_scanned = end_ip - start_ip + 1

        # Usa la funzione di discovery con progress indicator
        return await discover_vmc_devices_with_progress(
            subnet=subnet_base,
            port=self.port,
            timeout=self.timeout,
            progress_callback=self._update_discovery_progress,
            interrupt_check=lambda: getattr(self, "_scan_interrupted", False),
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
