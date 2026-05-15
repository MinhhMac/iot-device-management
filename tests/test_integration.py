import unittest
from unittest.mock import MagicMock, patch
import json
from ui import AppUI


class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Mock Tkinter to avoid GUI instantiation
        with patch('tkinter.Tk'):
            self.app = AppUI()

    def test_handshake_payload_construction(self):
        # Test that connect constructs handshake payload correctly
        self.app.client_id_var.set("test-client")
        self.app.auth_token_var.set("test-token")

        expected_payload = {
            "action": "handshake",
            "client_type": "iot_simulator",
            "version": "1.0",
            "capabilities": ["websocket", "http"],
            "session_id": self.app.session_id,
            "auth_token": "test-token",
            "client_id": "test-client",
        }

        # Mock ws_manager.connect to capture the payload
        self.app.ws_manager.connect = MagicMock()

        self.app.connect()

        self.app.ws_manager.connect.assert_called_once()
        args, kwargs = self.app.ws_manager.connect.call_args
        self.assertEqual(args[0], "")  # ws_url_var.get().strip() is empty in test
        self.assertIn('handshake_payload', kwargs)
        payload = kwargs['handshake_payload']
        self.assertEqual(payload['action'], 'handshake')
        self.assertEqual(payload['client_id'], 'test-client')
        self.assertEqual(payload['auth_token'], 'test-token')
        self.assertEqual(payload['session_id'], self.app.session_id)

    def test_handshake_ack_logging(self):
        # Test that handshake ack messages are logged
        message = json.dumps({"action": "handshake_ack", "status": "ok"})
        self.app._handle_ws_message(message)
        self.app.logger.log.assert_any_call("Handshake acknowledged by server.")

    def test_non_json_message_handling(self):
        # Test that non-JSON messages are still logged normally
        message = "plain text message"
        self.app._handle_ws_message(message)
        self.app.logger.log.assert_any_call(f"WebSocket received: {message}")
        # Should not log handshake ack
        ack_logs = [call for call in self.app.logger.log.call_args_list if "acknowledged" in str(call)]
        self.assertEqual(len(ack_logs), 0)
