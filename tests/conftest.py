"""Shared fixtures for VMC Helty Flow integration tests."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util.unit_system import METRIC_SYSTEM


@pytest.fixture
async def hass():
    """Create a Home Assistant instance for testing."""
    # Create Home Assistant instance with proper async setup
    hass = HomeAssistant("/tmp/test_config")

    # Set up basic configuration
    hass.config.units = METRIC_SYSTEM
    hass.config.time_zone = "UTC"
    hass.config.latitude = 45.0
    hass.config.longitude = 9.0
    hass.config.elevation = 0

    # Initialize core systems
    await hass.async_block_till_done()

    # Mock config entries
    hass.config_entries = Mock()
    hass.config_entries.async_entries = Mock(return_value=[])
    hass.config_entries.async_add = AsyncMock()
    hass.config_entries.async_remove = AsyncMock()

    # Mock states
    hass.states = Mock()
    hass.states.async_set = Mock()
    hass.states.async_remove = Mock()

    # Mock data registry
    hass.data = {}

    # Mock device registry
    hass.helpers = Mock()

    yield hass

    # Cleanup
    await hass.async_stop()


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    config_entry = Mock()
    config_entry.entry_id = "test_entry_id"
    config_entry.domain = "vmc_helty_flow"
    config_entry.title = "VMC Helty Flow Test"
    config_entry.data = {
        "ip": "192.168.1.100",
        "name": "VMC_Test",
        "port": 5001,
        "timeout": 10,
        "room_volume": 60.0,
    }
    config_entry.options = {"scan_interval": 60, "timeout": 10, "retry_attempts": 3}
    config_entry.unique_id = "192_168_1_100"
    config_entry.version = 1
    return config_entry


@pytest.fixture
def mock_device_info():
    """Create mock device info."""
    return {
        "identifiers": {("vmc_helty_flow", "192_168_1_100")},
        "name": "VMC Helty Flow Test",
        "manufacturer": "Helty",
        "model": "VMC Flow",
        "sw_version": "1.0.0",
    }


@pytest.fixture
def mock_discovered_devices():
    """Mock discovered devices."""
    return [
        {
            "ip": "192.168.1.100",
            "name": "VMC_Living",
            "model": "VMC Flow",
            "manufacturer": "Helty",
        },
        {
            "ip": "192.168.1.101",
            "name": "VMC_Kitchen",
            "model": "VMC Flow",
            "manufacturer": "Helty",
        },
    ]


@pytest.fixture
def mock_store():
    """Mock storage instance."""
    store = Mock()
    store.async_load = AsyncMock()
    store.async_save = AsyncMock()
    return store


@pytest.fixture
def mock_vmc_device():
    """Mock VMC device client."""
    device = Mock()
    device.ip = "192.168.1.100"
    device.name = "VMC_Test"
    device.model = "VMC Flow"
    device.manufacturer = "Helty"
    device.sw_version = "1.0.0"
    device.hw_version = "1.0"
    device.mac_address = "AA:BB:CC:DD:EE:FF"

    # Mock async methods
    device.async_connect = AsyncMock(return_value=True)
    device.async_disconnect = AsyncMock()
    device.async_get_status = AsyncMock(
        return_value={
            "fan_speed": 50,
            "temperature": 22.5,
            "humidity": 45,
            "filter_status": "ok",
        }
    )
    device.async_set_fan_speed = AsyncMock()
    device.async_turn_on = AsyncMock()
    device.async_turn_off = AsyncMock()

    return device


@pytest.fixture
def mock_discovery():
    """Mock discovery function."""
    with patch(
        "custom_components.vmc_helty_flow.discovery.discover_vmc_devices"
    ) as mock:
        mock.return_value = [
            {
                "ip": "192.168.1.100",
                "name": "VMC_Living",
                "model": "VMC Flow",
                "manufacturer": "Helty",
            }
        ]
        yield mock


# Pytest asyncio configuration
pytest_plugins = ["pytest_asyncio"]
