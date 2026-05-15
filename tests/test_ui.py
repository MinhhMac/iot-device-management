import pytest
import uuid
from unittest.mock import MagicMock, patch
import json


class SimpleVar:
    def __init__(self, value=""):
        self._value = value

    def set(self, value):
        self._value = value

    def get(self):
        return self._value

    def trace_add(self, *args, **kwargs):
        pass

    def trace(self, *args, **kwargs):
        pass


def DummyWidget(*args, **kwargs):
    return MagicMock()


class TestAppUI:
    def setup_method(self):
        patchers = [
            patch('tkinter.Tk', return_value=MagicMock()),
            patch('tkinter.ttk.Style', return_value=MagicMock()),
            patch('tkinter.ttk.Label', new=DummyWidget),
            patch('tkinter.ttk.Entry', new=DummyWidget),
            patch('tkinter.ttk.Button', new=DummyWidget),
            patch('tkinter.ttk.LabelFrame', new=DummyWidget),
            patch('tkinter.ttk.Checkbutton', new=DummyWidget),
            patch('tkinter.scrolledtext.ScrolledText', new=DummyWidget),
            patch('tkinter.ttk.Frame', new=DummyWidget),
            patch('tkinter.IntVar', new=SimpleVar),
            patch('tkinter.StringVar', new=SimpleVar),
            patch('uuid.uuid4', return_value=uuid.UUID('12345678-1234-5678-1234-567812345678')),
        ]
        self.patchers = patchers
        self.started_patches = [p.start() for p in patchers]

        from ui import AppUI
        self.app_ui = AppUI()

        self.app_ui.logger.log = MagicMock()
        self.app_ui.request_text = MagicMock()
        self.app_ui.log_text = MagicMock()
        self.app_ui.ws_manager = MagicMock()
        self.app_ui.http_client = MagicMock()

    def teardown_method(self):
        for patcher in reversed(self.patchers):
            patcher.stop()

    def test_handshake_payload_construction(self):
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

        self.app_ui.ws_manager.connect.assert_called_once()
        args, _kwargs = self.app_ui.ws_manager.connect.call_args
        assert args[0] == "ws://example.com"
        assert args[1] == expected_payload

    def test_handle_ws_message_handshake_ack(self):
        message = json.dumps({"action": "handshake_ack", "status": "ok"})
        self.app_ui._handle_ws_message(message)

        self.app_ui.logger.log.assert_any_call("Handshake acknowledged by server.")

    def test_handle_ws_message_other_action(self):
        message = json.dumps({"action": "ping", "data": "test"})
        self.app_ui._handle_ws_message(message)

        log_calls = [call[0][0] for call in self.app_ui.logger.log.call_args_list]
        assert "Handshake acknowledged by server." not in log_calls

    def test_handle_ws_message_invalid_json(self):
        message = "not json"
        self.app_ui._handle_ws_message(message)

        self.app_ui.logger.log.assert_any_call("WebSocket received: not json")

    def test_session_id_generated(self):
        assert isinstance(self.app_ui.session_id, str)
        uuid.UUID(self.app_ui.session_id)
