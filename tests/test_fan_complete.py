"""Test per il modulo fan con maggiore copertura."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.components.fan import FanEntity

from custom_components.vmc_helty_flow.fan import VmcHeltyFan, async_setup_entry


class TestVmcHeltyFan:
    """Test per la classe VmcHeltyFan."""

    def setup_method(self):
        """Set up test fixtures."""
        self.coordinator = Mock()
        self.coordinator.name_slug = "testvmc"
        self.coordinator.data = {}
        self.coordinator.async_request_refresh = AsyncMock()

    def test_init(self):
        """Test inizializzazione del fan."""
        fan = VmcHeltyFan(self.coordinator)

        assert fan.coordinator == self.coordinator
        assert fan._attr_unique_id == "vmc_helty_testvmc"
        assert fan._attr_name == f"VMC {self.coordinator.name}"
        assert fan._attr_speed_count == 4
        assert fan._attr_supported_features == 1  # FanEntityFeature.SET_SPEED
        assert isinstance(fan, FanEntity)

    def test_is_on_no_data(self):
        """Test is_on quando non ci sono dati."""
        self.coordinator.data = None
        fan = VmcHeltyFan(self.coordinator)

        assert fan.is_on is False

    def test_is_on_empty_data(self):
        """Test is_on con dati vuoti."""
        self.coordinator.data = {}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.is_on is False

    def test_is_on_invalid_status(self):
        """Test is_on con status non valido."""
        self.coordinator.data = {"status": "INVALID_STATUS"}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.is_on is False

    def test_is_on_valid_status_off(self):
        """Test is_on con status valido ma velocità 0."""
        self.coordinator.data = {"status": "VMGO,0,1,2,3,4,5"}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.is_on is False

    def test_is_on_valid_status_on(self):
        """Test is_on con status valido e velocità > 0."""
        self.coordinator.data = {"status": "VMGO,2,1,2,3,4,5"}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.is_on is True

    def test_percentage_no_data(self):
        """Test percentage quando non ci sono dati."""
        self.coordinator.data = None
        fan = VmcHeltyFan(self.coordinator)

        assert fan.percentage == 0

    def test_percentage_empty_data(self):
        """Test percentage con dati vuoti."""
        self.coordinator.data = {}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.percentage == 0

    def test_percentage_invalid_status(self):
        """Test percentage con status non valido."""
        self.coordinator.data = {"status": "INVALID"}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.percentage == 0

    def test_percentage_valid_status_speed_0(self):
        """Test percentage con velocità 0."""
        self.coordinator.data = {"status": "VMGO,0,1,2,3,4,5"}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.percentage == 0

    def test_percentage_valid_status_speed_1(self):
        """Test percentage con velocità 1."""
        self.coordinator.data = {"status": "VMGO,1,1,2,3,4,5"}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.percentage == 25

    def test_percentage_valid_status_speed_2(self):
        """Test percentage con velocità 2."""
        self.coordinator.data = {"status": "VMGO,2,1,2,3,4,5"}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.percentage == 50

    def test_percentage_valid_status_speed_3(self):
        """Test percentage con velocità 3."""
        self.coordinator.data = {"status": "VMGO,3,1,2,3,4,5"}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.percentage == 75

    def test_percentage_valid_status_speed_4(self):
        """Test percentage con velocità 4."""
        self.coordinator.data = {"status": "VMGO,4,1,2,3,4,5"}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.percentage == 100

    def test_percentage_valid_status_speed_invalid(self):
        """Test percentage con velocità non valida."""
        self.coordinator.data = {"status": "VMGO,invalid,1,2,3,4,5"}
        fan = VmcHeltyFan(self.coordinator)

        assert fan.percentage == 0

    @pytest.mark.asyncio
    async def test_async_turn_on_no_percentage(self):
        """Test turn_on senza percentuale specificata."""
        fan = VmcHeltyFan(self.coordinator)

        with patch("custom_components.vmc_helty_flow.fan.tcp_send_command") as mock_cmd:
            mock_cmd.return_value = "OK"
            await fan.async_turn_on()

        mock_cmd.assert_called_once_with(self.coordinator.ip, 5001, "VMWH0000001")

    @pytest.mark.asyncio
    async def test_async_turn_on_with_percentage_25(self):
        """Test turn_on con percentuale 25%."""
        fan = VmcHeltyFan(self.coordinator)

        with patch("custom_components.vmc_helty_flow.fan.tcp_send_command") as mock_cmd:
            mock_cmd.return_value = "OK"
            await fan.async_turn_on(percentage=25)

        mock_cmd.assert_called_once_with(self.coordinator.ip, 5001, "VMWH0000001")

    @pytest.mark.asyncio
    async def test_async_turn_on_with_percentage_50(self):
        """Test turn_on con percentuale 50%."""
        fan = VmcHeltyFan(self.coordinator)

        with patch("custom_components.vmc_helty_flow.fan.tcp_send_command") as mock_cmd:
            mock_cmd.return_value = "OK"
            await fan.async_turn_on(percentage=50)

        mock_cmd.assert_called_once_with(self.coordinator.ip, 5001, "VMWH0000002")

    @pytest.mark.asyncio
    async def test_async_turn_on_with_percentage_75(self):
        """Test turn_on con percentuale 75%."""
        fan = VmcHeltyFan(self.coordinator)

        with patch("custom_components.vmc_helty_flow.fan.tcp_send_command") as mock_cmd:
            mock_cmd.return_value = "OK"
            await fan.async_turn_on(percentage=75)

        mock_cmd.assert_called_once_with(self.coordinator.ip, 5001, "VMWH0000003")

    @pytest.mark.asyncio
    async def test_async_turn_on_with_percentage_100(self):
        """Test turn_on con percentuale 100%."""
        fan = VmcHeltyFan(self.coordinator)

        with patch("custom_components.vmc_helty_flow.fan.tcp_send_command") as mock_cmd:
            mock_cmd.return_value = "OK"
            await fan.async_turn_on(percentage=100)

        mock_cmd.assert_called_once_with(self.coordinator.ip, 5001, "VMWH0000004")

    @pytest.mark.asyncio
    async def test_async_turn_off(self):
        """Test turn_off."""
        fan = VmcHeltyFan(self.coordinator)

        with patch("custom_components.vmc_helty_flow.fan.tcp_send_command") as mock_cmd:
            mock_cmd.return_value = "OK"
            await fan.async_turn_off()

        mock_cmd.assert_called_once_with(self.coordinator.ip, 5001, "VMWH0000000")

    @pytest.mark.asyncio
    async def test_async_set_percentage_0(self):
        """Test set_percentage con 0%."""
        fan = VmcHeltyFan(self.coordinator)

        with patch("custom_components.vmc_helty_flow.fan.tcp_send_command") as mock_cmd:
            mock_cmd.return_value = "OK"
            await fan.async_set_percentage(0)

        mock_cmd.assert_called_once_with(self.coordinator.ip, 5001, "VMWH0000000")

    @pytest.mark.asyncio
    async def test_async_set_percentage_25(self):
        """Test set_percentage con 25%."""
        fan = VmcHeltyFan(self.coordinator)

        with patch("custom_components.vmc_helty_flow.fan.tcp_send_command") as mock_cmd:
            mock_cmd.return_value = "OK"
            await fan.async_set_percentage(25)

        mock_cmd.assert_called_once_with(self.coordinator.ip, 5001, "VMWH0000001")

    @pytest.mark.asyncio
    async def test_async_set_percentage_intermediate(self):
        """Test set_percentage con valore intermedio (30% -> velocità 1)."""
        fan = VmcHeltyFan(self.coordinator)

        with patch("custom_components.vmc_helty_flow.fan.tcp_send_command") as mock_cmd:
            mock_cmd.return_value = "OK"
            await fan.async_set_percentage(30)

        # 30% dovrebbe essere mappato alla velocità 1 (max(1, min(4, round(30 / 25))))
        mock_cmd.assert_called_once_with(self.coordinator.ip, 5001, "VMWH0000001")


class TestAsyncSetupEntry:
    """Test per la funzione async_setup_entry."""

    @pytest.mark.asyncio
    async def test_async_setup_entry(self):
        """Test setup entry."""
        # Mock degli oggetti Home Assistant
        hass = Mock()
        config_entry = Mock()
        config_entry.entry_id = "test_entry"
        async_add_entities = Mock()

        # Mock del coordinator
        coordinator = Mock()
        coordinator.ip = "192.168.1.100"
        coordinator.name = "Test VMC"

        # Simula i dati di hass
        hass.data = {"vmc_helty_flow": {"test_entry": coordinator}}

        await async_setup_entry(hass, config_entry, async_add_entities)

        # Verifica che async_add_entities sia stato chiamato
        async_add_entities.assert_called_once()

        # Verifica che sia stata aggiunta un'entità VmcHeltyFan
        added_entities = async_add_entities.call_args[0][0]
        assert len(added_entities) == 1
        assert isinstance(added_entities[0], VmcHeltyFan)
        assert added_entities[0].coordinator == coordinator
