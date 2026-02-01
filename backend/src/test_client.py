import asyncio
import wave

import websockets


async def stream_audio(file_path: str, uri: str):
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")

        # Start a background task to listen for responses
        async def listen():
            try:
                async for message in websocket:
                    print(f"\n[SERVER JSON]: {message}")
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed by server.")

        listener_task = asyncio.create_task(listen())

        # Your existing code to send audio
        with wave.open(file_path, "rb") as wav:
            while data := wav.readframes(1024):
                await websocket.send(data)
                await asyncio.sleep(0.02)  # Mimic real-time pace

        print("Finished sending audio. Waiting for final responses...")
        await asyncio.sleep(5)  # Give the server time to finish processing
        listener_task.cancel()


if __name__ == "__main__":
    print("Script started...")
    asyncio.run(stream_audio("test.wav", "ws://127.0.0.1:8000/ws"))
