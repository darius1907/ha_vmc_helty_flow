# 🎯 EASC (External Advanced Sensor Configuration) - Specifica Tecnica

> **External Advanced Sensor Configuration**: Sistema per permettere ai sensori evoluti VMC di utilizzare fonti dati esterne (sensori HA, ESPHome, Zigbee, etc.) al posto dei sensori interni della VMC, con fallback automatico.

---

## 📋 Indice
1. [Overview](#overview)
2. [Analisi Sensori Evoluti](#analisi-sensori-evoluti)
3. [Requirements](#requirements)
4. [Architecture](#architecture)
5. [Data Mapping](#data-mapping)
6. [Implementation Plan](#implementation-plan)
7. [Configuration Examples](#configuration-examples)
8. [Testing Strategy](#testing-strategy)

---

## Overview

### Motivazione
I sensori evoluti della VMC dipendono da sensori interni che potrebbero:
- Essere meno accurati di sensori esterni dedicati
- Non essere disponibili su tutti i modelli VMC
- Avere drift nel tempo
- Non dare visibilità nei dati storici

**Soluzione**: Permettere override configurabile da entità HA esterne mantenendo fallback ai sensori VMC.

### Caso d'uso tipico
```yaml
Utente ha:
- VMC Helty (temp/humidity interna)
- Netatmo extern (temp/humidity esterna)
- CO2 sensor (ESPHome)

Vuole:
- VmcHeltyDewPointDeltaSensor usi Netatmo per T_ext invece di VMC
- VmcHeltyAbsoluteHumiditySensor usi Netatmo per humidity più accurata
- Future: CO2-based automation usi sensore ESPHome esterno
```

---

## Analisi Sensori Evoluti

### 📊 Mapping Sensori Attuali

#### **Gruppo 1: Temperature + Humidity Derivate (CRITICAL)**

```
Sensore: VmcHeltyAbsoluteHumiditySensor
├── Formula: Magnus-Tetens
├── Input Richiesti:
│   ├── Temperature (interna) [VMGI pos 1]
│   └── Humidity (%) [VMGI pos 3]
├── Sources Attuali:
│   ├── VMC: VMGI response position 1 (decimi di °C)
│   └── VMC: VMGI response position 3 (decimi di %)
└── Configurabilità Proposta: ✅ HIGH PRIORITY
    ├── temperature_source: entity_id | "vmc_default"
    └── humidity_source: entity_id | "vmc_default"

Sensore: VmcHeltyDewPointSensor
├── Formula: Magnus-Tetens
├── Input Richiesti:
│   ├── Temperature (interna) [VMGI pos 1]
│   └── Humidity (%) [VMGI pos 3]
├── Sources Attuali: Same as AbsoluteHumidity
└── Configurabilità Proposta: ✅ HIGH PRIORITY

Sensore: VmcHeltyComfortIndexSensor
├── Formula: ASHRAE blend (temperature + humidity)
├── Input Richiesti:
│   ├── Temperature (interna) [VMGI pos 1]
│   └── Humidity (%) [VMGI pos 3]
├── Sources Attuali: Same
└── Configurabilità Proposta: ✅ HIGH PRIORITY

Sensore: VmcHeltyDewPointDeltaSensor
├── Formula: Magnus-Tetens (internal - external dew point)
├── Input Richiesti:
│   ├── Temperature (interna) [VMGI pos 1]
│   ├── Temperature (esterna) [VMGI pos 2]
│   └── Humidity (%) [VMGI pos 3]
├── Sources Attuali:
│   ├── VMC: VMGI pos 1 (internal temp, often room temp)
│   ├── VMC: VMGI pos 2 (external temp)
│   └── VMC: VMGI pos 3 (humidity)
├── Configurabilità Proposta: ✅ HIGHEST PRIORITY
│   ├── temperature_internal: entity_id | "vmc_default"
│   ├── temperature_external: entity_id | "weather.*" | "vmc_default"
│   └── humidity_source: entity_id | "vmc_default"
└── Notes: External temp often wrong - WeatherIntegration support critical
```

#### **Gruppo 2: Fan-based Calculations (MEDIUM)**

```
Sensore: VmcHeltyAirExchangeTimeSensor
├── Formula: room_volume / airflow_rate * 60
├── Input Richiesti:
│   ├── Fan Speed (0-7) [VMGO pos 1]
│   └── Room Volume (m³) [Config value]
├── Sources Attuali:
│   ├── VMC: VMGO response position 1
│   └── Config: entry.options["room_volume"]
└── Configurabilità Proposta: 🟡 MEDIUM PRIORITY
    ├── fan_speed_source: entity_id | "vmc_default"
    └── room_volume: float | "vmc_default_60"

Sensore: VmcHeltyDailyAirChangesSensor
├── Formula: (airflow_rate / room_volume) * 24
├── Input Richiesti: Same as AirExchangeTime
├── Sources: Same
└── Configurabilità Proposta: 🟡 MEDIUM PRIORITY
```

#### **Gruppo 3: Base Sensors (NOT YET CONFIGURABLE)**

```
Sensore: VmcHeltySensor (base type)
├── Types:
│   ├── "temperature_internal": VMGI pos 1
│   ├── "temperature_external": VMGI pos 2
│   ├── "humidity": VMGI pos 3
│   ├── "co2": VMGI pos 4
│   └── "voc": VMGI pos 11
├── Current: Hardcoded VMGI parsing
└── Future Consideration: ⚠️ MIGHT NEED EASC TOO
    └── Use case: Replace VMC CO2/VOC with external Zigbee sensors
    └── Priority: LOW (for v1.5.0+)
```

### 🏗️ Dependency Tree

```
Config Entry
├── VMGI Response (periodic from device)
│   ├── temp_internal ──► AbsoluteHumidity
│   │                 ──► DewPoint
│   │                 ──► ComfortIndex
│   │                 ──► DewPointDelta
│   │
│   ├── temp_external ──► DewPointDelta
│   │
│   ├── humidity ───────► AbsoluteHumidity
│   │               ───► DewPoint
│   │               ───► ComfortIndex
│   │               ───► DewPointDelta
│   │
│   ├── co2 ────────────► VmcHeltySensor(type="co2")
│   └── voc ────────────► VmcHeltySensor(type="voc")
│
├── VMGO Response (periodic from device)
│   ├── fan_speed ──────► AirExchangeTime
│   │              ───► DailyAirChanges
│   │
│   └── (NOT in response yet but needed)
│       └── filter_hours ──► FilterLifePercentage
│
└── Config: room_volume
    ├── AirExchangeTime
    └── DailyAirChanges
```

---

## Requirements

### Functional Requirements

**R1: Configurabilità Sensori Temperatura + Umidità**
- Utente deve poter selezionare entity_id custom per:
  - Temperatura interna (es. `climate.living_room` o `sensor.netatmo_indoor_temp`)
  - Temperatura esterna (es. `weather.provincia` o `sensor.netatmo_outdoor_temp`)
  - Umidità (es. `sensor.netatmo_indoor_humidity`)
- Per ogni source, permettere mapping da unità differenti (°C vs °F, 0-1 vs 0-100)
- Fallback automatico a VMC se entity_id non disponibile

**R2: Validazione Dati e Type Checking**
- Auto-detect unità di misura (es. se humidity > 100, è 0-1?)
- Validate ranges (es. humidity 0-100, temp -50 a +50)
- Handle missing attributes gracefully
- Log warnings se conversioni poco sicure

**R3: Configurazione Persistente**
- Salva mapping in `config_entry.options`
- Supporta update via config flow
- Supporta re-migration se schema cambia
- Mantieni backward-compatibility

**R4: Diagnostics & Debugging**
- Log quale source è usato per ogni calcolo
- Timestamp dato ultimo valido da fonte esterna
- Reason se fallback a VMC
- Sensor availability tracking

### Non-Functional Requirements

**NFR1: Performance**
- Zero impact se sources esterne non cambiano
- Caching dei dati per non parser ripetutamente
- Update frequency align con coordinator update interval

**NFR2: Reliability**
- Zero crashes se entity_id rimosso o non esiste
- Graceful fallback se external source sparisce
- Test coverage >95% su data provider

**NFR3: User Experience**
- Config flow intuitive
- Dropdown/entity picker in UI
- Error messages chiari se problemi

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│ Config Entry                                            │
│ ├── Data: {temperature_source, humidity_source, ...}   │
│ └── Options: {external_sensor_config: {...}}           │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ VmcHeltyCoordinator                                     │
│ ├── _get_vmc_data() → {status, sensors, ...}           │
│ ├── data: {status, sensors, EASCMappedData}            │
│ └── _init_easc_provider()                              │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ EASCDataProvider                                        │
│ ├── get_temperature(source_key) → float                │
│ ├── get_humidity(source_key) → float                   │
│ ├── _get_entity_state(entity_id) → float               │
│ ├── _convert_unit(value, from_unit, to_unit) → float  │
│ ├── _validate_range(value, expected_max) → bool        │
│ └── _log_source_usage() → None                         │
└────────────┬────────────────────────────────────────────┘
             │
             ├──────────────────────────────────────────────┐
             │                                              │
             ▼                                              ▼
   ┌──────────────────┐                        ┌──────────────────┐
   │ VMC data cache   │                        │ HA State Store   │
   │ (VMGI, VMGO)     │                        │ (entity_id data) │
   └──────────────────┘                        └──────────────────┘
             ▲                                              ▲
             │                                              │
             └──────────────────────┬───────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│ Advanced Sensors                                        │
│ ├── VmcHeltyAbsoluteHumiditySensor                      │
│ ├── VmcHeltyDewPointSensor                              │
│ ├── VmcHeltyComfortIndexSensor                          │
│ ├── VmcHeltyDewPointDeltaSensor                         │
│ ├── VmcHeltyAirExchangeTimeSensor                       │
│ └── VmcHeltyDailyAirChangesSensor                       │
└─────────────────────────────────────────────────────────┘
```

### Class Design

```python
class EASCDataProvider:
    """
    Data provider per EASC - gestisce override da fonti esterne.

    Responsabilità:
    - Recuperare dati da HA entities
    - Convertire unità di misura
    - Validare ranges
    - Fallback a VMC se necessario
    - Logging e diagnostics
    """

    def __init__(self, hass: HomeAssistant, coordinator: VmcHeltyCoordinator):
        self.hass = hass
        self.coordinator = coordinator
        self.config = coordinator.config_entry.options.get("easc", {})
        self._cache = {}
        self._last_update = {}
        self._fallback_reasons = {}  # Track why fallbacks happened

    # Public API
    def get_temperature(
        self,
        source_key: str,  # e.g., "temperature_internal", "temperature_external"
        default: float | None = None
    ) -> float | None:
        """Get temperature in °C, from external or VMC source."""

    def get_humidity(
        self,
        source_key: str,
        default: float | None = None
    ) -> float | None:
        """Get humidity in %, from external or VMC source."""

    def get_fan_speed(self) -> int | None:
        """Get fan speed (0-7), currently always from VMC."""

    def get_room_volume(self) -> float:
        """Get room volume in m³."""

    def get_diagnostics(self) -> dict:
        """Return diagnostic info for troubleshooting."""
        return {
            "temperature_sources": self._last_update.get("temp", {}),
            "humidity_sources": self._last_update.get("humidity", {}),
            "fallback_reasons": self._fallback_reasons,
            "cache_status": self._cache,
        }

    # Private helpers
    def _get_entity_state(self, entity_id: str) -> float | None:
        """Safe get entity state from HA."""

    def _convert_unit(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between temperature/humidity units."""

    def _validate_range(self, value: float, param_type: str) -> bool:
        """Validate value is in expected range."""

    def _use_vmc_fallback(self, source_key: str, reason: str) -> float | None:
        """Fallback a VMC data e log reason."""
```

### Config Flow Schema

```python
EASC_SCHEMA = vol.Schema({
    vol.Optional("enabled", default=False): cv.boolean,
    vol.Optional("advanced_sensors"): {
        vol.Optional("absolute_humidity"): {
            vol.Required("enabled", default=True): cv.boolean,
            vol.Optional("temperature_source"): cv.string,  # entity_id or "vmc_default"
            vol.Optional("humidity_source"): cv.string,
        },
        vol.Optional("dew_point"): {
            vol.Required("enabled", default=True): cv.boolean,
            vol.Optional("temperature_source"): cv.string,
            vol.Optional("humidity_source"): cv.string,
        },
        vol.Optional("comfort_index"): {
            vol.Required("enabled", default=True): cv.boolean,
            vol.Optional("temperature_source"): cv.string,
            vol.Optional("humidity_source"): cv.string,
        },
        vol.Optional("dew_point_delta"): {
            vol.Required("enabled", default=True): cv.boolean,
            vol.Optional("temperature_internal_source"): cv.string,
            vol.Optional("temperature_external_source"): cv.string,  # weather.* support
            vol.Optional("humidity_source"): cv.string,
        },
        # Fan-based sensors
        vol.Optional("air_exchange_time"): {
            vol.Required("enabled", default=True): cv.boolean,
            vol.Optional("fan_speed_source"): cv.string,
            vol.Optional("room_volume"): cv.positive_float,
        },
        vol.Optional("daily_air_changes"): {
            vol.Required("enabled", default=True): cv.boolean,
            vol.Optional("fan_speed_source"): cv.string,
            vol.Optional("room_volume"): cv.positive_float,
        },
    },
})
```

---

## Data Mapping

### Temperature Conversione Automatica

```python
# Auto-detect temperatura da unit_of_measurement
temp_f = 68.0  # °F
temp_c = (68.0 - 32) * 5/9 = 20°C

humidity_0_1 = 0.65  # Normalized 0-1
humidity_percent = 0.65 * 100 = 65%

# VMGI data è sempre in decimi
vmgi_temp_tenths = 220  → 22°C
vmgi_humidity_tenths = 650 → 65%
```

### Entity Picker Configuration

```yaml
# Config Flow Step: "external_sensors"

1. Ask: "Abilita sensori evoluti da fonte esterna?"
   → Yes: proceed to entity selection
   → No: skip section

2. For each sensor (AbsoluteHumidity, DewPoint, ...):

   a. "Vuoi usare sensore esterno per temperatura interna?"
      → Dropdown con filter [sensor.*, climate.*]
      → Selected: "sensor.netatmo_indoor_temperature"

   b. "Vuoi usare sensore esterno per umidità?"
      → Dropdown con filter [sensor.*humidity*]
      → Selected: "sensor.netatmo_indoor_humidity"
```

---

## Implementation Plan

### Phase 1: Infrastructure (Effort: 8h)

1. **Create EASCDataProvider class** (4h)
   - Basic data retrieval
   - Unit conversion logic
   - Range validation
   - Fallback mechanism

2. **Add to coordinator** (2h)
   - Initialize EASCDataProvider in `async_config_entry_first_refresh`
   - Add to coordinator.data

3. **Unit tests** (2h)
   - Test conversions (°C↔°F, humidity %)
   - Test fallback scenarios
   - Test missing entity handling

### Phase 2: Refactor Sensors (Effort: 10h)

4. **VmcHeltyAbsoluteHumiditySensor** (2h)
5. **VmcHeltyDewPointSensor** (2h)
6. **VmcHeltyComfortIndexSensor** (2h)
7. **VmcHeltyDewPointDeltaSensor** (2h)
8. **VmcHeltyAirExchangeTimeSensor** (1h)
9. **VmcHeltyDailyAirChangesSensor** (1h)

Per ogni sensore:
- Inject EASCDataProvider
- Replace hardcoded VMGI parsing con `provider.get_temperature()`
- Handle None returns properly
- Aggiorna unit tests per 3 scenari (VMC-only, external-only, fallback)

### Phase 3: Config Flow (Effort: 8h)

10. **Schema e Validation** (2h)
11. **Config Flow Steps** (4h)
12. **Entity Picker UI** (2h)

### Phase 4: Testing (Effort: 12h)

13. **Unit tests** (4h)
    - EASCDataProvider fully tested
    - Each sensor with external sources
    - Conversion edge cases

14. **Integration tests** (4h)
    - Multi-sensor with same source
    - Fallback scenarios
    - Weather entity support

15. **Manual testing** (4h)
    - Config flow UX
    - Real Netatmo/ESPHome entities
    - Graphical diagnostics

### Phase 5: Documentation (Effort: 4h)

16. **User Guide** (2h)
17. **Configuration Examples** (2h)

---

## Configuration Examples

### Scenario 1: Netatmo Esterno + VMC Interno

```yaml
config_entry:
  data: {...existing VMC config...}
  options:
    easc:
      enabled: true
      advanced_sensors:
        absolute_humidity:
          enabled: true
          temperature_source: "sensor.indoor_temp"  # Default VMC
          humidity_source: "sensor.indoor_humidity"  # Default VMC

        dew_point_delta:
          enabled: true
          temperature_internal_source: "sensor.indoor_temp"  # VMC default
          temperature_external_source: "weather.provincia"   # ✅ Netatmo esterno
          humidity_source: "sensor.indoor_humidity"
```

**Result**: DewPointDelta usera temp_ext da weather.provincia instead of VMGI pos 2

### Scenario 2: ESPHome Multi-Sensore

```yaml
options:
  easc:
    enabled: true
    advanced_sensors:
      comfort_index:
        enabled: true
        temperature_source: "sensor.esphome_living_room_temp"
        humidity_source: "sensor.esphome_living_room_humidity"

      dew_point:
        enabled: true
        temperature_source: "sensor.esphome_living_room_temp"
        humidity_source: "sensor.esphome_living_room_humidity"
```

**Benefit**: Più accurato di sensori VMC, update frequency controllabile via ESPHome

### Scenario 3: Fallback Automatico

```yaml
# User configures:
options:
  easc:
    advanced_sensors:
      absolute_humidity:
        temperature_source: "sensor.nonexistent_temp"  # ❌ Non esiste
        humidity_source: "sensor.humidity_ok"  # ✅ Esiste

# Behavior:
# - humidity_source fornisce senza problemi
# - temperature_source non trovato → fallback a VMC VMGI[1]
# - Log: "AbsoluteHumidity: entity_id 'sensor.nonexistent_temp' not found, using VMC default"
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_easc_provider.py
class TestEASCDataProvider:

    def test_get_temperature_from_sensor_celsius(self):
        """Test retrieval of °C from sensor."""

    def test_get_temperature_from_weather_entity(self):
        """Test weather.* entity parsing."""

    def test_temperature_conversion_fahrenheit_to_celsius(self):
        """Test F→C conversion."""

    def test_humidity_conversion_normalized_to_percent(self):
        """Test 0-1 → 0-100 conversion."""

    def test_fallback_to_vmc_on_missing_entity(self):
        """Test fallback when entity_id doesn't exist."""

    def test_fallback_logs_reason(self):
        """Test that fallback reason is logged."""

    def test_range_validation_temperature(self):
        """Test values outside -50 to +50 are rejected."""

    def test_range_validation_humidity(self):
        """Test values outside 0-100 are rejected."""

    def test_cache_performance(self):
        """Test caching reduces repeated state lookups."""
```

### Integration Tests

```python
# tests/test_easc_sensors_integration.py
class TestAbsoluteHumidityWithEASC:

    async def test_absolute_humidity_with_external_temp_humidity(self):
        """Test sensor with both external sources."""

    async def test_absolute_humidity_mixed_sources(self):
        """Test sensor with external temp, VMC humidity."""

    async def test_absolute_humidity_fallback_to_vmc(self):
        """Test sensor falls back to VMC when external fails."""

class TestDewPointDeltaWithWeatherEntity:

    async def test_dew_point_delta_with_weather_integration(self):
        """Test DewPointDelta using weather.* entity for external temp."""

    async def test_dew_point_delta_fallback_from_weather(self):
        """Test fallback when weather entity unavailable."""
```

---

## Success Criteria

✅ **Versione 1.0 del feature EASC considerata completata quando:**

1. **Funzionalità**
   - ✅ 4 sensori temperatura+umidità supportano EASC
   - ✅ 2 sensori fan-based supportano EASC
   - ✅ Fallback automatico funziona per tutti
   - ✅ Unit/range conversions accurate

2. **User Experience**
   - ✅ Config flow intuitivo
   - ✅ Entity picker funzionante
   - ✅ Error messages chiari
   - ✅ Documentation completa con esempi

3. **Quality**
   - ✅ >95% test coverage EASC
   - ✅ Zero warnings mypy/pylint
   - ✅ Pre-commit all pass

4. **Backwards Compatibility**
   - ✅ Zero breaking changes
   - ✅ VMC-only setup funziona esattamente come prima
   - ✅ Auto-migration di configs legacy

---

**Documento versione**: 1.0
**Data creazione**: 2026-03-24
**Status**: 🟡 Draft - Ready for Review
**Target milestone**: v1.4.0 (November 2026)
