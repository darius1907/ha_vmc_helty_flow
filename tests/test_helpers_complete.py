"""Test completi per il modulo helpers."""

import asyncio
import socket
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.vmc_helty_flow.helpers import (
    VMCConnectionError,
    VMCProtocolError,
    VMCResponseError,
    VMCTimeoutError,
    tcp_send_command,
)


class TestVMCExceptions:
    """Test per le eccezioni personalizzate."""

    def test_vmc_connection_error(self):
        """Test dell'eccezione VMCConnectionError."""
        error = VMCConnectionError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_vmc_timeout_error(self):
        """Test dell'eccezione VMCTimeoutError."""
        error = VMCTimeoutError("Timeout error")
        assert str(error) == "Timeout error"
        assert isinstance(error, VMCConnectionError)

    def test_vmc_response_error(self):
        """Test dell'eccezione VMCResponseError."""
        error = VMCResponseError("Response error")
        assert str(error) == "Response error"
        assert isinstance(error, Exception)

    def test_vmc_protocol_error(self):
        """Test dell'eccezione VMCProtocolError."""
        error = VMCProtocolError("Protocol error")
        assert str(error) == "Protocol error"
        assert isinstance(error, VMCResponseError)


class TestTcpSendCommand:
    """Test per la funzione tcp_send_command."""

    @pytest.mark.asyncio
    async def test_successful_command(self):
        """Test di un comando TCP con successo."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_reader.read.return_value = b"OK\r\n"

        with patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)):
            result = await tcp_send_command("192.168.1.100", 5001, "TEST")

        assert result == "OK"
        mock_writer.write.assert_called_once_with(b"TEST\r\n")
        mock_writer.drain.assert_called_once()
        mock_writer.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_command_with_existing_crlf(self):
        """Test comando che già termina con CRLF."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_reader.read.return_value = b"OK\r\n"

        with patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)):
            result = await tcp_send_command("192.168.1.100", 5001, "TEST\r\n")

        assert result == "OK"
        mock_writer.write.assert_called_once_with(b"TEST\r\n")

    @pytest.mark.asyncio
    async def test_custom_timeout(self):
        """Test con timeout personalizzato."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_reader.read.return_value = b"OK\r\n"

        with (
            patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)),
            patch("asyncio.wait_for") as mock_wait_for,
        ):
            mock_wait_for.side_effect = [
                (mock_reader, mock_writer),  # open_connection
                b"OK\r\n",  # reader.read
                None,  # writer.wait_closed
            ]

            result = await tcp_send_command("192.168.1.100", 5001, "TEST", timeout=10)

        assert result == "OK"
        # Verifica che wait_for sia stato chiamato almeno due volte con il timeout corretto
        assert mock_wait_for.call_count >= 2
        timeout_calls = [call[1]["timeout"] for call in mock_wait_for.call_args_list]
        assert timeout_calls[0] == 10  # timeout per la connessione
        assert timeout_calls[1] == 10  # timeout per la lettura

    @pytest.mark.asyncio
    async def test_connection_timeout(self):
        """Test timeout durante la connessione."""
        with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
            with pytest.raises(VMCTimeoutError) as exc_info:
                await tcp_send_command("192.168.1.100", 5001, "TEST")

            assert "Timeout durante la connessione" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_connection_refused(self):
        """Test connessione rifiutata."""
        with patch("asyncio.wait_for", side_effect=ConnectionRefusedError):
            with pytest.raises(VMCConnectionError) as exc_info:
                await tcp_send_command("192.168.1.100", 5001, "TEST")

            assert "Connessione rifiutata" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_socket_error(self):
        """Test errore socket."""
        error_msg = "Name resolution failed"
        with patch("asyncio.wait_for", side_effect=socket.gaierror(error_msg)):
            with pytest.raises(VMCConnectionError) as exc_info:
                await tcp_send_command("invalid.host", 5001, "TEST")

            assert "Errore di connessione" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_response_timeout(self):
        """Test timeout durante la lettura della risposta."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()

        with (
            patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)),
            patch("asyncio.wait_for") as mock_wait_for,
        ):
            mock_wait_for.side_effect = [
                (mock_reader, mock_writer),  # Connessione OK
                TimeoutError(),  # Timeout nella lettura
            ]

            with pytest.raises(VMCTimeoutError) as exc_info:
                await tcp_send_command("192.168.1.100", 5001, "TEST")

            assert "Timeout in attesa della risposta" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_unicode_decode_error_fallback(self):
        """Test fallback per errori di decodifica Unicode."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        # Bytes che causano UnicodeDecodeError con UTF-8
        mock_reader.read.return_value = b"\xff\xfe\x41\x00"  # UTF-16 BOM + 'A'

        with patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)):
            result = await tcp_send_command("192.168.1.100", 5001, "TEST")

        # Dovrebbe usare latin-1 come fallback
        assert result is not None

    @pytest.mark.asyncio
    async def test_protocol_error_response(self):
        """Test risposta che contiene un errore di protocollo."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_reader.read.return_value = b"ERROR: Invalid command\r\n"

        with patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)):
            with pytest.raises(VMCConnectionError) as exc_info:
                await tcp_send_command("192.168.1.100", 5001, "INVALID")

            # L'errore di protocollo viene catturato e rilanciato come VMCConnectionError
            assert "Errore durante la comunicazione" in str(exc_info.value)
            assert "Errore di protocollo" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_response(self):
        """Test risposta vuota."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_reader.read.return_value = b""

        with patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)):
            result = await tcp_send_command("192.168.1.100", 5001, "TEST")

        assert result == ""

    @pytest.mark.asyncio
    async def test_writer_cleanup_on_success(self):
        """Test che il writer venga sempre chiuso in caso di successo."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_reader.read.return_value = b"OK\r\n"

        with patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)):
            await tcp_send_command("192.168.1.100", 5001, "TEST")

        mock_writer.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_writer_cleanup_on_error(self):
        """Test che il writer venga sempre chiuso anche in caso di errore."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()

        with (
            patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)),
            patch("asyncio.wait_for") as mock_wait_for,
        ):
            mock_wait_for.side_effect = [
                (mock_reader, mock_writer),  # Connessione OK
                TimeoutError(),  # Errore nella lettura
            ]

            with pytest.raises(VMCTimeoutError):
                await tcp_send_command("192.168.1.100", 5001, "TEST")

        mock_writer.close.assert_called_once()
