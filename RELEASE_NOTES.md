# VMC Helty Flow Integration Release Notes

## Release Process and Standards

This document outlines the release process, versioning strategy, and standards for the VMC Helty Flow Home Assistant integration.

## 📋 Release Checklist

### Pre-Release Preparation
- [ ] Update version in `manifest.json`
- [ ] Update version in `hacs.json` (if changed)
- [ ] Update `CHANGELOG.md` with new features and fixes
- [ ] Update README.md if needed
- [ ] Run full test suite: `pytest tests/ --cov=custom_components.vmc_helty_flow`
- [ ] Run code quality checks: `pre-commit run --all-files`
- [ ] Test HACS installation process
- [ ] Validate manifest: `python -m script.hassfest --integration-path custom_components/vmc_helty_flow`
- [ ] Test with Home Assistant development version

### Release Creation
- [ ] Create git tag with version number: `git tag v1.0.0`
- [ ] Push tags: `git push origin --tags`
- [ ] Create GitHub release with changelog
- [ ] Attach zip file of `custom_components/vmc_helty_flow/` to release
- [ ] Mark release as latest if stable

### Post-Release
- [ ] Verify HACS can install the new release
- [ ] Update documentation if needed
- [ ] Announce release in community forums
- [ ] Monitor for issues and feedback

## 🔢 Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):

### Version Format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes, API changes, major architecture updates
- **MINOR**: New features, entity additions, backward-compatible changes
- **PATCH**: Bug fixes, documentation updates, minor improvements

### Examples:
- `1.0.0` → `1.1.0`: Added new sensor types
- `1.1.0` → `1.1.1`: Fixed config flow validation bug
- `1.x.x` → `2.0.0`: Changed entity naming scheme (breaking change)

### Pre-Release Versions:
- `1.0.0-alpha.1`: Early development version
- `1.0.0-beta.1`: Feature-complete, testing needed
- `1.0.0-rc.1`: Release candidate, final testing

## 🚀 Release Types

### Major Release (x.0.0)
**Frequency**: 6-12 months
**Contents**:
- New major features
- Architecture improvements
- Breaking changes (with migration guide)
- Home Assistant version updates

**Example**: `2.0.0`
- New climate entity support
- Redesigned config flow
- Updated entity naming (breaking change)

### Minor Release (x.y.0)
**Frequency**: 1-3 months
**Contents**:
- New features and entities
- Enhanced functionality
- Performance improvements
- New VMC model support

**Example**: `1.2.0`
- Added CO2 calibration sensor
- Enhanced error reporting
- Support for new VMC models

### Patch Release (x.y.z)
**Frequency**: As needed
**Contents**:
- Bug fixes
- Security updates
- Documentation improvements
- Minor enhancements

**Example**: `1.1.1`
- Fixed sensor update intervals
- Improved error handling
- Updated documentation

### Hotfix Release
**Emergency releases for critical issues**:
- Security vulnerabilities
- Data loss issues
- Integration breaking bugs

## 📝 Changelog Standards

### Format
We follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [1.1.0] - 2024-09-24

### Added
- New sensor for filter replacement countdown
- Support for VMC Model XYZ
- Configuration validation improvements

### Changed
- Improved sensor update frequency
- Enhanced error messages in config flow

### Fixed
- Fixed temperature sensor precision issues
- Resolved config flow timeout problems

### Deprecated
- Old filter sensor entity (use new filter countdown)

### Removed
- Legacy API support for pre-v1.0 devices

### Security
- Updated credential handling for enhanced security
```

### Categories:
- **Added**: New features, entities, or capabilities
- **Changed**: Modifications to existing functionality
- **Fixed**: Bug fixes and issue resolutions
- **Deprecated**: Soon-to-be removed features
- **Removed**: Deleted features or support
- **Security**: Security-related changes

## 🏷️ Release Naming

### Release Tags
- Format: `v{MAJOR}.{MINOR}.{PATCH}`
- Examples: `v1.0.0`, `v1.2.1`, `v2.0.0-beta.1`

### Release Titles
- Major: "VMC Helty Flow v2.0.0 - Major Update with Climate Control"
- Minor: "VMC Helty Flow v1.2.0 - Enhanced Sensors and Model Support"
- Patch: "VMC Helty Flow v1.1.1 - Bug Fixes and Improvements"

### Release Notes Template
```markdown
# VMC Helty Flow v1.2.0 - Enhanced Sensors and Model Support

