import unittest
from unittest.mock import MagicMock, patch
from ws_client import WebSocketManager


class TestWebSocketManager(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()

    def test_connect_with_handshake_payload(self):
        manager = WebSocketManager(self.logger)
        payload = {"action": "handshake", "client_type": "test"}
        manager.connect("ws://test", handshake_payload=payload)
        self.assertEqual(manager.handshake_payload, payload)

    def test_connect_without_handshake_payload(self):
        manager = WebSocketManager(self.logger)
        manager.connect("ws://test")
        self.assertIsNone(manager.handshake_payload)

    @patch('ws_client.WebSocketApp')
    @patch('ws_client.threading.Thread')
    def test_on_open_sends_valid_handshake(self, thread_mock, ws_app_mock):
        manager = WebSocketManager(self.logger)
        payload = {
            "action": "handshake",
            "client_type": "iot_simulator",
            "version": "1.0",
            "capabilities": ["websocket"],
        }
        manager.handshake_payload = payload
        manager.connected = False  # Initially not connected

        # Mock WebSocketApp instance
        ws_instance = MagicMock()
        ws_app_mock.return_value = ws_instance

        # Simulate on_open call
        manager._on_open(ws_instance)

        # Check that connected is set and handshake is sent
        self.assertTrue(manager.connected)
        ws_instance.send.assert_called_once()
        self.logger.log.assert_any_call("Handshake sent automatically.")

    @patch('ws_client.WebSocketApp')
    def test_on_open_invalid_handshake_not_sent(self, ws_app_mock):
        manager = WebSocketManager(self.logger)
        payload = {"action": "invalid"}  # Invalid handshake
        manager.handshake_payload = payload

        ws_instance = MagicMock()
        ws_app_mock.return_value = ws_instance

        manager._on_open(ws_instance)

        ws_instance.send.assert_not_called()
        self.logger.log.assert_any_call("Invalid handshake payload, not sent.")

    @patch('ws_client.WebSocketApp')
    def test_on_open_no_handshake_payload(self, ws_app_mock):
        manager = WebSocketManager(self.logger)
        manager.handshake_payload = None

        ws_instance = MagicMock()
        ws_app_mock.return_value = ws_instance

        manager._on_open(ws_instance)

        ws_instance.send.assert_not_called()
        # Should not log handshake messages
        handshake_logs = [call for call in self.logger.log.call_args_list if "handshake" in str(call)]
        self.assertEqual(len(handshake_logs), 0)

    def test_send_json_when_connected(self):
        manager = WebSocketManager(self.logger)
        manager.connected = True
        manager.ws_app = MagicMock()

        payload = {"action": "test"}
        manager.send_json(payload)

        manager.ws_app.send.assert_called_once_with('{"action": "test"}')
        self.logger.log.assert_any_call('Sent WebSocket message: {"action": "test"}')

    def test_send_json_when_not_connected(self):
        manager = WebSocketManager(self.logger)
        manager.connected = False

        payload = {"action": "test"}
        manager.send_json(payload)

        self.logger.log.assert_called_once_with("Cannot send via WebSocket: not connected.")
