#!/usr/bin/env node

/**
 * VMC Auto-Discovery Proof of Concept
 * Scansione automatica subnet locale per dispositivi VMC HELTY FLOW
 *
 * Usage: node vmc-autodiscovery-poc.js [subnet]
 * Example: node vmc-autodiscovery-poc.js 192.168.1.0/24
 */

const net = require('net');
const os = require('os');

class VMCAutoDiscovery {
  constructor(options = {}) {
    this.vmcPort = options.port || 5001;
    this.timeout = options.timeout || 3000;
    this.maxConcurrent = options.maxConcurrent || 50;
    this.discoveredDevices = new Map();
  }

  /**
   * Avvia il processo di auto-discovery
   */
  async discover(subnets = null) {
    console.log('🔍 VMC Auto-Discovery Proof of Concept v1.0');
    console.log('=' .repeat(50));

    const networksToScan = subnets || this.detectLocalNetworks();
    console.log(`📡 Scanning networks: ${networksToScan.join(', ')}`);
    console.log(`🔌 Looking for VMC devices on port ${this.vmcPort}`);
    console.log('');

    const startTime = Date.now();

    try {
      const allDevices = [];

      for (const network of networksToScan) {
        console.log(`🌐 Scanning ${network}...`);
        const devices = await this.scanNetwork(network);
        allDevices.push(...devices);

        if (devices.length > 0) {
          console.log(`✅ Found ${devices.length} VMC devices in ${network}`);
          devices.forEach(device => {
            console.log(`   └─ ${device.ip} - ${device.name} (${device.model})`);
          });
        } else {
          console.log(`❌ No VMC devices found in ${network}`);
        }
        console.log('');
      }

      const scanTime = Date.now() - startTime;

      console.log('📊 Discovery Summary');
      console.log('=' .repeat(30));
      console.log(`Total devices found: ${allDevices.length}`);
      console.log(`Scan duration: ${scanTime}ms`);
      console.log(`Networks scanned: ${networksToScan.length}`);

      if (allDevices.length > 0) {
        console.log('\\n🎯 Ready for integration!');
        this.generateIntegrationCode(allDevices);
      }

      return allDevices;

    } catch (error) {
      console.error('❌ Discovery failed:', error.message);
      return [];
    }
  }

  /**
   * Rileva automaticamente le reti locali
   */
  detectLocalNetworks() {
    const networks = [];
    const interfaces = os.networkInterfaces();

    Object.values(interfaces).flat().forEach(iface => {
      if (iface?.family === 'IPv4' &&
          !iface.internal &&
          iface.address.startsWith('192.168.')) {

        // Genera subnet /24 dall'IP
        const subnet = iface.address.split('.').slice(0, 3).join('.') + '.0/24';
        if (!networks.includes(subnet)) {
          networks.push(subnet);
        }
      }
    });

    // Fallback su reti comuni se non trova nulla
    if (networks.length === 0) {
      networks.push('192.168.1.0/24', '192.168.0.0/24');
    }

    return networks;
  }

  /**
   * Scansiona una rete specifica
   */
  async scanNetwork(subnet) {
    const ipList = this.generateIPRange(subnet);
    const devices = [];

    // Chunking per limitare concorrenza
    const chunks = this.chunkArray(ipList, this.maxConcurrent);

    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i];
      const progress = Math.round(((i + 1) / chunks.length) * 100);

      process.stdout.write(`\\r   Progress: ${progress}% (${i + 1}/${chunks.length} chunks)`);

      const results = await Promise.allSettled(
        chunk.map(ip => this.probeVMCDevice(ip))
      );