## 🎉 What's New

### ✨ New Features
- **CO2 Calibration Sensor**: Monitor and calibrate CO2 sensor accuracy
- **Enhanced Error Reporting**: Better diagnostics for troubleshooting
- **Model XYZ Support**: Full support for new VMC models

### 🔧 Improvements
- **Performance**: Faster sensor updates and reduced memory usage
- **Reliability**: Improved connection handling and retry logic
- **User Experience**: Better error messages and setup wizard

### 🐛 Bug Fixes
- Fixed sensor precision issues for temperature readings
- Resolved config flow timeout with slow networks
- Corrected entity state updates after HA restart

## 📦 Installation

### Via HACS (Recommended)
1. Update in HACS → Integrations → VMC Helty Flow
2. Restart Home Assistant
3. Enjoy the new features!

### Manual Installation
1. Download `vmc_helty_flow.zip` from release assets
2. Extract to `custom_components/`
3. Restart Home Assistant

## ⚡ Breaking Changes
None in this release - fully backward compatible!

## 🔧 Technical Details
- **Home Assistant**: 2024.1.0+ required
- **Python**: 3.11+ required
- **New Dependencies**: None
- **Configuration**: No changes needed

## 📊 Full Changelog
See [CHANGELOG.md](CHANGELOG.md) for complete details.

## 🐛 Known Issues
- None currently reported

## 👥 Contributors
Special thanks to community contributors:
- @contributor1 - Feature suggestion and testing
- @contributor2 - Bug report and validation

---

**Need Help?**
- 📖 [Documentation](README.md)
- 🐛 [Report Issues](https://github.com/dpezzoli/ha_vmc_helty_flow/issues)
- 💬 [Community Discussion](https://community.home-assistant.io/)
```

## 🧪 Testing Standards

### Pre-Release Testing
1. **Unit Tests**: All tests must pass with >95% coverage
2. **Integration Tests**: Test with real VMC devices if possible
3. **HACS Testing**: Verify installation via HACS custom repository
4. **HA Versions**: Test with current and beta HA versions
5. **Python Versions**: Test with supported Python versions

### Test Environments
- **Development**: Latest HA development version
- **Stable**: Current HA stable release
- **Previous**: Previous HA stable release (when possible)

### Device Testing
- Test with multiple VMC models when available
- Verify network discovery across different network configurations
- Test error conditions and recovery scenarios

## 🔐 Security Release Process

### Security Patches
1. **Private Development**: Fix developed privately
2. **Limited Testing**: Security team testing only
3. **Coordinated Release**: Release coordinated with HA security team
4. **Public Disclosure**: Security advisory published after fix release

### Security Release Naming
- Format: `v1.1.2-security`
- Immediate patch release
- Security advisory published separately

## 📈 Release Metrics

### Success Criteria
- [ ] All CI/CD checks pass
- [ ] No critical bugs reported within 48 hours
- [ ] HACS installation success rate >95%
- [ ] Positive community feedback
- [ ] No security vulnerabilities introduced

### Monitoring
- **Downloads**: Track HACS installation numbers
- **Issues**: Monitor GitHub issues and resolution time
- **Feedback**: Community forum and Discord feedback
- **Performance**: Integration performance metrics

## 🔄 Release Automation

### GitHub Actions
- **CI/CD**: Automated testing on every commit
- **Release Preparation**: Automated version bumping and changelog generation
- **Quality Checks**: Code quality, type checking, and linting
- **HACS Validation**: Automated HACS compatibility testing

### Manual Steps
- Final testing and validation
- Release notes creation
- Community announcement
- Documentation updates

---

This release process ensures high-quality, reliable releases that provide value to the Home Assistant community while maintaining backward compatibility and security standards.
