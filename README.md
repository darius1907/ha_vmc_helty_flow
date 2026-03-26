# 🌬️ VMC Helty Flow - Home Assistant Integration

[![hacs][hacsbadge]][hacs]
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

Complete integration for Helty Flow Mechanical Ventilation (VMC) systems with Home Assistant.

> **🇮🇹 Versione Italiana**: [README_IT.md](README_IT.md)

## 🚀 Quick Installation

### Via HACS (Recommended)

1. **Install the Integration**:
   - Open HACS in Home Assistant
   - Go to **Integrations**
   - Click the **Explore & Download Repositories** button in the bottom right
   - Search for "**VMC Helty Flow**"
   - Click "**Download**"
   - Restart Home Assistant

   > **Note**: If you can't find the integration in the search, it may take a few hours after publication. Alternatively, you can add it as a custom repository using the badge below:

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=darius1907&repository=ha_vmc_helty_flow&category=integration)

2. **Configure the Integration**:
   - Go to **Settings** → **Devices & Services**
   - Click "**Add Integration**"
   - Search for "**VMC Helty Flow**"
   - Follow the guided configuration procedure

### Manual Installation

1. Copy the `custom_components/vmc_helty_flow` folder into your `custom_components/` directory
2. Restart Home Assistant
3. Add the integration from the interface

## ✨ Main Features

### 🔍 **Advanced Device Discovery**

- **Incremental Scanning**: Find and configure devices one at a time with full user control
- **Smart Validation**: Automatic verification of subnet format, ports, and timeouts
- **Error Management**: Informative messages and error recovery capabilities

### 🎛️ **Complete VMC Control**

- **Fan Control**: Variable speed and operating modes
- **Environmental Monitoring**: Indoor/outdoor temperature, humidity, CO2, VOC
- **Filter Management**: Usage hours monitoring and filter reset
- **Lighting**: Integrated light control with timer
- **Network Configuration**: WiFi management and network parameters

## 🏠 Available Entities

### 🌪️ **Ventilation Control**

- **Fan**: Fan speed control and operating modes
- **Mode Switch**: Operating modes (hyperventilation, night, free_cooling)
- **Sensors Switch**: Enable/disable environmental sensors

### 📊 **Environmental Sensors**

- **Indoor/Outdoor Temperature**: Real-time temperature monitoring
- **Humidity**: Environmental humidity levels
- **CO2**: Carbon dioxide concentration (ppm)
- **VOC**: Volatile organic compounds
- **Air Quality**: Overall environmental quality indicators

### 🔧 **System Management**

- **Filter Hours**: Filter operating hours
- **Reset Filter Button**: Filter counter reset
- **Last Response**: Last communication timestamp
- **Panel LED Switch**: Front panel LED control

### 💡 **Lighting**

- **Light**: Integrated light control
- **Light Timer**: Automatic light shutdown timer

### 🌐 **Network Configuration**

- **IP Address**: Device IP address
- **Subnet Mask/Gateway**: Network parameters
- **SSID/Password**: WiFi configuration
- **Network Settings**: Complete network parameter management

### 📈 **Advanced Sensors**

- **Dew Point**: Dew point calculation for condensation prevention
- **Comfort Index**: Comfort index based on temperature and humidity
- **Dew Point Delta**: Difference between outdoor temperature and dew point
- **Air Exchange Time**: Air exchange time based on fan speed
- **Daily Air Changes**: Number of daily air changes

## 🎨 **Custom Dashboard**

### 📱 **VMC Helty Control Card**

Custom Lovelace card for complete VMC system control:

- **🎛️ Fan Control**: Intuitive interface with speed buttons (0-4)
- **📊 Environmental Monitor**: Sensor visualization with color indicators
- **🔄 Real-time Updates**: Real-time fan and sensor status
- **📱 Responsive Design**: Optimized for mobile, tablet, and desktop
- **🎨 Multiple Themes**: Default, Compact, Minimal
- **⚙️ Visual Configuration**: Integrated graphical editor in Lovelace

