
# VMC Helty Flow Control Card

Advanced Lovelace card for VMC Helty Flow Plus/Elite ventilation systems in Home Assistant.


## Card Structure

- **VMC Helty Flow Control Card**: Card for device commands only (fan speed, special modes, lights, timer). No sensor display or configuration.

**Device selection** is available in the card.


## 🚀 **Key Features**##



### 🎯 **Device Selection**
- **Multiple VMC Support**: Choose specific VMC device from available entities
- **Auto-Discovery**: Automatically finds VMC Helty Flow devices in your system
- **Device Status**: Real-time connection status and availability monitoring


### 🌀 **VMC Helty Flow Control Card**
- **Fan speed controls** (0-4 speeds)
- **Special modes**: Night Mode, Boost, Free Cooling
- **Panel LED and sensors toggles**
- **Light and timer controls** (if supported)
- **No sensor display/configuration**

## ✅ Home Assistant Guidelines Compliance

This card is **100% compliant** with Home Assistant development guidelines:

- ✅ **LitElement Architecture** - Built with LitElement for maximum compatibility
- ✅ **Mobile-First Design** - Responsive layout optimized for all devices
- ✅ **HA Theme Integration** - Uses only Home Assistant CSS variables
- ✅ **Complete Accessibility** - Full ARIA support and keyboard navigation
- ✅ **Material Design Icons** - MDI icons through ha-icon components
- ✅ **CSP Compliance** - No inline styles or scripts
- ✅ **Performance Optimized** - Efficient rendering and updates
- ✅ **Error Handling** - Robust error boundaries and user feedback



### 📋 Features Overview
- Fan speed and mode controls
- Device toggles (LED, sensors)
- Light/timer controls

### 📱 **Responsive Design**

- **Mobile-optimized** touch-friendly controls (44px minimum)
- **Tablet adaptation** with 2-column grid layout
- **Desktop layout** with full feature visibility
- **Dark/Light theme** automatic support
- **High contrast** and reduced motion support



### 🔧 **Visual Configuration**
- **Device Selection Dropdown**

## 🛠️ Installation


### Method 1: Manual Installation
1. **Download the files**:
  ```bash
  mkdir -p /config/www/vmc-helty-card
  # Copy vmc-helty-card.js, vmc-helty-card-editor.js, vmc-helty-advanced-sensors-card.js, vmc-helty-advanced-sensors-card-editor.js
  ```
2. **Add to Lovelace resources**:
  ```yaml
  resources:
    - url: /local/vmc-helty-card/vmc-helty-card.js
      type: module
    - url: /local/vmc-helty-card/vmc-helty-card-editor.js
      type: module
    - url: /local/vmc-helty-card/vmc-helty-advanced-sensors-card.js
      type: module
  ```

**Note**: Translation files are loaded automatically and should NOT be added to resources.

3. **Add the card** using the visual editor or YAML

### Method 2: HACS (Recommended)
```bash
# Add custom repository in HACS
# Repository: https://github.com/your-repo/vmc-helty-card
# Category: Lovelace
```

## ⚙️ Configuration


### Basic Configuration (Visual Editor)
1. **Click "Add Card"** in Lovelace edit mode
2. **Search for "VMC Helty"** and select the card
3. **Configure using the visual editor**:
  - Select your VMC device from dropdown


temperature_entity: sensor.kitchen_temperature_accurate
enable_comfort_calculations: true
enable_air_exchange: true
enable_air_exchange: true

### Advanced YAML Configuration
```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_flow_kitchen
name: "Kitchen VMC"
# Only device commands, no sensor config
```


### Configuration Example
```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_flow_kitchen
name: "Kitchen Ventilation"
```

## 🎯 Configuration Options



### Device Selection
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `entity` | string | **Required** | VMC fan entity ID to control |
| `name` | string | `"VMC Helty Flow"` | Display name for the card |





## � Troubleshooting


### Device Not Found

```text
Error: Please define a VMC fan entity
```

**Solution**: Select a valid VMC fan entity from the dropdown


### Performance Issues
- **Large installations**: Limit entities monitored
- **Slow updates**: Check Home Assistant performance
- **Memory usage**: Restart Home Assistant if needed

## 📝 Migration from Previous Versions

### Automatic Compatibility

- **Config preserved**: All previous configurations work unchanged
- **New defaults**: New features enabled by default
- **Gradual adoption**: Add new features when convenient

### Recommended Upgrades

1. **Add custom sensors** for more accurate readings
2. **Set room volume** for proper air exchange calculations
3. **Review display options** to show relevant sensors
4. **Enable advanced features** for detailed analysis

### Breaking Changes

- **None**: Full backward compatibility maintained

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for:

- Code style requirements
- Testing procedures
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [Full Documentation](README.md)
- **Quick Start**: [Quick Start Guide](QUICK-START.md)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [Community Forum](https://community.home-assistant.io/)
- **VMC Integration**: [VMC Helty Flow Integration](https://github.com/darius1907/ha_vmc_helty_flow)

---

**VMC Helty Flow Control Card** - Advanced ventilation control with custom sensor support and room-specific calculations! 🌀
