"""
GreenWeave — Elastic Router
Redis Service: Reads the carbon state written by the Grid Monitor.
The router NEVER calls WattTime / Electricity Maps directly.
"""

import json
import redis

from app.logger import get_logger

logger = get_logger("redis_service")

# Must match exactly what grid_monitor writes — key is "grid_status"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
FALLBACK_CARBON_STATUS = "MODERATE"


def _get_client() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=1,
    )


def get_carbon_state() -> dict:
    """
    Reads the grid_status key written by the Grid Monitor.

    Grid Monitor stores:
    {
        "region": "IN",
        "carbon_intensity": 642,
        "status": "HIGH",
        "timestamp_utc": "..."
    }

    Falls back to MODERATE if Redis is unreachable or key missing.
    """
    try:
        client = _get_client()
        raw = client.get("grid_status")   # matches grid_monitor key exactly

        if raw is None:
            logger.warning("Redis key 'grid_status' not found — using fallback")
            return _fallback_state("Key not found in Redis")

        state = json.loads(raw)

        # Normalise field names so the router always gets consistent keys
        return {
            "status":           state.get("status", FALLBACK_CARBON_STATUS),
            "carbon_intensity": state.get("carbon_intensity", 350),
            "region":           state.get("region", "Unknown"),   # ← fixed
            "timestamp":        state.get("timestamp_utc"),       # ← fixed
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