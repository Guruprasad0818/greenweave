import logging
from app.config import Settings

def setup_logger():
    logging.basicConfig(
        level=Settings.LOG_LEVEL,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    return logging.getLogger("GreenWeave-GridMonitor")