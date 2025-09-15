"""Tests for discovery module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.vmc_helty_flow.discovery import (
    async_discover_devices,
    check_helty_device,
    get_device_name,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    return MagicMock()


@pytest.fixture
def mock_adapters():
    """Create mock network adapters."""
    return [
        {
            "name": "eth0",
            "enabled": True,
            "ipv4": [
                {
                    "address": "192.168.1.100",
                    "network_prefix": 24,
                }
            ],
        },
        {
            "name": "eth1",
            "enabled": False,
            "ipv4": [
                {
                    "address": "10.0.0.1",
                    "network_prefix": 24,
                }
            ],
        },
        {
            "name": "wlan0",
            "enabled": True,
            "ipv4": [
                {
                    "address": "172.16.1.1",
                    "network_prefix": 16,
                }
            ],
        },
    ]


class TestAsyncDiscoverDevices:
    """Test async_discover_devices function."""

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.discovery.network.async_get_adapters")
    @patch("custom_components.vmc_helty_flow.discovery.check_helty_device")
    @patch("custom_components.vmc_helty_flow.discovery.get_device_name")
    async def test_discover_with_devices_found(
        self,
        mock_get_name,
        mock_check_device,
        mock_get_adapters,
        mock_hass,
        mock_adapters,
    ):
        """Test discovery with devices found."""
        mock_get_adapters.return_value = mock_adapters

        # Mock that only one device is found
        def mock_check_side_effect(ip):
            return ip == "192.168.1.101"

        mock_check_device.side_effect = mock_check_side_effect
        mock_get_name.return_value = "Test Helty Device"

        devices = await async_discover_devices(mock_hass)

        assert len(devices) == 1
        assert devices[0]["ip"] == "192.168.1.101"
        assert devices[0]["name"] == "Test Helty Device"
        assert devices[0]["model"] == "Flow"
        assert devices[0]["manufacturer"] == "Helty"

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.discovery.network.async_get_adapters")
    async def test_discover_no_adapters(self, mock_get_adapters, mock_hass):
        """Test discovery with no valid adapters."""
        mock_get_adapters.return_value = []

        devices = await async_discover_devices(mock_hass)

        assert devices == []

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.discovery.network.async_get_adapters")
    async def test_discover_disabled_adapters(self, mock_get_adapters, mock_hass):
        """Test discovery with all adapters disabled."""
        disabled_adapters = [
            {
                "name": "eth0",
                "enabled": False,
                "ipv4": [{"address": "192.168.1.100", "network_prefix": 24}],
            }
        ]
        mock_get_adapters.return_value = disabled_adapters

        devices = await async_discover_devices(mock_hass)

        assert devices == []

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.discovery.network.async_get_adapters")
    async def test_discover_no_ipv4(self, mock_get_adapters, mock_hass):
        """Test discovery with adapters without IPv4."""
        no_ipv4_adapters = [
            {
                "name": "eth0",
                "enabled": True,
                "ipv4": [],
            }
        ]
        mock_get_adapters.return_value = no_ipv4_adapters

        devices = await async_discover_devices(mock_hass)

        assert devices == []

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.discovery.network.async_get_adapters")
    async def test_discover_invalid_network(self, mock_get_adapters, mock_hass):
        """Test discovery with invalid network configuration."""
        invalid_adapters = [
            {
                "name": "eth0",
                "enabled": True,
                "ipv4": [
                    {
                        "address": "invalid",
                        "network_prefix": 24,
                    }
                ],
            }
        ]
        mock_get_adapters.return_value = invalid_adapters

        devices = await async_discover_devices(mock_hass)

        assert devices == []

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.discovery.network.async_get_adapters")
    @patch("custom_components.vmc_helty_flow.discovery.check_helty_device")
    @patch("custom_components.vmc_helty_flow.discovery.get_device_name")
    async def test_discover_device_name_error(
        self,
        mock_get_name,
        mock_check_device,
        mock_get_adapters,
        mock_hass,
        mock_adapters,
    ):
        """Test discovery when getting device name fails."""
        mock_get_adapters.return_value = mock_adapters[:1]  # Only first adapter

        def mock_check_side_effect(ip):
            return ip == "192.168.1.101"

        mock_check_device.side_effect = mock_check_side_effect
        mock_get_name.side_effect = Exception("Connection error")

        devices = await async_discover_devices(mock_hass)

        # Should still find device but not add it to results due to name error
        assert devices == []

    @pytest.mark.asyncio
    @patch("custom_components.vmc_helty_flow.discovery.network.async_get_adapters")
    @patch("custom_components.vmc_helty_flow.discovery.check_helty_device")
    @patch("custom_components.vmc_helty_flow.discovery.get_device_name")
    async def test_discover_no_device_name(
        self,
        mock_get_name,
        mock_check_device,
        mock_get_adapters,
        mock_hass,
        mock_adapters,
    ):
        """Test discovery when device name is not available."""
        mock_get_adapters.return_value = mock_adapters[:1]  # Only first adapter

        def mock_check_side_effect(ip):
            return ip == "192.168.1.101"

        mock_check_device.side_effect = mock_check_side_effect
        mock_get_name.return_value = ""

        devices = await async_discover_devices(mock_hass)

        assert len(devices) == 1
        assert devices[0]["name"] == "Helty Flow 192.168.1.101"


class TestCheckHeltyDevice:
    """Test check_helty_device function."""

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_check_device_success(self, mock_open_connection):
        """Test successful device check."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)
        mock_reader.readline.return_value = b"VMGO,1,2,3,4,5\r\n"

        result = await check_helty_device("192.168.1.100")

        assert result is True
        mock_writer.write.assert_called_once_with(b"VMGH?\r\n")
        mock_writer.drain.assert_called_once()
        mock_writer.close.assert_called_once()
        mock_writer.wait_closed.assert_called_once()

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_check_device_wrong_response(self, mock_open_connection):
        """Test device check with wrong response."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)
        mock_reader.readline.return_value = b"ERROR\r\n"

        result = await check_helty_device("192.168.1.100")

        assert result is False

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_check_device_connection_refused(self, mock_open_connection):
        """Test device check with connection refused."""
        mock_open_connection.side_effect = ConnectionRefusedError()

        result = await check_helty_device("192.168.1.100")

        assert result is False

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_check_device_timeout(self, mock_open_connection):
        """Test device check with timeout."""
        mock_open_connection.side_effect = TimeoutError()

        result = await check_helty_device("192.168.1.100")

        assert result is False

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_check_device_os_error(self, mock_open_connection):
        """Test device check with OS error."""
        mock_open_connection.side_effect = OSError("Network unreachable")

        result = await check_helty_device("192.168.1.100")

        assert result is False

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_check_device_read_timeout(self, mock_open_connection):
        """Test device check with read timeout."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)
        mock_reader.readline.side_effect = TimeoutError()

        result = await check_helty_device("192.168.1.100")

        assert result is False


