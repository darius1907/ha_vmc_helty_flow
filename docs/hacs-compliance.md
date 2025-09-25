# HACS Integration Guidelines

## VMC Helty Flow - HACS Compliance

This document outlines the HACS compliance status for the VMC Helty Flow integration.

### ✅ HACS Requirements Met

#### 1. Repository Structure
```
custom_components/vmc_helty_flow/
├── __init__.py
├── manifest.json
├── config_flow.py
├── const.py
├── sensor.py
├── fan.py
├── light.py
├── button.py
├── switch.py
└── ... (other required files)
```

#### 2. Required Files
- ✅ `hacs.json` - HACS configuration file
- ✅ `README.md` - Comprehensive documentation
- ✅ `manifest.json` - Home Assistant integration manifest
- ✅ `LICENSE` - MIT License

#### 3. Manifest.json Requirements
Required fields present:
- ✅ `domain`: "vmc_helty_flow"
- ✅ `name`: "VMC Helty Flow"
- ✅ `codeowners`: ["@dpezzoli"]
- ✅ `documentation`: GitHub repository URL
- ✅ `issue_tracker`: GitHub issues URL
- ✅ `version`: "1.0.0"

#### 4. HACS.json Configuration
- ✅ Display name: "VMC Helty Flow"
- ✅ Minimum HACS version: 1.6.0
- ✅ Minimum Home Assistant version: 2024.1.0
- ✅ IoT class: Local Polling
- ✅ Domains: vmc_helty_flow

### 📋 HACS Installation

#### For End Users
1. **Add Custom Repository** (until included in default HACS store):
   - Go to HACS → Integrations
   - Click "..." → "Custom repositories"
   - Add repository URL: `https://github.com/darius1907/ha_vmc_helty_flow`
   - Category: Integration
   - Click "Add"

2. **Install Integration**:
   - Find "VMC Helty Flow" in HACS integrations
   - Click "Download"
   - Restart Home Assistant

3. **Add Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "VMC Helty Flow"
   - Follow configuration wizard

#### My Home Assistant Quick Add
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dpezzoli&repository=ha_vmc_helty_flow&category=integration)

### 🚀 Future HACS Default Store Inclusion

To be included in the default HACS store, this integration will need:

1. **Home Assistant Brands Entry**
   - Submit to [home-assistant/brands](https://github.com/home-assistant/brands)
   - Provide integration icons and metadata

2. **Community Validation**
   - Active usage and positive feedback
   - Community testing and validation
   - Issue resolution and maintenance

3. **Quality Standards**
   - Code review and compliance
   - Test coverage and CI/CD
   - Documentation completeness

### 📊 Release Strategy

#### GitHub Releases
- Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
- Tag releases for HACS version management
- Include release notes and changelog

#### Version Management
- `manifest.json` version follows releases
- HACS automatically detects new releases
- Users get update notifications

### 🔧 Development Guidelines

#### Local Development
1. Clone repository
2. Link to Home Assistant `custom_components/`
3. Restart HA for changes
4. Test thoroughly before release

#### HACS Testing
1. Test installation via HACS custom repository
2. Verify all files are correctly installed
3. Test upgrade scenarios
4. Validate configuration flows

### 📝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Ensure HACS compliance

This integration is ready for HACS distribution and follows all required guidelines for quality and user experience.
