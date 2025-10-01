# VMC Helty Flow - Network Connectivity Troubleshooting

## Error: "Connect call failed ('192.168.1.117', 5001)"

This error indicates that Home Assistant cannot establish a TCP connection to your VMC Helty device. Here's how to troubleshoot and resolve this issue.

## Quick Diagnostics

You can now use the new network diagnostics service to test connectivity:

```yaml
service: vmc_helty_flow.network_diagnostics
data:
  ip: "192.168.1.117"
  port: 5001
```

## Common Causes and Solutions

### 1. Device is Offline or Unreachable

**Symptoms:**
- Error: "Host non raggiungibile" (Host unreachable)
- errno 113: Network unreachable

**Solutions:**
- Check that the VMC device is powered on
- Verify the device is connected to your network (WiFi/Ethernet)
- Check if the device's network LED indicators show connectivity
- Try accessing the device's web interface directly at `http://192.168.1.117`

### 2. Wrong IP Address

**Symptoms:**
- Connection timeouts
- Device not responding

**Solutions:**
- Check your router's DHCP client list to find the current IP
- Use the integration's discovery feature to scan for devices
- Access your router admin panel to verify device IP assignments

### 3. Firewall or Network Issues

**Symptoms:**
- Connection refused errors
- Intermittent connectivity

**Solutions:**
- Check if your router has firewall rules blocking port 5001
- Ensure the device and Home Assistant are on the same network segment
- Try temporarily disabling any network security features to test

### 4. Device Service Not Running

**Symptoms:**
- Error: "Connessione rifiutata" (Connection refused)
- errno 111: Connection refused

**Solutions:**
- Restart the VMC device (power cycle)
- Check if the device firmware is up to date
- Reset network settings on the device if necessary

## Enhanced Error Reporting

The integration now provides more detailed error messages:

- **Host unreachable**: Network routing issue
- **Connection refused**: Service not available on the device
- **Timeout**: Device not responding (may be busy or slow)

## Using Network Diagnostics Service

The new `vmc_helty_flow.network_diagnostics` service provides detailed connectivity testing:

```yaml
# Test basic connectivity
service: vmc_helty_flow.network_diagnostics
data:
  ip: "192.168.1.117"
  port: 5001
```

The service returns:
- **ping_success**: Basic network reachability
- **tcp_connection**: TCP port accessibility  
- **reachable**: Overall connectivity status
- **error_details**: Specific error information

## Integration Improvements

The integration now includes:

1. **Better Error Messages**: More specific network error descriptions
2. **Network Diagnostics**: Automated connectivity testing during errors
3. **Recovery Mode**: Automatic adjustment of update intervals when devices are unreachable
4. **Diagnostic Service**: Manual network testing capability

## Getting Help

If you continue having connectivity issues:

1. Run the network diagnostics service and note the results
2. Check Home Assistant logs for detailed error messages
3. Verify your network configuration
4. Consider using static IP assignment for your VMC device

## Technical Details

The VMC Helty Flow integration communicates with devices using:
- **Protocol**: TCP
- **Port**: 5001 (default)
- **Timeout**: 3 seconds (configurable)
- **Commands**: Custom VMC protocol (VMGH?, VMNM?, etc.)

The integration automatically handles network issues by:
- Reducing update frequency when devices are unreachable
- Providing detailed diagnostic information
- Attempting automatic recovery when connectivity is restored