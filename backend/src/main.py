import logging
from typing import AsyncIterator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from src.config import settings
from src.services.events import event_to_dict
from src.services.pipeline import pipeline

settings.validate()
app = FastAPI()

# logger for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    **Voice Streaming Endpoint**

    This endpoint accepts a WebSocket connection and expects raw audio bytes.
    - **Protocol**: WebSocket (Binary)
    - **Payload**: PCM Audio Chunks
    """
    await websocket.accept()
    logger.info("Client connected to voice WebSocket")

    async def websocket_audio_stream() -> AsyncIterator[bytes]:
        try:
            while True:
                # Receive raw bytes from frontend
                data = await websocket.receive_bytes()

                if not data:
                    break

                yield data
        except WebSocketDisconnect:
            logger.info("Client disconnected normally")
        except Exception as e:
            logger.error(f"Error receiving audio: {e}")
        finally:
            logger.info("Cleaning up audio stream resources")

    # send audio to pipeline
    # pipeline = input -> stt -> agent-> tts
    output_stream = pipeline.atransform(websocket_audio_stream())

    async for event in output_stream:
        await websocket.send_json(event_to_dict(event))
