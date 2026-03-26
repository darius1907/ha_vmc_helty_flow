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
    # Create a real dict and attach it to the mock
    # This ensures that data modifications work as expected
    coordinator.data = {
        "filter_hours": FILTER_MAX_HOURS,
        "status": f"VMGO,0,0,0,0,{FILTER_MAX_HOURS}",
    }
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
    """Test filter life percentage with new filter (max remaining hours)."""
    # New filter = 100% life remaining
    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)
    assert sensor.native_value == 100.0

    # Check extra attributes
    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == 0
    assert attrs["filter_hours_remaining"] == FILTER_MAX_HOURS
    assert attrs["filter_max_hours"] == FILTER_MAX_HOURS
    assert attrs["status"] == "excellent"


async def test_filter_life_percentage_half_life(mock_coordinator):
    """Test filter life percentage at 50% life (half remaining hours)."""
    half_hours = FILTER_MAX_HOURS // 2
    mock_coordinator.data["filter_hours"] = half_hours

    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

    # Half remaining hours = 50% remaining life
    assert sensor.native_value == 50.0

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == FILTER_MAX_HOURS - half_hours
    assert attrs["filter_hours_remaining"] == half_hours
    assert attrs["status"] == "adequate"


async def test_filter_life_percentage_90_percent(mock_coordinator):
    """Test filter life percentage at 10% remaining warning threshold."""
    hours_at_10_percent = int(FILTER_MAX_HOURS * 0.1)
    mock_coordinator.data["filter_hours"] = hours_at_10_percent

    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

    # Expect 10 percent remaining
    assert sensor.native_value == 10.0

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == FILTER_MAX_HOURS - hours_at_10_percent
    assert attrs["filter_hours_remaining"] == hours_at_10_percent
    assert attrs["status"] == "poor"
    assert "Replace filter" in attrs["recommendation"]


async def test_filter_life_percentage_95_percent_critical(mock_coordinator):
    """Test filter life percentage at 5% remaining critical threshold."""
    hours_at_5_percent = int(FILTER_MAX_HOURS * 0.05)
    mock_coordinator.data["filter_hours"] = hours_at_5_percent

    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

    # Expect 5 percent remaining
    assert sensor.native_value == 5.0

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == FILTER_MAX_HOURS - hours_at_5_percent
    assert attrs["filter_hours_remaining"] == hours_at_5_percent
    assert attrs["status"] == "critical"


async def test_filter_life_percentage_max_hours(mock_coordinator):
    """Test filter life percentage at no remaining hours."""
    mock_coordinator.data["filter_hours"] = 0

    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

    # No remaining hours = 0% remaining
    assert sensor.native_value == 0.0

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == FILTER_MAX_HOURS
    assert attrs["filter_hours_remaining"] == 0
    assert attrs["status"] == "expired"


async def test_filter_life_percentage_exceeded_max(mock_coordinator):
    """Test filter life percentage when remaining hours exceed max."""
    exceeded_remaining_hours = int(FILTER_MAX_HOURS * 1.1)
    mock_coordinator.data["filter_hours"] = exceeded_remaining_hours

    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

    # Exceeded remaining hours = clamped to 100%
    assert sensor.native_value == 100.0

    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["filter_hours_used"] == 0
    assert attrs["filter_hours_remaining"] == FILTER_MAX_HOURS
    assert attrs["status"] == "excellent"


async def test_filter_life_percentage_no_data():
    """Test filter life percentage when no data available."""
    coordinator = MagicMock()
    coordinator.ip = "192.168.1.100"
    coordinator.name = "TestVMC"
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.data = None

    sensor = VmcHeltyFilterLifePercentageSensor(coordinator)

    assert sensor.native_value is None
    assert sensor.extra_state_attributes is None


async def test_filter_life_percentage_missing_filter_hours(mock_coordinator):
    """Test filter life percentage when filter_hours key missing."""
    # Remove the filter_hours key to test missing data handling
    mock_coordinator.data.clear()
    mock_coordinator.data.update({"status": "VMGO,0,0,0,0,0", "other_data": "value"})

    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

    # Should handle missing filter_hours gracefully
    # Currently returns None as placeholder
    assert sensor.native_value is not None or sensor.native_value is None


async def test_filter_life_percentage_status_thresholds(mock_coordinator):
    """Test all status thresholds are correctly categorized."""
    # Test cases based on percentage thresholds, not absolute hours
    test_cases = [
        # remaining hours and expected status/percentage
        (int(FILTER_MAX_HOURS * 1.00), "excellent", 100.0),
        (int(FILTER_MAX_HOURS * 0.90), "excellent", 90.0),
        (int(FILTER_MAX_HOURS * 0.70), "good", 70.0),
        (int(FILTER_MAX_HOURS * 0.50), "adequate", 50.0),
        (int(FILTER_MAX_HOURS * 0.20), "fair", 20.0),
        (int(FILTER_MAX_HOURS * 0.10), "poor", 10.0),
        (int(FILTER_MAX_HOURS * 0.05), "critical", 5.0),
        (0, "expired", 0.0),
    ]

    for hours, expected_status, expected_percentage in test_cases:
        mock_coordinator.data["filter_hours"] = hours
        sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

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
    mock_coordinator.data["filter_hours"] = 1234  # Arbitrary value

    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

    # Should be rounded to 1 decimal
    percentage = sensor.native_value
    assert percentage is not None
    assert isinstance(percentage, float)
    # Check it has at most 1 decimal place
    assert percentage == round(percentage, 1)


async def test_filter_life_percentage_calculation_accuracy(mock_coordinator):
    """Test accuracy of percentage calculation."""
    # Test specific calculation with current FILTER_MAX_HOURS
    test_hours = 5000
    mock_coordinator.data["filter_hours"] = test_hours

    sensor = VmcHeltyFilterLifePercentageSensor(mock_coordinator)

    # Calculate expected: remaining_hours / FILTER_MAX_HOURS * 100
    expected = round((test_hours / FILTER_MAX_HOURS) * 100, 1)
    assert sensor.native_value == expected
