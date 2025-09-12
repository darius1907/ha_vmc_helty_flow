"""
Config flow per l'integrazione VMC Helty Flow
"""
from homeassistant import config_entries
from .const import DOMAIN
from .helpers import discover_vmc_devices, get_device_name
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

class VmcHeltyFlowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.subnet = None
        self.port = None
        self.discovered_devices = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            schema = vol.Schema({
                vol.Required("subnet", default="192.168.1."): str,
                vol.Required("port", default=5001): int
            })
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                description_placeholders={
                    "help": "Inserisci la subnet e la porta TCP per la ricerca dei dispositivi Helty."
                }
            )

        # Salva i parametri per il prossimo step
        self.subnet = user_input["subnet"]
        self.port = user_input["port"]

        # Passa al discovery
        return await self.async_step_discovery()

    async def async_step_discovery(self, user_input=None):
        """Handle device discovery and selection."""
        errors = {}

        if user_input is None:
            # Prima volta: esegui discovery
            try:
                ips = await discover_vmc_devices(subnet=self.subnet, port=self.port)

                if not ips:
                    return self.async_show_form(
                        step_id="discovery",
                        data_schema=vol.Schema({}),
                        errors={"base": "no_devices_found"},
                        description_placeholders={
                            "subnet": self.subnet,
                            "port": str(self.port)
                        }
                    )

                # Recupera i nomi dei dispositivi
                self.discovered_devices = []
                for ip in ips:
                    try:
                        name = await get_device_name(ip, port=self.port)
                        if not name:
                            name = f"VMC {ip}"
                        self.discovered_devices.append({"ip": ip, "name": name})
                    except Exception:
                        # Se non riusciamo a ottenere il nome, usa l'IP
                        self.discovered_devices.append({"ip": ip, "name": f"VMC {ip}"})

                # Crea le opzioni per la selezione
                device_options = {}
                for device in self.discovered_devices:
                    key = f"{device['ip']}"
                    device_options[key] = f"{device['name']} ({device['ip']})"

                schema = vol.Schema({
                    vol.Required("selected_devices", default=list(device_options.keys())):
                    vol.All(cv.multi_select(device_options), vol.Length(min=1))
                })

                return self.async_show_form(
                    step_id="discovery",
                    data_schema=schema,
                    description_placeholders={
                        "count": str(len(self.discovered_devices)),
                        "subnet": self.subnet,
                        "port": str(self.port)
                    }
                )

            except Exception as e:
                errors["base"] = "cannot_connect"
                return self.async_show_form(
                    step_id="discovery",
                    data_schema=vol.Schema({}),
                    errors=errors,
                    description_placeholders={
                        "subnet": self.subnet,
                        "port": str(self.port)
                    }
                )
        else:
            # L'utente ha selezionato i dispositivi
            try:
                selected_ips = user_input["selected_devices"]
                selected_devices = []

                for device in self.discovered_devices:
                    if device["ip"] in selected_ips:
                        selected_devices.append(device)

                # Crea l'entry di configurazione
                return self.async_create_entry(
                    title="VMC Helty Flow",
                    data={
                        "devices": selected_devices,
                        "subnet": self.subnet,
                        "port": self.port
                    }
                )

            except Exception as e:
                errors["base"] = "unknown"
                schema = vol.Schema({
                    vol.Required("selected_devices"): vol.All(cv.multi_select({}), vol.Length(min=1))
                })
                return self.async_show_form(
                    step_id="discovery",
                    data_schema=schema,
                    errors=errors
                )
