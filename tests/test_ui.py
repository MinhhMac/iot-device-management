import pytest
from unittest.mock import MagicMock
import json


class TestAppUI:
    def setup_method(self, mocker):
        # Mock tkinter to avoid GUI
        mocker.patch('tkinter.Tk')
        mocker.patch('tkinter.ttk.Style')
        mocker.patch('tkinter.ttk.Label')
        mocker.patch('tkinter.ttk.Entry')
        mocker.patch('tkinter.ttk.Button')
        mocker.patch('tkinter.ttk.LabelFrame')
        mocker.patch('tkinter.ttk.Checkbutton')
        mocker.patch('tkinter.scrolledtext.ScrolledText')
        mocker.patch('tkinter.ttk.Frame')
        mocker.patch('tkinter.IntVar')
        mocker.patch('tkinter.StringVar')
        mocker.patch('uuid.uuid4', return_value='test-uuid')

        from ui import AppUI
        self.app_ui = AppUI()
        # Mock the root and other widgets if needed
        self.app_ui.root = MagicMock()
        self.app_ui.request_text = MagicMock()
        self.app_ui.log_text = MagicMock()
        self.app_ui.ws_manager = MagicMock()
        self.app_ui.http_client = MagicMock()

    def test_handshake_payload_construction(self):
        # Set values
        self.app_ui.client_id_var.set("test-client")
        self.app_ui.auth_token_var.set("test-token")
        self.app_ui.session_id = "test-session-id"
        self.app_ui.ws_url_var.set("ws://example.com")

        expected_payload = {
            "action": "handshake",
            "client_type": "iot_simulator",
            "version": "1.0",
            "capabilities": ["websocket", "http"],
            "session_id": "test-session-id",
            "auth_token": "test-token",
            "client_id": "test-client",
        }

        self.app_ui.connect()

        self.app_ui.ws_manager.connect.assert_called_once_with("ws://example.com", expected_payload)

    def test_handle_ws_message_handshake_ack(self):
        message = json.dumps({"action": "handshake_ack", "status": "ok"})
        self.app_ui._handle_ws_message(message)

        self.app_ui.logger.log.assert_any_call("Handshake acknowledged by server.")

    def test_handle_ws_message_other_action(self):
        message = json.dumps({"action": "ping", "data": "test"})
        self.app_ui._handle_ws_message(message)

        # Should not log handshake ack
        log_calls = [call[0][0] for call in self.app_ui.logger.log.call_args_list]
        assert "Handshake acknowledged by server." not in log_calls

    def test_handle_ws_message_invalid_json(self):
        message = "not json"
        self.app_ui._handle_ws_message(message)

        # Should not crash, and log the message
        self.app_ui.logger.log.assert_any_call("WebSocket received: not json")

    def test_session_id_generated(self):
        # session_id should be a string UUID
        import uuid
        assert isinstance(self.app_ui.session_id, str)
        # Try to parse as UUID
        uuid.UUID(self.app_ui.session_id)