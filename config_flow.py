"""
Config flow per l'integrazione VMC Helty Flow
"""
from homeassistant import config_entries
from .const import DOMAIN
from .helpers import discover_vmc_devices, get_device_name
import voluptuous as vol

class VmcHeltyFlowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Salva selezione dispositivi (nome e IP) direttamente in config_entry.data
            selected = user_input["devices"]
            devices = []
            for key in selected:
                ip = key.split("|")[1]
                name = key.split("|")[0]
                devices.append({"ip": ip, "name": name})
            return self.async_create_entry(title="VMC Helty Flow", data={"devices": devices})
        # Discovery automatica
        ips = await discover_vmc_devices()
        if not ips:
            return self.async_show_form(
                step_id="user",
                errors={"base": "no_device_found"}
            )
        # Recupera i nomi
        device_keys = []
        for ip in ips:
            name = await get_device_name(ip)
            if not name:
                name = f"VMC {ip}"
            device_keys.append(f"{name}|{ip}")
        schema = vol.Schema({
            vol.Required("devices", default=device_keys): vol.All(vol.Length(min=1), [vol.In(device_keys)])
        })
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={"count": str(len(device_keys))}
        )
