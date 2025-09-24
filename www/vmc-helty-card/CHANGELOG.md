# Changelog

All notable changes to the VMC Helty Card will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-24

### Added
- 🎉 **Initial release** of VMC Helty Control Card
- 🎛️ **Complete fan speed control** with visual buttons (0-4 speeds)
- 📊 **Environmental monitoring** for temperature, humidity, CO₂, VOC
- 🔄 **Real-time updates** with animated fan icon and status indicators
- 📱 **Responsive design** optimized for mobile, tablet, and desktop
- 🎨 **Multiple themes** support (Default, Compact, Minimal)
- ⚙️ **Visual configuration editor** with auto-discovery of VMC entities
- 🚀 **Special modes support** (Night Mode, Boost, Free Cooling)
- 💡 **Light controls** for VMC LED panel management
- 📈 **Advanced sensors** (Dew Point, Comfort Index, Air Exchange calculations)
- 🟢 **Connection status** monitoring with WiFi indicators
- 🎯 **Color-coded status** indicators for all sensor values
- 📋 **Comprehensive documentation** with installation guide and examples
- 🔧 **Compact card variant** for smaller dashboard layouts

### Features

#### Core Functionality
- Fan speed control with percentage-based commands
- Real-time environmental sensor monitoring
- Connection status with automatic reconnection detection
- Entity auto-discovery based on fan entity configuration

#### Visual Interface
- Animated fan icon with rotation based on speed
- Color-coded sensor cards with status indicators
- Touch-friendly controls optimized for mobile devices
- Hover effects and smooth transitions

#### Compatibility
- **VMC Helty Flow Plus**: Basic speed control, temperature, humidity
- **VMC Helty Flow Elite**: Full feature set including CO₂ and VOC sensors
- **Home Assistant**: Compatible with HA Core ≥2024.1.0
- **Browsers**: Modern browsers with ES6+ support

#### Configuration Options
- Entity selection with auto-discovery
- Granular display control (show/hide individual sensors)
- Theme selection for different layout preferences  
- Advanced YAML configuration for power users

### Technical Details
- Built as native Web Component (Custom Element)
- No external dependencies beyond Home Assistant
- Efficient entity state monitoring with change detection
- Responsive CSS Grid layouts with mobile-first approach
- TypeScript-style JSDoc documentation

### Documentation
- Complete installation guide with troubleshooting
- Configuration examples for all use cases
- API documentation for developers
- Performance optimization guidelines

## [Unreleased]

### Planned Features
- 📊 **Historical charts** integration with Chart.js
- 🤖 **Automation status** display and quick controls
- 🔔 **Notification center** for VMC alerts and maintenance
- 🌡️ **Weather integration** for external temperature sources
- 📅 **Schedule display** showing upcoming automation events
- 🎛️ **Advanced controls** for filter reset and diagnostic modes
- 🔒 **User permissions** support for restricted controls
- 🌍 **Multi-language** support with translations
- 🎨 **Custom themes** with CSS variable overrides
- 📱 **Progressive Web App** features for mobile installation

### Planned Improvements
- Performance optimizations for large sensor datasets
- Enhanced accessibility (ARIA labels, keyboard navigation)
- Improved error handling with user-friendly messages
- Automated testing suite for quality assurance
- HACS (Home Assistant Community Store) integration

---

## Version History Notes

### Versioning Strategy
- **Major versions** (x.0.0): Breaking changes, major new features
- **Minor versions** (1.x.0): New features, improvements, non-breaking changes  
- **Patch versions** (1.0.x): Bug fixes, documentation updates, minor improvements

### Compatibility Promise
- **Patch versions**: No breaking changes, always safe to update
- **Minor versions**: No breaking configuration changes, may add new features
- **Major versions**: May include breaking changes, migration guide provided

### Support Policy
- **Current version**: Full support with bug fixes and security updates
- **Previous minor**: Critical security fixes only
- **Older versions**: Community support through GitHub issues

---

## Migration Guide

### From Future Versions
*Migration guides will be added here when breaking changes are introduced*

### Configuration Migration
*Automated migration tools and guides will be provided for major version changes*

---

## Contributors

- **Development Team**: VMC Helty Integration Team
- **Testing**: Home Assistant Community
- **Documentation**: Community contributors
- **Translations**: Community volunteers (future)

## Acknowledgments

- Home Assistant Core team for the excellent platform
- Helty for creating quality VMC systems
- Community members for feedback and testing
- Contributors to similar custom cards for inspiration