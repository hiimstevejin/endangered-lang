import io
import wave

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_wav_conversion_integrity():
    """
    Verifies that raw PCM bytes sent by the client are correctly
    sealed into a valid WAV format in the server's memory.
    """
    with client.websocket_connect("/ws/audio") as websocket:
        # 1. Simulate Input Phase (Client streams raw PCM)
        # We send 2 chunks of dummy audio (1 second of silence)
        # 44100 Hz * 2 bytes/sample * 1 channel = 88200 bytes per second
        # Let's send a small snippet: 10ms = 882 bytes
        chunk_size = 882
        dummy_pcm = b"\x00\x00" * (chunk_size // 2)

        websocket.send_bytes(dummy_pcm)  # Chunk 1
        websocket.send_bytes(dummy_pcm)  # Chunk 2

        # 2. Simulate Trigger Phase (User stops speaking)
        websocket.send_text('{"type": "speech_end"}')

        # 3. Verify Server State (The "Sealed" Response)
        response = websocket.receive_json()

        assert response["status"] == "sealed"
        assert response["format"] == "wav"

        # calculate expected WAV size:
        # Header (44 bytes) + Data (882 * 2 bytes)
        expected_size = 44 + (chunk_size * 2)
        assert response["size"] == expected_size

        print(
            f"\n✅ Trigger Phase Verified: Server created a {response['size']} byte WAV file from raw stream."
        )


def test_empty_buffer_handling():
    """
    Edge Case: User presses record but says nothing (0 bytes sent).
    The server should still create a valid (but empty) WAV file.
    """
    with client.websocket_connect("/ws/audio") as websocket:
        # Directly trigger end without sending bytes
        websocket.send_text('{"type": "speech_end"}')

        response = websocket.receive_json()

        # A valid WAV file with no data is just the header (44 bytes)
        assert response["size"] == 44
        assert response["status"] == "sealed"
