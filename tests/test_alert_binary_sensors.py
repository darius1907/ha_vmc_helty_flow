"""Tests for alert binary sensors."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

from homeassistant.util import dt as dt_util

from custom_components.vmc_helty_flow.sensor import (
    VmcHeltyAirQualityAlertBinarySensor,
    VmcHeltyCondensationRiskBinarySensor,
    VmcHeltyOfflineBinarySensor,
)


def _build_vmgi(
    temp_internal_tenths: int,
    temp_external_tenths: int,
    humidity_tenths: int,
    co2_ppm: int,
) -> str:
    """Build a valid VMGI payload with enough parts for parsing."""
    return (
        f"VMGI,{temp_internal_tenths},{temp_external_tenths},{humidity_tenths},"
        f"{co2_ppm},0,0,0,0,0,0,0,0,0,0"
    )


def test_air_quality_alert_triggers_after_five_minutes(monkeypatch) -> None:
    """Air quality alert turns on only after 5 minutes above threshold."""
    coordinator = MagicMock()
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.name = "TestVMC"
    coordinator.data = {"sensors": _build_vmgi(240, 220, 600, 1200)}

    sensor_entity = VmcHeltyAirQualityAlertBinarySensor(coordinator)

    base_time = datetime(2026, 3, 26, 10, 0, tzinfo=dt_util.UTC)
    current_time = [base_time]
    monkeypatch.setattr(dt_util, "utcnow", lambda: current_time[0])

    assert sensor_entity.is_on is False

    current_time[0] = base_time + timedelta(minutes=4, seconds=59)
    assert sensor_entity.is_on is False

    current_time[0] = base_time + timedelta(minutes=5)
    assert sensor_entity.is_on is True

    coordinator.data = {"sensors": _build_vmgi(240, 220, 600, 900)}
    assert sensor_entity.is_on is False


def test_condensation_risk_alert_on_with_low_delta() -> None:
    """Condensation risk alert is on when dew point delta is below 2°C."""
    coordinator = MagicMock()
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.name = "TestVMC"

    # Internal/external temperatures very close -> low dew point delta
    coordinator.data = {"sensors": _build_vmgi(240, 231, 600, 700)}

    sensor_entity = VmcHeltyCondensationRiskBinarySensor(coordinator)

    assert sensor_entity.is_on is True


def test_condensation_risk_alert_off_with_safe_delta() -> None:
    """Condensation risk alert is off when dew point delta is safely above 2°C."""
    coordinator = MagicMock()
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.name = "TestVMC"

    # Temperatures far apart -> high dew point delta
    coordinator.data = {"sensors": _build_vmgi(240, 180, 600, 700)}

    sensor_entity = VmcHeltyCondensationRiskBinarySensor(coordinator)

    assert sensor_entity.is_on is False


def test_offline_alert_reflects_coordinator_status() -> None:
    """Offline alert follows coordinator.last_update_success state."""
    coordinator = MagicMock()
    coordinator.name_slug = "vmc_helty_testvmc"
    coordinator.name = "TestVMC"

    sensor_entity = VmcHeltyOfflineBinarySensor(coordinator)

    coordinator.last_update_success = True
    assert sensor_entity.is_on is False

    coordinator.last_update_success = False
    assert sensor_entity.is_on is True
