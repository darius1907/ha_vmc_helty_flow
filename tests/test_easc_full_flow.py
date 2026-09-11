"""TEST-006: Full integration testing EASC — end-to-end pipeline.

Verifies:
1. Full pipeline: options config → sensor reads correct values
2. Multiple EASC sensors enabled simultaneously
3. Regression: non-EASC sensors unaffected by EASC options
4. Config flow complete: _flatten → _build round-trip preserves all values
5. EASC options change propagates to sensor behaviour at runtime
6. is_sensor_enabled reflects options config correctly
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from custom_components.vmc_helty_flow.config_flow import (
    _build_easc_config_from_input,
    _flatten_easc_config,
)
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
from custom_components.vmc_helty_flow.easc_schema import (
    is_sensor_enabled,
    validate_easc_config,
)
from custom_components.vmc_helty_flow.sensor import (
    VmcHeltyAbsoluteHumiditySensor,
    VmcHeltyComfortIndexSensor,
    VmcHeltyDewPointDeltaSensor,
    VmcHeltyDewPointSensor,
    VmcHeltySensor,
)

# ---------------------------------------------------------------------------
# Shared stubs
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


def _all_easc_options(
    t_source: str = EASC_SOURCE_VMC,
    h_source: str = EASC_SOURCE_VMC,
    formula: str = EASC_FORMULA_MAGNUS,
) -> dict:
    """Build options enabling all 4 advanced sensors with given sources."""
    sensors = {
        CONF_EASC_ABSOLUTE_HUMIDITY: {
            CONF_EASC_ENABLED: True,
            CONF_EASC_TEMPERATURE_SOURCE: t_source,
            CONF_EASC_HUMIDITY_SOURCE: h_source,
            CONF_EASC_FORMULA: formula,
        },
        CONF_EASC_DEW_POINT: {
            CONF_EASC_ENABLED: True,
            CONF_EASC_TEMPERATURE_SOURCE: t_source,
            CONF_EASC_HUMIDITY_SOURCE: h_source,
            CONF_EASC_FORMULA: formula,
        },
        CONF_EASC_COMFORT_INDEX: {
            CONF_EASC_ENABLED: True,
            CONF_EASC_TEMPERATURE_SOURCE: t_source,
            CONF_EASC_HUMIDITY_SOURCE: h_source,
            CONF_EASC_FORMULA: formula,
        },
        CONF_EASC_DEW_POINT_DELTA: {
            CONF_EASC_ENABLED: True,
            CONF_EASC_TEMPERATURE_INTERNAL: t_source,
            CONF_EASC_TEMPERATURE_EXTERNAL: h_source,  # reuse for simplicity
            CONF_EASC_HUMIDITY_SOURCE: h_source,
            CONF_EASC_FORMULA: formula,
        },
    }
    return {CONF_EASC_CONFIG: {"advanced_sensors": sensors}}


# ---------------------------------------------------------------------------
# 1. Full pipeline: options → sensor reads correct values
# ---------------------------------------------------------------------------


class TestFullPipeline:
    def test_all_sensors_return_values_with_vmc_source(self):
        """All 4 advanced sensors compute non-None values from VMC data."""
        options = _all_easc_options()
        coord = _make_coordinator(options=options)
        hass = _make_hass()

        sensors = [
            VmcHeltyAbsoluteHumiditySensor(coord),
            VmcHeltyDewPointSensor(coord),
            VmcHeltyComfortIndexSensor(coord),
        ]
        dpd = VmcHeltyDewPointDeltaSensor(coord)

        for sensor in [*sensors, dpd]:
            sensor.hass = hass
            assert (
                sensor.native_value is not None
            ), f"{sensor.__class__.__name__} returned None"

    def test_sensor_uses_external_entity_when_configured(self):
        """External entity value propagates through options → sensor."""
        ext_temp = "sensor.living_room_temp"
        hass = _make_hass({ext_temp: _make_state("28.0", "°C")})
        options = {
            CONF_EASC_CONFIG: {
                "advanced_sensors": {
                    CONF_EASC_ABSOLUTE_HUMIDITY: {
                        CONF_EASC_ENABLED: True,
                        CONF_EASC_TEMPERATURE_SOURCE: ext_temp,
                        CONF_EASC_HUMIDITY_SOURCE: EASC_SOURCE_VMC,
                    }
                }
            }
        }
        coord = _make_coordinator(options=options)
        sensor = VmcHeltyAbsoluteHumiditySensor(coord)
        sensor.hass = hass

        attrs = sensor.extra_state_attributes
        assert attrs is not None
        assert attrs["temperature_source"] == ext_temp
        # temperature_value should come from the entity (28.0°C), not VMC (22.0°C)
        assert "28.0" in attrs["temperature_value"]

    def test_options_change_updates_sensor_behaviour(self):
        """Changing coordinator options at runtime changes sensor readings."""
        coord = _make_coordinator()
        hass = _make_hass({"sensor.hot": _make_state("40.0", "°C")})

        sensor = VmcHeltyAbsoluteHumiditySensor(coord)
        sensor.hass = hass

        # Default: no EASC config → reads from VMC (22.0°C)
        value_vmc = sensor.native_value
        assert value_vmc is not None

        # Change options to use hot entity (40.0°C) → result should differ
        coord.config_entry.options = {
            CONF_EASC_CONFIG: {
                "advanced_sensors": {
                    CONF_EASC_ABSOLUTE_HUMIDITY: {
                        CONF_EASC_ENABLED: True,
                        CONF_EASC_TEMPERATURE_SOURCE: "sensor.hot",
                    }
                }
            }
        }
        value_hot = sensor.native_value
        assert value_hot is not None
        assert value_hot != value_vmc


# ---------------------------------------------------------------------------
# 2. Multiple EASC sensors enabled simultaneously
# ---------------------------------------------------------------------------


class TestMultipleSensorsEnabled:
    def test_all_four_sensors_active_simultaneously(self):
        """Four advanced sensors can compute values in parallel without interference."""
        coord = _make_coordinator(options=_all_easc_options())
        hass = _make_hass()

        ah = VmcHeltyAbsoluteHumiditySensor(coord)
        dp = VmcHeltyDewPointSensor(coord)
        ci = VmcHeltyComfortIndexSensor(coord)
        dpd = VmcHeltyDewPointDeltaSensor(coord)

        for s in (ah, dp, ci, dpd):
            s.hass = hass

        ah_val = ah.native_value
        dp_val = dp.native_value
        ci_val = ci.native_value
        dpd_val = dpd.native_value

        assert ah_val is not None
        assert dp_val is not None
        assert ci_val is not None
        assert dpd_val is not None

        # Sanity checks on units/ranges
        assert ah_val > 0  # g/m³
        assert dp_val <= 22.0  # dew point ≤ air temperature
        assert 0.0 <= ci_val <= 100.0  # comfort index
        assert isinstance(dpd_val, float)  # delta in °C

    def test_each_sensor_uses_its_own_source_independently(self):
        """Each sensor reads its own source; one source doesn't affect others."""
        ah_entity = "sensor.ah_temp"
        hass = _make_hass({ah_entity: _make_state("35.0", "°C")})

        # Only AbsoluteHumidity uses an external entity; others use VMC
        options = {
            CONF_EASC_CONFIG: {
                "advanced_sensors": {
                    CONF_EASC_ABSOLUTE_HUMIDITY: {
                        CONF_EASC_ENABLED: True,
                        CONF_EASC_TEMPERATURE_SOURCE: ah_entity,
                    },
                    CONF_EASC_DEW_POINT: {CONF_EASC_ENABLED: True},
                }
            }
        }
        coord = _make_coordinator(options=options)

        ah = VmcHeltyAbsoluteHumiditySensor(coord)
        dp = VmcHeltyDewPointSensor(coord)
        ah.hass = dp.hass = hass

        ah_attrs = ah.extra_state_attributes
        dp_attrs = dp.extra_state_attributes

        assert ah_attrs["temperature_source"] == ah_entity
        assert dp_attrs["temperature_source"] == EASC_SOURCE_VMC


