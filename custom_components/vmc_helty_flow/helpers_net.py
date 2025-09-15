"""Funzioni di rete standalone per subnet e IP, testabili senza Home Assistant."""

import ipaddress
import re


def validate_subnet(subnet: str) -> bool:
    """Valida se la subnet è in formato CIDR valido (es. 192.168.1.0/24)."""
    cidr_pattern = r"^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$"
    if not re.match(cidr_pattern, subnet):
        return False
    try:
        network = ipaddress.IPv4Network(subnet, strict=False)
        return (
            network.is_private
            or str(network.network_address).startswith("127.")
            or str(network.network_address).startswith("169.254.")
        )
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
        return False


def count_ips_in_subnet(subnet: str) -> int:
    """Conta quanti IP sono disponibili nella subnet CIDR."""
    try:
        network = ipaddress.IPv4Network(subnet, strict=False)
        return network.num_addresses - 2
    except Exception:
        return 0


def parse_subnet_for_discovery(subnet: str) -> str:
    """Converte la subnet CIDR in formato utilizzabile per la discovery."""
    try:
        network = ipaddress.IPv4Network(subnet, strict=False)
        base_ip = str(network.network_address)
        parts = base_ip.split(".")
        return ".".join(parts[:3]) + "."
    except Exception:
        return "192.168.1."
