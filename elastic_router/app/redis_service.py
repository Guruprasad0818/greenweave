"""
GreenWeave — Elastic Router
Redis Service: Reads the carbon state written by the Grid Monitor.
"""

import json
import os
import redis

from app.logger import get_logger

logger = get_logger("redis_service")

# Uses "redis" as the default host so Docker containers can talk to each other
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
FALLBACK_CARBON_STATUS = "MODERATE"


def _get_client() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=1,
    )


def get_carbon_state() -> dict:
    try:
        client = _get_client()
        raw = client.get("grid_status")

        if raw is None:
            logger.warning("Redis key 'grid_status' not found — using fallback")
            return _fallback_state("Key not found in Redis")

        state = json.loads(raw)
        
        return {
            "status":           state.get("status", FALLBACK_CARBON_STATUS),
            "carbon_intensity": state.get("carbon_intensity", 350),
            "region":           state.get("region", "Unknown"),
            "timestamp":        state.get("timestamp_utc"),
        }
    except redis.ConnectionError as exc:
        logger.error("Redis unreachable: %s — using fallback", exc)
        return _fallback_state("Redis connection error")
    except (json.JSONDecodeError, KeyError) as exc:
        logger.error("Malformed Redis data: %s — using fallback", exc)
        return _fallback_state("Malformed data")


def _fallback_state(reason: str) -> dict:
    return {
        "status":           FALLBACK_CARBON_STATUS,
        "carbon_intensity": 350,
        "region":           "Unknown (fallback)",
        "timestamp":        None,
        "fallback_reason":  reason,
    }