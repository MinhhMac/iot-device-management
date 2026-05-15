from datetime import datetime


def validate_handshake(payload: dict) -> bool:
    required_fields = ["action", "client_type", "version", "capabilities"]
    for field in required_fields:
        if field not in payload:
            return False
    if payload.get("action") != "handshake":
        return False
    if not isinstance(payload.get("capabilities"), list):
        return False
    return True


DEFAULT_COMMANDS = [
    {
        "name": "Ping",
        "payload": {
            "action": "ping",
            "timestamp": "2026-03-27T12:00:00Z",
        },
    },
    {
        "name": "Login",
        "payload": {
            "action": "login",
            "username": "demo_user",
            "token": "replace-me",
        },
    },
    {
        "name": "Subscribe",
        "payload": {
            "action": "subscribe",
            "channel": "events",
        },
    },
    {
        "name": "Echo",
        "payload": {
            "action": "echo",
            "message": "hello from tkinter client",
        },
    },
    {
        "name": "Handshake",
        "payload": {
            "action": "handshake",
            "client_type": "iot_simulator",
            "version": "1.0",
            "capabilities": ["websocket", "http"],
            "session_id": "",
            "auth_token": "",
        },
    },
    {
        "name": "HTTP POST sample",
        "payload": {
            "method": "POST",
            "path": "/api/commands",
            "headers": {
                "Content-Type": "application/json",
            },
            "body": {
                "action": "status",
            },
            "timeout": 10,
        },
    },
]


class AppLogger:
    def __init__(self, callback) -> None:
        self.callback = callback

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.callback(f"[{timestamp}] {message}\n")
