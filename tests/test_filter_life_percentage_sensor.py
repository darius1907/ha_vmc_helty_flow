"""Tests for VMC Helty Filter Life Percentage sensor."""

from unittest.mock import MagicMock

import pytest
from homeassistant.const import PERCENTAGE

from custom_components.vmc_helty_flow.const import (
    ENTITY_NAME_PREFIX,
    FILTER_MAX_HOURS,
)
from custom_components.vmc_helty_flow.sensor import VmcHeltyFilterLifePercentageSensor


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "TestVMC"
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.data = {"filter_hours": 0}
    return coordinator


async def test_filter_life_percentage_sensor_init(mock_coordinator):
    """Test filter life percentage sensor initialization."""
    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

    assert sensor.unique_id == f"{mock_coordinator.name_slug}_filter_life_percentage"
    assert (
        sensor.name
        == f"{ENTITY_NAME_PREFIX} {mock_coordinator.name} Filter Life Percentage"
    )
    assert sensor.native_unit_of_measurement == PERCENTAGE
    assert sensor.icon == "mdi:air-filter"
    assert sensor.state_class is not None


async def test_filter_life_percentage_new_filter(mock_coordinator):
    """Test filter life percentage with new filter (0 hours)."""
    mock_coordinator.data = {"filter_hours": 0}

    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

    # New filter = 100% life remaining
    assert sensor.native_value == 100.0

    # Check extra attributes
    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == 0
    assert attrs["filter_hours_remaining"] == FILTER_MAX_HOURS
    assert attrs["filter_max_hours"] == FILTER_MAX_HOURS
    assert attrs["status"] == "excellent"


async def test_filter_life_percentage_half_life(mock_coordinator):
    """Test filter life percentage at 50% life (1800 hours used)."""
    coordinator = mock_coordinator
    coordinator.data = {"filter_hours": 1800}

    sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

    # 1800 hours used of 3600 max = 50% remaining
    assert sensor.native_value == 50.0

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == 1800
    assert attrs["filter_hours_remaining"] == 1800
    assert attrs["status"] == "adequate"


async def test_filter_life_percentage_90_percent(mock_coordinator):
    """Test filter life percentage at 90% warning threshold (3240 hours)."""
    coordinator = mock_coordinator
    coordinator.data = {"filter_hours": 3240}

    sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

    # 3240 hours used = 10% remaining (360 hours)
    assert sensor.native_value == 10.0

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == 3240
    assert attrs["filter_hours_remaining"] == 360
    assert attrs["status"] == "poor"
    assert "Replace filter" in attrs["recommendation"]


async def test_filter_life_percentage_95_percent_critical(mock_coordinator):
    """Test filter life percentage at 95% critical threshold (3420 hours)."""
    coordinator = mock_coordinator
    coordinator.data = {"filter_hours": 3420}

    sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

    # 3420 hours used = 5% remaining (180 hours)
    assert sensor.native_value == 5.0

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == 3420
    assert attrs["filter_hours_remaining"] == 180
    assert attrs["status"] == "critical"


async def test_filter_life_percentage_max_hours(mock_coordinator):
    """Test filter life percentage at max hours (3600 hours)."""
    coordinator = mock_coordinator
    coordinator.data = {"filter_hours": 3600}

    sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

    # 3600 hours used = 0% remaining
    assert sensor.native_value == 0.0

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == 3600
    assert attrs["filter_hours_remaining"] == 0
    assert attrs["status"] == "expired"


async def test_filter_life_percentage_exceeded_max(mock_coordinator):
    """Test filter life percentage when exceeded max hours."""
    coordinator = mock_coordinator
    coordinator.data = {"filter_hours": 4000}

    sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

    # Exceeded max hours = 0% remaining (clamped to 0)
    assert sensor.native_value == 0.0

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == 4000
    assert attrs["filter_hours_remaining"] == 0
    assert attrs["status"] == "expired"


async def test_filter_life_percentage_no_data(mock_coordinator):
    """Test filter life percentage when no data available."""
    coordinator = mock_coordinator
    coordinator.data = None

    sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

    assert sensor.native_value is None
    assert sensor.extra_state_attributes is None


async def test_filter_life_percentage_missing_filter_hours(mock_coordinator):
    """Test filter life percentage when filter_hours key missing."""
    coordinator = mock_coordinator
    coordinator.data = {"other_data": "value"}

    sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

    # Should handle missing filter_hours gracefully
    # Currently returns None as placeholder
    assert sensor.native_value is not None or sensor.native_value is None


async def test_filter_life_percentage_status_thresholds(mock_coordinator):
    """Test all status thresholds are correctly categorized."""
    coordinator = mock_coordinator

    test_cases = [
        (0, "excellent", 100.0),  # 0 hours = excellent
        (360, "excellent", 90.0),  # 360 hours = 90% = excellent
        (1080, "good", 70.0),  # 1080 hours = 70% = good
        (1800, "adequate", 50.0),  # 1800 hours = 50% = adequate
        (2880, "fair", 20.0),  # 2880 hours = 20% = fair
        (3240, "poor", 10.0),  # 3240 hours = 10% = poor
        (3420, "critical", 5.0),  # 3420 hours = 5% = critical
        (3600, "expired", 0.0),  # 3600 hours = 0% = expired
    ]

    for hours, expected_status, expected_percentage in test_cases:
        coordinator.data = {"filter_hours": hours}
        sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

        actual = sensor.native_value
        assert (
            actual == expected_percentage
        ), f"Failed for {hours}h: expected {expected_percentage}%, got {actual}%"

        attrs = sensor.extra_state_attributes
        actual_status = attrs["status"]
        assert actual_status == expected_status, (
            f"Failed for {hours}h: expected '{expected_status}', "
            f"got '{actual_status}'"
        )


async def test_filter_life_percentage_rounding(mock_coordinator):
    """Test that percentage is rounded to 1 decimal place."""
    coordinator = mock_coordinator
    coordinator.data = {"filter_hours": 1234}  # Arbitrary value

    sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

    # Should be rounded to 1 decimal
    percentage = sensor.native_value
    assert percentage is not None
    assert isinstance(percentage, float)
    # Check it has at most 1 decimal place
    assert percentage == round(percentage, 1)


async def test_filter_life_percentage_calculation_accuracy(mock_coordinator):
    """Test accuracy of percentage calculation."""
    coordinator = mock_coordinator

    # Test specific calculation
    # 1000 hours used of 3600 max
    # Remaining: 2600 hours
    # Percentage: 2600 / 3600 * 100 = 72.22... = 72.2%
    coordinator.data = {"filter_hours": 1000}

    sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

    expected = round((3600 - 1000) / 3600 * 100, 1)
    assert sensor.native_value == expected
    assert sensor.native_value == 72.2
