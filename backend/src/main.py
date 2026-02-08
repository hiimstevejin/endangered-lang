import io
import json
import wave

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standard browser AudioContext sample rate is usually 44.1kHz or 48kHz.
# Since we didn't downsample on the client, we assume 44100 Hz for now.
SAMPLE_RATE = 44100


@app.websocket("/ws/audio")
async def audio_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    # 1. The Temporary Audio Buffer (Raw PCM)
    pcm_buffer = io.BytesIO()

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                print("Client disconnected")
                break

            if "bytes" in message:
                # Append Raw chunks
                pcm_buffer.write(message["bytes"])

            elif "text" in message:
                try:
                    data = json.loads(message["text"])
                    if data.get("type") == "speech_end":
                        # --- THE TRIGGER PHASE COMPLETION ---

                        # A. Seal the Raw Buffer
                        raw_bytes = pcm_buffer.getvalue()

                        # B. Convert to WAV in Memory (The Requirement)
                        wav_buffer = io.BytesIO()
                        with wave.open(wav_buffer, "wb") as wf:
                            wf.setnchannels(1)  # Mono
                            wf.setsampwidth(2)  # 16-bit PCM
                            wf.setframerate(SAMPLE_RATE)
                            wf.writeframes(raw_bytes)

                        # Reset pointer to start of file so it can be read later
                        wav_buffer.seek(0)

                        # C. Validation
                        wav_size = wav_buffer.getbuffer().nbytes
                        print(
                            f"✅ Trigger Phase Complete. WAV File in Memory: {wav_size} bytes."
                        )

                        # D. Acknowledge to Client
                        await websocket.send_json(
                            {"status": "sealed", "size": wav_size, "format": "wav"}
                        )

                        # Handover Point: wav_buffer is now ready for Research Core
                        # process_research_core(wav_buffer)

                        # Reset for next turn
                        pcm_buffer = io.BytesIO()

                except json.JSONDecodeError:
                    print("Error decoding JSON")

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Connection closed: {e}")
