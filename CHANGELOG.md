# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Prepared for HACS distribution
- Added comprehensive HACS compliance documentation
- Enhanced README with installation badges and community links

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
