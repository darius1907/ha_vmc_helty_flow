# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-09-11

### 🐛 Fixed

- **Home Assistant responsiveness during VMC communication failures** (#5): the coordinator now honors the configured connection timeout instead of silently falling back to a hardcoded 5s default, and the blocking `subprocess.run()` ping diagnostic no longer runs on the event loop (moved to a worker thread via `asyncio.to_thread`) — this was the root cause of multi-second-to-minute HA UI freezes when multiple VMC devices went offline at once.
- **Hardcoded TCP port** (#9): the port selected during device discovery/setup is now actually used at runtime. Every command (coordinator polling, fan/light/switch/sensor/button entities, device registry, device actions) previously always targeted port 5001 regardless of what was configured, making any device on a non-default port completely unreachable.
- **Crash on config entry reload** (#11): reloading a config entry (triggered automatically whenever a VMC device's mnemonic name changes) no longer raises `ConfigEntryError`. The integration now delegates to Home Assistant's own `hass.config_entries.async_reload()` instead of manually re-implementing unload+setup, which bypassed Home Assistant's state-machine transition and could leave the entry in a degraded state.
- **`scan_interval` and `retry_attempts` options ignored** (#13, #14): both values, configurable in the options flow, were saved but never read back. Polling now honors the configured `scan_interval` instead of always defaulting to 180s, and failed TCP commands are now actually retried up to `retry_attempts` times instead of failing on the first attempt.
- **Retry not triggered by empty/invalid device responses** (#16): the VMC hardware occasionally closes the connection with an empty payload instead of a proper status response, without raising a network-level error — this silently bypassed the retry logic and could delay integration startup (`ConfigEntryNotReady`) or fail a polling cycle outright. The coordinator now retries on this condition too. Device registration/reload lookups (`device_registry.py`) also now honor the configured timeout and retry count, not just the port.

### 🧪 Testing

- **754 tests** — all passing.
- New/updated coverage for TCP retry behavior (connection errors, empty responses, protocol errors), coordinator `timeout`/`port`/`retry_attempts`/`scan_interval` properties, and device registry timeout/retry threading.

## [1.2.0] - 2026-03-30

### ✨ Added

#### EASC — External Advanced Sensor Configuration

- **`EASCDataProvider`** (`easc_provider.py`): single access point for temperature and humidity data used by the four advanced calculated sensors. Reads from the VMC device (`source = "vmc"`) or any Home Assistant entity, with automatic unit conversion (°F→°C, 0–1 fraction→%) and automatic VMC fallback when an external entity is unavailable or non-numeric.
- **`magnus_coefficients(formula)`**: pure function returning `(a, b)` coefficients for two supported formulas:
  - `"magnus"` — Magnus-Tetens (a=17.27, b=237.7), general purpose −40 °C to +50 °C.
  - `"custom"` — August-Roche-Magnus (a=17.625, b=243.04), WMO standard, more accurate 0–60 °C.
- **EASC Options Flow step** (`async_step_advanced_sensors`): new two-step options form. Step 1 adds a *"Configure advanced sensors"* checkbox. Step 2 exposes 17 fields (enable, temperature source, humidity source, formula) for each of the four advanced sensors. Sources validated with `validate_source`; formulas validated with `validate_formula`.
- **EASC schema helpers** (`easc_schema.py`): `validate_easc_config`, `validate_source`, `validate_formula`, `get_sensor_config`, `is_sensor_enabled`.
- **EASC diagnostics** (`diagnostics.py`): new `easc` section in `async_get_config_entry_diagnostics` showing configured/enabled state and availability of each source entity (`available`, `state`, `last_updated`, `reason`).
- **New advanced sensor** `VmcHeltyAbsoluteHumiditySensor`: calculates absolute humidity in g/m³ using the Magnus formula. Supports EASC external sources (SENS-004 / EASC-004).
- **Advanced sensors refactored** to use `EASCDataProvider`: `VmcHeltyDewPointSensor`, `VmcHeltyComfortIndexSensor`, `VmcHeltyDewPointDeltaSensor` all support configurable external sources and formula selection (EASC-005→007, EASC-009).
- **New binary sensor** `VmcHeltyFilterWarningBinarySensor`: turns ON when filter hours exceed 90 % of maximum filter life (~15 970 h out of 17 744 h) (SENS-005).
- **Debug logging** for every EASC data read: source, value, and fallback reason emitted at `DEBUG` level (EASC-008).
- **`strings.json`** updated with labels and descriptions for all 17 EASC options fields and `invalid_easc_formula` error key.
- **Documentation**: `docs/EXTERNAL_ADVANCED_SENSORS.md` — full EASC guide including step-by-step setup, source field reference, formula comparison table, Netatmo/ESPHome/weather integration examples, automatic fallback behaviour, and troubleshooting.

### 🔄 Changed

- `_flatten_easc_config` / `_build_easc_config_from_input` (config_flow helpers) now include per-sensor `formula` fields (total: 17 flat keys, up from 13).
- `VmcHeltyDewPointDeltaSensor._calculate_dew_point()` now accepts a `formula` parameter and uses `magnus_coefficients(formula)` instead of hardcoded coefficients.
- `extra_state_attributes` for all four advanced sensors now report `"formula"`, `"temperature_source"`, and `"humidity_source"` reflecting the active configuration.

### 🧪 Testing

- **757 tests** — all passing. Coverage **84 %** (gate: 65 %).
- New test files:
  - `tests/test_easc_provider.py` — 45 tests: `celsius_from_unit`, `humidity_to_percent`, `magnus_coefficients`, `EASCDataProvider` (VMC source, entity source, fallback, logging).
  - `tests/test_easc_integration_sensors.py` — 24 tests: 3 source scenarios × 4 advanced sensors (VMC, external entity, fallback), error conditions, formula attribute propagation.
  - `tests/test_easc_full_flow.py` — 14 tests: full options→sensor pipeline, multi-sensor simultaneous operation, non-EASC sensor regression, config flow round-trip, `is_sensor_enabled`.
  - `tests/test_easc_options_flow.py` — 23 tests: `_flatten_easc_config`, `_build_easc_config_from_input`, options step init/advanced_sensors, formula validation.

### 📚 Documentation

- `README.md`: added EASC quick-setup section with Netatmo example, updated sensor list with `(EASC-enabled)` tags, updated "What's new" section.
- `docs/EXTERNAL_ADVANCED_SENSORS.md`: new comprehensive EASC guide.

---

## [1.1.1] - 2026-03-26

### ⚠️ Breaking changes
- Removed obsolete `update_room_volume` service: room volume is now managed only through Options Flow

### 🔄 Changed
- `VmcHeltySSIDText` is now explicitly read-only: SSID edits are blocked with a clear user-facing error
- `VmcHeltyPasswordText` now supports password updates while preserving the current SSID
- WiFi password updates now validate length using integration constraints (`MIN_PASSWORD_LENGTH` / `MAX_PASSWORD_LENGTH`)
- WiFi password updates now use protocol payload padding (`VMSL <ssid_padded><password_padded>`) and trigger coordinator refresh after success
- `VmcHeltyResetFilterButton` now uses `FILTER_MAX_HOURS` dynamically for reset command generation
- Service callbacks are now registered with proper async handlers (instead of lambda wrappers) so Home Assistant always awaits coroutine services correctly
- Removed obsolete `update_room_volume` service: room volume is now managed only through Options Flow
- Cleaned service metadata/translations to remove legacy `update_room_volume` references

### 🐛 Fixed
- Prevented accidental synchronous writes on text entities by raising explicit `HomeAssistantError` in sync `set_value` paths
- Fixed warning `coroutine '_handle_set_special_mode' was never awaited` during special mode service execution
- Aligned special mode mappings between the integration and the Lovelace card so `hyperventilation` uses speed `5` and `night_mode` uses speed `6` consistently

### ✨ Added
- New advanced sensor `VmcHeltyFilterLifePercentageSensor` (SENS-001)
- New sensor `VmcHeltyPowerSensor` for instantaneous power estimate in W (SENS-003)
- New sensor `VmcHeltyDailyEnergyEstimateSensor` for daily energy estimate in Wh (SENS-002)
- New binary sensor `VmcHeltyAirQualityAlertBinarySensor` (SENS-006)
- New binary sensor `VmcHeltyCondensationRiskBinarySensor` (SENS-007)
- New binary sensor `VmcHeltyOfflineBinarySensor` (SENS-008)

### 🔄 Changed
- Filter hours are now parsed from device response and exposed consistently for filter-life calculations
- Updated `FILTER_MAX_HOURS` from `3600` to `17744` (value aligned with real filter reset behavior)
- Updated humidity blueprint notification default service (`notify.mobile_app_m2101k9g`)

### 🐛 Fixed
- Refactored filter-life tests to use dynamic expectations based on `FILTER_MAX_HOURS`
- Improved robustness of filter-life test fixtures and edge-case handling

### 🧪 Testing
- Full test suite validated: 578 tests passed
- Pre-commit checks passed (format, lint, type-check, tests)

### 📚 Documentation
- Added comprehensive roadmap and planning updates for upcoming releases
- Added `EASC_SPECIFICATION.md` for External Advanced Sensor Configuration planning
- Updated roadmap filter thresholds to match new max filter lifetime (`17744h`)
- Added English blueprint guide: `blueprints/BLUEPRINT_GUIDE_EN.md`
- Blueprint references updated:
  - `blueprints/README.md`
  - `blueprints/BLUEPRINT_GUIDE.md`
  - `blueprints/BLUEPRINT_GUIDE_EN.md`

## [1.1.0] - 2026-03-23

### 🎉 Major Improvements

#### Room Volume Management Enhancement
- **BREAKING CHANGE**: Room volume now managed through `config_entry.options` instead of `config_entry.data`
- Automatic migration from old format to new format (backward compatible)
- Enhanced Options Flow UI with room volume configuration
- Volume now modifiable via integration options (⚙️ button in UI)
- Improved validation with consistent limits (5.0-200.0 m³)
- Automatic reload after options update

#### Options Flow Enhancements
- New comprehensive options UI
- Support for configurable parameters:
  - Room volume (5.0-200.0 m³)
  - Scan interval (30-600 seconds)
  - Connection timeout (5-60 seconds)
  - Retry attempts (1-10)
- Better descriptions and suggested values
- Help text improvements

### 🐛 Bug Fixes
- Fixed fan slider disabled when fan speed set to 0
- Fixed special modes (hyperventilation, night mode, free cooling) disabled when fan off
- Fixed sensors toggle disabled when fan off
- Users can now turn the fan back on using slider or special modes

### 🔧 Technical Improvements
- Removed duplicate constants in const.py
- Standardized volume limits across all components
- Updated coordinator to read only from options
- Improved type safety and error handling
- Service `update_room_volume` now uses options instead of data
- Enhanced code quality (Black formatting, Ruff compliance)
- Updated documentation in strings.json and services.yaml
- VMC Helty Card updated to v2.1.1

### 📝 Service Updates
- `update_room_volume` service updated to use config_entry.options
- Proper reload trigger after volume update
- Improved validation using MIN_ROOM_VOLUME and MAX_ROOM_VOLUME constants

### ✅ Testing
- All core tests passing (18/18)
- Updated test fixtures to use options
- Added migration scenario tests
- Fixed async mocks in service tests
- Pylint rating: 9.83/10

### 📚 Documentation
- Updated strings.json with clearer descriptions
- Updated services.yaml with correct volume limits
- Enhanced help text for all configuration steps

## [1.0.0] - 2024-09-24

### Added
- 🚀 Complete VMC Helty Flow integration for Home Assistant
- 🔍 Advanced device discovery (incremental scan mode)
- 🎛️ Full VMC control (fan, modes, sensors, lighting)
- 📊 Comprehensive environmental monitoring (temperature, humidity, CO2, VOC)
- 🔧 System management (filter monitoring, reset, network configuration)
- 💡 Integrated lighting control with timer functionality
- 📈 Advanced sensor calculations (dew point, air quality indices)
- 🌐 Network configuration management (IP, WiFi settings)
- ✅ Professional Lovelace card with LitElement implementation
- 📝 Visual card editor with real-time validation
- 🎨 Home Assistant theming and accessibility compliance
- 🔧 Comprehensive diagnostics and error handling
- 🧪 Complete test suite with >95% coverage
- 📚 Extensive documentation and quick start guides

### Features
- **Device Discovery**: Smart network scanning with user control
- **Multi-VMC Support**: Handle multiple devices in single installation
- **Environmental Monitoring**: Real-time air quality data
- **Filter Management**: Automatic filter life tracking
- **Lighting Control**: Integrated light control with timers
- **Network Management**: WiFi and IP configuration
- **Custom Card**: Professional Lovelace interface
- **Accessibility**: Full ARIA support and keyboard navigation
- **Responsive Design**: Adapts to all screen sizes
- **Theming**: Follows Home Assistant design system

### Technical
- **Architecture**: Modern async Python implementation
- **Quality Scale**: Silver level Home Assistant integration
- **Standards**: Strict Home Assistant guidelines compliance
- **Testing**: Comprehensive test coverage with pytest
- **CI/CD**: Automated deployment and validation
- **Documentation**: Complete user and developer guides
- **HACS Ready**: Prepared for Home Assistant Community Store

### Supported Entities
- **Fan**: Variable speed control and operational modes
- **Sensors**: Temperature, humidity, CO2, VOC, air quality
- **Switches**: Mode control, sensor activation, panel LED
- **Lights**: Integrated lighting with timer support
- **Buttons**: Filter reset and system controls
- **Advanced Sensors**: Dew point, air change rates, flow calculations

### Installation Methods
1. **HACS** (Recommended): Easy installation and updates
2. **Manual**: Direct file copy for advanced users
3. **Automated**: CI/CD deployment for development

## [0.9.0] - 2024-09-20

### Added
- Initial beta release
- Basic VMC connectivity and control
- Core sensor implementation
- Initial config flow

### Changed
- Refactored device discovery logic
- Improved error handling
- Enhanced entity organization

## [0.1.0] - 2024-09-15

### Added
- Project initialization
- Basic integration structure
- Initial development environment setup

---

**Note**: This integration follows [Semantic Versioning](https://semver.org/).
- **Major** version changes may include breaking changes
- **Minor** version changes add functionality in a backwards compatible manner
- **Patch** version changes include backwards compatible bug fixes
