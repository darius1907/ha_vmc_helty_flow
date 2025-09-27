# Contributing to VMC Helty Flow

Thank you for your interest in contributing to the VMC Helty Flow Home Assistant integration! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Home Assistant development environment
- Python 3.11+
- Git knowledge
- Basic understanding of Home Assistant integrations

### Development Setup
1. **Fork and Clone**:
   ```bash
   git clone https://github.com/darius1907/ha_vmc_helty_flow.git
   cd ha_vmc_helty_flow
   ```

2. **Development Environment**:
   ```bash
   # Install development dependencies
   pip install -r requirements_test.txt

   # Install pre-commit hooks
   pre-commit install
   ```

3. **Link to Home Assistant**:
   ```bash
   # Symlink to your HA custom_components
   ln -s $(pwd)/custom_components/vmc_helty_flow /path/to/homeassistant/custom_components/
   ```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=custom_components.vmc_helty_flow --cov-report=html --cov-report=term

# Run specific test
pytest tests/test_config_flow.py -v
```

### Code Quality
```bash
# Lint code
pylint custom_components/vmc_helty_flow/

# Type checking
mypy custom_components/vmc_helty_flow/

# Format code
black .

# Run all pre-commit checks
pre-commit run --all-files
```

## 📝 Contribution Guidelines

### Code Style
- Follow [Home Assistant coding standards](https://developers.home-assistant.io/docs/development_guidelines/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Follow [PEP 8](https://pep8.org/) style guide
- Add type hints to all functions
- Write comprehensive docstrings

### Commit Messages
Use conventional commits format:
```
feat: add new sensor for air quality index
fix: resolve config flow validation issue
docs: update installation instructions
test: add coverage for device discovery
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process
1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**:
   - Write code following style guidelines
   - Add/update tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Submit PR**:
   - Provide clear description of changes
   - Include testing steps
   - Reference any related issues
   - Ensure CI passes

### Testing Requirements
- **Unit Tests**: All new code must have tests
- **Integration Tests**: Test end-to-end functionality
- **Coverage**: Maintain >95% test coverage
- **Mock External**: Mock all external API calls

## 🐛 Bug Reports

### Before Reporting
- Search existing issues to avoid duplicates
- Test with latest version
- Gather relevant logs and configuration

### Bug Report Template
```markdown
**Describe the Bug**
Clear description of the issue.

**Steps to Reproduce**
1. Go to...
2. Click on...
3. See error...

**Expected Behavior**
What you expected to happen.

**Screenshots/Logs**
Add logs or screenshots if applicable.

**Environment**
- Home Assistant version:
- Integration version:
- VMC model:
- Network configuration:
```

## ✨ Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the requested feature.

**Use Case**
Why this feature would be useful.

**Proposed Implementation**
Ideas for how it could be implemented.

**Alternatives Considered**
Other solutions you've considered.
```

## 🏗️ Architecture Overview

### Integration Structure
```
custom_components/vmc_helty_flow/
├── __init__.py          # Entry point and setup
├── config_flow.py       # Configuration UI
├── const.py            # Constants and configuration
├── coordinator.py      # Data update coordinator
├── device_*.py         # Device management
├── diagnostics.py      # Diagnostic data collection
├── discovery.py        # Device discovery logic
├── helpers*.py         # Utility functions
├── manifest.json       # Integration metadata
├── sensor.py           # Sensor entities
├── fan.py              # Fan control entity
├── light.py            # Light control entity
├── button.py           # Button entities
└── switch.py           # Switch entities
```

### Key Components
- **Config Flow**: Handles device discovery and setup
- **Coordinator**: Manages data updates and API calls
- **Entities**: Implement Home Assistant entity types
- **Device Management**: Handles VMC device information
- **Helpers**: Utility functions for network and calculations

## 🧩 Adding New Features

### Adding New Sensors
1. Define sensor in `sensor.py`
2. Add constants to `const.py`
3. Update device data parsing
4. Add tests in `tests/test_sensor.py`
5. Update documentation

### Adding New Controls
1. Create entity file (e.g., `climate.py`)
2. Implement entity class
3. Register in `__init__.py`
4. Add config flow support if needed
5. Write comprehensive tests

### Extending Device Discovery
1. Update `discovery.py` logic
2. Add new detection methods
3. Update config flow UI
4. Test with various network configurations
5. Document new discovery options

## 📚 Documentation

### Types of Documentation
- **User Documentation**: Installation and usage guides
- **Developer Documentation**: Code architecture and APIs
- **API Documentation**: VMC protocol and commands
- **Troubleshooting**: Common issues and solutions

### Documentation Standards
- Use clear, concise language
- Include code examples
- Add screenshots for UI elements
- Keep documentation up-to-date with changes

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Help newcomers learn
- Provide constructive feedback
- Focus on collaboration

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Home Assistant Community**: Integration discussion
- **Discord**: Real-time chat and support

## 🏆 Recognition

Contributors will be recognized in:
- **CHANGELOG.md**: Feature credits
- **README.md**: Contributor list
- **GitHub**: Contributor statistics
- **Release Notes**: Acknowledgments

### Types of Contributions
- **Code**: New features, bug fixes, improvements
- **Documentation**: Guides, examples, translations
- **Testing**: Test cases, device testing, validation
- **Design**: UI/UX improvements, icons, themes
- **Support**: Helping users, answering questions

## 📋 Development Roadmap

### Current Priorities
1. **HACS Distribution**: Complete HACS preparation
2. **Device Support**: Expand VMC model compatibility
3. **Advanced Features**: Seasonal profiles, automation
4. **Performance**: Optimize polling and data handling

### Future Goals
- Automatic device discovery (mDNS/UPnP)
- Advanced analytics and historical data
- Integration with weather services
- Mobile app companion features

## 🔧 Development Tools

### Recommended Tools
- **IDE**: VS Code with Python extension
- **Debugger**: Built-in Python debugger
- **Testing**: pytest with coverage
- **Formatting**: Black and isort
- **Linting**: pylint and mypy

### Useful Commands
```bash
# Start Home Assistant with integration
hass --config /path/to/config --debug

# Watch log for integration messages
tail -f /path/to/config/home-assistant.log | grep vmc_helty_flow

# Validate manifest
python -m script.hassfest --integration-path custom_components/vmc_helty_flow
```

---

Thank you for contributing to VMC Helty Flow! Your contributions help make this integration better for everyone. 🌟
