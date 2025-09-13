import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import config_flow

@pytest.fixture(autouse=True)
def cleanup_devices_file():
    """Fixture che pulisce automaticamente il file devices.json dopo ogni test."""
    yield  # Esegue il test
    # Non è più necessaria la pulizia del file devices.json
    # poiché ora usiamo il sistema di storage di Home Assistant

@pytest.mark.asyncio
async def test_async_step_user_no_devices():
    flow = config_flow.VmcHeltyFlowConfigFlow()
    flow.hass = MagicMock()

    # Mock del sistema di storage che restituisce lista vuota
    mock_store = AsyncMock()
    mock_store.async_load.return_value = None

    with patch.object(flow, '_get_store', return_value=mock_store):
        result = await flow.async_step_user()
        assert result['type'] == 'form'
        assert result['step_id'] == 'user'
        schema_keys = result['data_schema'].schema.keys()
        # La UI mostra subito i campi di configurazione se non ci sono dispositivi
        assert 'subnet' in schema_keys
        assert 'port' in schema_keys
        assert 'timeout' in schema_keys

    # Simula inserimento parametri validi
    with patch.object(flow, '_get_store', return_value=mock_store):
        result = await flow.async_step_user({'subnet': '192.168.1.0/24', 'port': 5001, 'timeout': 10})
        assert result['type'] == 'form'
        assert result['step_id'] == 'user' or result['step_id'] == 'discovery'

@pytest.mark.asyncio
async def test_async_step_user_with_devices_confirm_false():
    flow = config_flow.VmcHeltyFlowConfigFlow()
    flow.hass = MagicMock()

    devices = [{'ip': '192.168.1.10', 'name': 'VMC Helty 10'}]

    # Mock del sistema di storage che restituisce dispositivi esistenti
    mock_store = AsyncMock()
    mock_store.async_load.return_value = {"devices": devices}

    with patch.object(flow, '_get_store', return_value=mock_store):
        # Primo step: mostra conferma
        result = await flow.async_step_user()
        assert result['type'] == 'form'
        assert result['step_id'] == 'user'
        schema_keys = result['data_schema'].schema.keys()
        assert 'confirm' in schema_keys

        # Secondo step: utente rifiuta la scansione
        result = await flow.async_step_user({'confirm': False})
        assert result['type'] == 'form'
        assert result['step_id'] == 'user'
        # Non viene mostrato uno schema, ma solo la lista dispositivi
        assert 'help' in result['description_placeholders']
        assert 'Dispositivi configurati' in result['description_placeholders']['help']
        assert result.get('data_schema') is None

@pytest.mark.asyncio
async def test_async_step_discovery_devices_found():
    flow = config_flow.VmcHeltyFlowConfigFlow()
    flow.hass = MagicMock()
    flow.subnet = '192.168.1.0/24'
    flow.port = 5001
    flow.timeout = 10

    devices = [
        {'ip': '192.168.1.10', 'name': 'VMC Helty 10'},
        {'ip': '192.168.1.11', 'name': 'VMC Helty 11'}
    ]

    # Mock del sistema di storage
    mock_store = AsyncMock()
    mock_store.async_save = AsyncMock()

    async def mock_discover(*args, **kwargs):
        return devices

    with patch('config_flow.discover_vmc_devices', new=mock_discover), \
         patch.object(flow, '_get_store', return_value=mock_store):
        result = await flow.async_step_discovery()
        assert result['type'] == 'form'
        # Verifica che il form abbia i campi di selezione dispositivi
        schema_keys = result['data_schema'].schema.keys()
        assert 'selected_devices' in schema_keys
        assert mock_store.async_save.called
        assert 'Scansione completata' in result['description_placeholders']['help']

@pytest.mark.asyncio
async def test_async_step_discovery_no_devices():
    flow = config_flow.VmcHeltyFlowConfigFlow()
    flow.hass = MagicMock()
    flow.subnet = '192.168.1.0/24'
    flow.port = 5001
    flow.timeout = 10

    # Mock del sistema di storage
    mock_store = AsyncMock()
    mock_store.async_save = AsyncMock()

    async def mock_discover(*args, **kwargs):
        return []

    with patch('config_flow.discover_vmc_devices', new=mock_discover), \
         patch.object(flow, '_get_store', return_value=mock_store):
        result = await flow.async_step_discovery()
        assert result['type'] == 'form'
        assert result['step_id'] == 'user'
        # selected_devices non deve essere presente se non ci sono dispositivi
        if result.get('data_schema'):
            schema_keys = result['data_schema'].schema.keys()
            assert 'selected_devices' not in schema_keys
        assert 'Errore nella scansione' in result['description_placeholders']['help']

