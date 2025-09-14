"""
Config flow per l'integrazione VMC Helty Flow
"""
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.storage import Store
from .const import DOMAIN
from .helpers import discover_vmc_devices
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

STORAGE_KEY = f"{DOMAIN}.devices"
STORAGE_VERSION = 1

class VmcHeltyFlowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

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
        except Exception as e:
            return []

    async def _save_devices(self, devices: list) -> None:
        """Salva la lista dei dispositivi nello storage di Home Assistant."""
        try:
            await self._get_store().async_save({"devices": devices})
        except Exception as e:
            pass  # Log error se necessario

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        existing_devices = await self._load_devices()
        if existing_devices:
            if user_input is None or user_input.get("confirm") is None:
                schema = vol.Schema({
                    vol.Required("confirm", default=False): bool
                })
                return self.async_show_form(
                    step_id="user",
                    data_schema=schema,
                    description_placeholders={
                        "help": f"Sono già configurati {len(existing_devices)} dispositivi. Vuoi avviare una nuova scansione?"
                    }
                )
            if not user_input["confirm"]:
                device_list = "\n".join([f"{d['name']} ({d['ip']})" for d in existing_devices])
                return self.async_show_form(
                    step_id="user",
                    description_placeholders={
                        "help": f"Dispositivi configurati:\n{device_list}"
                    },
                    errors={"base": "scan_annullata"}
                )
        # Se confermato o nessun dispositivo, chiedi subnet, porta e timeout
        if user_input is None or user_input.get("subnet") is None:
            schema = vol.Schema({
                vol.Required("subnet", default="192.168.1.0/24"): str,
                vol.Required("port", default=5001): int,
                vol.Required("timeout", default=10): int
            })
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                description_placeholders={
                    "help": "Inserisci la subnet in formato CIDR (es. 192.168.1.0/24), la porta TCP e il timeout (secondi) per la ricerca dei dispositivi Helty."
                }
            )
        # Validazione subnet/porta
        self.subnet = user_input["subnet"]
        self.port = user_input["port"]
        self.timeout = user_input.get("timeout", 10)
        errors = {}
        if not self._validate_subnet(self.subnet):
            errors["subnet"] = "subnet_non_valida"
        if not (1 <= self.port <= 65535):
            errors["port"] = "porta_non_valida"
        if not (1 <= self.timeout <= 60):
            errors["timeout"] = "timeout_non_valido"
        ip_count = self._count_ips_in_subnet(self.subnet)
        if ip_count > 254:
            errors["subnet"] = "subnet_troppo_grande"
        if errors:
            schema = vol.Schema({
                vol.Required("subnet", default=self.subnet): str,
                vol.Required("port", default=self.port): int,
                vol.Required("timeout", default=self.timeout): int
            })
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors,
                description_placeholders={
                    "help": "Controlla i parametri inseriti. La subnet deve essere in formato CIDR (es. 192.168.1.0/24) e non deve generare più di 254 IP."
                }
            )
        return await self.async_step_discovery()

    async def async_step_discovery(self, user_input=None):
        """Handle device discovery and selection."""
        # Se l'utente ha selezionato i dispositivi, processa la selezione
        if user_input and user_input.get("selected_devices"):
            selected_ips = user_input["selected_devices"]
            selected_devices = [d for d in self.discovered_devices if d["ip"] in selected_ips]

            # Salva i dispositivi selezionati nello storage
            await self._save_devices(selected_devices)

            # Crea entry separate per ogni dispositivo selezionato
            entries_created = 0
            first_entry = None

            for device in selected_devices:
                # Verifica che non esista già una entry per questo dispositivo
                existing_entries = [
                    entry for entry in self._async_current_entries()
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
                        }
                    )

                    entries_created += 1
                    if first_entry is None:
                        first_entry = entry

            # Se tutti i dispositivi erano già configurati
            if entries_created == 0:
                return self.async_abort(reason="all_devices_already_configured")

            # Ritorna la prima entry creata (Home Assistant gestisce le altre automaticamente)
            return first_entry

        errors = {}
        self.scan_interrupted = False
        devices = []
        try:
            self.progress = 0
            total_ips = self._count_ips_in_subnet(self.subnet)
            # Converte la subnet CIDR nel formato richiesto dalla funzione discover_vmc_devices
            subnet_base = self._parse_subnet_for_discovery(self.subnet)
            discovered_devices = await discover_vmc_devices(subnet=subnet_base, port=self.port, timeout=self.timeout)

            for idx, device in enumerate(discovered_devices):
                if self.scan_interrupted or (user_input and user_input.get("interrupt_scan")):
                    errors["base"] = "scan_interrotta"
                    break
                devices.append(device)
                self.progress = int((idx + 1) / len(discovered_devices) * 100)

            self.discovered_devices = devices
        except Exception as ex:
            errors["base"] = "discovery_failed"

        await self._save_devices(devices)

        if not devices or len(devices) == 0:
            errors["base"] = errors.get("base") or "no_devices_found"
            schema = vol.Schema({
                vol.Required("subnet", default=self.subnet): str,
                vol.Required("port", default=self.port): int,
                vol.Required("timeout", default=self.timeout): int
            })
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors,
                description_placeholders={
                    "help": "Errore nella scansione. Riprova."
                }
            )

        # Solo se ci sono dispositivi, mostra la selezione
        device_options = {d["ip"]: f"{d['name']} ({d['ip']})" for d in devices}
        schema = vol.Schema({
            vol.Required("selected_devices"): cv.multi_select(device_options),
            vol.Optional("interrupt_scan", default=False): bool
        })
        return self.async_show_form(
            step_id="discovery",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "help": f"Scansione completata. Trovati {len(devices)} dispositivi. Seleziona i dispositivi da configurare:"
            }
        )

    async def async_step_import(self, import_info):
        """Handle import from configuration.yaml (se supportato)."""
        return await self.async_step_user(import_info)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return VmcHeltyOptionsFlowHandler(config_entry)

    def _validate_subnet(self, subnet):
        """Valida se la subnet è in formato CIDR valido (es. 192.168.1.0/24)."""
        import re
        import ipaddress

        # Pattern per formato CIDR
        cidr_pattern = r"^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$"

        if not re.match(cidr_pattern, subnet):
            return False

        try:
            # Verifica che sia una rete IP valida
            network = ipaddress.IPv4Network(subnet, strict=False)
            # Controlla che sia una subnet privata o locale
            return (network.is_private or
                   str(network.network_address).startswith('127.') or
                   str(network.network_address).startswith('169.254.'))
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            return False

    def _count_ips_in_subnet(self, subnet):
        """Conta quanti IP sono disponibili nella subnet CIDR."""
        try:
            import ipaddress
            network = ipaddress.IPv4Network(subnet, strict=False)
            # Restituisce il numero di host disponibili (esclude network e broadcast)
            return network.num_addresses - 2
        except:
            return 0

    def _parse_subnet_for_discovery(self, subnet):
        """Converte la subnet CIDR in formato utilizzabile per la discovery."""
        try:
            import ipaddress
            network = ipaddress.IPv4Network(subnet, strict=False)
            # Restituisce la base della rete (es. da 192.168.1.0/24 -> "192.168.1.")
            base_ip = str(network.network_address)
            parts = base_ip.split('.')
            return '.'.join(parts[:3]) + '.'
        except:
            return "192.168.1."


class VmcHeltyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle VMC Helty Flow options."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize VMC Helty Flow options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the VMC Helty Flow options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Optional(
                "scan_interval",
                default=self.config_entry.options.get("scan_interval", 60)
            ): vol.All(vol.Coerce(int), vol.Range(min=30, max=600)),
            vol.Optional(
                "timeout",
                default=self.config_entry.options.get("timeout", 10)
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
            vol.Optional(
                "retry_attempts",
                default=self.config_entry.options.get("retry_attempts", 3)
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={
                "help": "Configura le opzioni avanzate per l'integrazione VMC Helty Flow."
            }
        )
