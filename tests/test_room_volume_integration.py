"""Test integration room volume configuration."""

import unittest
from unittest.mock import Mock

from custom_components.vmc_helty_flow import VmcHeltyCoordinator
from custom_components.vmc_helty_flow.const import DEFAULT_ROOM_VOLUME
from custom_components.vmc_helty_flow.sensor import (
    VmcHeltyAirExchangeTimeSensor,
    VmcHeltyDailyAirChangesSensor,
)


class TestRoomVolumeIntegration(unittest.TestCase):
    """Test room volume configuration throughout the system."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock config entry with room_volume
        self.config_entry = Mock()
        self.config_entry.data = {
            "ip": "192.168.1.100",
            "name": "TestVMC",
            "room_volume": 75.0,  # Custom room volume
        }
        self.config_entry.options = {}

        # Mock hass
        self.hass = Mock()

    def test_coordinator_room_volume_from_data(self):
        """Test coordinator reads room_volume from config entry data."""
        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        assert coordinator.room_volume == 75.0

    def test_coordinator_room_volume_fallback_to_options(self):
        """Test coordinator falls back to options if data doesn't have room_volume."""
        # Remove room_volume from data
        self.config_entry.data = {
            "ip": "192.168.1.100",
            "name": "TestVMC",
        }
        # Add to options
        self.config_entry.options = {"room_volume": 80.0}

        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        assert coordinator.room_volume == 80.0

    def test_coordinator_room_volume_default_fallback(self):
        """Test coordinator uses default if neither data nor options have it."""
        # Remove room_volume from both data and options
        self.config_entry.data = {
            "ip": "192.168.1.100",
            "name": "TestVMC",
        }
        self.config_entry.options = {}

        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        assert coordinator.room_volume == DEFAULT_ROOM_VOLUME  # Default fallback

    def test_air_exchange_sensor_uses_coordinator_room_volume(self):
        """Test that air exchange sensor uses coordinator room_volume."""
        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        sensor = VmcHeltyAirExchangeTimeSensor(coordinator)

        # Set up test data
        coordinator.data = {
            "status": "VMGO,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        }  # Fan speed 2 -> 17 m³/h

        # Expected: (75.0 / 17) * 60 = 264.7 minutes
        expected_time = (75.0 / 17) * 60

        assert sensor.native_value == round(expected_time, 1)

    def test_daily_air_changes_sensor_uses_coordinator_room_volume(self):
        """Test that daily air changes sensor uses coordinator room_volume."""
        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        sensor = VmcHeltyDailyAirChangesSensor(coordinator, "test_device")

        # Set up test data
        coordinator.data = {
            "status": "VMGO,2,0,0,0,0,0,0,0,0,0,0,0,0,0"
        }  # Fan speed 2 -> 17 m³/h

        # Expected: (17 / 75.0) * 24 = 5.4 changes/day
        expected_changes = round((17 / 75.0) * 24, 1)

        assert sensor.native_value == expected_changes

    def test_air_exchange_sensor_attributes_show_configured_volume(self):
        """Test that air exchange sensor attributes show the configured room volume."""
        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        sensor = VmcHeltyAirExchangeTimeSensor(coordinator)

        # Set up test data
        coordinator.data = {"status": "VMGO,2,0,0,0"}  # Fan speed 2

        attrs = sensor.extra_state_attributes
        assert attrs["room_volume"] == "75.0 m³"

    def test_daily_air_changes_sensor_attributes_show_configured_volume(self):
        """Test that daily air changes sensor attributes show configured room volume."""
        coordinator = VmcHeltyCoordinator(self.hass, self.config_entry)
        sensor = VmcHeltyDailyAirChangesSensor(coordinator, "test_device")

        # Set up test data
        coordinator.data = {"status": "VMGO,2,0,0,0,0,0,0,0,0,0,0,0,0,0"}  # Fan speed 2

        attrs = sensor.extra_state_attributes
        assert attrs["room_volume_m3"] == 75.0


if __name__ == "__main__":
    unittest.main()
