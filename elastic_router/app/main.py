"""
GreenWeave — Elastic Router
Main: FastAPI entry point.

Endpoints:
  POST /chat/completions     — Carbon-aware AI inference
  GET  /health               — Health check
  GET  /carbon/status        — Current grid carbon state
  GET  /budget               — Get current carbon budget
  POST /budget/set           — Set a carbon budget
  POST /budget/reset         — Reset budget usage to 0
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import DEFAULT_WEIGHT_PROFILE, ROUTER_PORT
from app.logger import get_logger
from app.redis_service import get_carbon_state
from app.router_logic import (
    select_model, get_budget, set_budget,
    reset_budget, add_to_budget, get_budget_pressure
)
from app.impact_model import calculate_impact
from app.llm_client import call_model
from app.receipt_builder import build_receipt

logger = get_logger("main")


# ─────────────────────────────────────────────
#  Schemas
# ─────────────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    system_prompt: str | None = None
    task_type: str = Field(default="casual_chat")
    weight_profile: str | None = None


class ChatResponse(BaseModel):
    response: str
    carbon_receipt: dict
    model_used: str

    model_config = {"protected_namespaces": ()}


class BudgetSetRequest(BaseModel):
    limit_g: float = Field(..., description="Monthly CO₂ budget in grams (e.g. 2000 = 2kg)")


# ─────────────────────────────────────────────
#  App
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🌿 GreenWeave Elastic Router starting up…")
    state = get_carbon_state()
    logger.info(
        "Initial carbon state: %s @ %s gCO₂/kWh [%s]",
        state.get("status"), state.get("carbon_intensity"), state.get("region"),
    )
    yield
    logger.info("GreenWeave Elastic Router shutting down.")


app = FastAPI(
    title="GreenWeave — Elastic Router",
    description="Carbon-intelligent AI inference middleware.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
#  Chat
# ─────────────────────────────────────────────

@app.post("/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest):
    t_start = time.perf_counter()

    chosen_model, carbon_state = select_model(task_type=request.task_type)

    profile = request.weight_profile or DEFAULT_WEIGHT_PROFILE
    carbon_intensity = carbon_state.get("carbon_intensity", 350)
    impact = calculate_impact(
        chosen_model=chosen_model,
        carbon_intensity=carbon_intensity,
        weight_profile=profile,
    )

    try:
        messages_dicts = [m.model_dump() for m in request.messages]
        llm_resp = call_model(
            model=chosen_model,
            messages=messages_dicts,
            system_prompt=request.system_prompt,
        )
    except ValueError as exc:
        logger.error("LLM call failed: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected LLM error: %s", exc)
        raise HTTPException(status_code=500, detail="LLM inference failed")

    total_latency = (time.perf_counter() - t_start) * 1000

    # Track CO₂ usage against budget
    add_to_budget(impact.chosen_co2_g)

    # Add budget info to receipt
    receipt = build_receipt(
        chosen_model=chosen_model,
        carbon_state=carbon_state,
        impact=impact,
        latency_ms=round(total_latency, 1),
        weight_profile=profile,
    )

    # Inject budget state into receipt
    budget = get_budget()
    if budget:
        receipt["budget_limit_g"] = budget["limit_g"]
        receipt["budget_used_g"] = round(budget["used_g"], 4)
        receipt["budget_pressure"] = get_budget_pressure()
        receipt["budget_pct"] = round((budget["used_g"] / budget["limit_g"]) * 100, 1)

    logger.info(
        "✅ Request complete | model=%s | latency=%.0fms | CO₂=%.5fg",
        chosen_model.model_id, total_latency, impact.chosen_co2_g,
    )

    return ChatResponse(
        response=llm_resp.text,
        carbon_receipt=receipt,
        model_used=chosen_model.model_id,
    )


# ─────────────────────────────────────────────
#  Budget Endpoints
# ─────────────────────────────────────────────

@app.get("/budget")
async def get_budget_status():
    """Get current carbon budget state."""
    budget = get_budget()
    if not budget:
        return {"budget_set": False}
    pct = (budget["used_g"] / budget["limit_g"]) * 100 if budget["limit_g"] > 0 else 0
    return {
        "budget_set": True,
        "limit_g": budget["limit_g"],
        "used_g": round(budget["used_g"], 4),
        "remaining_g": round(budget["limit_g"] - budget["used_g"], 4),
        "pct_used": round(pct, 1),
        "pressure": get_budget_pressure(),
    }


@app.post("/budget/set")
async def set_budget_endpoint(req: BudgetSetRequest):
    """Set a monthly carbon budget in grams."""
    set_budget(req.limit_g)
    return {"message": f"Budget set to {req.limit_g}g CO₂", "limit_g": req.limit_g}


@app.post("/budget/reset")
async def reset_budget_endpoint():
    """Reset budget usage back to 0."""
    reset_budget()
    return {"message": "Budget usage reset to 0"}


# ─────────────────────────────────────────────
#  Status Endpoints
# ─────────────────────────────────────────────

@app.get("/carbon/status")
async def carbon_status():
    return get_carbon_state()


@app.get("/health")
async def health():
    state = get_carbon_state()
    redis_ok = "fallback_reason" not in state
    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else f"fallback ({state.get('fallback_reason')})",
        "carbon": state,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=ROUTER_PORT, reload=True)