class TestGetDeviceName:
    """Test get_device_name function."""

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_get_name_success(self, mock_open_connection):
        """Test successful device name retrieval."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)
        mock_reader.readline.return_value = b"VMNM,Test Device Name\r\n"

        result = await get_device_name("192.168.1.100")

        assert result == "Test Device Name"
        mock_writer.write.assert_called_once_with(b"VMNM?\r\n")

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_get_name_wrong_response(self, mock_open_connection):
        """Test device name with wrong response."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)
        mock_reader.readline.return_value = b"ERROR\r\n"

        result = await get_device_name("192.168.1.100")

        assert result == ""

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_get_name_invalid_format(self, mock_open_connection):
        """Test device name with invalid response format."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)
        mock_reader.readline.return_value = b"VMNM\r\n"

        result = await get_device_name("192.168.1.100")

        assert result == ""

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_get_name_connection_error(self, mock_open_connection):
        """Test device name with connection error."""
        mock_open_connection.side_effect = ConnectionRefusedError()

        result = await get_device_name("192.168.1.100")

        assert result == ""

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_get_name_timeout(self, mock_open_connection):
        """Test device name with timeout."""
        mock_open_connection.side_effect = TimeoutError()

        result = await get_device_name("192.168.1.100")

        assert result == ""

    @pytest.mark.asyncio
    @patch("asyncio.open_connection")
    async def test_get_name_os_error(self, mock_open_connection):
        """Test device name with OS error."""
        mock_open_connection.side_effect = OSError("Network unreachable")

        result = await get_device_name("192.168.1.100")

        assert result == ""
