import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from custom_components.vmc_helty_flow import helpers_net


def test_validate_subnet():
    assert helpers_net.validate_subnet("192.168.1.0/24") is True
    assert helpers_net.validate_subnet("10.0.0.0/8") is True
    assert helpers_net.validate_subnet("172.16.0.0/16") is True
    assert helpers_net.validate_subnet("127.0.0.0/8") is True
    assert helpers_net.validate_subnet("192.168.1.") is False
    assert helpers_net.validate_subnet("192.168.1") is False
    assert helpers_net.validate_subnet("invalid") is False
    assert helpers_net.validate_subnet("192.168.1.1") is False
    assert helpers_net.validate_subnet("300.300.300.0/24") is False
    assert helpers_net.validate_subnet("192.168.1.0/35") is False


def test_count_ips_in_subnet():
    assert helpers_net.count_ips_in_subnet("192.168.1.0/24") == 254
    assert helpers_net.count_ips_in_subnet("10.0.0.0/24") == 254
    assert helpers_net.count_ips_in_subnet("192.168.1.0/28") == 14
    assert helpers_net.count_ips_in_subnet("192.168.1.0/30") == 2
    assert helpers_net.count_ips_in_subnet("192.168.1.") == 0
    assert helpers_net.count_ips_in_subnet("invalid") == 0


def test_parse_subnet_for_discovery():
    assert helpers_net.parse_subnet_for_discovery("192.168.1.0/24") == "192.168.1."
    assert helpers_net.parse_subnet_for_discovery("10.0.0.0/24") == "10.0.0."
    assert helpers_net.parse_subnet_for_discovery("172.16.5.0/24") == "172.16.5."
    assert helpers_net.parse_subnet_for_discovery("invalid") == "192.168.1."
