# Security Policy

## Supported Versions

We provide security updates for the following versions of VMC Helty Flow:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Yes             |
| < 1.0   | ❌ No              |

## Reporting a Vulnerability

The VMC Helty Flow team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:

1. **Email**: Send details to `dario.pezzoli@par-tec.it`
2. **Subject**: Include "SECURITY" in the subject line
3. **Details**: Provide as much information as possible

### What to Include

Please include the following information in your report:

- **Description**: Clear description of the vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Impact**: Potential security impact and affected components
- **Environment**: Home Assistant version, integration version, network setup
- **Suggested Fix**: If you have ideas for remediation

### Response Process

1. **Acknowledgment**: We'll acknowledge receipt within 48 hours
2. **Investigation**: Initial assessment within 5 business days
3. **Updates**: Regular updates on investigation progress
4. **Resolution**: Security fix and coordinated disclosure

### Security Considerations

#### Network Security
- **Local Network Only**: Integration only communicates within local network
- **No External Connections**: No data sent to external servers
- **Encryption**: Supports secure communication protocols where available

#### Data Privacy  
- **Local Processing**: All data processing happens locally
- **No Cloud Storage**: No user data stored in cloud services
- **Minimal Data**: Only necessary device data is collected

#### Authentication
- **Device Authentication**: Secure authentication with VMC devices
- **Home Assistant Integration**: Follows HA security best practices
- **Configuration Protection**: Sensitive config data is encrypted

### Known Security Features

#### Integration Security
- ✅ Input validation for all user inputs
- ✅ Sanitized network communications
- ✅ Secure credential storage
- ✅ Rate limiting for API calls
- ✅ Error handling without information disclosure

#### Network Security
- ✅ Local network communication only
- ✅ Configurable timeouts and retries
- ✅ No hardcoded credentials
- ✅ Secure default configurations
- ✅ Network isolation support

### Security Best Practices for Users

#### Installation Security
1. **Official Sources**: Only install from official HACS or GitHub releases
2. **Verify Checksums**: Verify file integrity when possible
3. **Update Regularly**: Keep integration updated to latest version
4. **Review Permissions**: Understand what permissions the integration needs

#### Network Security  
1. **Isolate VMC Network**: Consider network isolation for IoT devices
2. **Firewall Rules**: Configure appropriate firewall rules
3. **Monitor Traffic**: Monitor network traffic for unusual activity
4. **Secure WiFi**: Use strong WiFi passwords for VMC devices

#### Home Assistant Security
1. **HTTPS**: Enable HTTPS for Home Assistant access
2. **Authentication**: Use strong authentication methods
3. **Updates**: Keep Home Assistant updated
4. **Backups**: Regular configuration backups

### Vulnerability Disclosure Timeline

We aim to follow this timeline for security vulnerability handling:

- **Day 0**: Vulnerability reported
- **Day 1-2**: Acknowledge receipt and begin investigation
- **Day 3-5**: Complete initial assessment
- **Day 6-14**: Develop and test security fix
- **Day 15-21**: Coordinate disclosure and release fix
- **Day 22+**: Public disclosure (if appropriate)

We may adjust this timeline based on the complexity and severity of the vulnerability.

### Security Updates

Security updates will be:

1. **Released Promptly**: Critical fixes released as soon as possible
2. **Clearly Marked**: Security releases clearly identified
3. **Documented**: Security fixes documented in release notes
4. **Communicated**: Users notified through appropriate channels

### Scope

This security policy applies to:

- ✅ VMC Helty Flow integration code
- ✅ Configuration and setup processes  
- ✅ Network communication protocols
- ✅ Data handling and storage
- ✅ Authentication and authorization

This policy does NOT cover:

- ❌ Home Assistant core vulnerabilities
- ❌ Third-party VMC device firmware
- ❌ Network infrastructure security
- ❌ Operating system vulnerabilities

### Recognition

We appreciate security researchers and will:

- Acknowledge your contribution (with permission)
- Credit you in security advisories (unless you prefer anonymity)
- Work with you on coordinated disclosure

### Contact Information

- **Security Email**: dario.pezzoli@par-tec.it
- **General Issues**: https://github.com/dpezzoli/ha_vmc_helty_flow/issues
- **Documentation**: https://github.com/dpezzoli/ha_vmc_helty_flow/blob/main/README.md

---

Thank you for helping keep VMC Helty Flow and our users safe! 🔒