# Room Volume Synchronization Feature

## 🎯 Overview

The VMC Helty Flow integration now supports **automatic synchronization** between the card editor room volume and the device configuration used for sensor calculations.

## 🔄 How It Works

### Before (Manual Process)
1. User configures room volume in card editor → stored in `config.room_volume`
2. Device sensors use volume from config entry → stored in `entry.data["room_volume"]` 
3. **Values could be different** → inaccurate calculations

### After (Automatic Sync)
1. User configures room volume in card editor → stored in `config.room_volume`
2. **Card automatically calls service** → updates `entry.data["room_volume"]`
3. **Both values stay synchronized** → accurate calculations

## 🛠️ Technical Implementation

### New Service: `vmc_helty_flow.update_room_volume`

**Parameters:**
- `entity_id` (required): Any VMC Helty entity ID from the device
- `room_volume` (required): New room volume in m³ (1.0-1000.0)

**Example:**
```yaml
service: vmc_helty_flow.update_room_volume
data:
  entity_id: fan.vmc_helty_192_168_1_100
  room_volume: 85.5
```

### Card Editor Enhancements

1. **Manual Volume Input**: Calls service on `@input` event
2. **Calculated Volume**: Calls service when "Use Calculated Volume" is clicked
3. **Visual Feedback**: Shows sync status icon and notifications
4. **Error Handling**: Displays error notifications if service call fails

### JavaScript Methods Added

```javascript
// Sync room volume with device configuration
async _syncRoomVolumeToDevice(volume) {
  await this.hass.callService('vmc_helty_flow', 'update_room_volume', {
    entity_id: this.config.entity,
    room_volume: volume
  });
}

// Enhanced value change handler
_valueChanged(ev) {
  // ... existing logic ...
  
  // Auto-sync room volume changes
  if (key === 'room_volume' && this.config.entity && value > 0) {
    this._syncRoomVolumeToDevice(value);
  }
}
```

## 🎨 User Experience

### Visual Indicators

**When Device Selected:**
- ✅ Green sync icon next to "Room Volume" label
- ✅ "Changes will be automatically synced with device configuration"

**When No Device Selected:**
- ⚠️ Warning message: "Select a device above to enable automatic sync"

### Notifications

**Success:**
- 🟢 "Room volume updated successfully" (3 seconds)

**Error:**
- 🔴 "Failed to update room volume: [error message]" (5 seconds)

## 📊 Data Flow

```
User Input → Card Config → Service Call → Config Entry → Coordinator → Sensors
     ↓           ↓             ↓             ↓             ↓           ↓
room_volume  config.     vmc_helty_flow. entry.data.  coordinator. accurate
changes   room_volume  update_room_   room_volume   room_volume  calculations
                       volume service
```

## 🧪 Testing

### Manual Test
1. Open card editor
2. Select a VMC device 
3. Change room volume value
4. Observe notification and sync icon
5. Check device configuration in Home Assistant

### Test File
Use `test-editor.html` for development testing with mock Home Assistant environment.

## 🔧 Configuration Locations

### Card Configuration
```yaml
# Stored in Lovelace card config
type: custom:vmc-helty-card
entity: fan.vmc_helty_192_168_1_100
room_volume: 85.5  # ← Card display value
```

### Device Configuration  
```yaml
# Stored in config entry data
{
  "ip": "192.168.1.100",
  "name": "VMC Helty",
  "room_volume": 85.5  # ← Used for sensor calculations
}
```

## 🎯 Benefits

1. **Consistency**: Card and sensors always use same volume
2. **Convenience**: No manual service calls needed
3. **Real-time**: Changes take effect immediately
4. **Feedback**: Clear visual confirmation of sync status
5. **Error Handling**: Graceful failure with user notification

## 🔄 Backward Compatibility

- Existing cards continue to work
- Service is optional - only called when device is selected
- Manual volume input still supported
- No breaking changes to existing functionality