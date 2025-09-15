"""Discovery service for VMC Helty Flow devices."""

import asyncio
import logging
from ipaddress import IPv4Network
from typing import Any

from homeassistant.components import network
from homeassistant.core import HomeAssistant

from .const import DEFAULT_PORT, TCP_TIMEOUT

_LOGGER = logging.getLogger(__name__)


async def async_discover_devices(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Discover Helty Flow devices in the network."""
    _LOGGER.debug("Starting discovery of Helty Flow devices")
    devices = []

    # Ottiene le interfacce di rete disponibili
    adapters = await network.async_get_adapters(hass)
    ipv4_addresses = []

    for adapter in adapters:
        if adapter["enabled"] and adapter["ipv4"]:
            for ip_info in adapter["ipv4"]:
                if ip_info["address"] and ip_info["network_prefix"]:
                    try:
                        network_obj = IPv4Network(
                            f"{ip_info['address']}/{ip_info['network_prefix']}",
                            strict=False,
                        )
                        ipv4_addresses.append((adapter["name"], network_obj))
                    except ValueError:
                        continue

    if not ipv4_addresses:
        _LOGGER.warning("No valid IPv4 network interfaces found")
        return []

    # Esegue la scansione su tutte le interfacce di rete
    for adapter_name, network_obj in ipv4_addresses:
        _LOGGER.debug("Scanning network %s on adapter %s", network_obj, adapter_name)

        # Limita la scansione a 254 host per evitare un uso eccessivo di risorse
        hosts = list(network_obj.hosts())[:254]

        # Usa asyncio.gather per eseguire le scansioni in parallelo
        tasks = []
        for host in hosts:
            tasks.append(check_helty_device(str(host)))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue

            if result:  # Device trovato
                ip = str(hosts[i])
                _LOGGER.info("Found Helty Flow device at IP: %s", ip)

                # Ottieni il nome del dispositivo
                try:
                    device_name = await get_device_name(ip)
                    devices.append(
                        {
                            "ip": ip,
                            "name": device_name or f"Helty Flow {ip}",
                            "model": "Flow",
                            "manufacturer": "Helty",
                        }
                    )
                except Exception as err:
                    _LOGGER.error("Error getting device info for %s: %s", ip, err)

    _LOGGER.debug("Discovery completed, found %d devices", len(devices))
    return devices


async def check_helty_device(ip: str) -> bool:
    """Check if a Helty device is available at the given IP."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, DEFAULT_PORT), timeout=TCP_TIMEOUT
        )

        writer.write(b"VMGH?\r\n")
        await writer.drain()

        response = await asyncio.wait_for(reader.readline(), timeout=TCP_TIMEOUT)
        writer.close()
        await writer.wait_closed()

        return response.startswith(b"VMGO")
    except (TimeoutError, ConnectionRefusedError, OSError):
        return False


async def get_device_name(ip: str) -> str:
    """Get the name of a Helty device."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, DEFAULT_PORT), timeout=TCP_TIMEOUT
        )

        writer.write(b"VMNM?\r\n")
        await writer.drain()

        response = await asyncio.wait_for(reader.readline(), timeout=TCP_TIMEOUT)
        writer.close()
        await writer.wait_closed()

        if response.startswith(b"VMNM"):
            parts = response.decode("utf-8").strip().split(",")
            if len(parts) > 1:
                return parts[1]

        return ""
    except (TimeoutError, ConnectionRefusedError, OSError):
        return ""
