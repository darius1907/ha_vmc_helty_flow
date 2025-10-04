"""Helper functions per l'integrazione VMC Helty Flow."""

import asyncio
import logging
import socket
import subprocess
import sys

from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_PORT, IP_RANGE_END, IP_RANGE_START, TCP_TIMEOUT

_LOGGER = logging.getLogger(__name__)

# Constants
MIN_RESPONSE_LENGTH = 64

# Network error constants
ERROR_HOST_UNREACHABLE = 113  # EHOSTUNREACH
ERROR_CONNECTION_REFUSED = 111  # ECONNREFUSED
ERROR_TIMEOUT = 110  # ETIMEDOUT


class VMCConnectionError(HomeAssistantError):
    """Errore di connessione al dispositivo VMC."""


class VMCTimeoutError(VMCConnectionError):
    """Timeout durante la comunicazione con il dispositivo VMC."""


class VMCResponseError(HomeAssistantError):
    """Errore nella risposta dal dispositivo VMC."""


class VMCProtocolError(VMCResponseError):
    """Errore di protocollo nella comunicazione con VMC."""


async def _establish_connection(ip: str, port: int, timeout: int) -> tuple:
    """Stabilisce una connessione TCP."""
    try:
        return await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout
        )
    except TimeoutError:
        raise VMCTimeoutError(f"Timeout durante la connessione a {ip}:{port}") from None
    except ConnectionRefusedError:
        raise VMCConnectionError(
            f"Connessione rifiutata da {ip}:{port} - "
            "Il dispositivo potrebbe essere spento o non raggiungibile"
        ) from None
    except (OSError, socket.gaierror) as err:
        # Provide more specific error messages based on errno
        if hasattr(err, "errno"):
            if err.errno == ERROR_HOST_UNREACHABLE:
                error_msg = (
                    f"Host non raggiungibile {ip}:{port} - "
                    "Verificare la connessione di rete e l'indirizzo IP"
                )
            elif err.errno == ERROR_CONNECTION_REFUSED:
                error_msg = (
                    f"Connessione rifiutata da {ip}:{port} - "
                    "Il servizio potrebbe non essere in esecuzione"
                )
            elif err.errno == ERROR_TIMEOUT:
                error_msg = (
                    f"Timeout di connessione a {ip}:{port} - "
                    "Il dispositivo potrebbe essere irraggiungibile"
                )
            else:
                error_msg = (
                    f"Errore di rete ({err.errno}) connettendo a {ip}:{port}: {err}"
                )
        else:
            error_msg = f"Errore di connessione a {ip}:{port}: {err}"
        raise VMCConnectionError(error_msg) from err


async def _send_and_receive(
    reader, writer, command: str, ip: str, port: int, timeout: int
) -> str:
    """Invia un comando e legge la risposta."""
    # Invia il comando
    writer.write(command.encode("utf-8"))
    await writer.drain()

    # Leggi la risposta con timeout
    try:
        response = await asyncio.wait_for(reader.read(1024), timeout=timeout)
    except TimeoutError:
        raise VMCTimeoutError(
            f"Timeout in attesa della risposta da {ip}:{port}"
        ) from None

    # Decodifica la risposta
    decoded_response: str
    try:
        decoded_response = response.decode("utf-8").strip()
    except UnicodeDecodeError:
        # Se la decodifica UTF-8 fallisce,
        # prova con latin-1 che non fallisce mai
        decoded_response = response.decode("latin-1").strip()
        _LOGGER.warning("Risposta da %s:%s non era in UTF-8, usato latin-1", ip, port)

    _LOGGER.debug("Risposta da %s:%s: %s", ip, port, decoded_response)

    # Controlla se la risposta contiene un errore di protocollo
    if decoded_response.startswith("ERROR"):
        raise VMCProtocolError(f"Errore di protocollo: {decoded_response}")

    return decoded_response


async def tcp_send_command(
    ip: str, port: int, command: str, timeout: int | None = None
) -> str:
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
    _LOGGER.info(
        "tcp_send_command-> ip: %s, port: %s, command: %s, timeout: %s",
        ip,
        port,
        command,
        timeout,
    )
    if timeout is None:
        timeout = TCP_TIMEOUT

        # Assicura che il comando termini con NLCR (\n\r)
        if not command.endswith("\n\r"):
            # Rimuovi eventuali terminazioni errate
            command = command.rstrip("\r\n")
            command += "\n\r"

    try:
        _LOGGER.debug("Connessione a %s:%s, comando: %s", ip, port, command.strip())

        reader, writer = await _establish_connection(ip, port, timeout)

        try:
            return await _send_and_receive(reader, writer, command, ip, port, timeout)
        finally:
            # Chiudi sempre la connessione
            try:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=1.0)
            except (TimeoutError, Exception) as err:
                _LOGGER.debug("Errore durante la chiusura della connessione: %s", err)

    except VMCConnectionError:
        # Rilancia le eccezioni specifiche
        raise
    except Exception as err:
        # Cattura qualsiasi altra eccezione e convertila in un errore appropriato
        _LOGGER.exception(
            "Errore imprevisto durante la comunicazione con %s:%s", ip, port
        )
        raise VMCConnectionError(
            f"Errore durante la comunicazione con {ip}:{port}: {err}"
        ) from err


