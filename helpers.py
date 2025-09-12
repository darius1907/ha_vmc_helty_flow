"""
Helper functions per l'integrazione VMC Helty Flow
"""
import json
import os
import asyncio
from typing import List, Optional, Dict

from .const import DEFAULT_PORT, TCP_TIMEOUT, IP_RANGE_START, IP_RANGE_END

DEVICES_FILE = os.path.join(os.path.dirname(__file__), "devices.json")


def load_devices():
    """Carica la lista dispositivi dal file JSON."""
    if not os.path.exists(DEVICES_FILE):
        return []
    with open(DEVICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_devices(devices):
    """Salva la lista dispositivi nel file JSON."""
    with open(DEVICES_FILE, "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=2)


async def tcp_send_command(ip: str, port: int, command: str) -> Optional[str]:
    """Invia un comando TCP al dispositivo VMC e restituisce la risposta."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=TCP_TIMEOUT
        )

        # Invia il comando
        writer.write(command.encode())
        await writer.drain()

        # Leggi la risposta
        response = await asyncio.wait_for(
            reader.read(1024), timeout=TCP_TIMEOUT
        )

        writer.close()
        await writer.wait_closed()

        return response.decode().strip()
    except Exception:
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
                # VMNM nome_dispositivo
                nome = name_response[5:].strip() if len(name_response) > 5 else f"VMC Helty {ip.split('.')[-1]}"
            else:
                nome = f"VMC Helty {ip.split('.')[-1]}"
            return {
                "ip": ip,
                "name": nome,
                "model": modello,
                "manufacturer": "Helty",
                "available": True
            }
        except Exception:
            pass
    return None


async def discover_vmc_devices(subnet: str = "192.168.1.", port: int = DEFAULT_PORT) -> List[Dict[str, str]]:
    """Scopre i dispositivi VMC sulla rete."""
    devices = []

    # Rimuovi il punto finale se presente
    if subnet.endswith('.'):
        subnet = subnet[:-1]

    # Crea le task per testare tutti gli IP in parallelo
    tasks = []
    for i in range(IP_RANGE_START, IP_RANGE_END + 1):
        ip = f"{subnet}.{i}"
        tasks.append(get_device_info(ip, port))

    # Esegui tutte le task in parallelo
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filtra i risultati validi
    for result in results:
        if isinstance(result, dict) and result is not None:
            devices.append(result)

    return devices


def get_device_name(ip: str) -> str:
    """Restituisce un nome di default per il dispositivo basato sull'IP."""
    return f"VMC Helty {ip.split('.')[-1]}"
