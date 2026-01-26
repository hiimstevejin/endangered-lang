from typing import AsyncIterator

from src.services.cartesia_tts import CartesiaTTS
from src.services.events import VoiceAgentEvent
from src.services.utils import merge_async_iters


async def tts_stream(
    event_stream: AsyncIterator[VoiceAgentEvent],
) -> AsyncIterator[VoiceAgentEvent]:
    """
    Transform stream: Voice Events → Voice Events (with Audio)

    This function takes a stream of upstream voice agent events and processes them.
    When agent_chunk events arrive, it sends the text to Cartesia for TTS synthesis.
    Audio is streamed back as tts_chunk events as it's generated.
    All upstream events are passed through unchanged.

    It uses merge_async_iters to combine two concurrent streams:
    - process_upstream(): Iterates through incoming events, yields them for
      passthrough, and sends agent text chunks to Cartesia for synthesis.
    - tts.receive_events(): Yields audio chunks from Cartesia as they are
      synthesized.

    The merge utility runs both iterators concurrently, yielding items from
    either stream as they become available. This allows audio generation to
    begin before the agent has finished generating all text, minimizing latency.

    Args:
        event_stream: An async iterator of upstream voice agent events

    Yields:
        All upstream events plus tts_chunk events for synthesized audio
    """
    tts = CartesiaTTS()

    async def process_upstream() -> AsyncIterator[VoiceAgentEvent]:
        """
        Process upstream events, yielding them while sending text to Cartesia.

        This async generator serves two purposes:
        1. Pass through all upstream events (stt_chunk, stt_output, agent_chunk)
           so downstream consumers can observe the full event stream.
        2. Buffer agent_chunk text and send to Cartesia when agent_end arrives.
           This ensures the full response is sent at once for better TTS quality.
        """
        buffer: list[str] = []
        async for event in event_stream:
            # Pass through all events to downstream consumers
            yield event
            # Buffer agent text chunks
            if event.type == "agent_chunk":
                buffer.append(event.text)
            # Send all buffered text to Cartesia when agent finishes
            if event.type == "agent_end":
                await tts.send_text("".join(buffer))
                buffer = []

    try:
        # Merge the processed upstream events with TTS audio events
        # Both streams run concurrently, yielding events as they arrive
        async for event in merge_async_iters(process_upstream(), tts.receive_events()):
            yield event
    finally:
        # Cleanup: close the WebSocket connection to Cartesia
        await tts.close()
