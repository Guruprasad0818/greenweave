import time
import sys

from app.config import Settings
from app.logger import setup_logger
from app.carbon_service import CarbonService
from app.redis_service import RedisService

logger = setup_logger()

def run():
    try:
        Settings.validate()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    carbon_service = CarbonService()
    redis_service = RedisService()

    try:
        redis_service.health_check()
    except Exception:
        logger.error("Redis connection failed.")
        sys.exit(1)

    logger.info("GreenWeave Grid Monitor started successfully.")

    while True:
        try:
            logger.info("Fetching carbon intensity...")

            intensity = carbon_service.fetch_intensity()
            status = carbon_service.categorize(intensity)

            payload = carbon_service.build_payload(intensity, status)

            redis_service.store_grid_status(payload)

            logger.info(
                f"Updated Redis | Intensity={intensity} gCO₂/kWh | Status={status}"
            )

        except Exception as e:
            logger.error(f"Worker error: {str(e)}")

        time.sleep(Settings.POLL_INTERVAL)

if __name__ == "__main__":
    run()