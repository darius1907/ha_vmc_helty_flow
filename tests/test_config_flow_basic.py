"""Test config flow semplice senza fixture complessi."""

from unittest.mock import AsyncMock, Mock, patch

from custom_components.vmc_helty_flow.config_flow import VmcHeltyFlowConfigFlow


def test_config_flow_init():
    """Test semplice di inizializzazione config flow."""
    flow = VmcHeltyFlowConfigFlow()

    assert flow.VERSION == 1
    assert flow.subnet is None
    assert flow.port is None
    assert flow.timeout == 10
    assert flow.discovered_devices == []
    assert flow._store is None


def test_config_flow_with_mock_hass():
    """Test config flow con hass mockato."""
    flow = VmcHeltyFlowConfigFlow()

    # Mock hass semplice
    mock_hass = Mock()
    mock_hass.config_entries = Mock()
    mock_hass.config_entries.async_entries = Mock(return_value=[])
    mock_hass.data = {}
    mock_hass.states = Mock()

    flow.hass = mock_hass

    assert flow.hass is not None
    assert hasattr(flow.hass, "config_entries")
    assert hasattr(flow.hass, "data")
    assert hasattr(flow.hass, "states")


async def test_get_store():
    """Test _get_store method."""
    flow = VmcHeltyFlowConfigFlow()

    mock_store = Mock()
    with patch(
        "custom_components.vmc_helty_flow.config_flow.Store", return_value=mock_store
    ):
        store = flow._get_store()
        assert store == mock_store

        # Second call should return cached store
        store2 = flow._get_store()
        assert store2 == mock_store
        assert flow._store is not None


async def test_load_devices_success():
    """Test _load_devices with successful data load."""
    flow = VmcHeltyFlowConfigFlow()

    mock_store = Mock()
    mock_data = {"devices": [{"ip": "192.168.1.100", "name": "Test"}]}
    mock_store.async_load = AsyncMock(return_value=mock_data)

    with patch.object(flow, "_get_store", return_value=mock_store):
        devices = await flow._load_devices()
        assert devices == mock_data["devices"]


async def test_load_devices_no_data():
    """Test _load_devices with no data."""
    flow = VmcHeltyFlowConfigFlow()

    mock_store = Mock()
    mock_store.async_load = AsyncMock(return_value=None)

    with patch.object(flow, "_get_store", return_value=mock_store):
        devices = await flow._load_devices()
        assert devices == []


async def test_load_devices_exception():
    """Test _load_devices with exception."""
    flow = VmcHeltyFlowConfigFlow()

    mock_store = Mock()
    mock_store.async_load = AsyncMock(side_effect=Exception("Load error"))

    with patch.object(flow, "_get_store", return_value=mock_store):
        devices = await flow._load_devices()
        assert devices == []


async def test_save_devices_success():
    """Test _save_devices with successful save."""
    flow = VmcHeltyFlowConfigFlow()

    mock_store = Mock()
    mock_store.async_save = AsyncMock()
    devices = [{"ip": "192.168.1.100", "name": "Test"}]

    with patch.object(flow, "_get_store", return_value=mock_store):
        await flow._save_devices(devices)
        mock_store.async_save.assert_called_once_with({"devices": devices})


async def test_save_devices_exception():
    """Test _save_devices with exception."""
    flow = VmcHeltyFlowConfigFlow()

    mock_store = Mock()
    mock_store.async_save = AsyncMock(side_effect=Exception("Save error"))
    devices = [{"ip": "192.168.1.100", "name": "Test"}]

    with patch.object(flow, "_get_store", return_value=mock_store):
        # Should not raise exception
        await flow._save_devices(devices)
