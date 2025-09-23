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
