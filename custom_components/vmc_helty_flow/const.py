"""Costanti per l'integrazione VMC Helty Flow."""

DOMAIN = "vmc_helty_flow"
DEFAULT_PORT = 5001
DEFAULT_SUBNET = "192.168.1."

# Timeout per le connessioni TCP
TCP_TIMEOUT = 3

# Range di scansione IP
IP_RANGE_START = 1
IP_RANGE_END = 254

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

# Numero minimo di parti nel response per essere valido
MIN_RESPONSE_PARTS = 15

# Percentuali velocità ventola
FAN_PERCENTAGE_STEP = 25  # 100% / 4 velocità = 25% per step

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
