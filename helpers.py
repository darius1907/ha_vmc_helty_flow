"""
Helper functions per l'integrazione VMC Helty Flow
"""
import asyncio
import logging
import socket
from typing import List, Optional, Dict, Tuple

from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_PORT, TCP_TIMEOUT, IP_RANGE_START, IP_RANGE_END

_LOGGER = logging.getLogger(__name__)

class VMCConnectionError(HomeAssistantError):
    """Errore di connessione al dispositivo VMC."""

class VMCTimeoutError(VMCConnectionError):
    """Timeout durante la comunicazione con il dispositivo VMC."""

class VMCResponseError(HomeAssistantError):
    """Errore nella risposta dal dispositivo VMC."""

class VMCProtocolError(VMCResponseError):
    """Errore di protocollo nella comunicazione con VMC."""


async def tcp_send_command(ip: str, port: int, command: str, timeout: int = None) -> str:
    """Invia un comando TCP al dispositivo VMC e restituisce la risposta.

    Args:
        ip: Indirizzo IP del dispositivo
        port: Porta TCP del dispositivo
        command: Comando da inviare (senza terminatori)
        timeout: Timeout in secondi (usa il default se None)

    Returns:
        La risposta dal dispositivo come stringa

    Raises:
        VMCConnectionError: Se non è possibile connettersi al dispositivo
        VMCTimeoutError: Se la comunicazione ha un timeout
        VMCResponseError: Se c'è un errore nella risposta
    """
    if timeout is None:
        timeout = TCP_TIMEOUT

    # Assicura che il comando termini con CRLF
    if not command.endswith("\r\n"):
        command += "\r\n"

    try:
        _LOGGER.debug("Connessione a %s:%s, comando: %s", ip, port, command.strip())

        try:
            # Crea la connessione con timeout
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port), timeout=timeout
            )
        except asyncio.TimeoutError:
            raise VMCTimeoutError(f"Timeout durante la connessione a {ip}:{port}")
        except ConnectionRefusedError:
            raise VMCConnectionError(f"Connessione rifiutata da {ip}:{port}")
        except (OSError, socket.gaierror) as err:
            raise VMCConnectionError(f"Errore di connessione a {ip}:{port}: {err}")

        try:
            # Invia il comando
            writer.write(command.encode('utf-8'))
            await writer.drain()

            # Leggi la risposta con timeout
            try:
                response = await asyncio.wait_for(
                    reader.read(1024), timeout=timeout
                )
            except asyncio.TimeoutError:
                raise VMCTimeoutError(f"Timeout in attesa della risposta da {ip}:{port}")

            # Decodifica la risposta
            try:
                decoded_response = response.decode('utf-8').strip()
            except UnicodeDecodeError:
                # Se la decodifica UTF-8 fallisce, prova con latin-1 che non fallisce mai
                decoded_response = response.decode('latin-1').strip()
                _LOGGER.warning("Risposta decodificata con latin-1 invece di UTF-8: %s", decoded_response)

            _LOGGER.debug("Risposta da %s:%s: %s", ip, port, decoded_response)

            # Controlla se la risposta contiene un errore di protocollo
            if decoded_response.startswith("ERROR"):
                raise VMCProtocolError(f"Errore di protocollo: {decoded_response}")

            return decoded_response

        finally:
            # Chiudi sempre la connessione
            try:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=1.0)
            except (asyncio.TimeoutError, Exception) as err:
                _LOGGER.debug("Errore durante la chiusura della connessione: %s", err)

    except VMCConnectionError:
        # Rilancia le eccezioni specifiche
        raise
    except asyncio.CancelledError:
        # Non catturare le cancellazioni di task
        raise
    except Exception as err:
        # Cattura qualsiasi altra eccezione e convertila in un errore appropriato
        _LOGGER.exception("Errore imprevisto durante la comunicazione con %s:%s: %s", ip, port, err)
        raise VMCConnectionError(f"Errore durante la comunicazione con {ip}:{port}: {err}")


