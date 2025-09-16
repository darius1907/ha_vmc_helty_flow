"""Test del progress indicator durante discovery."""

from unittest.mock import patch

import pytest

from custom_components.vmc_helty_flow.helpers import discover_vmc_devices_with_progress


class TestProgressIndicator:
    """Test per il progress indicator."""

    @pytest.mark.asyncio
    async def test_discover_vmc_devices_with_progress_callback(self):
        """Test del callback di progresso durante la discovery."""
        progress_updates = []
        interrupt_called = False

        def progress_callback(info):
            progress_updates.append(info)

        def interrupt_check():
            return interrupt_called

        # Mock della funzione get_device_info per simulare dispositivi
        with patch(
            "custom_components.vmc_helty_flow.helpers.get_device_info"
        ) as mock_get_info:
            mock_get_info.return_value = None  # Nessun dispositivo trovato

            # Esegui discovery con progress
            devices = await discover_vmc_devices_with_progress(
                subnet="192.168.1",
                port=5001,
                timeout=1,
                progress_callback=progress_callback,
                interrupt_check=interrupt_check,
            )

            # Verifica che il callback sia stato chiamato
            assert len(progress_updates) > 0

            # Verifica la struttura dei dati di progresso
            first_update = progress_updates[0]
            assert "current_ip" in first_update
            assert "progress" in first_update
            assert "devices_found" in first_update
            assert "scanned" in first_update
            assert "total" in first_update

            # Verifica che il progresso aumenti
            last_update = progress_updates[-1]
            assert last_update["progress"] >= first_update["progress"]
            assert last_update["scanned"] >= first_update["scanned"]

    @pytest.mark.asyncio
    async def test_discover_vmc_devices_with_interrupt(self):
        """Test dell'interruzione della discovery."""
        progress_updates = []
        interrupt_after = 5  # Interrompi dopo 5 aggiornamenti

        def progress_callback(info):
            progress_updates.append(info)

        def interrupt_check():
            return len(progress_updates) >= interrupt_after

        # Mock della funzione get_device_info
        with patch(
            "custom_components.vmc_helty_flow.helpers.get_device_info"
        ) as mock_get_info:
            mock_get_info.return_value = None

            # Esegui discovery con interruzione
            devices = await discover_vmc_devices_with_progress(
                subnet="192.168.1",
                port=5001,
                timeout=1,
                progress_callback=progress_callback,
                interrupt_check=interrupt_check,
            )

            # Verifica che la scansione sia stata interrotta
            assert len(progress_updates) >= interrupt_after

            # Verifica che non abbia scansionato tutti gli IP
            last_update = progress_updates[-1]
            assert last_update["progress"] < 100

    @pytest.mark.asyncio
    async def test_discover_vmc_devices_with_found_devices(self):
        """Test del progress indicator con dispositivi trovati."""
        progress_updates = []
        found_devices = []

        def progress_callback(info):
            progress_updates.append(info)
            # Tiene traccia dei dispositivi trovati nel progresso
            found_devices.append(info["devices_found"])

        # Mock di un dispositivo trovato
        mock_device = {
            "ip": "192.168.1.100",
            "name": "VMC Test",
            "model": "VMC Flow",
            "manufacturer": "Helty",
            "available": True,
        }

        with patch(
            "custom_components.vmc_helty_flow.helpers.get_device_info"
        ) as mock_get_info:
            # Simula un dispositivo trovato al 50° IP
            def side_effect(ip, _port, _timeout):
                if ip == "192.168.1.50":
                    return mock_device
                return None

            mock_get_info.side_effect = side_effect

            # Esegui discovery
            devices = await discover_vmc_devices_with_progress(
                subnet="192.168.1",
                port=5001,
                timeout=1,
                progress_callback=progress_callback,
                interrupt_check=None,
            )

            # Verifica che il dispositivo sia stato trovato
            assert len(devices) == 1
            assert devices[0]["ip"] == "192.168.1.100"

            # Verifica che il contatore dei dispositivi nel progresso aumenti
            max_found = max(found_devices) if found_devices else 0
            assert max_found >= 1

    @pytest.mark.asyncio
    async def test_discover_without_callbacks(self):
        """Test della discovery senza callback (compatibilità)."""
        with patch(
            "custom_components.vmc_helty_flow.helpers.get_device_info"
        ) as mock_get_info:
            mock_get_info.return_value = None

            # Esegui discovery senza callback
            devices = await discover_vmc_devices_with_progress(
                subnet="192.168.1",
                port=5001,
                timeout=1,
                progress_callback=None,
                interrupt_check=None,
            )

            # Deve funzionare anche senza callback
            assert isinstance(devices, list)
