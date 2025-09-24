# VMC Helty Flow Control Card# VMC Helty Flow Control Card

Advanced Lovelace card for VMC Helty Flow Plus/Elite ventilation systems in Home Assistant with **device selection**, **custom sensor support**, and **room volume configuration**.


## 🚀 **Key Features**##


### 🎯 **Device Selection**

- **Multiple VMC Support**: Choose specific VMC device from available entities

- **Auto-Discovery**: Automatically finds VMC Helty Flow devices in your system

- **Device Status**: Real-time connection status and availability monitoring



### 🌡️ **Custom Sensor Selection** ### 🌡️ **Custom Sensor Selection**

- **Temperature Override**: Use any temperature sensor instead of VMC internal sensor

- **Humidity Override**: Use any humidity sensor instead of VMC internal sensor

- **Smart Calculations**: Advanced sensors use your selected sensors for accurate results

- **Source Indicators**: Clear display of which sensors are being used



### 📏 **Room Volume Configuration**### � **Room Volume Configuration**

- **Accurate Air Exchange**: Calculate precise air exchange times based on actual room size

- **Volume Calculator**: Built-in calculator for room dimensions (L×W×H)

- **Efficiency Analysis**: Determine if ventilation is adequate for your space

- **Custom Units**: Support for different room sizes (1-10,000 m³)

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

## 📋 Features Overview

### 🎛️ **Complete Control Panel**
- **Visual fan speed controls** (0-4 speeds) with percentage display
- **Real-time status display** with animated fan icon
- **Connection status indicator** with WiFi icon
- **Special modes**: Night Mode, Boost, Free Cooling with visual feedback

### 📊 **Environmental Monitoring**
- **Flexible Sensor Sources**: VMC internal OR custom external sensors
- **Temperature monitoring** with configurable source (VMC/Custom)
- **Humidity monitoring** with configurable source (VMC/Custom)
- **CO₂ levels** (Elite models) with air quality alerts
- **VOC measurements** (Elite models) with trend indicators
- **Source indicators** showing which sensors are active

### 🧮 **Advanced Calculations**
- **Dew Point Calculation** using selected temperature/humidity sensors
- **Comfort Index** with excellent/good/fair/poor ratings
- **Air Exchange Time** calculated with actual room volume
- **Ventilation Efficiency** analysis based on room size and airflow
- **Real-time Updates** as conditions change

### 📱 **Responsive Design**
- **Mobile-optimized** touch-friendly controls (44px minimum)
- **Tablet adaptation** with 2-column grid layout
- **Desktop layout** with full feature visibility
- **Dark/Light theme** automatic support
- **High contrast** and reduced motion support

### 🔧 **Visual Configuration**
- **Device Selection Dropdown** - Choose from available VMC entities
- **Sensor Selection Dropdowns** - Pick custom temperature/humidity sensors
- **Room Volume Input** - Set actual room volume or use calculator
- **Feature Toggles** - Show/hide sensors and advanced features
- **Real-time Validation** - Immediate feedback on configuration

## 🛠️ Installation

### Method 1: Manual Installation

1. **Download the files**:
   ```bash
   mkdir -p /config/www/vmc-helty-card
   # Copy vmc-helty-card.js and vmc-helty-card-editor.js
   ```

2. **Add to Lovelace resources**:
   ```yaml
   resources:
     - url: /local/vmc-helty-card/vmc-helty-card.js
       type: module
   ```

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
   - Choose custom sensors (optional)
   - Set room volume or use calculator
   - Toggle display options

### Advanced YAML Configuration

```yaml
type: custom:vmc-helty-card
# Required
entity: fan.vmc_helty_flow_kitchen  # Select your specific VMC device

# Optional - Custom Sensors
temperature_entity: sensor.kitchen_temperature    # Use custom temp sensor
humidity_entity: sensor.kitchen_humidity         # Use custom humidity sensor

# Optional - Room Configuration
room_volume: 45.5  # Room volume in m³ for accurate calculations

# Optional - Display Settings
name: "Kitchen VMC"
show_temperature: true
show_humidity: true
show_co2: true
show_voc: false
show_advanced: true

# Optional - Advanced Features
enable_comfort_calculations: true  # Use selected sensors for comfort
enable_air_exchange: true         # Calculate air exchange with room volume

# Optional - Theme
theme: default
layout: auto
```

### Configuration Examples

#### Example 1: Kitchen VMC with Room Sensors
```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_flow_kitchen
name: "Kitchen Ventilation"
temperature_entity: sensor.kitchen_temperature_accurate
humidity_entity: sensor.kitchen_humidity_accurate
room_volume: 32.4  # 4.5m × 3.6m × 2.0m
show_advanced: true
enable_comfort_calculations: true
enable_air_exchange: true
```

#### Example 2: Living Room VMC with Large Space
```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_flow_living_room
name: "Living Room VMC"
room_volume: 89.6  # 8m × 5.6m × 2.0m
show_co2: true
show_voc: true
show_advanced: true
enable_air_exchange: true
```

#### Example 3: Bathroom VMC - Minimal Setup
```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_flow_bathroom
name: "Bathroom Fan"
room_volume: 15.75  # 2.5m × 3.5m × 1.8m
show_co2: false
show_voc: false
show_advanced: false
```