#### Card Installation

```bash
# Copy card files to www/
/config/www/vmc-helty-card/
├── vmc-helty-card.js              # Main card
└── vmc-helty-card-editor.js       # Configuration editor
```

Add to Lovelace resources:

```yaml
resources:
  - url: /local/vmc-helty-card/vmc-helty-card.js
    type: module
  - url: /local/vmc-helty-card/vmc-helty-card-editor.js
    type: module
```

**Note**: Translation files are loaded automatically and should NOT be added to resources.

Card configuration:

```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty
name: "VMC Living Room"
show_temperature: true
show_humidity: true
show_co2: true
show_voc: true
```

## 🚀 Guided Configuration

### 📡 **Incremental Scanning**

1. **Start Configuration**
   - Open Home Assistant → Settings → Devices & Services
   - Click "Add Integration" → Search for "VMC Helty Flow"

2. **Scan Configuration**
   - **Subnet**: Enter the network to scan (e.g., `192.168.1.0/24`)
   - **Port**: VMC device TCP port (default: `5001`)
   - **Timeout**: Connection timeout in seconds (1-60)
   - **Mode**: Select "Incremental scan"

3. **Incremental Process**
   - The scan starts and automatically stops at each device found
   - For each discovered VMC device, you can choose:
     - **➕ Add and continue**: Adds the device and continues scanning
     - **⏭️ Skip and continue**: Ignores this device and continues
     - **✅ Add and finish**: Adds the device and terminates
     - **🛑 Stop scan**: Stops everything without adding

4. **Immediate Feedback**
   - Real-time display of found devices
   - Detailed information (name, IP, model) for each device
   - Progressive counter and scan position indicator

### 🔧 **Validations and Security**

- **Subnet Format**: Automatic CIDR format validation
- **IP Limit**: Maximum 254 addresses per scan (for performance)
- **Port Check**: Port range validation (1-65535)
- **Smart Timeout**: Balance between speed and reliability
- **Duplicate Management**: Automatic duplicate configuration prevention

## 📋 **Configuration Examples**

### Basic Configuration

```text
Subnet: 192.168.1.0/24
Port: 5001
Timeout: 10 seconds
```

### Custom Network Configuration

```text
Subnet: 10.0.0.0/24
Port: 8080
Timeout: 5 seconds
Mode: Full scan
```

### Extended Network Configuration

```text
Subnet: 192.168.0.0/23
Port: 5001
Timeout: 15 seconds
```

## 🔄 **Automations and Integrations**

All entities are fully integrated with Home Assistant:

### Air Quality Automation

```yaml
automation:
  - alias: "VMC Boost on High CO2"
    trigger:
      platform: numeric_state
      entity_id: sensor.vmc_helty_living_room_co2
      above: 800
    action:
      service: fan.set_percentage
      target:
        entity_id: fan.vmc_helty_living_room
      data:
        percentage: 80
```

### Custom Dashboard

```yaml
cards:
  - type: entities
    title: "Living Room VMC Control"
    entities:
      - fan.vmc_helty_living_room
      - sensor.vmc_helty_living_room_indoor_temperature
      - sensor.vmc_helty_living_room_co2
      - switch.vmc_helty_living_room_mode
      - light.vmc_helty_living_room_light
```

## 🛠️ **Troubleshooting**

### Common Issues

**Devices not found?**

- Verify that VMC devices are powered on and connected to the network
- Check that the subnet is correct
- Try increasing the connection timeout
- Verify that port 5001 is not blocked by firewall

**Slow scanning?**

- Reduce the subnet (e.g., from /23 to /24)
- Decrease timeout for fast networks
- Use incremental mode for granular control

**Connection errors?**

- Verify the VMC device network configuration
- Check that Home Assistant can reach the specified subnet
- Try restarting the VMC device

