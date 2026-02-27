"""
GreenWeave — Elastic Router
Router Logic: Reads carbon state → selects the right model.
Also enforces Carbon Budget Mode if a budget is set.
"""

from app.config import MODEL_ROUTES, ModelConfig
from app.redis_service import get_carbon_state
from app.logger import get_logger
import redis
import json
import os  # NEW: imported os to read Docker environment variables

logger = get_logger("router_logic")

# Task-type overrides: minimum required accuracy score
TASK_ACCURACY_FLOOR: dict[str, float] = {
    "casual_chat":    0.0,
    "summarization":  0.0,
    "coding":         0.75,
    "legal_drafting": 1.0,
    "medical":        1.0,
}

# Redis connection for budget tracking - fixed to work with Docker!
_redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"), 
    port=int(os.getenv("REDIS_PORT", 6379)), 
    decode_responses=True
)

BUDGET_KEY = "carbon_budget"          # stores { "limit_g": 2000, "used_g": 0.0 }


# ─────────────────────────────────────────────
#  Budget Functions
# ─────────────────────────────────────────────

def set_budget(limit_g: float):
    """Set a new carbon budget (resets usage to 0)."""
    _redis_client.set(BUDGET_KEY, json.dumps({"limit_g": limit_g, "used_g": 0.0}))
    logger.info("Carbon budget set: %.1f g CO₂", limit_g)


def get_budget() -> dict | None:
    """Get current budget state. Returns None if no budget set."""
    raw = _redis_client.get(BUDGET_KEY)
    if raw:
        return json.loads(raw)
    return None


def add_to_budget(co2_g: float):
    """Add CO₂ usage to the budget tracker."""
    budget = get_budget()
    if budget:
        budget["used_g"] = round(budget["used_g"] + co2_g, 6)
        _redis_client.set(BUDGET_KEY, json.dumps(budget))


def reset_budget():
    """Reset usage to 0 (keep the limit)."""
    budget = get_budget()
    if budget:
        budget["used_g"] = 0.0
        _redis_client.set(BUDGET_KEY, json.dumps(budget))


def get_budget_pressure() -> str:
    """
    Returns budget pressure level:
      NONE     → no budget set
      LOW      → < 70% used
      MEDIUM   → 70–90% used  → prefer small model
      HIGH     → 90–100% used → force small model
      EXCEEDED → over budget  → force smallest model
    """
    budget = get_budget()
    if not budget or budget["limit_g"] <= 0:
        return "NONE"

    pct = (budget["used_g"] / budget["limit_g"]) * 100

    if pct >= 100:
        return "EXCEEDED"
    elif pct >= 90:
        return "HIGH"
    elif pct >= 70:
        return "MEDIUM"
    else:
        return "LOW"


# ─────────────────────────────────────────────
#  Main Routing Decision
# ─────────────────────────────────────────────

def select_model(task_type: str = "casual_chat") -> tuple[ModelConfig, dict]:
    """
    Main routing decision.

    Priority order:
    1. Carbon budget pressure  (overrides everything if EXCEEDED)
    2. Task accuracy floor     (some tasks always need full model)
    3. Grid carbon status      (LOW / MODERATE / HIGH)
    """
    carbon = get_carbon_state()
    carbon_status = carbon["status"]
    carbon_intensity = carbon.get("carbon_intensity", 350)

    # ── Step 1: Start with carbon-tier model ─────────────────────
    chosen = MODEL_ROUTES[carbon_status]

    # ── Step 2: Task accuracy override ───────────────────────────
    required_accuracy = TASK_ACCURACY_FLOOR.get(task_type.lower(), 0.0)
    if chosen.accuracy_score < required_accuracy:
        for tier in ["HIGH", "MODERATE", "LOW"]:
            candidate = MODEL_ROUTES[tier]
            if candidate.accuracy_score >= required_accuracy:
                logger.info(
                    "Task override: '%s' requires accuracy≥%.2f — upgrading %s → %s",
                    task_type, required_accuracy, chosen.model_id, candidate.model_id,
                )
                chosen = candidate
                break

    # ── Step 3: Carbon Budget pressure override ───────────────────
    pressure = get_budget_pressure()

    if pressure == "EXCEEDED":
        # Force smallest model regardless of task
        chosen = MODEL_ROUTES["HIGH"]
        logger.warning("Budget EXCEEDED — forcing smallest model")

    elif pressure == "HIGH" and chosen.model_id != MODEL_ROUTES["HIGH"].model_id:
        # Budget >90% — downgrade one tier if possible
        if carbon_status == "LOW":
            chosen = MODEL_ROUTES["MODERATE"]
        else:
            chosen = MODEL_ROUTES["HIGH"]
        logger.warning("Budget pressure HIGH — downgrading model to save CO₂")

    elif pressure == "MEDIUM" and carbon_status == "LOW":
        # Budget >70% — use moderate instead of full model
        chosen = MODEL_ROUTES["MODERATE"]
        logger.info("Budget pressure MEDIUM — using moderate model")

    logger.info(
        "Routing decision | carbon=%s (%d gCO₂/kWh) | task=%s | budget=%s | model=%s",
        carbon_status, carbon_intensity, task_type, pressure, chosen.model_id,
    )

    return chosen, carbon