import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import config_flow

@pytest.mark.asyncio
async def test_async_step_user_no_devices():
    flow = config_flow.VmcHeltyFlowConfigFlow()
    # Simula prima la richiesta di conferma
    with patch('helpers.load_devices', return_value=[]):
        result = await flow.async_step_user()
        assert result['type'] == 'form'
        assert result['step_id'] == 'user'
        assert 'confirm' in result['data_schema'].schema
    # Simula la conferma dell'utente
    with patch('helpers.load_devices', return_value=[]):
        result = await flow.async_step_user({'confirm': True})
        assert result['type'] == 'form'
        assert result['step_id'] == 'user'
        assert 'subnet' in result['data_schema'].schema
        assert 'port' in result['data_schema'].schema

@pytest.mark.asyncio
async def test_async_step_user_with_devices_confirm_false():
    flow = config_flow.VmcHeltyFlowConfigFlow()
    devices = [{'ip': '192.168.1.10', 'name': 'VMC Helty 10'}]
    with patch('helpers.load_devices', return_value=devices):
        result = await flow.async_step_user({'confirm': False})
        assert result['type'] == 'form'
        assert result['step_id'] == 'user'
        assert result.get('errors', {}).get('base') == 'scan_annullata'
        assert 'Dispositivi configurati' in result['description_placeholders']['help']

@pytest.mark.asyncio
async def test_async_step_discovery_devices_found():
    flow = config_flow.VmcHeltyFlowConfigFlow()
    flow.subnet = '192.168.1.'
    flow.port = 5001
    devices = [
        {'ip': '192.168.1.10', 'name': 'VMC Helty 10'},
        {'ip': '192.168.1.11', 'name': 'VMC Helty 11'}
    ]
    with patch('helpers.discover_vmc_devices', return_value=devices) as mock_discover, \
         patch('helpers.save_devices', MagicMock()) as mock_save:
        result = await flow.async_step_discovery()
        assert result['type'] == 'form'
        assert result['step_id'] == 'discovery'
        assert 'selected_devices' in result['data_schema'].schema
        assert mock_save.called
        assert 'Scansione completata' in result['description_placeholders']['help']

@pytest.mark.asyncio
async def test_async_step_discovery_no_devices():
    flow = config_flow.VmcHeltyFlowConfigFlow()
    flow.subnet = '192.168.1.'
    flow.port = 5001
    with patch('helpers.discover_vmc_devices', return_value=[]), \
         patch('helpers.save_devices', MagicMock()):
        result = await flow.async_step_discovery()
        assert result['type'] == 'form'
        assert result['step_id'] == 'discovery'
        # errors può essere vuoto, quindi controllo che non ci siano dispositivi
        assert not result.get('data_schema').schema['selected_devices'].options
        assert 'Scansione completata' in result['description_placeholders']['help']
