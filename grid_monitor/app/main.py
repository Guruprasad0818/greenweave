# import time
# import sys

# from app.config import Settings
# from app.logger import setup_logger
# from app.carbon_service import CarbonService
# from app.redis_service import RedisService
# from app.prediction_service import PredictionService   # NEW

# logger = setup_logger()


# def run():
#     try:
#         Settings.validate()
#     except Exception as e:
#         logger.error(f"Configuration error: {e}")
#         sys.exit(1)

#     carbon_service = CarbonService()
#     redis_service = RedisService()
#     prediction_service = PredictionService(redis_service)  # NEW

#     try:
#         redis_service.health_check()
#     except Exception:
#         logger.error("Redis connection failed.")
#         sys.exit(1)

#     logger.info("GreenWeave Grid Monitor started successfully.")

#     while True:
#         try:
#             logger.info("Fetching carbon intensity...")

#             intensity = carbon_service.fetch_intensity()
#             status = carbon_service.categorize(intensity)

#             payload = carbon_service.build_payload(intensity, status)

#             # Store latest grid snapshot
#             redis_service.store_grid_status(payload)

#             # Store carbon history for prediction
#             redis_service.store_carbon_history(intensity)

#             # Predict trend
#             trend_data = prediction_service.calculate_trend()
#             delay_execution = prediction_service.should_delay_execution()

#             logger.info(
#                 f"Updated Redis | Intensity={intensity} gCO₂/kWh | "
#                 f"Status={status} | "
#                 f"Trend={trend_data['trend']} | "
#                 f"Confidence={trend_data['confidence']} | "
#                 f"DelayExecution={delay_execution}"
#             )

#         except Exception as e:
#             logger.error(f"Worker error: {str(e)}")

#         time.sleep(Settings.POLL_INTERVAL)


# if __name__ == "__main__":
#     run() 
import time
import sys

from app.config import Settings
from app.logger import setup_logger
from app.carbon_service import CarbonService
from app.redis_service import RedisService
from app.prediction_service import PredictionService
from app.region_router import RegionRouter
from app.self_learning_engine import SelfLearningEngine

logger = setup_logger()


def run():
    try:
        Settings.validate()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    carbon_service = CarbonService()
    redis_service = RedisService()
    prediction_service = PredictionService(redis_service)
    region_router = RegionRouter()
    learning_engine = SelfLearningEngine()

    try:
        redis_service.health_check()
    except Exception:
        logger.error("Redis connection failed.")
        sys.exit(1)

    logger.info("GreenWeave Intelligent Engine started.")

    while True:
        try:
            logger.info("Fetching multi-region carbon data...")

            # 1️⃣ Multi-region fetch
            region_data = carbon_service.fetch_multi_region_intensity()

            # 2️⃣ Select cleanest region
            routing_decision = region_router.select_best_region(region_data)

            best_region = routing_decision["best_region"]
            best_intensity = routing_decision["intensity"]

            status = carbon_service.categorize(best_intensity)

            payload = carbon_service.build_payload(
                best_intensity,
                status,
                region=best_region
            )

            redis_service.store_grid_status(payload)
            redis_service.store_carbon_history(best_intensity)

            # 3️⃣ Predictive optimization
            trend_data = prediction_service.calculate_trend()
            delay_execution = prediction_service.should_delay_execution()

            # 4️⃣ Self-learning adjustment
            learning_engine.update_learning(delay_execution)
            adaptive_threshold = learning_engine.adaptive_threshold()

            logger.info(
                f"Region={best_region} | "
                f"Intensity={best_intensity} | "
                f"Trend={trend_data['trend']} | "
                f"Delay={delay_execution} | "
                f"AdaptiveThreshold={adaptive_threshold}"
            )

        except Exception as e:
            logger.error(f"Worker error: {str(e)}")

        time.sleep(Settings.POLL_INTERVAL)


if __name__ == "__main__":
    run()