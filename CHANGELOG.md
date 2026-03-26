# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-03-226

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