async def _get_device_name(ip: str, port: int, timeout: int) -> str:
    """Get device mnemonic name."""
    _LOGGER.info("_get_device_name-> ip: %s, port: %s, timeout: %s", ip, port, timeout)
    try:
        name_response = await tcp_send_command(ip, port, "VMNM?", timeout)
        _LOGGER.debug("Risposta VMNM? da %s: %s", ip, name_response)
        if name_response and name_response.startswith("VMNM"):
            nome_parts = name_response.split(" ")
            if len(nome_parts) > 1 and nome_parts[1].strip():
                return nome_parts[1].strip()
    except VMCConnectionError as err:
        _LOGGER.warning(
            "Impossibile recuperare il nome del dispositivo %s: %s", ip, err
        )

    return f"VMC Helty {ip.split('.')[-1]}"


async def get_device_info(
    ip: str, port: int = DEFAULT_PORT, timeout: int = TCP_TIMEOUT
) -> dict[str, str] | None:
    """Recupera le informazioni del dispositivo VMC.

    Args:
        ip: Indirizzo IP del dispositivo
        port: Porta TCP del dispositivo
        timeout: Timeout in secondi

    Returns:
        Dizionario con le informazioni del dispositivo o None se non disponibile
    """
    _LOGGER.info("get_device_info-> ip: %s, port: %s, timeout: %s", ip, port, timeout)
    try:
        response = await tcp_send_command(ip, port, "VMGH?", timeout)
        _LOGGER.debug("get_device_info-> response: [%s]", response)
        if not response or not response.startswith("VMGO"):
            _LOGGER.warning(
                "Dispositivo %s ha risposto con un formato non riconosciuto: [%s]",
                ip,
                response,
            )
            return None

        try:
            modello = "VMC Helty Flow"

            # Recupera nome
            nome = await _get_device_name(ip, port, timeout)

        except Exception:
            _LOGGER.exception("Errore parsing info dispositivo %s", ip)
            # Restituisci un set minimo di informazioni se il parsing fallisce
            return {
                "ip": ip,
                "name": f"VMC Helty {ip.split('.')[-1]}",
                "model": "VMC Helty Flow",
                "manufacturer": "Helty",
                "available": "True",
                "parse_error": "Errore di parsing",
            }
        else:
            # Parsing riuscito, restituisci le informazioni complete
            return {
                "ip": ip,
                "name": nome,
                "model": modello,
                "manufacturer": "Helty",
                "available": "True",
            }

    except VMCConnectionError:
        _LOGGER.exception("Errore di connessione al dispositivo %s", ip)
        return None
    except Exception:
        _LOGGER.exception("Errore imprevisto recuperando le info per %s", ip)
        return None


async def discover_vmc_devices(
    subnet: str = "192.168.1.", port: int = DEFAULT_PORT, timeout: int = TCP_TIMEOUT
) -> list[dict[str, str]]:
    """Scopre i dispositivi VMC sulla rete."""
    devices = []
    if subnet.endswith("."):
        subnet = subnet[:-1]
    tasks = []
    for i in range(IP_RANGE_START, IP_RANGE_END + 1):
        ip = f"{subnet}.{i}"
        tasks.append(get_device_info(ip, port, timeout))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Filtra e deduplica i risultati validi per IP
    seen_ips = set()
    for result in results:
        if (
            isinstance(result, dict)
            and result is not None
            and result["ip"] not in seen_ips
        ):
            devices.append(result)
            seen_ips.add(result["ip"])
    return devices


def get_device_name(ip: str) -> str:
    """Restituisce un nome di default per il dispositivo basato sull'IP."""
    return f"VMC Helty {ip.split('.')[-1]}"


async def validate_network_connectivity(
    ip: str, port: int = DEFAULT_PORT
) -> dict[str, str | bool | int | None]:
    """Validate network connectivity to a VMC device and return diagnostic info."""
    diagnostics = {
        "ip": ip,
        "port": port,
        "reachable": False,
        "ping_success": False,
        "tcp_connection": False,
        "error_details": None
    }

    # Test ping connectivity (basic network reachability)
    try:
        if sys.platform.startswith("win"):
            ping_cmd = ["ping", "-n", "1", "-w", "1000", ip]
        else:
            ping_cmd = ["ping", "-c", "1", "-W", "1", ip]

        result = subprocess.run(ping_cmd, capture_output=True, timeout=5, check=False)
        diagnostics["ping_success"] = result.returncode == 0
        if not diagnostics["ping_success"]:
            error_output = (
                result.stderr.decode() if result.stderr else "Host unreachable"
            )
            diagnostics["error_details"] = f"Ping failed: {error_output}"
    except Exception as err:
        diagnostics["error_details"] = f"Ping test failed: {err}"

    # Test TCP connection
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=3
        )
        diagnostics["tcp_connection"] = True
        diagnostics["reachable"] = True
        writer.close()
        await writer.wait_closed()
    except Exception as err:
        diagnostics["tcp_connection"] = False
        if not diagnostics["error_details"]:
            diagnostics["error_details"] = f"TCP connection failed: {err}"

    return diagnostics


def parse_vmsl_response(response: str):
    """Parsa la risposta VMSL? e restituisce SSID e password senza padding."""
    if not response or len(response) < MIN_RESPONSE_LENGTH:
        return "", ""
    ssid = response[:32].replace("*", "").strip()
    password = response[32:64].replace("*", "").strip()
    return ssid, password