@pytest.mark.asyncio
async def test_async_step_discovery_device_selection():
    """Test la selezione dei dispositivi e la creazione delle config entry."""
    flow = config_flow.VmcHeltyFlowConfigFlow()
    flow.hass = MagicMock()
    flow.subnet = '192.168.1.0/24'
    flow.port = 5001
    flow.timeout = 10

    # Simula dispositivi già scoperti
    flow.discovered_devices = [
        {'ip': '192.168.1.10', 'name': 'VMC Helty 10', 'model': 'VMC Flow', 'manufacturer': 'Helty'},
        {'ip': '192.168.1.11', 'name': 'VMC Helty 11', 'model': 'VMC Flow', 'manufacturer': 'Helty'}
    ]

    # Mock del sistema di storage
    mock_store = AsyncMock()
    mock_store.async_save = AsyncMock()

    # Mock delle funzioni di config entries
    flow._async_current_entries = MagicMock(return_value=[])
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_create_entry = MagicMock(return_value={'type': 'create_entry'})

    with patch.object(flow, '_get_store', return_value=mock_store):
        # Simula la selezione di un dispositivo
        user_input = {'selected_devices': ['192.168.1.10']}
        result = await flow.async_step_discovery(user_input)

        # Verifica che sia stata chiamata la creazione della config entry
        flow.async_create_entry.assert_called_once()
        call_args = flow.async_create_entry.call_args

        assert call_args[1]['title'] == 'VMC Helty 10'
        assert call_args[1]['data']['ip'] == '192.168.1.10'
        assert call_args[1]['data']['name'] == 'VMC Helty 10'
        assert mock_store.async_save.called

@pytest.mark.asyncio
async def test_async_step_discovery_all_devices_configured():
    """Test quando tutti i dispositivi selezionati sono già configurati."""
    flow = config_flow.VmcHeltyFlowConfigFlow()
    flow.hass = MagicMock()

    # Simula dispositivi già scoperti
    flow.discovered_devices = [
        {'ip': '192.168.1.10', 'name': 'VMC Helty 10', 'model': 'VMC Flow', 'manufacturer': 'Helty'}
    ]

    # Mock del sistema di storage
    mock_store = AsyncMock()
    mock_store.async_save = AsyncMock()

    # Simula che il dispositivo sia già configurato
    existing_entry = MagicMock()
    existing_entry.data = {'ip': '192.168.1.10'}
    flow._async_current_entries = MagicMock(return_value=[existing_entry])
    flow.async_abort = MagicMock(return_value={'type': 'abort'})

    with patch.object(flow, '_get_store', return_value=mock_store):
        user_input = {'selected_devices': ['192.168.1.10']}
        result = await flow.async_step_discovery(user_input)

        # Verifica che sia stato chiamato l'abort
        flow.async_abort.assert_called_with(reason="all_devices_already_configured")

@pytest.mark.asyncio
async def test_async_step_user_validation_errors():
    """Test gli errori di validazione nell'input utente."""
    flow = config_flow.VmcHeltyFlowConfigFlow()
    flow.hass = MagicMock()

    # Mock del sistema di storage che restituisce lista vuota
    mock_store = AsyncMock()
    mock_store.async_load.return_value = None

    with patch.object(flow, '_get_store', return_value=mock_store):
        # Test subnet non valida
        result = await flow.async_step_user({
            'subnet': 'invalid_subnet',
            'port': 5001,
            'timeout': 10
        })
        assert result['type'] == 'form'
        assert 'subnet_non_valida' in result['errors'].values()

        # Test porta non valida
        result = await flow.async_step_user({
            'subnet': '192.168.1.0/24',
            'port': 99999,
            'timeout': 10
        })
        assert result['type'] == 'form'
        assert 'porta_non_valida' in result['errors'].values()

        # Test timeout non valido
        result = await flow.async_step_user({
            'subnet': '192.168.1.0/24',
            'port': 5001,
            'timeout': 100
        })
        assert result['type'] == 'form'
        assert 'timeout_non_valido' in result['errors'].values()

