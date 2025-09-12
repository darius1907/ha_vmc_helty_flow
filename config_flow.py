"""
Config flow per l'integrazione VMC Helty Flow
"""
from homeassistant import config_entries
from .const import DOMAIN
from .helpers import discover_vmc_devices, get_device_name
import voluptuous as vol

class VmcHeltyFlowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        # Step avanzato: subnet e porta
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
        # Passa a step discovery
        return await self.async_step_discovery(user_input)

    async def async_step_discovery(self, user_input):
        subnet = user_input["subnet"]
        port = user_input["port"]
        # Discovery automatica
        ips = await discover_vmc_devices(subnet=subnet, port=port)
        if not ips:
            schema = vol.Schema({})
            return self.async_show_form(
                step_id="discovery",
                data_schema=schema,
                errors={"base": "no_device_found"},
                description_placeholders={
                    "count": "0",
                    "subnet": subnet,
                    "port": str(port),
                    "help": "Nessun dispositivo trovato. Assicurati che i VMC Helty siano accesi, collegati alla rete e che la subnet sia corretta. Premi 'Riprova' per effettuare una nuova scansione."
                }
            )
        # Recupera i nomi
        device_keys = []
        for ip in ips:
            name = await get_device_name(ip, port=port)
            if not name:
                name = f"VMC {ip}"
            device_keys.append(f"{name}|{ip}")
        schema = vol.Schema({
            vol.Required("devices", default=device_keys): vol.All(vol.Length(min=1), [vol.In(device_keys)])
        })
        return self.async_show_form(
            step_id="discovery",
            data_schema=schema,
            description_placeholders={
                "count": str(len(device_keys)),
                "subnet": subnet,
                "port": str(port),
                "help": "Seleziona i dispositivi VMC Helty da integrare. Puoi modificare il nome in seguito."
            },
            last_step=True
        )

    async def async_step_discovery(self, user_input):
        subnet = user_input["subnet"]
        port = user_input["port"]
        # Quando l'utente seleziona i dispositivi
        if "devices" in user_input:
            selected = user_input["devices"]
            devices = []
            for key in selected:
                ip = key.split("|")[1]
                name = key.split("|")[0]
                devices.append({"ip": ip, "name": name})
            return self.async_create_entry(
                title="VMC Helty Flow",
                data={"devices": devices, "subnet": subnet, "port": port}
            )
