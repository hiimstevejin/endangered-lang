import asyncio
import os

from dotenv import load_dotenv

# 1. Load your .env file
load_dotenv()


async def check_assemblyai():
    import assemblyai as aai

    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    try:
        # A simple list call is the fastest way to check auth
        transcriber = aai.Transcriber()
        print("AssemblyAI: Key is valid.")
    except Exception as e:
        print(f"❌ AssemblyAI Error: {e}")


async def check_cartesia():
    from cartesia import Cartesia

    api_key = os.getenv("CARTESIA_API_KEY") or ""
    try:
        client = Cartesia(api_key=api_key)
        # List voices to verify the key works
        client.voices.list()
        print("Cartesia: Key is valid.")
    except Exception as e:
        print(f"❌ Cartesia Error: {e}")


async def check_openai():
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        # Simple model list call
        client.models.list()
        print("OpenAI: Key is valid.")
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")


async def main():
    print("--- API Key Smoke Test ---")
    await check_assemblyai()
    await check_cartesia()
    await check_openai()


if __name__ == "__main__":
    asyncio.run(main())
