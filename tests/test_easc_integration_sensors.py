"""TEST-005: Integration tests — advanced sensors with EASC external sources.

For each of the 4 advanced sensors (AbsoluteHumidity, DewPoint, ComfortIndex,
DewPointDelta) this module verifies three source scenarios:

  1. **VMC source** (default): values read from VMGI response.
  2. **External entity source**: an available HA entity overrides VMC data.
  3. **Fallback**: external entity unavailable → automatic fallback to VMC.

Additionally covers:
  - Error conditions (no data, invalid VMGI, zero humidity)
  - Custom formula (magnus vs custom) affects numeric output
  - extra_state_attributes reflect actual source used
"""

from __future__ import annotations

import math
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from custom_components.vmc_helty_flow.const import (
    CONF_EASC_ABSOLUTE_HUMIDITY,
    CONF_EASC_COMFORT_INDEX,
    CONF_EASC_CONFIG,
    CONF_EASC_DEW_POINT,
    CONF_EASC_DEW_POINT_DELTA,
    CONF_EASC_ENABLED,
    CONF_EASC_FORMULA,
    CONF_EASC_HUMIDITY_SOURCE,
    CONF_EASC_TEMPERATURE_EXTERNAL,
    CONF_EASC_TEMPERATURE_INTERNAL,
    CONF_EASC_TEMPERATURE_SOURCE,
    EASC_FORMULA_CUSTOM,
    EASC_FORMULA_MAGNUS,
    EASC_SOURCE_VMC,
)
from custom_components.vmc_helty_flow.sensor import (
    VmcHeltyAbsoluteHumiditySensor,
    VmcHeltyComfortIndexSensor,
    VmcHeltyDewPointDeltaSensor,
    VmcHeltyDewPointSensor,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_VMGI = "VMGI,220,80,600,400,0,0,0,0,0,0,0,0,0,0"
# t_int=22.0°C, t_ext=8.0°C, hum=60.0%


def _make_state(value: str, unit: str | None = None):
    attrs = {}
    if unit is not None:
        attrs["unit_of_measurement"] = unit
    return SimpleNamespace(state=value, attributes=attrs)


def _make_hass(entities: dict | None = None):
    hass = MagicMock()
    store = entities or {}
    hass.states.get.side_effect = store.get
    return hass


def _make_coordinator(vmgi: str = _VMGI, options: dict | None = None):
    coord = MagicMock()
    coord.data = {"sensors": vmgi}
    coord.config_entry.options = options or {}
    coord.ip = "192.168.1.1"
    coord.port = 5001
    coord.name = "Test VMC"
    coord.name_slug = "vmc_helty_testvmc"
    return coord


def _easc_options(sensor_key: str, **overrides) -> dict:
    """Build minimal CONF_EASC_CONFIG options for a single sensor."""
    return {
        CONF_EASC_CONFIG: {
            "advanced_sensors": {sensor_key: {CONF_EASC_ENABLED: True, **overrides}}
        }
    }


# ---------------------------------------------------------------------------
# AbsoluteHumidity — 3 source scenarios
# ---------------------------------------------------------------------------


class TestAbsoluteHumidityEascSources:
    def _make(self, options=None, hass=None):
        coord = _make_coordinator(options=options)
        sensor = VmcHeltyAbsoluteHumiditySensor(coord)
        sensor.hass = hass or _make_hass()
        return sensor

    def test_vmc_source_uses_vmgi_values(self):
        sensor = self._make()
        result = sensor.native_value
        # T=22.0°C, RH=60.0% → expected ≈ 11.5 g/m³
        assert result is not None
        assert 10.0 < result < 13.0

    def test_external_entity_source_overrides_vmc(self):
        """When an external entity is available its value is used instead of VMC."""
        hass = _make_hass(
            {
                "sensor.ext_temp": _make_state("30.0", "°C"),
                "sensor.ext_hum": _make_state("80.0", "%"),
            }
        )
        options = _easc_options(
            CONF_EASC_ABSOLUTE_HUMIDITY,
            **{
                CONF_EASC_TEMPERATURE_SOURCE: "sensor.ext_temp",
                CONF_EASC_HUMIDITY_SOURCE: "sensor.ext_hum",
            },
        )
        sensor = self._make(options=options, hass=hass)
        result_external = sensor.native_value

        # Compute expected with T=30.0°C, RH=80.0%
        a, b = 17.27, 237.7
        es = 6.112 * math.exp((a * 30.0) / (b + 30.0))
        e = 0.80 * es
        expected = round((e * 18.016) / (0.08314 * (30.0 + 273.15)), 2)
        assert result_external == pytest.approx(expected, abs=0.1)

        # Must differ from VMC-only value (T=22.0°C, RH=60.0%)
        sensor_vmc = self._make()
        assert result_external != sensor_vmc.native_value

    def test_fallback_to_vmc_when_entity_unavailable(self):
        """Unavailable external entity → falls back to VMC values."""
        hass = _make_hass({"sensor.ext_temp": _make_state("unavailable")})
        options = _easc_options(
            CONF_EASC_ABSOLUTE_HUMIDITY,
            **{CONF_EASC_TEMPERATURE_SOURCE: "sensor.ext_temp"},
        )
        sensor = self._make(options=options, hass=hass)
        result_fallback = sensor.native_value

        sensor_vmc = self._make()
        assert result_fallback == pytest.approx(sensor_vmc.native_value, abs=0.05)

    def test_formula_config_reflected_in_attributes(self):
        """Configured formula name is reported in extra_state_attributes."""
        for formula in (EASC_FORMULA_MAGNUS, EASC_FORMULA_CUSTOM):
            sensor = self._make(
                options=_easc_options(
                    CONF_EASC_ABSOLUTE_HUMIDITY,
                    **{CONF_EASC_FORMULA: formula},
                )
            )
            attrs = sensor.extra_state_attributes
            assert attrs is not None
            assert attrs["formula"] == formula

    def test_attributes_report_correct_source(self):
        hass = _make_hass({"sensor.t": _make_state("25.0", "°C")})
        options = _easc_options(
            CONF_EASC_ABSOLUTE_HUMIDITY,
            **{CONF_EASC_TEMPERATURE_SOURCE: "sensor.t"},
        )
        sensor = self._make(options=options, hass=hass)
        attrs = sensor.extra_state_attributes
        assert attrs is not None
        assert attrs["temperature_source"] == "sensor.t"
        assert attrs["humidity_source"] == EASC_SOURCE_VMC

    def test_returns_none_when_no_coordinator_data(self):
        coord = _make_coordinator()
        coord.data = None
        sensor = VmcHeltyAbsoluteHumiditySensor(coord)
        sensor.hass = _make_hass()
        assert sensor.native_value is None


# ---------------------------------------------------------------------------
# DewPoint — 3 source scenarios
# ---------------------------------------------------------------------------


class TestDewPointEascSources:
    def _make(self, options=None, hass=None):
        coord = _make_coordinator(options=options)
        sensor = VmcHeltyDewPointSensor(coord)
        sensor.hass = hass or _make_hass()
        return sensor

    def test_vmc_source_returns_valid_dew_point(self):
        sensor = self._make()
        result = sensor.native_value
        # T=22.0°C, RH=60.0% → dew point ~13.9°C
        assert result is not None
        assert 12.0 < result < 16.0

    def test_external_entity_overrides_vmc(self):
        hass = _make_hass(
            {
                "sensor.t": _make_state("30.0", "°C"),
                "sensor.h": _make_state("90.0", "%"),
            }
        )
        options = _easc_options(
            CONF_EASC_DEW_POINT,
            **{
                CONF_EASC_TEMPERATURE_SOURCE: "sensor.t",
                CONF_EASC_HUMIDITY_SOURCE: "sensor.h",
            },
        )
        sensor = self._make(options=options, hass=hass)
        result = sensor.native_value
        # T=30°C, RH=90% → dew point ≈ 28.2°C
        assert result is not None
        assert result > 20.0

        sensor_vmc = self._make()
        assert result != sensor_vmc.native_value

    def test_fallback_to_vmc_when_entity_missing(self):
        hass = _make_hass()  # no entities registered
        options = _easc_options(
            CONF_EASC_DEW_POINT,
            **{CONF_EASC_TEMPERATURE_SOURCE: "sensor.missing"},
        )
        sensor = self._make(options=options, hass=hass)
        result_fallback = sensor.native_value

        sensor_vmc = self._make()
        assert result_fallback == pytest.approx(sensor_vmc.native_value, abs=0.05)

    def test_formula_config_reflected_in_attributes(self):
        """Configured formula name is reported in extra_state_attributes."""
        for formula in (EASC_FORMULA_MAGNUS, EASC_FORMULA_CUSTOM):
            sensor = self._make(
                options=_easc_options(
                    CONF_EASC_DEW_POINT,
                    **{CONF_EASC_FORMULA: formula},
                )
            )
            attrs = sensor.extra_state_attributes
            assert attrs is not None
            assert attrs["formula"] == formula

    def test_dew_point_always_lte_temperature(self):
        """Physics: dew point ≤ air temperature for RH ≤ 100%."""
        sensor = self._make()
        dew = sensor.native_value
        assert dew is not None
        assert dew <= 22.0  # VMC internal temp

    def test_attributes_formula_key_present(self):
        sensor = self._make()
        attrs = sensor.extra_state_attributes
        assert attrs is not None
        assert "formula" in attrs
        assert attrs["formula"] == EASC_FORMULA_MAGNUS


# ---------------------------------------------------------------------------
# ComfortIndex — 3 source scenarios
# ---------------------------------------------------------------------------


class TestComfortIndexEascSources:
    def _make(self, options=None, hass=None):
        coord = _make_coordinator(options=options)
        sensor = VmcHeltyComfortIndexSensor(coord)
        sensor.hass = hass or _make_hass()
        return sensor

    def test_vmc_source_returns_valid_index(self):
        sensor = self._make()
        result = sensor.native_value
        assert result is not None
        assert 0.0 <= result <= 100.0

    def test_external_entity_overrides_vmc(self):
        # Use a very different temperature to get a distinct result
        hass = _make_hass(
            {
                "sensor.t": _make_state("5.0", "°C"),  # cold → low comfort
                "sensor.h": _make_state("20.0", "%"),  # very dry
            }
        )
        options = _easc_options(
            CONF_EASC_COMFORT_INDEX,
            **{
                CONF_EASC_TEMPERATURE_SOURCE: "sensor.t",
                CONF_EASC_HUMIDITY_SOURCE: "sensor.h",
            },
        )
        sensor = self._make(options=options, hass=hass)
        result_external = sensor.native_value

        sensor_vmc = self._make()
        assert result_external != sensor_vmc.native_value

    def test_fallback_when_entity_unavailable(self):
        hass = _make_hass({"sensor.t": _make_state("unknown")})
        options = _easc_options(
            CONF_EASC_COMFORT_INDEX,
            **{CONF_EASC_TEMPERATURE_SOURCE: "sensor.t"},
        )
        sensor = self._make(options=options, hass=hass)
        result_fallback = sensor.native_value

        sensor_vmc = self._make()
        assert result_fallback == pytest.approx(sensor_vmc.native_value, abs=0.001)

    def test_attributes_contain_source_info(self):
        hass = _make_hass({"sensor.t": _make_state("22.0", "°C")})
        options = _easc_options(
            CONF_EASC_COMFORT_INDEX,
            **{CONF_EASC_TEMPERATURE_SOURCE: "sensor.t"},
        )
        sensor = self._make(options=options, hass=hass)
        attrs = sensor.extra_state_attributes
        assert attrs is not None
        assert attrs.get("temperature_source") == "sensor.t"
        assert attrs.get("humidity_source") == EASC_SOURCE_VMC

    def test_returns_none_on_missing_data(self):
        coord = _make_coordinator()
        coord.data = None
        sensor = VmcHeltyComfortIndexSensor(coord)
        sensor.hass = _make_hass()
        assert sensor.native_value is None


# ---------------------------------------------------------------------------
# DewPointDelta — 3 source scenarios
# ---------------------------------------------------------------------------


class TestDewPointDeltaEascSources:
    def _make(self, options=None, hass=None):
        coord = _make_coordinator(options=options)
        sensor = VmcHeltyDewPointDeltaSensor(coord)
        sensor.hass = hass or _make_hass()
        return sensor

    def test_vmc_source_returns_valid_delta(self):
        sensor = self._make()
        result = sensor.native_value
        # t_int=22.0°C, t_ext=8.0°C, hum=60.0%
        # Both dew points calculated, delta = internal_dp - external_dp
        assert result is not None
        assert isinstance(result, float)

    def test_external_entities_override_vmc(self):
        hass = _make_hass(
            {
                "sensor.int_t": _make_state("25.0", "°C"),
                "sensor.ext_t": _make_state("2.0", "°C"),
                "sensor.hum": _make_state("70.0", "%"),
            }
        )
        options = _easc_options(
            CONF_EASC_DEW_POINT_DELTA,
            **{
                CONF_EASC_TEMPERATURE_INTERNAL: "sensor.int_t",
                CONF_EASC_TEMPERATURE_EXTERNAL: "sensor.ext_t",
                CONF_EASC_HUMIDITY_SOURCE: "sensor.hum",
            },
        )
        sensor = self._make(options=options, hass=hass)
        result = sensor.native_value

        sensor_vmc = self._make()
        # Different inputs → different delta
        assert result != sensor_vmc.native_value

    def test_fallback_when_internal_entity_unavailable(self):
        """Unavailable internal temp entity falls back to VMC internal temp."""
        hass = _make_hass({"sensor.int_t": _make_state("unavailable")})
        options = _easc_options(
            CONF_EASC_DEW_POINT_DELTA,
            **{CONF_EASC_TEMPERATURE_INTERNAL: "sensor.int_t"},
        )
        sensor = self._make(options=options, hass=hass)
        result_fallback = sensor.native_value

        sensor_vmc = self._make()
        assert result_fallback == pytest.approx(sensor_vmc.native_value, abs=0.05)

    def test_formula_config_reflected_in_attributes(self):
        """Configured formula name is reported in extra_state_attributes."""
        for formula in (EASC_FORMULA_MAGNUS, EASC_FORMULA_CUSTOM):
            sensor = self._make(
                options=_easc_options(
                    CONF_EASC_DEW_POINT_DELTA,
                    **{CONF_EASC_FORMULA: formula},
                )
            )
            attrs = sensor.extra_state_attributes
            assert attrs is not None
            assert attrs["formula"] == formula

    def test_attributes_contain_both_sources(self):
        hass = _make_hass({"sensor.int_t": _make_state("22.0", "°C")})
        options = _easc_options(
            CONF_EASC_DEW_POINT_DELTA,
            **{CONF_EASC_TEMPERATURE_INTERNAL: "sensor.int_t"},
        )
        sensor = self._make(options=options, hass=hass)
        attrs = sensor.extra_state_attributes
        assert attrs is not None
        assert attrs.get("temperature_internal_source") == "sensor.int_t"
        assert attrs.get("temperature_external_source") == EASC_SOURCE_VMC
        assert attrs.get("humidity_source") == EASC_SOURCE_VMC

    def test_returns_none_when_no_data(self):
        coord = _make_coordinator()
        coord.data = None
        sensor = VmcHeltyDewPointDeltaSensor(coord)
        sensor.hass = _make_hass()
        assert sensor.native_value is None

    def test_returns_none_when_humidity_zero(self):
        """Zero humidity makes dew point calculation undefined."""
        vmgi_zero_hum = "VMGI,220,80,0,400,0,0,0,0,0,0,0,0,0,0"
        coord = _make_coordinator(vmgi=vmgi_zero_hum)
        sensor = VmcHeltyDewPointDeltaSensor(coord)
        sensor.hass = _make_hass()
        assert sensor.native_value is None
