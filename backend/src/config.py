import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
    CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")

    @classmethod
    def validate(cls):
        """Ensure all keys are present at startup."""
        for key, value in cls.__dict__.items():
            if key.isupper() and not value:
                raise ValueError(f"CRITICAL: {key} is missing from .env")


settings = Settings()
