import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

def test_parse_vmsl_response_pure():
    from helpers import parse_vmsl_response
    response = "ValentinoNet********************Password************************00000000000000005001000000000000000000000000000000101"
    ssid, password = parse_vmsl_response(response)
    assert ssid == "ValentinoNet"
    assert password == "Password"

def test_get_device_name_pure():
    from helpers import get_device_name
    assert get_device_name("192.168.1.8") == "VMC Helty 8"
    assert get_device_name("10.0.0.123") == "VMC Helty 123"
