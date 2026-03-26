# 📘 VMC Helty Flow - Complete Blueprint Guide

## 📑 Index
1. [Available blueprints](#available-blueprints)
2. [How to choose](#how-to-choose-the-right-blueprint)
3. [Installation](#installation)
4. [Configuration](#detailed-configuration)
5. [Practical examples](#practical-examples)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Available blueprints

### 1. 📅 VMC Schedule Plan
**File**: `vmc_schedule_plan.yaml`
**Complexity**: ⭐ Easy
**Required sensors**: None

Manages day/night cycles with configurable fixed speeds.

**Pros**: Simple, reliable, no sensors required
**Cons**: Does not adapt to changing conditions

**Use it when**:
- You are creating your first VMC automation
- Your home usage pattern is regular
- You do not have extra sensors

---

### 2. ⚡ VMC Schedule Boost
**File**: `vmc_schedule_boost.yaml`
**Complexity**: ⭐⭐ Medium
**Required sensors**: `input_boolean` helper

Creates periodic boost cycles with separate configurable durations for day and night.

**Pros**: Better air exchange, energy optimization
**Cons**: Requires helper, slightly more setup

**Use it when**:
- You want automatic periodic boosts
- You prefer pulse-based ventilation
- You want better energy efficiency

**Prerequisite setup**:
```yaml
input_boolean:
  vmc_boost_active:
    name: "VMC Boost Active"
```

---

### 3. 🌬️ VMC Air Quality Adaptive 🆕
**File**: `vmc_air_quality_adaptive.yaml`
**Complexity**: ⭐⭐⭐ Advanced
**Required sensors**: CO2 sensor (VOC optional)

Automatically adjusts speed based on real-time indoor air quality.

**Pros**: Best comfort, smart behavior, efficient
**Cons**: Requires reliable sensors and more setup

**Logic**:
- CO2 < 800 ppm → minimum speed (25%)
- CO2 800-1000 ppm → medium speed (50%)
- CO2 > 1000 ppm → high speed (75%) or Hyperventilation
- High VOC → independent boost

**Use it when**:
- You have CO2/VOC sensors
- Home occupancy is variable
- You want the best air quality automation

**Compatible sensors**:
- `sensor.vmc_helty_co2` (built into VMC)
- External CO2 sensors (Netatmo, ESPHome, etc.)
- `sensor.vmc_helty_voc` (optional)

---

### 4. 💧 VMC Humidity Control 🆕
**File**: `vmc_humidity_control.yaml`
**Complexity**: ⭐⭐ Medium
**Required sensors**: Humidity sensor

Triggers automatic boost when humidity exceeds the configured threshold (shower, kitchen).

**Pros**: Helps prevent mold, fully automatic, customizable
**Cons**: Requires a reliable humidity sensor

**Logic**:
1. Humidity > threshold (for example 70%) → start 100% boost
2. Keep boost for a minimum duration (for example 15 min)
3. If humidity is still high → extend boost
4. Humidity < return threshold (for example 60%) → return to normal speed
5. Optional cooldown before next boost

**Use it when**:
- You have a bathroom with shower use
- You cook often and get moisture peaks
- You want to reduce mold/condensation risk

**Compatible sensors**:
- `sensor.vmc_helty_humidity` (built into VMC)
- Aqara, Xiaomi, ESPHome humidity sensors
- Multi-sensors (temperature + humidity)

---

### 5. 🔔 VMC Filter Reminder 🆕
**File**: `vmc_filter_reminder.yaml`
**Complexity**: ⭐ Easy
**Required sensors**: `sensor.vmc_helty_filter_hours`

Complete notification system for filter maintenance.

**Pros**: You never miss maintenance, multiple channels, useful tracking
**Cons**: None

**Notifications**:
- **90% (~15970h)**: preventive warning
- **95% (~16857h)**: critical warning
- **100% (17744h)**: urgent daily reminder

**Supported channels**:
- ✅ Persistent notification (Home Assistant UI)
- ✅ Mobile app notifications (iOS/Android)
- ✅ Email
- ✅ Telegram (configurable)
- ✅ Action buttons for quick reset

**Use it when**:
- Always (recommended)
- You want predictable maintenance
- You want to extend VMC lifetime

---

## How to choose the right blueprint

### 🎯 Decision tree

```
Do you have CO2/VOC sensors?
├─ YES → Use "Air Quality Adaptive" (best comfort)
│   └─ + "Humidity Control" for bathroom/kitchen
│   └─ + "Filter Reminder" for maintenance
│
└─ NO → Do you have a humidity sensor in bathroom?
    ├─ YES → Use "Schedule Plan" as baseline
    │   └─ + "Humidity Control" for shower boost
    │   └─ + "Filter Reminder"
    │
    └─ NO → Use "Schedule Plan" or "Schedule Boost"
        └─ + "Filter Reminder" (always)
```

### 💡 Recommended combinations

#### Minimum setup (no extra sensors)
```
✅ VMC Schedule Plan
✅ VMC Filter Reminder
```
**Result**: day/night automation + filter alerts

#### Bathroom/Kitchen setup
```
✅ VMC Schedule Plan
✅ VMC Humidity Control (bathroom)
✅ VMC Filter Reminder
```
**Result**: baseline schedule + automatic shower boost

#### Full setup (with sensors)
```
✅ VMC Air Quality Adaptive
✅ VMC Humidity Control
✅ VMC Filter Reminder
```
**Result**: maximum intelligence + best comfort

#### Energy-saving setup
```
✅ VMC Schedule Boost (periodic cycles)
✅ VMC Filter Reminder
```
**Result**: pulse ventilation + maintenance alerts

---

## Installation

### Method 1: Automatic import (recommended) ✨

1. Click the "Import Blueprint" badge in documentation
2. Home Assistant opens the import page automatically
3. Click **Preview Blueprint**
4. Click **Import Blueprint**
5. ✅ Done

### Method 2: Import by URL

1. Go to **Settings → Automations & Scenes**
2. Open the **Blueprints** tab
3. Click **Import Blueprint** (bottom-right)
4. Paste URL:
   ```
   https://raw.githubusercontent.com/darius1907/ha_vmc_helty_flow/main/blueprints/automation/vmc_schedule_plan/[file_name].yaml
   ```
5. Click **Preview Blueprint**
6. Click **Import Blueprint**

**Available URLs**:
- Schedule Plan: `...vmc_schedule_plan.yaml`
- Schedule Boost: `...vmc_schedule_boost.yaml`
- Air Quality: `...vmc_air_quality_adaptive.yaml`
- Humidity: `...vmc_humidity_control.yaml`
- Filter Reminder: `...vmc_filter_reminder.yaml`

### Method 3: Manual file copy (advanced)

1. Connect with SSH or File Editor
2. Copy blueprint file to:
   ```
   /config/blueprints/automation/vmc_schedule_plan/[file_name].yaml
   ```
3. Go to **Developer Tools → YAML → Check Configuration**
4. Restart Home Assistant

---

## Detailed configuration

### 1) Create an automation from blueprint

1. Open **Settings → Automations & Scenes**
2. Open **Automations** tab
3. Click **+ Create Automation**
4. Select **Start with a blueprint**
5. Choose the VMC blueprint
6. Fill required fields
7. Configure optional fields
8. Click **Save**
9. Use a clear name (for example: `VMC - Shower Auto Boost`)

### 2) Common fields

#### VMC entity ⚠️ Required
- **Type**: entity selector (domain `fan`)
- **Example**: `fan.vmc_helty_living_room`

#### Notification service (optional)
- **Type**: service selector
- **Example**: `notify.mobile_app_your_phone`

### 3) Test checklist after setup

- Trigger condition manually (high humidity/high CO2)
- Confirm fan speed changes as expected
- Confirm restore condition works correctly
- Confirm notifications are delivered
- Validate no log errors in Home Assistant

---

## Practical examples

### Example A - Simple daily schedule
- **Blueprint**: `VMC Schedule Plan`
- **Day speed**: 50%
- **Night speed**: 25%
- **Day start**: 07:00
- **Night start**: 23:00

### Example B - Shower boost
- **Blueprint**: `VMC Humidity Control`
- **High threshold**: 70%
- **Return threshold**: 60%
- **Minimum boost**: 15 minutes
- **Cooldown**: 20 minutes

### Example C - Air quality adaptive
- **Blueprint**: `VMC Air Quality Adaptive`
- **CO2 low/medium/high**: 800 / 1000 ppm
- **VOC boost**: enabled
- **Anti-oscillation delay**: enabled

---

## Troubleshooting

### Blueprint does not appear in Home Assistant
- Verify file is in `/config/blueprints/automation/vmc_schedule_plan/`
- Check YAML syntax in **Developer Tools → YAML**
- Restart Home Assistant

### Automation never triggers
- Confirm selected sensor exists and updates
- Check thresholds (too high/too low)
- Check automation is enabled
- Review **Traces** for the automation

### Fan speed does not change
- Confirm selected entity is a `fan` domain entity
- Test manual speed set from **Developer Tools → Services**
- Verify integration entity is available and online

### Too many notifications
- Increase thresholds or add cooldown
- Disable repeated notifications if not needed
- Keep only one channel for non-critical alerts

---

## FAQ

### Can I use multiple VMC blueprints together?
Yes. Use only one primary speed-control blueprint at a time (`Schedule Plan`, `Schedule Boost`, or `Air Quality Adaptive`) and combine with `Filter Reminder` safely.

### Is `Filter Reminder` useful without extra sensors?
Yes. It uses filter-hour data from the integration and does not require additional devices.

### Can I use external sensors instead of VMC built-in sensors?
Yes. Blueprints accept generic Home Assistant sensor entities, including ESPHome, Zigbee, and cloud-connected sensors.

### What should I start with?
If you are new, start with `VMC Schedule Plan + VMC Filter Reminder`, then add humidity/air-quality automation after validation.
