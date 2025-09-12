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
                devices = await discover_vmc_devices(subnet=self.subnet, port=self.port)
                self.discovered_devices = devices

                if not devices:
                    errors["base"] = "no_devices_found"
                else:
                    # Crea le opzioni per la selezione con formato: "Nome (IP)"
                    device_options = {}
                    for device in devices:
                        key = device["ip"]
                        display_name = f"{device['name']} ({device['ip']})"
                        device_options[key] = display_name

                    schema = vol.Schema({
                        vol.Required("selected_devices"): cv.multi_select(device_options)
                    })

                    return self.async_show_form(
                        step_id="discovery",
                        data_schema=schema,
                        errors=errors,
                        description_placeholders={
                            "help": f"Trovati {len(devices)} dispositivi. Seleziona quelli da aggiungere."
                        }
                    )

            except Exception as ex:
                errors["base"] = "discovery_failed"

            # Se ci sono errori, mostra di nuovo la form iniziale
            schema = vol.Schema({
                vol.Required("subnet", default=self.subnet): str,
                vol.Required("port", default=self.port): int
            })
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors
            )

        # L'utente ha selezionato i dispositivi
        selected_ips = user_input["selected_devices"]

        # Crea le entry per ogni dispositivo selezionato
        for ip in selected_ips:
            # Trova il dispositivo corrispondente
            device = next((d for d in self.discovered_devices if d["ip"] == ip), None)
            if device:
                await self.async_set_unique_id(ip)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=device["name"],
                    data={
                        "ip": ip,
                        "port": self.port,
                        "name": device["name"]
                    }
                )

        # Se non ci sono dispositivi selezionati validi
        return self.async_abort(reason="no_devices_selected")