# ---------------------------------------------------------------------------
# 3. Regression: non-EASC sensors unaffected by EASC options
# ---------------------------------------------------------------------------


class TestNonEascSensorRegression:
    def test_vmheltysensor_unaffected_by_easc_options(self):
        """Base VmcHeltySensor (temperature_internal) reads from VMGI correctly."""
        options = _all_easc_options(t_source="sensor.ext", h_source="sensor.ext")
        coord = _make_coordinator(options=options)

        # VmcHeltySensor reads directly from VMGI, doesn't use EASCDataProvider
        sensor = VmcHeltySensor(
            coord, "temperature_internal", "Temperatura Interna", "°C"
        )
        assert sensor.native_value == pytest.approx(22.0)

    def test_vmheltysensor_humidity_unaffected(self):
        options = _all_easc_options()
        coord = _make_coordinator(options=options)
        sensor = VmcHeltySensor(coord, "humidity", "Umidità", "%")
        assert sensor.native_value == pytest.approx(60.0)

    def test_vmheltysensor_no_data_returns_none(self):
        coord = _make_coordinator(options=_all_easc_options())
        coord.data = None
        sensor = VmcHeltySensor(coord, "temperature_internal", "Temp", "°C")
        assert sensor.native_value is None


# ---------------------------------------------------------------------------
# 4. Config flow complete round-trip
# ---------------------------------------------------------------------------


