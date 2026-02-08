import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_full_audio_flow():
    """
    Simulates:
    1. Client connects.
    2. Client streams audio chunks (PCM data).
    3. Client detects silence and sends 'speech_end'.
    4. Server seals buffer and responds.
    """
    with client.websocket_connect("/ws/audio") as websocket:
        # 1. Simulate streaming audio (3 chunks of dummy PCM data)
        # 16000 Hz * 2 bytes/sample * 0.1s = 3200 bytes per chunk
        chunk = b"\x00\x01" * 1600

        websocket.send_bytes(chunk)
        websocket.send_bytes(chunk)
        websocket.send_bytes(chunk)

        # 2. Send Control Signal
        websocket.send_text('{"type": "speech_end"}')

        # 3. Verify Response
        response = websocket.receive_json()
        assert response["status"] == "sealed"
        # 3 chunks * 3200 bytes = 9600 bytes
        assert response["size"] == 9644


def test_disconnect_handling():
    """Ensure server handles abrupt disconnects without crashing."""
    with client.websocket_connect("/ws/audio") as websocket:
        websocket.send_bytes(b"\x00\x00" * 100)
        websocket.close()
    # If the test passes without raising an exception, the server handled it.
