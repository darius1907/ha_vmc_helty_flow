#!/usr/bin/env python3
"""Test debug del config flow per verificare che la discovery venga chiamata."""

import asyncio
import logging
from unittest.mock import AsyncMock, patch

# Setup logging
logging.basicConfig(level=logging.INFO)

# Mock degli imports necessari
import sys
sys.path.insert(0, 'custom_components')

from custom_components.vmc_helty_flow.config_flow import VmcHeltyFlowConfigFlow
from custom_components.vmc_helty_flow.const import DOMAIN


async def test_config_flow_scanning():
    """Test che la scanning sia effettivamente chiamata."""
    print("=== TEST CONFIG FLOW SCANNING START ===")
    
    # Create config flow instance
    flow = VmcHeltyFlowConfigFlow()
    flow.hass = AsyncMock()
    
    # Mock discovery function
    with patch('custom_components.vmc_helty_flow.config_flow.discover_vmc_devices_with_progress') as mock_discover:
        mock_discover.return_value = []
        
        # Simula async_step_user
        user_input = {
            "subnet": "192.168.1.0/24",
            "port": 8899,
            "timeout": 5
        }
        
        print(f"Calling async_step_user with: {user_input}")
        result1 = await flow.async_step_user(user_input)
        print(f"Result 1: {result1}")
        
        # Simula async_step_scanning
        if result1.get("step_id") == "scanning":
            print("Calling async_step_scanning with proceed=True")
            result2 = await flow.async_step_scanning({"proceed": True})
            print(f"Result 2: {result2}")
            print(f"Discovery called: {mock_discover.called}")
            print(f"Discovery call count: {mock_discover.call_count}")
            if mock_discover.called:
                print(f"Discovery args: {mock_discover.call_args}")

    print("=== TEST CONFIG FLOW SCANNING END ===")


if __name__ == "__main__":
    asyncio.run(test_config_flow_scanning())