#!/usr/bin/env python3
"""Script per sostituire i magic numbers con costanti."""

import re
from pathlib import Path

# Mappatura dei magic numbers alle costanti
MAGIC_NUMBER_REPLACEMENTS = {
    # Fan speed special modes
    "fan_speed == 5": "fan_speed == FAN_SPEED_NIGHT_MODE",
    "fan_speed == 6": "fan_speed == FAN_SPEED_HYPERVENTILATION", 
    "fan_speed == 7": "fan_speed == FAN_SPEED_FREE_COOLING",
    "fan_speed <= 4": "fan_speed <= FAN_SPEED_MAX_NORMAL",
    
    # Protocol indices  
    "len(parts) > 2": "len(parts) > PART_INDEX_PANEL_LED",
    "parts[2]": "parts[PART_INDEX_PANEL_LED]",
    "len(parts) > 4": "len(parts) > PART_INDEX_SENSORS", 
    "parts[4]": "parts[PART_INDEX_SENSORS]",
    "len(parts) > 11": "len(parts) > PART_INDEX_LIGHTS_LEVEL",
    "parts[11]": "parts[PART_INDEX_LIGHTS_LEVEL]",
    "len(parts) > 15": "len(parts) > PART_INDEX_LIGHTS_TIMER",
    "parts[15]": "parts[PART_INDEX_LIGHTS_TIMER]",
    "len(parts) < 15": "len(parts) < MIN_RESPONSE_PARTS",
    
    # Validation limits
    "len(name) > 32": "len(name) > MAX_DEVICE_NAME_LENGTH",
    "len(ssid) > 32": "len(ssid) > MAX_SSID_LENGTH",
    "len(password) < 8": "len(password) < MIN_PASSWORD_LENGTH",
    "len(password) > 32": "len(password) > MAX_PASSWORD_LENGTH",
    
    # Percentage calculations
    "return 25": "return FAN_PERCENTAGE_STEP",
    "* 25": "* FAN_PERCENTAGE_STEP",
    "/ 25": "/ FAN_PERCENTAGE_STEP",
    
    # Fan speed range
    "min(4,": "min(FAN_SPEED_MAX_NORMAL,",
    "max(1,": "max(1,",  # This one is OK as is
}

# Import statements to add to each file
IMPORT_ADDITIONS = {
    "device_action.py": [
        "FAN_SPEED_MAX_NORMAL",
        "MAX_DEVICE_NAME_LENGTH", 
        "MAX_PASSWORD_LENGTH",
        "MAX_SSID_LENGTH",
        "MIN_PASSWORD_LENGTH",
    ],
    "diagnostics.py": [
        "PART_INDEX_LIGHTS_LEVEL",
        "PART_INDEX_LIGHTS_TIMER", 
        "PART_INDEX_PANEL_LED",
        "PART_INDEX_SENSORS",
    ],
    "fan.py": [
        "FAN_PERCENTAGE_STEP",
        "FAN_SPEED_FREE_COOLING",
        "FAN_SPEED_HYPERVENTILATION",
        "FAN_SPEED_MAX_NORMAL", 
        "FAN_SPEED_NIGHT_MODE",
        "PART_INDEX_PANEL_LED",
        "PART_INDEX_SENSORS",
    ],
    "light.py": [
        "PART_INDEX_LIGHTS_LEVEL",
        "PART_INDEX_LIGHTS_TIMER",
    ],
    "sensor.py": [
        "MIN_RESPONSE_PARTS",
    ],
    "switch.py": [
        "PART_INDEX_PANEL_LED",
        "PART_INDEX_SENSORS",
    ],
}

def fix_imports(file_path: Path, constants: list[str]) -> str:
    """Aggiunge le costanti agli import."""
    content = file_path.read_text()
    
    # Trova l'import di const
    import_pattern = r'from \.const import DOMAIN'
    if re.search(import_pattern, content):
        # Costruisci il nuovo import
        all_imports = ["DOMAIN"] + constants
        new_import = f"from .const import (\n    " + ",\n    ".join(all_imports) + ",\n)"
        content = re.sub(import_pattern, new_import, content)
    
    return content

def fix_magic_numbers(content: str) -> str:
    """Sostituisce i magic numbers con le costanti."""
    for magic, constant in MAGIC_NUMBER_REPLACEMENTS.items():
        content = content.replace(magic, constant)
    
    return content

def main():
    """Funzione principale."""
    source_dir = Path("custom_components/vmc_helty_flow")
    
    for file_name, constants in IMPORT_ADDITIONS.items():
        file_path = source_dir / file_name
        if not file_path.exists():
            print(f"⚠️  File non trovato: {file_path}")
            continue
            
        print(f"🔧 Fixing {file_name}...")
        
        # Fix imports
        content = fix_imports(file_path, constants)
        
        # Fix magic numbers
        content = fix_magic_numbers(content)
        
        # Salva il file
        file_path.write_text(content)
        print(f"✅ Completato: {file_name}")

if __name__ == "__main__":
    main()