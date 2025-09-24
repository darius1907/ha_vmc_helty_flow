"""Costanti per l'integrazione VMC Helty Flow."""

DOMAIN = "vmc_helty_flow"
DEFAULT_PORT = 5001
DEFAULT_SUBNET = "192.168.1."

# Timeout per le connessioni TCP
TCP_TIMEOUT = 3

# Intervalli di aggiornamento (in secondi)
SENSORS_UPDATE_INTERVAL = 60  # Sensori e stato
NETWORK_INFO_UPDATE_INTERVAL = 900  # Nome e info rete (15 minuti)

# Range di scansione IP
IP_RANGE_START = 1
IP_RANGE_END = 254
IP_NETWORK_PREFIX = 24

# Indici delle parti nel response del dispositivo VMC
PART_INDEX_FAN_SPEED = 1
PART_INDEX_PANEL_LED = 2
PART_INDEX_SENSORS = 4
PART_INDEX_LIGHTS_LEVEL = 11
PART_INDEX_LIGHTS_TIMER = 15

# Valori speciali per la velocità ventola
FAN_SPEED_NIGHT_MODE = 5
FAN_SPEED_HYPERVENTILATION = 6
FAN_SPEED_FREE_COOLING = 7
FAN_SPEED_MAX_NORMAL = 4
FAN_SPEED_OFF = 0

# Numero minimo di parti nel response per essere valido
MIN_RESPONSE_PARTS = 15

# Numero minimo di parti nello status data per calcoli
MIN_STATUS_PARTS = 2

# Percentuali velocità ventola
FAN_PERCENTAGE_STEP = 25  # 100% / 4 velocità = 25% per step

# Mappatura portata d'aria per velocità ventola (M³/h)
AIRFLOW_MAPPING = {
    0: 0,  # Spenta
    1: 10,  # Velocità 1
    2: 17,  # Velocità 2
    3: 26,  # Velocità 3
    4: 37,  # Velocità 4
    5: 7,   # Night Mode
    6: 42,  # Hyperventilation
    7: 26,  # Free Cooling
}

# Validazione lunghezza campi
MAX_DEVICE_NAME_LENGTH = 32
MAX_SSID_LENGTH = 32
MAX_PASSWORD_LENGTH = 32
MIN_PASSWORD_LENGTH = 8

# Per la validazione unique ID
MIN_UNIQUE_ID_LENGTH = 8
MAX_UNIQUE_ID_LENGTH = 24

# Indici multipli per la diagnostica e sensori
DIAG_PANEL_LED_INDEX = 2
DIAG_SENSORS_INDEX = 4
DIAG_LIGHTS_LEVEL_INDEX = 11
DIAG_LIGHTS_TIMER_INDEX = 15

# Per i timer delle luci
DEFAULT_LIGHT_TIMER_SECONDS = 300  # 5 minuti

# Limiti per discovery
MAX_DEVICES_LIMIT = 254

# Soglie comfort per punto di rugiada (°C) - Standard ASHRAE 55-2020
DEW_POINT_VERY_DRY = 10
DEW_POINT_DRY_MIN = 10
DEW_POINT_DRY_MAX = 13
DEW_POINT_COMFORTABLE_MIN = 13
DEW_POINT_COMFORTABLE_MAX = 16
DEW_POINT_GOOD_MIN = 16
DEW_POINT_GOOD_MAX = 18
DEW_POINT_ACCEPTABLE_MIN = 18
DEW_POINT_ACCEPTABLE_MAX = 21
DEW_POINT_HUMID_MIN = 21
DEW_POINT_HUMID_MAX = 24
DEW_POINT_OPPRESSIVE = 24

# Soglie comfort per l'indice di comfort igrometrico
# Temperature (°C)
COMFORT_TEMP_OPTIMAL_MIN = 20
COMFORT_TEMP_OPTIMAL_MAX = 24
COMFORT_TEMP_ACCEPTABLE_MIN = 18
COMFORT_TEMP_ACCEPTABLE_MAX = 26
COMFORT_TEMP_TOLERABLE_MIN = 16
COMFORT_TEMP_TOLERABLE_MAX = 28
COMFORT_TEMP_REFERENCE = 22  # Temperatura di riferimento per il calcolo

