import json
import os
import asyncio

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

async def get_device_name(ip, port=5001, timeout=2):
    """Recupera il nome del dispositivo VMC tramite comando VMGN?."""
    try:
        reader, writer = await asyncio.open_connection(ip, port)
        writer.write(b"VMGN?\r\n")
        await writer.drain()
        data = await asyncio.wait_for(reader.read(128), timeout)
        writer.close()
        await writer.wait_closed()
        if data:
            resp = data.decode("ascii").strip()
            # Parsing risposta: VMGO,<nome>
            if resp.startswith("VMGO,"):
                return resp.split(",", 1)[1]
        return None
    except Exception:
        return None

async def discover_vmc_devices(subnet="192.168.1.", port=5001, timeout=1):
    """Scansiona la subnet e restituisce una lista di IP con VMC attivi."""
    found = []
    tasks = []
    async def check_ip(ip):
        try:
            reader, writer = await asyncio.open_connection(ip, port)
            writer.write(b"VMGH?\r\n")
            await writer.drain()
            data = await asyncio.wait_for(reader.read(64), timeout)
            writer.close()
            await writer.wait_closed()
            if data and data.decode("ascii").startswith("VMGO"):
                found.append(ip)
        except Exception:
            pass
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        tasks.append(check_ip(ip))
    await asyncio.gather(*tasks)
    return found

async def tcp_send_command(ip, port, command, timeout=2):
    """Invia un comando TCP e restituisce la risposta come stringa."""
    try:
        reader, writer = await asyncio.open_connection(ip, port)
        writer.write((command + '\r\n').encode('ascii'))
        await writer.drain()
        data = await asyncio.wait_for(reader.read(256), timeout)
        writer.close()
        await writer.wait_closed()
        return data.decode('ascii').strip()
    except Exception:
        return None