async def get_device_info(ip: str, port: int = DEFAULT_PORT, timeout: int = TCP_TIMEOUT) -> Optional[Dict[str, str]]:
    """Recupera le informazioni del dispositivo VMC.

    Args:
        ip: Indirizzo IP del dispositivo
        port: Porta TCP del dispositivo
        timeout: Timeout in secondi

    Returns:
        Dizionario con le informazioni del dispositivo o None se non disponibile
    """
    try:
        response = await tcp_send_command(ip, port, "VMGH?", timeout)

        if response and response.startswith("VMGO"):
            try:
                parts = response.split(",")
                modello = parts[1] if len(parts) > 1 else "VMC Flow"

                # Recupera il nome mnemonico con VMNM?
                try:
                    name_response = await tcp_send_command(ip, port, "VMNM?", timeout)
                    _LOGGER.debug(f"Risposta VMNM? da {ip}: {name_response}")
                    if name_response and name_response.startswith("VMNM"):
                        nome_parts = name_response.split(" ")
                    _LOGGER.warning("Impossibile recuperare il nome del dispositivo %s: %s", ip, err)
                    nome = f"VMC Helty {ip.split('.')[-1]}"

                # Recupera versione firmware se disponibile
                sw_version = None
                try:
                    version_response = await tcp_send_command(ip, port, "VMCV?", timeout)
                    if version_response:
                        import re
                        # Cerca un pattern che assomigli a una versione
                        version_match = re.search(r"(\d+\.\d+(\.\d+)?)", version_response)
                        if version_match:
                            sw_version = version_match.group(1)
                except Exception:
                    _LOGGER.debug("Impossibile determinare la versione firmware del dispositivo %s", ip)

                # Estendibile: aggiungi altri parametri qui (es. stato filtri)
                return {
                    "ip": ip,
                    "name": nome,
                    "model": modello,
                    "manufacturer": "Helty",
                    "sw_version": sw_version,
                    "available": True
                }
            except Exception as e:
                _LOGGER.error("Errore parsing info dispositivo %s: %s", ip, e)
                # Restituisci un set minimo di informazioni se il parsing fallisce
                return {
                    "ip": ip,
                    "name": f"VMC Helty {ip.split('.')[-1]}",
                    "model": "VMC Flow",
                    "manufacturer": "Helty",
                    "available": True,
                    "parse_error": str(e)
                }
        else:
            _LOGGER.warning("Dispositivo %s ha risposto con un formato non riconosciuto: %s", ip, response)
            return None

    except VMCConnectionError as err:
        _LOGGER.error("Errore di connessione al dispositivo %s: %s", ip, err)
        return None
    except Exception as err:
        _LOGGER.exception("Errore imprevisto recuperando le info per %s: %s", ip, err)
        return None


async def discover_vmc_devices(subnet: str = "192.168.1.", port: int = DEFAULT_PORT, timeout: int = TCP_TIMEOUT) -> List[Dict[str, str]]:
    """Scopre i dispositivi VMC sulla rete."""
    devices = []
    if subnet.endswith('.'):
        subnet = subnet[:-1]
    tasks = []
    for i in range(IP_RANGE_START, IP_RANGE_END + 1):
        ip = f"{subnet}.{i}"
        tasks.append(get_device_info(ip, port, timeout))
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


async def check_device_availability(ip: str, port: int = DEFAULT_PORT, retries: int = 2) -> Tuple[bool, Optional[Dict]]:
    """Verifica la disponibilità di un dispositivo con tentativi multipli.

    Args:
        ip: Indirizzo IP del dispositivo
        port: Porta TCP del dispositivo
        retries: Numero di tentativi prima di considerare il dispositivo non disponibile

    Returns:
        Tupla (disponibilità, info_dispositivo)
    """
    for attempt in range(retries):
        try:
            # Usa un timeout più breve per i controlli di disponibilità
            device_info = await get_device_info(ip, port, timeout=TCP_TIMEOUT/2)
            if device_info:
                return True, device_info
        except Exception as err:
            _LOGGER.debug("Tentativo %d fallito per %s: %s", attempt + 1, ip, err)
            # Breve attesa tra i tentativi
            if attempt < retries - 1:
                await asyncio.sleep(0.5)

    return False, None
