# VMC Helty Card Installation Guide

## Quick Start (5 minutes)

### Step 1: Install the Card Files

**Option A: Manual Installation**
1. Create directory: `/config/www/vmc-helty-card/`
2. Copy all files from this directory to your Home Assistant `www` folder
3. Restart Home Assistant

**Option B: File Editor Add-on**
1. Open File Editor add-on in Home Assistant
2. Navigate to `www` folder (create if it doesn't exist)
3. Create `vmc-helty-card` folder
4. Upload/create the following files:
   - `vmc-helty-card.js`
   - `vmc-helty-card-editor.js` 
   - `vmc-helty-compact-card.js`

### Step 2: Add to Lovelace Resources

1. Go to **Settings** → **Dashboards** → **Resources**
2. Click **Add Resource**
3. Add these resources:

```yaml
URL: /local/vmc-helty-card/vmc-helty-card.js
Resource type: JavaScript Module
```

### Step 3: Add Card to Dashboard

1. Edit your dashboard
2. Click **Add Card**
3. Search for "VMC Helty"
4. Configure your VMC fan entity

## Detailed Installation

### Prerequisites

✅ **Home Assistant Core** ≥ 2024.1.0  
✅ **VMC Helty Integration** installed and configured  
✅ **VMC Fan Entity** available (e.g., `fan.vmc_helty`)  
✅ **Lovelace UI** configured  

### File Structure

Your `/config/www/vmc-helty-card/` directory should contain:

```
vmc-helty-card/
├── vmc-helty-card.js              # Main card component
├── vmc-helty-card-editor.js       # Configuration editor
├── vmc-helty-compact-card.js      # Compact version
├── package.json                   # Metadata
├── README.md                      # Documentation
├── examples.yaml                  # Configuration examples
└── INSTALLATION.md                # This file
```

### Verify Installation

1. **Check Resources**:
   - Settings → Dashboards → Resources  
   - Verify `/local/vmc-helty-card/vmc-helty-card.js` is listed
   - Status should show "Loaded"

2. **Check Card Availability**:
   - Edit any dashboard
   - Click "Add Card"
   - Search for "VMC Helty Card"
   - Should appear in custom cards section

3. **Test Configuration**:
   - Add the card with your fan entity
   - Verify all sensors display correctly
   - Test fan speed controls

## Troubleshooting

### ❌ "Custom element doesn't exist" error

**Solution**: Resource not loaded properly
1. Check resource URL is exactly: `/local/vmc-helty-card/vmc-helty-card.js`
2. Verify file exists at `/config/www/vmc-helty-card/vmc-helty-card.js`
3. Clear browser cache (Ctrl+F5)
4. Restart Home Assistant

### ❌ Card not showing in card picker

**Solution**: Missing resource registration
1. Ensure resource type is "JavaScript Module"
2. Check browser console for JavaScript errors
3. Verify file syntax is correct
4. Try adding resource with full URL: `http://your-ha-ip:8123/local/vmc-helty-card/vmc-helty-card.js`

### ❌ "Entity not found" error

**Solution**: VMC integration issues
1. Verify VMC Helty integration is installed
2. Check fan entity exists in Developer Tools → States
3. Ensure entity ID is exactly correct (case-sensitive)
4. Restart VMC Helty integration if needed

### ❌ Sensors not displaying

**Solution**: Entity naming issues
1. Check sensor entity names in Developer Tools → States
2. Verify entities follow pattern: `sensor.{device_id}_{sensor_type}`
3. Elite-only sensors (CO₂/VOC) won't show on Plus models
4. Check entities are not disabled in Settings → Devices & Services

### ❌ Controls not working

**Solution**: Service call issues
1. Test fan control manually in Developer Tools → Services
2. Verify fan entity supports `fan.set_percentage` service
3. Check Home Assistant logs for errors
4. Ensure user has appropriate permissions

## Advanced Configuration

### Custom Resource Loading

For advanced users wanting to load from external sources:

```yaml
# configuration.yaml
lovelace:
  resources:
    - url: /local/vmc-helty-card/vmc-helty-card.js
      type: module
    - url: /local/vmc-helty-card/vmc-helty-compact-card.js  # Optional
      type: module
```

### Development Mode

For developers or beta testers:

```yaml
# Load from development server
- url: http://localhost:5000/vmc-helty-card.js
  type: module
```

### Multiple Card Versions

You can install multiple versions side-by-side:

```
www/
├── vmc-helty-card/           # Stable version
│   └── vmc-helty-card.js
├── vmc-helty-card-beta/      # Beta version  
│   └── vmc-helty-card.js
└── vmc-helty-card-dev/       # Development version
    └── vmc-helty-card.js
```

## Performance Optimization

### Minimize Resource Loading

Only load cards you actually use:

```yaml
resources:
  # Load main card only
  - url: /local/vmc-helty-card/vmc-helty-card.js
    type: module
    
  # Load compact card only if needed
  # - url: /local/vmc-helty-card/vmc-helty-compact-card.js
  #   type: module
```

### Browser Caching

The card includes proper cache headers. For manual cache control:

```yaml
# Force cache refresh
- url: /local/vmc-helty-card/vmc-helty-card.js?v=1.0.1
  type: module
```

## Security Considerations

### File Permissions

Ensure proper permissions on card files:

```bash
# On Home Assistant OS/Supervised
chmod 644 /config/www/vmc-helty-card/*.js

# Verify files are readable
ls -la /config/www/vmc-helty-card/
```

### Content Security Policy

If you have strict CSP, you may need to allow:

```yaml
# configuration.yaml
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 127.0.0.1
  # Allow local resources
  cors_allowed_origins:
    - http://localhost:8123
```

## Updates

### Manual Updates

1. Backup current card files
2. Download new version files
3. Replace old files with new ones
4. Clear browser cache
5. Refresh dashboard

### Version Checking

Check current version in browser console:
- Open Developer Tools (F12)
- Look for "VMC-HELTY-CARD v1.0.0" message

### Breaking Changes

Always check README.md for breaking changes between versions:
- Configuration format changes
- Entity name changes  
- Required Home Assistant version updates

## Support

### Before Requesting Support

1. ✅ Check this installation guide
2. ✅ Verify VMC Helty integration works independently  
3. ✅ Test with basic configuration first
4. ✅ Check browser console for errors
5. ✅ Review Home Assistant logs

### Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/your-repo/vmc-helty-card/issues)
- **Community Forum**: [Ask questions](https://community.home-assistant.io/)
- **Documentation**: [Full guide](README.md)

### Providing Debug Info

When requesting support, include:

```yaml
# Home Assistant version
# VMC Helty integration version  
# Card version
# Browser and version
# Full error messages
# Configuration YAML
# Relevant entities from Developer Tools → States
```