      results.forEach(result => {
        if (result.status === 'fulfilled' && result.value) {
          devices.push(result.value);
        }
      });
    }

    process.stdout.write('\\r' + ' '.repeat(50) + '\\r'); // Clear progress
    return devices;
  }

  /**
   * Testa se un IP ha un dispositivo VMC
   */
  async probeVMCDevice(ip) {
    return new Promise((resolve) => {
      const socket = new net.Socket();
      let responseData = '';

      const cleanup = () => {
        socket.destroy();
      };

      // Timeout
      const timeoutId = setTimeout(() => {
        cleanup();
        resolve(null);
      }, this.timeout);

      socket.on('connect', () => {
        // Invia comando identificazione VMC
        socket.write('VMGN?\\n');
      });

      socket.on('data', (data) => {
        responseData += data.toString();

        // Verifica se è una risposta VMC valida
        if (responseData.includes('VMGN,')) {
          clearTimeout(timeoutId);

          // Estrai informazioni dispositivo
          const deviceInfo = this.parseVMCResponse(responseData);
          if (deviceInfo) {
            deviceInfo.ip = ip;
            deviceInfo.discoveredAt = new Date().toISOString();
          }

          cleanup();
          resolve(deviceInfo);
        }
      });

      socket.on('error', () => {
        clearTimeout(timeoutId);
        cleanup();
        resolve(null);
      });

      socket.on('timeout', () => {
        clearTimeout(timeoutId);
        cleanup();
        resolve(null);
      });

      // Avvia connessione
      socket.connect(this.vmcPort, ip);
    });
  }

  /**
   * Analizza la risposta VMC e estrae informazioni
   */
  parseVMCResponse(responseData) {
    try {
      // Formato atteso: VMGN,nome,versione,modello,...
      const lines = responseData.split('\\n');
      const vmgnLine = lines.find(line => line.startsWith('VMGN,'));

      if (!vmgnLine) return null;

      const parts = vmgnLine.split(',');

      // Determina modello in base a risposta
      const hasEliteFeatures = parts.length > 5; // ELITE ha più parametri

      return {
        name: parts[1] || 'VMC-Unknown',
        firmware: parts[2] || 'Unknown',
        model: hasEliteFeatures ? 'HELTY_FLOW_ELITE' : 'HELTY_FLOW_PLUS',
        capabilities: {
          basicControl: true,
          temperatureSensors: true,
          humiditySensor: true,
          co2Sensor: hasEliteFeatures,
          vocSensor: hasEliteFeatures,
          advancedAutomation: hasEliteFeatures
        },
        rawResponse: responseData.trim()
      };

    } catch (error) {
      console.warn(`Parse error for response: ${responseData}`, error);
      return null;
    }
  }

  /**
   * Genera range IP da subnet CIDR
   */
  generateIPRange(subnet) {
    const [network, prefixLength] = subnet.split('/');
    const [a, b, c, d] = network.split('.').map(Number);

    if (prefixLength !== '24') {
      throw new Error('Solo subnet /24 supportate in questo POC');
    }

    const ips = [];
    for (let i = 1; i < 255; i++) { // Esclude .0 e .255
      ips.push(`${a}.${b}.${c}.${i}`);
    }

    return ips;
  }

  /**
   * Divide array in chunks
   */
  chunkArray(array, chunkSize) {
    const chunks = [];
    for (let i = 0; i < array.length; i += chunkSize) {
      chunks.push(array.slice(i, i + chunkSize));
    }
    return chunks;
  }

  /**
   * Genera codice di integrazione per dispositivi trovati
   */
  generateIntegrationCode(devices) {
    console.log('\\n📝 Integration Code Generated:');
    console.log('=' .repeat(40));

    // Genera configurazione YAML per Home Assistant
    console.log('\\n# Home Assistant Configuration:');
    devices.forEach((device, index) => {
      console.log(`
# VMC ${device.name}
sensor:
  - platform: command_line
    name: vmc_${device.name.toLowerCase()}_status
    command: 'echo "{\\"ip\\": \\"${device.ip}\\", \\"model\\": \\"${device.model}\\"}"'
    value_template: '{{ value_json.ip }}'
    scan_interval: 30`);
    });

    // Genera configurazione JSON per dashboard
    console.log('\\n# Dashboard Configuration JSON:');
    const config = {
      discovered_devices: devices.map(device => ({
        id: device.ip.replace(/\\./g, '_'),
        name: device.name,
        ip: device.ip,
        model: device.model,
        capabilities: device.capabilities,
        auto_discovered: true,
        discovered_at: device.discoveredAt
      })),
      auto_discovery: {
        enabled: true,
        last_scan: new Date().toISOString(),
        scan_interval: 3600 // 1 ora
      }
    };

    console.log(JSON.stringify(config, null, 2));

    // Genera comandi di test
    console.log('\\n# Test Commands:');
    devices.forEach(device => {
      console.log(`# Test ${device.name}:`);
      console.log(`curl -X POST http://localhost:3000/api/vmc/${device.ip}/command -d '{"command": "VMGH?"}'`);
    });
  }
}

// Esecuzione da command line
if (require.main === module) {
  const subnet = process.argv[2];
  const discovery = new VMCAutoDiscovery({
    timeout: 5000,
    maxConcurrent: 30
  });

  discovery.discover(subnet ? [subnet] : null)
    .then(devices => {
      if (devices.length === 0) {
        console.log('\\n💡 Tips per troubleshooting:');
        console.log('   1. Verifica che le VMC siano accese e connesse alla rete');
        console.log('   2. Controlla che gli IP siano nella subnet corretta');
        console.log('   3. Verifica firewall e porte aperte');
        console.log('   4. Prova scan manuale: node vmc-autodiscovery-poc.js 192.168.1.0/24');
      }
    })
    .catch(error => {
      console.error('❌ Errore durante discovery:', error);
      process.exit(1);
    });
}

module.exports = VMCAutoDiscovery;
