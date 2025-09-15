"""Test per le costanti del modulo vmc_helty_flow."""

import custom_components.vmc_helty_flow.const as const_module
from custom_components.vmc_helty_flow.const import (
    DEFAULT_PORT,
    DEFAULT_SUBNET,
    DOMAIN,
    IP_RANGE_END,
    IP_RANGE_START,
    TCP_TIMEOUT,
)


class TestConstants:
    """Test per tutte le costanti del modulo."""

    def test_domain_constant(self):
        """Test che la costante DOMAIN sia corretta."""
        assert DOMAIN == "vmc_helty_flow"
        assert isinstance(DOMAIN, str)
        assert len(DOMAIN) > 0

    def test_default_port_constant(self):
        """Test che la costante DEFAULT_PORT sia corretta."""
        assert DEFAULT_PORT == 5001
        assert isinstance(DEFAULT_PORT, int)
        assert DEFAULT_PORT > 0
        assert DEFAULT_PORT < 65536

    def test_default_subnet_constant(self):
        """Test che la costante DEFAULT_SUBNET sia corretta."""
        assert DEFAULT_SUBNET == "192.168.1."
        assert isinstance(DEFAULT_SUBNET, str)
        assert DEFAULT_SUBNET.endswith(".")
        assert DEFAULT_SUBNET.count(".") == 3

    def test_tcp_timeout_constant(self):
        """Test che la costante TCP_TIMEOUT sia corretta."""
        assert TCP_TIMEOUT == 3
        assert isinstance(TCP_TIMEOUT, int)
        assert TCP_TIMEOUT > 0

    def test_ip_range_constants(self):
        """Test che le costanti IP_RANGE siano corrette."""
        assert IP_RANGE_START == 1
        assert IP_RANGE_END == 254
        assert isinstance(IP_RANGE_START, int)
        assert isinstance(IP_RANGE_END, int)
        assert IP_RANGE_START > 0
        assert IP_RANGE_END < 256
        assert IP_RANGE_START < IP_RANGE_END

    def test_all_constants_defined(self):
        """Test che tutte le costanti essenziali siano definite."""
        required_constants = [
            "DOMAIN",
            "DEFAULT_PORT",
            "DEFAULT_SUBNET",
            "TCP_TIMEOUT",
            "IP_RANGE_START",
            "IP_RANGE_END",
        ]

        for constant in required_constants:
            assert hasattr(const_module, constant), f"Costante {constant} non definita"
            value = getattr(const_module, constant)
            assert value is not None, f"Costante {constant} è None"
