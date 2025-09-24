# VMC Helty Control Card

Advanced Lovelace card for controlling VMC Helty Flow Plus/Elite ventilation systems in Home Assistant.

## Features

### 🎛️ **Complete Control Panel**
- **Visual fan speed controls** with intuitive button interface (0-4 speeds)
- **Real-time status display** with animated fan icon
- **Connection status indicator** with WiFi icon
- **One-click special modes** (Night Mode, Boost, Free Cooling)

### 📊 **Environmental Monitoring** 
- **Temperature sensors** (Internal/External) with color-coded status
- **Humidity monitoring** with optimal range indicators  
- **CO₂ levels** (Elite models only) with air quality alerts
- **VOC measurements** (Elite models only) with trend indicators
- **Advanced sensors** (Dew Point, Comfort Index) when enabled

### 📱 **Responsive Design**
- **Mobile-optimized** layout with touch-friendly controls
- **Tablet adaptation** with 2-column grid layout
- **Desktop layout** with full feature visibility
- **Dark/Light theme** support following HA theme

### 🔧 **Easy Configuration**
- **Visual configuration editor** in Lovelace UI
- **Auto-discovery** of VMC entities
- **Flexible display options** to show/hide features
- **Multiple themes** (Default, Compact, Minimal)

## Installation

### Method 1: Manual Installation

1. **Download the files**:
   ```bash
   mkdir -p /config/www/vmc-helty-card
   # Copy vmc-helty-card.js and vmc-helty-card-editor.js to the directory
   ```

2. **Add to Lovelace resources**:
   ```yaml
   # In Lovelace configuration
   resources:
     - url: /local/vmc-helty-card/vmc-helty-card.js
       type: module
   ```

3. **Add the card** to your dashboard:
   ```yaml
   type: custom:vmc-helty-card
   entity: fan.vmc_helty  # Your VMC fan entity
   name: "Living Room VMC"
   ```

### Method 2: HACS Installation (Recommended)

*Coming soon - will be available through HACS custom repository*

## Configuration

### Basic Configuration

```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_living_room
name: "Living Room VMC"
```

### Full Configuration

```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_living_room
name: "Living Room VMC"
show_temperature: true
show_humidity: true
show_co2: true          # Elite models only
show_voc: true          # Elite models only  
show_lights: true
show_advanced: false
theme: default
volume_m3: 150          # Room volume for calculations
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `entity` | string | **Required** | Main VMC fan entity ID |
| `name` | string | `VMC Helty` | Display name for the card |
| `show_temperature` | boolean | `true` | Show temperature sensors |
| `show_humidity` | boolean | `true` | Show humidity sensor |
| `show_co2` | boolean | `true` | Show CO₂ sensor (Elite only) |
| `show_voc` | boolean | `true` | Show VOC sensor (Elite only) |
| `show_lights` | boolean | `false` | Show light controls |
| `show_advanced` | boolean | `false` | Show advanced sensors |
| `theme` | string | `default` | Card theme (`default`, `compact`, `minimal`) |
| `volume_m3` | number | - | Room volume for air exchange calculations |

## Entity Mapping

The card automatically discovers related entities based on your fan entity:

| Sensor | Entity Pattern | Description |
|--------|----------------|-------------|
| **Fan Control** | `fan.{device}_*` | Main ventilation control |
| **Temperature** | `sensor.{device}_temperature_*` | Internal/External temperature |
| **Humidity** | `sensor.{device}_humidity` | Relative humidity |
| **CO₂** | `sensor.{device}_co2` | Carbon dioxide (Elite only) |
| **VOC** | `sensor.{device}_voc` | Volatile organic compounds |
| **Modes** | `switch.{device}_*_mode` | Special operation modes |
| **Lights** | `light.{device}_lights*` | VMC LED controls |

## Supported Models

### ✅ **VMC Helty Flow Plus**
- Basic speed control (0-4)
- Temperature monitoring (Internal/External)
- Humidity monitoring
- Special modes (Night, Boost, Free Cooling)
- LED panel control

### ✅ **VMC Helty Flow Elite** 
- All Flow Plus features
- **CO₂ monitoring** (400-5000 ppm)
- **VOC monitoring** (0-500 IAQ)
- **Advanced air quality automation**
- **Enhanced analytics**

## Visual Indicators

### Speed Control
- **Speed 0 (OFF)**: Gray background, static fan icon
- **Speed 1 (Min)**: Blue background, slow rotation
- **Speed 2 (Low)**: Green background, medium rotation  
- **Speed 3 (Med)**: Orange background, fast rotation
- **Speed 4 (Max)**: Red background, very fast rotation

### Sensor Status Colors
- **🟢 Green**: Optimal values (good air quality, comfortable temperature)
- **🟡 Yellow**: Moderate/attention values (watch levels)
- **🟠 Orange**: Poor values (action recommended)
- **🔴 Red**: Critical values (immediate attention needed)

### Connection Status
- **🟢 WiFi Icon**: Connected and responsive
- **🔴 WiFi-Off Icon**: Disconnected or unavailable

## Troubleshooting

### Common Issues

**❌ "Entity not found" error**
- Verify your VMC integration is properly configured
- Check that the fan entity exists in Developer Tools → States
- Ensure entity ID matches exactly (case-sensitive)

**❌ Sensors not showing**
- Elite-only sensors (CO₂/VOC) won't show on Plus models
- Check sensor entity names match the expected pattern
- Verify sensors are not disabled in the entity registry

**❌ Card not loading**
- Confirm the resource is properly added to Lovelace
- Check browser console for JavaScript errors
- Clear browser cache and refresh

**❌ Controls not working**  
- Verify fan entity supports `fan.set_percentage` service
- Check Home Assistant logs for service call errors
- Ensure user has appropriate permissions

### Debug Mode

Add this to your configuration for detailed logging:
```yaml
logger:
  default: warning
  logs:
    custom_components.vmc_helty_flow: debug
```

## Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/darius1907/vmc-helty-card
cd vmc-helty-card

# Development server
npm install
npm run dev

# Build for production  
npm run build
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Changelog

### v1.0.0 (2025-09-24)
- ✨ Initial release
- 🎛️ Complete fan speed control
- 📊 Environmental sensor monitoring
- 📱 Responsive design
- 🎨 Multiple themes
- ⚙️ Visual configuration editor

## Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/darius1907/vmc-helty-card/issues)
- **Community Forum**: [Home Assistant Community](https://community.home-assistant.io/)
- **Documentation**: [Full integration guide](https://github.com/darius1907/vmc-helty-flow)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the Home Assistant community**