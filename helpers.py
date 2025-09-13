"""
Helper functions per l'integrazione VMC Helty Flow
"""
import json
import os
import asyncio
import logging
from typing import List, Optional, Dict

from const import DEFAULT_PORT, TCP_TIMEOUT, IP_RANGE_START, IP_RANGE_END

async def tcp_send_command(ip: str, port: int, command: str) -> Optional[str]:
    """Invia un comando TCP al dispositivo VMC e restituisce la risposta."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=TCP_TIMEOUT
        )
        writer.write(command.encode())
        await writer.drain()
        response = await asyncio.wait_for(
            reader.read(1024), timeout=TCP_TIMEOUT
        )
        writer.close()
        await writer.wait_closed()
        return response.decode().strip()
    except Exception as e:
        logging.error(f"Errore TCP su {ip}:{port} comando {command}: {e}")
        return None


async def get_device_info(ip: str, port: int = DEFAULT_PORT) -> Optional[Dict[str, str]]:
    """Recupera le informazioni del dispositivo VMC."""
    response = await tcp_send_command(ip, port, "VMGH?")
    if response and response.startswith("VMGO"):
        try:
            parts = response.split(",")
            modello = parts[1] if len(parts) > 1 else "VMC Flow"
            # Recupera il nome mnemonico con VMNM?
            name_response = await tcp_send_command(ip, port, "VMNM?")
            if name_response and name_response.startswith("VMNM"):
                nome = name_response[5:].strip() if len(name_response) > 5 else f"VMC Helty {ip.split('.')[-1]}"
            else:
                nome = f"VMC Helty {ip.split('.')[-1]}"
            # Estendibile: aggiungi altri parametri qui (es. firmware, stato filtri)
            return {
                "ip": ip,
                "name": nome,
                "model": modello,
                "manufacturer": "Helty",
                "available": True
            }
        except Exception as e:
            logging.error(f"Errore parsing info dispositivo {ip}: {e}")
    return None


async def discover_vmc_devices(subnet: str = "192.168.1.", port: int = DEFAULT_PORT) -> List[Dict[str, str]]:
    """Scopre i dispositivi VMC sulla rete."""
    devices = []
    if subnet.endswith('.'):
        subnet = subnet[:-1]
    tasks = []
    for i in range(IP_RANGE_START, IP_RANGE_END + 1):
        ip = f"{subnet}.{i}"
        tasks.append(get_device_info(ip, port))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Filtra e deduplica i risultati validi per IP
    seen_ips = set()
    for result in results:
        if isinstance(result, dict) and result is not None:
            if result["ip"] not in seen_ips:
                devices.append(result)
                seen_ips.add(result["ip"])
    return devices


def get_device_name(ip: str) -> str:
    """Restituisce un nome di default per il dispositivo basato sull'IP."""
    return f"VMC Helty {ip.split('.')[-1]}"


def parse_vmsl_response(response: str):
    """Parsa la risposta VMSL? e restituisce SSID e password senza padding."""
    if not response or len(response) < 64:
        return "", ""
    ssid = response[:32].replace("*", "").strip()
    password = response[32:64].replace("*", "").strip()
    return ssid, password
