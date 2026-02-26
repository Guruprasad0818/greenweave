import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API
    API_KEY = os.getenv("ELECTRICITY_MAPS_API_KEY")
    ZONE = os.getenv("ZONE")

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    # Thresholds
    LOW_THRESHOLD = int(os.getenv("LOW_THRESHOLD", 150))
    MODERATE_THRESHOLD = int(os.getenv("MODERATE_THRESHOLD", 400))

    # Polling
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 300))
    REDIS_TTL = int(os.getenv("REDIS_TTL", 600))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def validate():
        if not Settings.API_KEY:
            raise ValueError("Missing ELECTRICITY_MAPS_API_KEY in .env")
        if not Settings.ZONE:
            raise ValueError("Missing ZONE in .env")