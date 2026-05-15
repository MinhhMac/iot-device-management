import unittest
import uuid
from unittest.mock import MagicMock, patch
import json
from ui import AppUI


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


class TestIntegration(unittest.TestCase):
    def setUp(self):
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

        self.app = AppUI()
        self.app.logger.log = MagicMock()

    def tearDown(self):
        for patcher in reversed(self.patchers):
            patcher.stop()

    def test_handshake_payload_construction(self):
        self.app.client_id_var.set("test-client")
        self.app.auth_token_var.set("test-token")
        self.app.ws_url_var.set("")

        expected_payload = {
            "action": "handshake",
            "client_type": "iot_simulator",
            "version": "1.0",
            "capabilities": ["websocket", "http"],
            "session_id": self.app.session_id,
            "auth_token": "test-token",
            "client_id": "test-client",
        }

        self.app.ws_manager.connect = MagicMock()
        self.app.connect()

        self.app.ws_manager.connect.assert_called_once()
        args, _kwargs = self.app.ws_manager.connect.call_args
        self.assertEqual(args[0], "")
        self.assertEqual(args[1], expected_payload)

    def test_handshake_ack_logging(self):
        message = json.dumps({"action": "handshake_ack", "status": "ok"})
        self.app._handle_ws_message(message)
        self.app.logger.log.assert_any_call("Handshake acknowledged by server.")

    def test_non_json_message_handling(self):
        message = "plain text message"
        self.app._handle_ws_message(message)
        self.app.logger.log.assert_any_call(f"WebSocket received: {message}")
        ack_logs = [call for call in self.app.logger.log.call_args_list if "acknowledged" in str(call)]
        self.assertEqual(len(ack_logs), 0)
