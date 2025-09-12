from .fan import VmcHeltyFan
from .sensor import VmcHeltySensor, VmcHeltyOnOffSensor, VmcHeltyResetFilterButton, VmcHeltyNameText
from .switch import VmcHeltyModeSwitch, VmcHeltyPanelLedSwitch
from .light import VmcHeltyLight
from .light_timer import VmcHeltyLightTimer


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup delle entità VMC Helty Flow."""
    devices = config_entry.data.get("devices", [])
    entities = []
    for dev in devices:
        ip = dev["ip"]
        name = dev["name"]
        entities.append(VmcHeltyFan(ip, name))
        entities.append(VmcHeltySensor(ip, name, "Temperatura Interna"))
        entities.append(VmcHeltySensor(ip, name, "Temperatura Esterna"))
        entities.append(VmcHeltySensor(ip, name, "Umidità"))
        entities.append(VmcHeltySensor(ip, name, "CO2"))
        entities.append(VmcHeltySensor(ip, name, "VOC"))
        entities.append(VmcHeltyModeSwitch(ip, name, "hyperventilation"))
        entities.append(VmcHeltyModeSwitch(ip, name, "night"))
        entities.append(VmcHeltyModeSwitch(ip, name, "free_cooling"))
        entities.append(VmcHeltyPanelLedSwitch(ip, name))
        entities.append(VmcHeltyLight(ip, name))
        entities.append(VmcHeltyLightTimer(ip, name))
        entities.append(VmcHeltyOnOffSensor(ip, name))
        entities.append(VmcHeltyResetFilterButton(ip, name))
        entities.append(VmcHeltyNameText(ip, name))
    async_add_entities(entities)
    return True