### Logging and Debug

To enable detailed logging, add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.vmc_helty_flow: debug
```

## 🔮 **Future Developments**

We have an active development roadmap with exciting features planned!

### 📋 Development Resources

- **[Project Roadmap](PROJECT_ROADMAP.md)** - Detailed development plan with milestones, tasks, and progress tracking
- **[Improvement Plan](IMPROVEMENT_PLAN.md)** - Complete analysis and proposed improvements for upcoming versions
- **[Blueprint Guide](blueprints/BLUEPRINT_GUIDE.md)** - Comprehensive automation blueprint documentation

### 🎯 Upcoming Features (v1.2.0+)

**High Priority**:
- 🔔 **Notification System**: Complete alerting for critical events (filter, air quality, offline)
- 📘 **6 New Automation Blueprints**: Air quality adaptive, humidity control, filter reminders, and more
- 📊 **Statistical Sensors**: Filter life percentage, energy estimates, running time tracking
- 📦 **Ready-to-Use Dashboard Package**: Complete importable package with helpers, automations, and views

**Medium Priority** (v1.3.0):
- ⭐ **Quality Scale Gold**: Upgrade from Silver to Gold certification
- ⚡ **Energy Dashboard Integration**: Track VMC power consumption in Home Assistant Energy
- 🎭 **Predefined Scenes**: Night mode, boost, energy saving scenarios

**Community Requests**:
- 🤖 Machine Learning air quality predictions
- 🗣️ Voice assistant advanced integrations
- 📱 Mobile companion app
- 🌐 Multi-zone VMC coordination

See the [full roadmap](PROJECT_ROADMAP.md) for detailed timeline and task breakdown.

## 📞 **Support**

For issues, feature requests, or contributions:

- 🐛 [Open an issue](https://github.com/darius1907/ha_vmc_helty_flow/issues) on GitHub
- 💬 Join the [community discussion](https://community.home-assistant.io/)

### How to Contribute

We welcome contributions! See our [Contributing Guidelines](CONTRIBUTING.md) and [Project Roadmap](PROJECT_ROADMAP.md) for current priorities.

1. 🍴 Fork the repository
2. 🌱 Create a branch for the feature
3. ✅ Add tests for changes (coverage >95%)
4. 📝 Update documentation
5. 🎯 Check [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) for priority tasks
5. 🔄 Submit a pull request

---

## 📊 **Project Status**

![GitHub release (latest by date)][releases-shield]
![GitHub Release Date][release-date-shield]
![GitHub commits since latest release][commits-since-shield]
![GitHub last commit][last-commit-shield]

**Version**: 1.1.1
**Compatibility**: Home Assistant 2024.1+
**License**: MIT
**HACS Status**: ✅ Available in the official HACS repository

---

**⭐ If this integration is useful to you, star the repository!**

**☕ Do you like this integration? Buy me a coffee!**

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/darius1907)

Your support helps me maintain and improve this integration!

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license]: https://github.com/darius1907/ha_vmc_helty_flow/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/darius1907/ha_vmc_helty_flow.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40darius1907-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/darius1907/ha_vmc_helty_flow.svg?style=for-the-badge
[releases]: https://github.com/darius1907/ha_vmc_helty_flow/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/darius1907/ha_vmc_helty_flow.svg?style=for-the-badge
[commits]: https://github.com/darius1907/ha_vmc_helty_flow/commits/main
[user_profile]: https://github.com/darius1907
[buymecoffee]: https://www.buymeacoffee.com/darius1907
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[release-date-shield]: https://img.shields.io/github/release-date/darius1907/ha_vmc_helty_flow?style=for-the-badge
[commits-since-shield]: https://img.shields.io/github/commits-since/darius1907/ha_vmc_helty_flow/latest?style=for-the-badge
[last-commit-shield]: https://img.shields.io/github/last-commit/darius1907/ha_vmc_helty_flow?style=for-the-badge
