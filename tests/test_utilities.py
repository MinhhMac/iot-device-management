import unittest
from utilities import validate_handshake


class TestUtilities(unittest.TestCase):
    def test_validate_handshake_valid(self):
        payload = {
            "action": "handshake",
            "client_type": "iot_simulator",
            "version": "1.0",
            "capabilities": ["websocket", "http"],
        }
        self.assertTrue(validate_handshake(payload))

    def test_validate_handshake_missing_action(self):
        payload = {
            "client_type": "iot_simulator",
            "version": "1.0",
            "capabilities": ["websocket"],
        }
        self.assertFalse(validate_handshake(payload))

    def test_validate_handshake_wrong_action(self):
        payload = {
            "action": "ping",
            "client_type": "iot_simulator",
            "version": "1.0",
            "capabilities": ["websocket"],
        }
        self.assertFalse(validate_handshake(payload))

    def test_validate_handshake_missing_client_type(self):
        payload = {
            "action": "handshake",
            "version": "1.0",
            "capabilities": ["websocket"],
        }
        self.assertFalse(validate_handshake(payload))

    def test_validate_handshake_missing_version(self):
        payload = {
            "action": "handshake",
            "client_type": "iot_simulator",
            "capabilities": ["websocket"],
        }
        self.assertFalse(validate_handshake(payload))

    def test_validate_handshake_missing_capabilities(self):
        payload = {
            "action": "handshake",
            "client_type": "iot_simulator",
            "version": "1.0",
        }
        self.assertFalse(validate_handshake(payload))

    def test_validate_handshake_capabilities_not_list(self):
        payload = {
            "action": "handshake",
            "client_type": "iot_simulator",
            "version": "1.0",
            "capabilities": "websocket",
        }
        self.assertFalse(validate_handshake(payload))

    def test_validate_handshake_extra_fields_allowed(self):
        payload = {
            "action": "handshake",
            "client_type": "iot_simulator",
            "version": "1.0",
            "capabilities": ["websocket"],
            "extra": "field",
        }
        self.assertTrue(validate_handshake(payload))