class TestConfigFlowRoundTrip:
    def test_flatten_build_roundtrip_with_formula(self):
        """Full round-trip: flatten → build → flatten should be identity."""
        original = {
            "advanced_sensors": {
                CONF_EASC_ABSOLUTE_HUMIDITY: {
                    CONF_EASC_ENABLED: True,
                    CONF_EASC_TEMPERATURE_SOURCE: "sensor.t",
                    CONF_EASC_HUMIDITY_SOURCE: EASC_SOURCE_VMC,
                    CONF_EASC_FORMULA: EASC_FORMULA_CUSTOM,
                },
                CONF_EASC_DEW_POINT: {
                    CONF_EASC_ENABLED: False,
                    CONF_EASC_TEMPERATURE_SOURCE: EASC_SOURCE_VMC,
                    CONF_EASC_HUMIDITY_SOURCE: EASC_SOURCE_VMC,
                    CONF_EASC_FORMULA: EASC_FORMULA_MAGNUS,
                },
                CONF_EASC_COMFORT_INDEX: {
                    CONF_EASC_ENABLED: True,
                    CONF_EASC_TEMPERATURE_SOURCE: "sensor.ci_t",
                    CONF_EASC_HUMIDITY_SOURCE: "sensor.ci_h",
                    CONF_EASC_FORMULA: EASC_FORMULA_CUSTOM,
                },
                CONF_EASC_DEW_POINT_DELTA: {
                    CONF_EASC_ENABLED: False,
                    CONF_EASC_TEMPERATURE_INTERNAL: EASC_SOURCE_VMC,
                    CONF_EASC_TEMPERATURE_EXTERNAL: EASC_SOURCE_VMC,
                    CONF_EASC_HUMIDITY_SOURCE: EASC_SOURCE_VMC,
                    CONF_EASC_FORMULA: EASC_FORMULA_MAGNUS,
                },
            }
        }
        flat = _flatten_easc_config(original)
        rebuilt = _build_easc_config_from_input(flat)
        flat2 = _flatten_easc_config(rebuilt)
        assert flat == flat2

    def test_all_17_fields_present_after_flatten(self):
        flat = _flatten_easc_config({})
        assert len(flat) == 17

    def test_formula_fields_survive_round_trip(self):
        flat_in = _flatten_easc_config({})
        flat_in["abs_hum_formula"] = EASC_FORMULA_CUSTOM
        flat_in["dew_point_delta_formula"] = EASC_FORMULA_CUSTOM

        rebuilt = _build_easc_config_from_input(flat_in)
        flat_out = _flatten_easc_config(rebuilt)

        assert flat_out["abs_hum_formula"] == EASC_FORMULA_CUSTOM
        assert flat_out["dew_point_delta_formula"] == EASC_FORMULA_CUSTOM
        # Others remain default
        assert flat_out["dew_point_formula"] == EASC_FORMULA_MAGNUS


# ---------------------------------------------------------------------------
# 5. is_sensor_enabled reflects options config
# ---------------------------------------------------------------------------


class TestIsSensorEnabled:
    def _cfg(self, sensor_key: str, enabled: bool) -> dict:
        raw = {"advanced_sensors": {sensor_key: {CONF_EASC_ENABLED: enabled}}}
        return validate_easc_config(raw)

    def test_enabled_true_for_all_sensors(self):
        for key in (
            CONF_EASC_ABSOLUTE_HUMIDITY,
            CONF_EASC_DEW_POINT,
            CONF_EASC_COMFORT_INDEX,
            CONF_EASC_DEW_POINT_DELTA,
        ):
            assert is_sensor_enabled(self._cfg(key, True), key) is True

    def test_enabled_false_by_default(self):
        empty = validate_easc_config({})
        for key in (
            CONF_EASC_ABSOLUTE_HUMIDITY,
            CONF_EASC_DEW_POINT,
            CONF_EASC_COMFORT_INDEX,
            CONF_EASC_DEW_POINT_DELTA,
        ):
            assert is_sensor_enabled(empty, key) is False

    def test_enabled_flag_does_not_affect_native_value(self):
        """CONF_EASC_ENABLED is a UI flag; sensor computes regardless."""
        # disabled EASC → sensor still computes from VMC
        coord_disabled = _make_coordinator(
            options={
                CONF_EASC_CONFIG: {
                    "advanced_sensors": {
                        CONF_EASC_ABSOLUTE_HUMIDITY: {CONF_EASC_ENABLED: False}
                    }
                }
            }
        )
        coord_enabled = _make_coordinator(
            options={
                CONF_EASC_CONFIG: {
                    "advanced_sensors": {
                        CONF_EASC_ABSOLUTE_HUMIDITY: {CONF_EASC_ENABLED: True}
                    }
                }
            }
        )
        s_disabled = VmcHeltyAbsoluteHumiditySensor(coord_disabled)
        s_enabled = VmcHeltyAbsoluteHumiditySensor(coord_enabled)
        s_disabled.hass = s_enabled.hass = _make_hass()

        # Both should return the same value (from VMC) since no external source is set
        assert s_disabled.native_value == pytest.approx(
            s_enabled.native_value, abs=0.01
        )