# Umidità (%)
COMFORT_HUMIDITY_OPTIMAL_MIN = 40
COMFORT_HUMIDITY_OPTIMAL_MAX = 60
COMFORT_HUMIDITY_ACCEPTABLE_MIN = 30
COMFORT_HUMIDITY_ACCEPTABLE_MAX = 70
COMFORT_HUMIDITY_TOLERABLE_MIN = 25
COMFORT_HUMIDITY_TOLERABLE_MAX = 80
COMFORT_HUMIDITY_REFERENCE = 50  # Umidità di riferimento per il calcolo
COMFORT_HUMIDITY_MAX = 100  # Massimo valore valido per umidità

# Soglie per classificazione indice comfort igrometrico (%)
COMFORT_INDEX_EXCELLENT = 85  # Eccellente
COMFORT_INDEX_GOOD = 70  # Buono
COMFORT_INDEX_ACCEPTABLE = 55  # Accettabile
COMFORT_INDEX_MEDIOCRE = 40  # Mediocre
# Sotto 40% = Scarso

# Soglie per delta punto di rugiada (°C) - Controllo condensazione
DEW_POINT_DELTA_CRITICAL = -2  # Rischio condensazione critico
DEW_POINT_DELTA_HIGH_RISK = 0  # Rischio condensazione alto
DEW_POINT_DELTA_MODERATE_RISK = 2  # Rischio condensazione moderato
DEW_POINT_DELTA_LOW_RISK = 5  # Rischio condensazione basso
DEW_POINT_DELTA_SAFE = 8  # Zona sicura, nessun rischio

# Costanti per il rischio delta punto di rugiada
DEW_POINT_DELTA_RISK_HIGH = "High Risk"
DEW_POINT_DELTA_RISK_MEDIUM = "Medium Risk"
DEW_POINT_DELTA_RISK_LOW = "Low Risk"

# Air Exchange Time Categories (ricambio aria)
AIR_EXCHANGE_EXCELLENT = "Excellent"
AIR_EXCHANGE_GOOD = "Good"
AIR_EXCHANGE_ACCEPTABLE = "Acceptable"
AIR_EXCHANGE_POOR = "Poor"

# Standard room volume (cubic meters) for calculation - configurable default
DEFAULT_ROOM_VOLUME = 150  # m³ (typical 60m² room with 2.5m height)

# Air Exchange Time Thresholds (minutes) - Tempo ideale per ricambio completo aria
AIR_EXCHANGE_TIME_EXCELLENT = 20  # Meno di 20 minuti = eccellente
AIR_EXCHANGE_TIME_GOOD = 30       # 20-30 minuti = buono
AIR_EXCHANGE_TIME_ACCEPTABLE = 60 # 30-60 minuti = accettabile
# Oltre 60 minuti = scarso

# Daily Air Changes Categories and thresholds
DAILY_AIR_CHANGES_EXCELLENT = "Excellent"
DAILY_AIR_CHANGES_GOOD = "Good" 
DAILY_AIR_CHANGES_ADEQUATE = "Adequate"
DAILY_AIR_CHANGES_POOR = "Poor"

# Daily Air Changes Thresholds (changes per 24h) - Standard di ventilazione
DAILY_AIR_CHANGES_EXCELLENT_MIN = 24  # 24+ ricambi/giorno = eccellente (1/ora)
DAILY_AIR_CHANGES_GOOD_MIN = 12      # 12-24 ricambi/giorno = buono (0.5-1/ora)
DAILY_AIR_CHANGES_ADEQUATE_MIN = 6   # 6-12 ricambi/giorno = adeguato (0.25-0.5/ora)
# Meno di 6 ricambi/giorno = scarso

# Configuration constants
CONF_DEVICE_ID = "device_id"

# Comfort Index Levels
COMFORT_LEVEL_EXCELLENT = "Excellent"
COMFORT_LEVEL_GOOD = "Good"
COMFORT_LEVEL_FAIR = "Fair"
COMFORT_LEVEL_POOR = "Poor"