## 🎯 Configuration Options

### Device Selection
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `entity` | string | **Required** | VMC fan entity ID to control |
| `name` | string | `"VMC Helty Flow"` | Display name for the card |

### Sensor Configuration
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `temperature_entity` | string | `""` | Custom temperature sensor entity |
| `humidity_entity` | string | `""` | Custom humidity sensor entity |

### Room Configuration
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `room_volume` | number | `60` | Room volume in cubic meters (m³) |

### Display Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_temperature` | boolean | `true` | Show temperature sensor |
| `show_humidity` | boolean | `true` | Show humidity sensor |
| `show_co2` | boolean | `true` | Show CO₂ sensor |
| `show_voc` | boolean | `false` | Show VOC sensor |
| `show_advanced` | boolean | `true` | Show calculated sensors |

### Advanced Features
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_comfort_calculations` | boolean | `true` | Calculate comfort using selected sensors |
| `enable_air_exchange` | boolean | `true` | Calculate air exchange with room volume |

## 🔧 Room Volume Calculation

### Manual Input
Set the `room_volume` parameter directly in m³:
```yaml
room_volume: 45.5  # 45.5 cubic meters
```

### Using Built-in Calculator
In the visual editor:
1. **Enter dimensions**: Length × Width × Height (in meters)
2. **Click Calculate**: Automatically sets room volume
3. **Fine-tune**: Adjust the calculated value if needed

### Standard Room Volumes
- **Small bathroom**: 10-20 m³
- **Bedroom**: 30-50 m³
- **Kitchen**: 25-45 m³
- **Living room**: 60-120 m³
- **Open plan**: 100-300 m³

## 🌡️ Custom Sensor Selection

### Why Use Custom Sensors?

1. **More Accurate Readings**: External room sensors vs. VMC internal sensors
2. **Better Placement**: Sensors positioned in optimal room locations
3. **Higher Quality**: Premium sensors with better accuracy
4. **Specific Zones**: Match sensors to the actual ventilated area

### Sensor Selection Process

1. **Temperature Sensors**: Any `sensor.*` entity with temperature device class or `°C` unit
2. **Humidity Sensors**: Any `sensor.*` entity with humidity device class or `%` unit
3. **Auto-Discovery**: Card automatically finds compatible sensors
4. **Real-time Preview**: See current sensor values during selection

### Calculation Impact

When custom sensors are selected:
- **Dew Point**: Calculated using custom temp/humidity
- **Comfort Index**: Uses custom sensors for accuracy
- **Source Display**: Shows "Custom" vs "VMC" sensor source
- **Advanced Sensors**: All calculations use selected sources

## 📊 Advanced Sensor Calculations

### Dew Point Calculation
- **Formula**: Magnus formula using selected temperature/humidity
- **Purpose**: Condensation risk assessment
- **Units**: °C
- **Accuracy**: Depends on sensor quality and placement

### Comfort Index
- **Algorithm**: Temperature + humidity comfort scoring
- **Ranges**:
  - Excellent: 85-100%
  - Good: 70-84%
  - Fair: 55-69%
  - Poor: 0-54%
- **Factors**: Optimal temp 20-24°C, optimal humidity 40-60%

### Air Exchange Time
- **Calculation**: Room volume ÷ Fan airflow × 60 (minutes)
- **Airflow Mapping**:
  - Speed 0: 0 m³/h (Off)
  - Speed 1: 10 m³/h
  - Speed 2: 17 m³/h
  - Speed 3: 26 m³/h
  - Speed 4: 37 m³/h
- **Categories**:
  - Excellent: ≤20 minutes
  - Good: 21-30 minutes
  - Acceptable: 31-60 minutes
  - Poor: >60 minutes

## 🚀 Performance Features

### Optimized Rendering
- **Smart Updates**: Only re-renders when relevant entities change
- **Entity Monitoring**: Tracks only configured VMC and sensor entities
- **Memory Efficient**: Cleanup on disconnect
- **Error Boundaries**: Graceful degradation on failures

### Accessibility Features
- **ARIA Labels**: Complete screen reader support
- **Keyboard Navigation**: Full keyboard control
- **Focus Management**: Proper tab order and focus indicators
- **High Contrast**: Supports high contrast mode
- **Reduced Motion**: Respects motion preferences

## 🐛 Troubleshooting

### Device Not Found
```
Error: Please define a VMC fan entity
```
**Solution**: Select a valid VMC fan entity from the dropdown

### Custom Sensor Issues
```
Warning: Custom sensor unavailable
```
**Solutions**:
1. Check sensor entity exists and is available
2. Verify sensor has correct device class or unit
3. Use the visual editor to re-select sensor

### Volume Calculation Problems
```
Air exchange showing "Poor" category
```
**Solutions**:
1. Verify room volume is accurate for the space
2. Check if VMC airflow matches your model specifications
3. Consider room layout (open doors, connections to other rooms)

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
- **VMC Integration**: [VMC Helty Flow Integration](https://github.com/your-repo/vmc-helty-flow)

---

**VMC Helty Flow Control Card** - Advanced ventilation control with custom sensor support and room-specific calculations! 🌀
