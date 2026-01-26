from langchain_core.runnables import RunnableGenerator

from src.services.agent import agent_stream
from src.services.stt import stt_stream
from src.services.tts import tts_stream

pipeline = (
    RunnableGenerator(stt_stream)
    | RunnableGenerator(agent_stream)
    | RunnableGenerator(tts_stream)
)
