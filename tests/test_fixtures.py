"""Test fixture hass personalizzato."""


def test_fixture_hass_available(hass):
    """Test che il fixture hass sia disponibile e funzionante."""
    assert hass is not None
    assert hasattr(hass, "config")
    assert hasattr(hass, "data")
    assert hasattr(hass, "states")
    print(f"Home Assistant instance: {hass}")
    print(f"Config dir: {hass.config.config_dir}")


def test_mock_config_entry_available(mock_config_entry):
    """Test che il fixture mock_config_entry sia disponibile."""
    assert mock_config_entry is not None
    assert mock_config_entry.domain == "vmc_helty_flow"
    assert mock_config_entry.data["ip"] == "192.168.1.100"
    print(f"Mock config entry: {mock_config_entry}")


def test_mock_store_available(mock_store):
    """Test che il fixture mock_store sia disponibile."""
    assert mock_store is not None
    assert hasattr(mock_store, "async_load")
    assert hasattr(mock_store, "async_save")
    print(f"Mock store: {mock_store}")
