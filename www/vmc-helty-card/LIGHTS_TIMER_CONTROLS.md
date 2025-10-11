# VMC Helty Card - Light and Timer Controls

## New Configuration Options (v2.1)

The VMC Helty Card now includes toggles to control the visibility of light and timer controls, allowing better compatibility with different VMC models.

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_lights` | boolean | `true` | Show/hide light brightness controls |
| `show_timer` | boolean | `true` | Show/hide light timer controls |

### Usage Examples

#### For VMC models WITH lighting support:
```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_living_room
show_lights: true    # Show light controls
show_timer: true     # Show timer controls
```

#### For VMC models WITHOUT lighting support:
```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_living_room
show_lights: false   # Hide light controls
show_timer: false    # Hide timer controls
```

#### For VMC models with lights but NO timer:
```yaml
type: custom:vmc-helty-card
entity: fan.vmc_helty_living_room
show_lights: true    # Show light controls
show_timer: false    # Hide timer controls
```

### Visual Editor

The new options are available in the visual card editor:

1. Open the card configuration in the Lovelace editor
2. Scroll to the "Display Options" section
3. Toggle "Show Lights" and "Show Timer" as needed
4. The toggles include helpful descriptions about VMC model compatibility

### Backward Compatibility

- Both options default to `true` for maximum backward compatibility
- Existing card configurations will continue to work without changes
- Light/timer sections will only show if the corresponding entities exist AND the option is enabled

### Technical Implementation

- Light controls check: `config.show_lights !== false && lightEntity exists`
- Timer controls check: `config.show_timer !== false && timerEntity exists`
- If both are disabled or entities don't exist, the entire "Controlli Luci" section is hidden

### Supported VMC Models

| Model | Lighting | Timer | Recommended Settings |
|-------|----------|-------|---------------------|
| Helty Flow Plus | ✅ Yes | ✅ Yes | `show_lights: true, show_timer: true` |
| Helty Flow Elite | ✅ Yes | ✅ Yes | `show_lights: true, show_timer: true` |
| Helty Flow Standard | ❌ No | ❌ No | `show_lights: false, show_timer: false` |
| Helty Flow Basic | ❌ No | ❌ No | `show_lights: false, show_timer: false` |

### Changelog

**v2.1 Features:**
- ✅ Added `show_lights` configuration option
- ✅ Added `show_timer` configuration option
- ✅ Updated visual editor with new toggles
- ✅ Added helpful descriptions for VMC model compatibility
- ✅ Maintained full backward compatibility