@pytest.mark.asyncio
async def test_async_step_import():
    """Test del metodo async_step_import."""
    flow = config_flow.VmcHeltyFlowConfigFlow()
    flow.hass = MagicMock()

    # Mock del sistema di storage
    mock_store = AsyncMock()
    mock_store.async_load.return_value = None

    with patch.object(flow, '_get_store', return_value=mock_store):
        import_info = {'subnet': '192.168.1.0/24', 'port': 5001, 'timeout': 10}
        result = await flow.async_step_import(import_info)

        # Dovrebbe comportarsi come async_step_user
        assert result['type'] == 'form'

@pytest.mark.asyncio
async def test_options_flow():
    """Test dell'Options Flow."""
    # Mock config entry
    mock_entry = MagicMock()
    mock_entry.options = {
        'scan_interval': 120,
        'timeout': 15,
        'retry_attempts': 5
    }

    options_flow = config_flow.VmcHeltyOptionsFlowHandler(mock_entry)

    # Test step init senza input utente (mostra il form)
    result = await options_flow.async_step_init()
    assert result['type'] == 'form'
    assert result['step_id'] == 'init'
    schema_keys = result['data_schema'].schema.keys()
    assert 'scan_interval' in [str(key) for key in schema_keys]
    assert 'timeout' in [str(key) for key in schema_keys]
    assert 'retry_attempts' in [str(key) for key in schema_keys]

    # Test step init con input utente (crea entry)
    options_flow.async_create_entry = MagicMock(return_value={'type': 'create_entry'})
    user_input = {
        'scan_interval': 180,
        'timeout': 20,
        'retry_attempts': 3
    }
    result = await options_flow.async_step_init(user_input)
    options_flow.async_create_entry.assert_called_once_with(title="", data=user_input)

def test_validate_subnet():
    """Test della funzione di validazione subnet."""
    flow = config_flow.VmcHeltyFlowConfigFlow()

    # Test subnet valide in formato CIDR
    assert flow._validate_subnet('192.168.1.0/24') is True
    assert flow._validate_subnet('10.0.0.0/8') is True
    assert flow._validate_subnet('172.16.0.0/16') is True
    assert flow._validate_subnet('127.0.0.0/8') is True  # localhost

    # Test subnet non valide
    assert flow._validate_subnet('192.168.1.') is False  # vecchio formato
    assert flow._validate_subnet('192.168.1') is False
    assert flow._validate_subnet('invalid') is False
    assert flow._validate_subnet('192.168.1.1') is False  # IP singolo senza CIDR
    assert flow._validate_subnet('300.300.300.0/24') is False  # IP non valido
    assert flow._validate_subnet('192.168.1.0/35') is False  # CIDR non valido

def test_count_ips_in_subnet():
    """Test della funzione di conteggio IP nella subnet."""
    flow = config_flow.VmcHeltyFlowConfigFlow()

    # Test conteggio corretto per diverse subnet CIDR
    assert flow._count_ips_in_subnet('192.168.1.0/24') == 254  # 256 - 2 (network + broadcast)
    assert flow._count_ips_in_subnet('10.0.0.0/24') == 254
    assert flow._count_ips_in_subnet('192.168.1.0/28') == 14   # 16 - 2
    assert flow._count_ips_in_subnet('192.168.1.0/30') == 2    # 4 - 2

    # Test input non validi
    assert flow._count_ips_in_subnet('192.168.1.') == 0  # vecchio formato
    assert flow._count_ips_in_subnet('invalid') == 0

def test_parse_subnet_for_discovery():
    """Test della funzione di parsing subnet per discovery."""
    flow = config_flow.VmcHeltyFlowConfigFlow()

    # Test conversione da CIDR a formato discovery
    assert flow._parse_subnet_for_discovery('192.168.1.0/24') == '192.168.1.'
    assert flow._parse_subnet_for_discovery('10.0.0.0/24') == '10.0.0.'
    assert flow._parse_subnet_for_discovery('172.16.5.0/24') == '172.16.5.'

    # Test con subnet non valide (dovrebbe restituire default)
    assert flow._parse_subnet_for_discovery('invalid') == '192.168.1.'
