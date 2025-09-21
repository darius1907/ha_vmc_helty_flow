"""Test per il modulo helpers_net."""

from custom_components.vmc_helty_flow.helpers_net import (
    count_ips_in_subnet,
    parse_subnet_for_discovery,
    validate_subnet,
)


class TestValidateSubnet:
    """Test per validate_subnet."""

    def test_valid_private_subnets(self):
        """Test subnet private valide."""
        valid_subnets = [
            "192.168.1.0/24",
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16",
            "10.1.1.0/24",
            "172.20.0.0/16",
        ]
        for subnet in valid_subnets:
            assert (
                validate_subnet(subnet) is True
            ), f"Subnet {subnet} dovrebbe essere valida"

    def test_valid_localhost_subnets(self):
        """Test subnet localhost valide."""
        valid_subnets = [
            "127.0.0.0/8",
            "127.0.0.1/32",
            "127.1.0.0/16",
        ]
        for subnet in valid_subnets:
            assert (
                validate_subnet(subnet) is True
            ), f"Subnet {subnet} dovrebbe essere valida"

    def test_valid_link_local_subnets(self):
        """Test subnet link-local valide."""
        valid_subnets = [
            "169.254.0.0/16",
            "169.254.1.0/24",
        ]
        for subnet in valid_subnets:
            assert (
                validate_subnet(subnet) is True
            ), f"Subnet {subnet} dovrebbe essere valida"

    def test_invalid_format_subnets(self):
        """Test subnet con formato non valido."""
        invalid_subnets = [
            "192.168.1.0",  # Manca il CIDR
            "192.168.1.0/",  # CIDR incompleto
            "192.168.1.0/33",  # CIDR troppo grande
            "192.168.1.0/-1",  # CIDR negativo
            "192.168.1.256/24",  # IP non valido
            "300.168.1.0/24",  # IP non valido
            "192.168.1.0/xy",  # CIDR non numerico
            "",  # Vuoto
            "not_an_ip",  # Non è un IP
        ]
        for subnet in invalid_subnets:
            assert (
                validate_subnet(subnet) is False
            ), f"Subnet {subnet} dovrebbe essere non valida"

    def test_public_ip_subnets(self):
        """Test che le subnet con IP pubblici siano considerate non valide."""
        public_subnets = [
            "8.8.8.0/24",  # Google DNS
            "1.1.1.0/24",  # Cloudflare DNS
            "74.125.224.0/19",  # Google range
        ]
        for subnet in public_subnets:
            assert (
                validate_subnet(subnet) is False
            ), f"Subnet pubblica {subnet} dovrebbe essere non valida"

    def test_edge_cases(self):
        """Test casi limite."""
        assert validate_subnet("192.168.1.1/32") is True  # Single host
        assert validate_subnet("10.0.0.0/8") is True  # Largest private subnet
        assert validate_subnet("0.0.0.0/0") is False  # Global subnet


class TestCountIpsInSubnet:
    """Test per count_ips_in_subnet."""

    def test_valid_subnets_count(self):
        """Test conteggio IP per subnet valide."""
        test_cases = [
            ("192.168.1.0/24", 254),  # 256 - 2 (network e broadcast)
            ("10.0.0.0/8", 16777214),  # 16777216 - 2
            ("192.168.1.0/30", 2),  # 4 - 2
            ("192.168.1.1/32", -1),  # 1 - 2 (negative for single host)
            ("172.16.0.0/16", 65534),  # 65536 - 2
        ]
        for subnet, expected in test_cases:
            result = count_ips_in_subnet(subnet)
            assert (
                result == expected
            ), f"Subnet {subnet}: atteso {expected}, ottenuto {result}"

    def test_invalid_subnets_count(self):
        """Test conteggio IP per subnet non valide."""
        invalid_subnets = [
            "not_a_subnet",  # Non è una subnet
            "192.168.1.256/24",  # IP non valido
            "",  # Vuoto
            "192.168.1.0/33",  # CIDR non valido
        ]
        for subnet in invalid_subnets:
            result = count_ips_in_subnet(subnet)
            assert result == 0, f"Subnet non valida {subnet} dovrebbe restituire 0"

        # Test caso speciale: IP senza CIDR viene trattato diversamente
        result = count_ips_in_subnet("192.168.1.0")  # Manca CIDR
        assert result == -1  # Viene interpretato come /32 (1 IP), quindi 1-2=-1

    def test_edge_cases_count(self):
        """Test casi limite per il conteggio."""
        assert count_ips_in_subnet("192.168.1.0/31") == 0  # /31 ha 2 IP, 2-2=0
        assert count_ips_in_subnet("10.0.0.0/24") == 254


class TestParseSubnetForDiscovery:
    """Test per parse_subnet_for_discovery."""

    def test_valid_subnets_parsing(self):
        """Test parsing per subnet valide."""
        test_cases = [
            ("192.168.1.0/24", "192.168.1."),
            ("10.0.0.0/8", "10.0.0."),
            ("172.16.5.0/24", "172.16.5."),
            ("192.168.100.0/24", "192.168.100."),
            ("10.1.2.0/24", "10.1.2."),  # /24 non /16
        ]
        for subnet, expected in test_cases:
            result = parse_subnet_for_discovery(subnet)
            assert (
                result == expected
            ), f"Subnet {subnet}: atteso {expected}, ottenuto {result}"

    def test_invalid_subnets_parsing(self):
        """Test parsing per subnet non valide."""
        invalid_subnets = [
            "not_a_subnet",
            "192.168.1.256/24",
            "",
            "192.168.1.0",  # Manca CIDR
            "invalid_format",
        ]
        for subnet in invalid_subnets:
            result = parse_subnet_for_discovery(subnet)
            assert (
                result == "192.168.1."
            ), f"Subnet non valida {subnet} dovrebbe restituire il default"

    def test_different_cidr_sizes(self):
        """Test parsing con diverse dimensioni CIDR."""
        test_cases = [
            ("192.168.1.0/30", "192.168.1."),
            ("10.0.0.0/16", "10.0.0."),
            ("172.16.0.0/12", "172.16.0."),
            ("192.168.1.1/32", "192.168.1."),
        ]
        for subnet, expected in test_cases:
            result = parse_subnet_for_discovery(subnet)
            assert (
                result == expected
            ), f"Subnet {subnet}: atteso {expected}, ottenuto {result}"

    def test_default_fallback(self):
        """Test che il fallback restituisca il valore di default."""
        result = parse_subnet_for_discovery("invalid")
        assert result == "192.168.1."

    def test_subnet_with_host_bits(self):
        """Test parsing di subnet con bit host impostati."""
        # strict=False converte alla rete base
        test_cases = [
            ("192.168.1.100/24", "192.168.1."),  # Viene convertito a 192.168.1.0/24
            ("10.0.5.50/16", "10.0.0."),  # Viene convertito a 10.0.0.0/16
        ]
        for subnet, expected in test_cases:
            result = parse_subnet_for_discovery(subnet)
            assert (
                result == expected
            ), f"Subnet {subnet}: atteso {expected}, ottenuto {result}"
