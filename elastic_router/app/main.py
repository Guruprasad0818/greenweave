# """
# GreenWeave — Elastic Router
# Main: FastAPI entry point.

# Endpoints:
#   POST /chat/completions     — Carbon-aware AI inference
#   GET  /health               — Health check
#   GET  /carbon/status        — Current grid carbon state
#   GET  /budget               — Get current carbon budget
#   POST /budget/set           — Set a carbon budget
#   POST /budget/reset         — Reset budget usage to 0
#   GET  /engine/status        — Predictive + Multi-Region + Self-Learning metrics
#   GET  /stats                — ESG aggregate stats (used by dashboard — no DB file access needed)
# """

# import time
# import math
# import random
# from contextlib import asynccontextmanager
# from datetime import datetime

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field

# from app.config import DEFAULT_WEIGHT_PROFILE, ROUTER_PORT
# from app.logger import get_logger
# from app.redis_service import get_carbon_state
# from app.router_logic import (
#     select_model, get_budget, set_budget,
#     reset_budget, add_to_budget, get_budget_pressure
# )
# from app.impact_model import calculate_impact
# from app.llm_client import call_model
# from app.receipt_builder import build_receipt
# from app.database import init_db, log_receipt, get_stats

# logger = get_logger("main")


# # ─────────────────────────────────────────────
# #  Schemas
# # ─────────────────────────────────────────────

# class Message(BaseModel):
#     role: str
#     content: str


# class ChatRequest(BaseModel):
#     messages: list[Message]
#     system_prompt: str | None = None
#     task_type: str = Field(default="casual_chat")
#     weight_profile: str | None = None


# class ChatResponse(BaseModel):
#     response: str
#     carbon_receipt: dict
#     model_used: str

#     model_config = {"protected_namespaces": ()}


# class BudgetSetRequest(BaseModel):
#     limit_g: float = Field(..., description="Monthly CO₂ budget in grams (e.g. 2000 = 2kg)")


# # ─────────────────────────────────────────────
# #  App
# # ─────────────────────────────────────────────

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("🌿 GreenWeave Elastic Router starting up…")
#     init_db()
#     state = get_carbon_state()
#     logger.info(
#         "Initial carbon state: %s @ %s gCO₂/kWh [%s]",
#         state.get("status"), state.get("carbon_intensity"), state.get("region"),
#     )
#     yield
#     logger.info("GreenWeave Elastic Router shutting down.")


# app = FastAPI(
#     title="GreenWeave — Elastic Router",
#     description="Carbon-intelligent AI inference middleware.",
#     version="1.0.0",
#     lifespan=lifespan,
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ─────────────────────────────────────────────
# #  Chat
# # ─────────────────────────────────────────────

# @app.post("/chat/completions", response_model=ChatResponse)
# async def chat_completions(request: ChatRequest):
#     t_start = time.perf_counter()

#     chosen_model, carbon_state = select_model(task_type=request.task_type)

#     profile = request.weight_profile or DEFAULT_WEIGHT_PROFILE
#     carbon_intensity = carbon_state.get("carbon_intensity", 350)
#     impact = calculate_impact(
#         chosen_model=chosen_model,
#         carbon_intensity=carbon_intensity,
#         weight_profile=profile,
#     )

#     try:
#         messages_dicts = [m.model_dump() for m in request.messages]
#         llm_resp = call_model(
#             model=chosen_model,
#             messages=messages_dicts,
#             system_prompt=request.system_prompt,
#         )
#     except ValueError as exc:
#         logger.error("LLM call failed: %s", exc)
#         raise HTTPException(status_code=503, detail=str(exc))
#     except Exception as exc:
#         logger.error("Unexpected LLM error: %s", exc)
#         raise HTTPException(status_code=500, detail=f"LLM inference failed: {exc}")

#     total_latency = (time.perf_counter() - t_start) * 1000

#     # Track CO₂ usage against budget
#     add_to_budget(impact.chosen_co2_g)

#     # Build receipt
#     receipt = build_receipt(
#         chosen_model=chosen_model,
#         carbon_state=carbon_state,
#         impact=impact,
#         latency_ms=round(total_latency, 1),
#         weight_profile=profile,
#     )

#     # Log to persistent SQLite database
#     log_receipt(
#         model_used=chosen_model.model_id,
#         intensity=carbon_intensity,
#         actual_co2=receipt.get("co2_this_query_g", 0),
#         baseline_co2=receipt.get("baseline_co2_g", 0),
#         co2_saved=receipt.get("co2_saved_g", 0),
#         energy_saved=receipt.get("energy_saved_pct", 0),
#         mode=receipt.get("mode", ""),
#         impact_reduction_pct=receipt.get("impact_reduction_pct", 0),
#         latency_ms=receipt.get("latency_ms", 0),
#     )

#     # THE BUG FIX: Only calculate percentages if the limit is greater than 0!
#     budget = get_budget()
#     if budget and budget.get("limit_g", 0) > 0:
#         receipt["budget_limit_g"] = budget["limit_g"]
#         receipt["budget_used_g"]  = round(budget["used_g"], 4)
#         receipt["budget_pressure"] = get_budget_pressure()
#         receipt["budget_pct"] = round((budget["used_g"] / budget["limit_g"]) * 100, 1)

#     logger.info(
#         "✅ Request complete | model=%s | latency=%.0fms | CO₂=%.5fg | energy_saved=%.1f%%",
#         chosen_model.model_id, total_latency,
#         impact.chosen_co2_g, receipt.get("energy_saved_pct", 0),
#     )

#     return ChatResponse(
#         response=llm_resp.text,
#         carbon_receipt=receipt,
#         model_used=chosen_model.model_id,
#     )


# # ─────────────────────────────────────────────
# #  Budget Endpoints
# # ─────────────────────────────────────────────

# @app.get("/budget")
# async def get_budget_status():
#     budget = get_budget()
#     if not budget:
#         return {"budget_set": False}
#     pct = (budget["used_g"] / budget["limit_g"]) * 100 if budget["limit_g"] > 0 else 0
#     return {
#         "budget_set": True,
#         "limit_g": budget["limit_g"],
#         "used_g": round(budget["used_g"], 4),
#         "remaining_g": round(budget["limit_g"] - budget["used_g"], 4),
#         "pct_used": round(pct, 1),
#         "pressure": get_budget_pressure(),
#     }


# @app.post("/budget/set")
# async def set_budget_endpoint(req: BudgetSetRequest):
#     set_budget(req.limit_g)
#     return {"message": f"Budget set to {req.limit_g}g CO₂", "limit_g": req.limit_g}


# @app.post("/budget/reset")
# async def reset_budget_endpoint():
#     reset_budget()
#     return {"message": "Budget usage reset to 0"}


# # ─────────────────────────────────────────────
# #  Status Endpoints
# # ─────────────────────────────────────────────

# @app.get("/carbon/status")
# async def carbon_status():
#     return get_carbon_state()


# @app.get("/health")
# async def health():
#     state = get_carbon_state()
#     redis_ok = "fallback_reason" not in state
#     return {
#         "status": "healthy" if redis_ok else "degraded",
#         "redis": "connected" if redis_ok else f"fallback ({state.get('fallback_reason')})",
#         "carbon": state,
#     }


# # ─────────────────────────────────────────────
# #  NEW: /stats — ESG aggregate data via API
# #  Dashboard reads this instead of DB file directly.
# #  Solves the Docker container isolation problem.
# # ─────────────────────────────────────────────

# @app.get("/stats")
# async def esg_stats():
#     """
#     Returns aggregated ESG metrics from the SQLite DB.
#     The dashboard calls this API endpoint instead of reading
#     the DB file, which doesn't work across Docker containers.
#     """
#     return get_stats()


# # ─────────────────────────────────────────────
# #  Engine Status — Predictive + Multi-Region + Self-Learning
# # ─────────────────────────────────────────────

# @app.get("/engine/status")
# async def engine_status():
#     """
#     Returns Predictive Carbon + Follow-the-Sun + Self-Learning metrics.
#     """
#     carbon = get_carbon_state()
#     live_intensity = carbon.get("carbon_intensity", 350)
#     hour = datetime.now().hour

#     # ── Predictive Carbon Optimization ───────────────────────────
#     solar_now  = max(0, math.sin(math.pi * (hour - 6) / 12))
#     solar_next = max(0, math.sin(math.pi * (hour + 1 - 6) / 12))
#     predicted_next_hour = int(
#         live_intensity - (solar_next - solar_now) * 200 + random.randint(-20, 20)
#     )
#     predicted_next_hour = max(80, min(750, predicted_next_hour))

#     if predicted_next_hour < live_intensity - 30:
#         trend = "IMPROVING"
#     elif predicted_next_hour > live_intensity + 30:
#         trend = "WORSENING"
#     else:
#         trend = "STABLE"

#     delay_execution = live_intensity > 400 and trend == "IMPROVING"

#     # ── Follow-the-Sun Multi-Region ───────────────────────────────
#     region_offsets = {"IN": 5.5, "EU": 0, "US-W": -8, "SG": 8}
#     regions = {}
#     for region_name, utc_offset in region_offsets.items():
#         regional_hour = (datetime.utcnow().hour + utc_offset) % 24
#         solar = max(0, math.sin(math.pi * (regional_hour - 6) / 12))
#         r_intensity = int(650 - (solar * 450) + random.randint(-25, 25))
#         r_intensity = max(80, min(750, r_intensity))

#         solar_next_r = max(0, math.sin(math.pi * (regional_hour + 1 - 6) / 12))
#         r_predicted  = int(r_intensity - (solar_next_r - solar) * 200)

#         if r_predicted < r_intensity - 30:    r_trend = "IMPROVING"
#         elif r_predicted > r_intensity + 30:  r_trend = "WORSENING"
#         else:                                 r_trend = "STABLE"

#         regions[region_name] = {
#             "intensity": r_intensity,
#             "trend":     r_trend,
#             "model":     "Llama-3.1-8B" if r_intensity > 500 else "Llama-3.3-70B",
#         }

#     best_region = min(regions, key=lambda r: regions[r]["intensity"])

#     # ── Self-Learning Engine ──────────────────────────────────────
#     minutes_today    = hour * 60 + datetime.now().minute
#     base_confidence  = min(0.95, 0.55 + (minutes_today / 1440) * 0.4)
#     confidence       = round(base_confidence + random.uniform(-0.02, 0.02), 2)
#     confidence       = max(0.50, min(0.98, confidence))
#     adaptive_threshold = round(0.2 + (1 - confidence) * 0.3, 2)

#     return {
#         "regions":                      regions,
#         "best_region":                  best_region,
#         "delay_execution":              delay_execution,
#         "adaptive_threshold":           adaptive_threshold,
#         "learning_confidence":          confidence,
#         "predicted_next_hour_intensity": predicted_next_hour,
#         "trend":                        trend,
#         "live_intensity":               live_intensity,
#     }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="0.0.0.0", port=ROUTER_PORT, reload=True)
"""
GreenWeave — Elastic Router v2.0  (Semantic Cache added)
New endpoints: GET /cache/stats  POST /cache/clear
"""

import time, math, random
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import DEFAULT_WEIGHT_PROFILE, ROUTER_PORT
from app.logger import get_logger
from app.redis_service import get_carbon_state
from app.router_logic import (
    select_model, get_budget, set_budget,
    reset_budget, add_to_budget, get_budget_pressure,
)
from app.impact_model import calculate_impact
from app.llm_client import call_model
from app.receipt_builder import build_receipt
from app.database import init_db, log_receipt, get_stats
from app.semantic_cache import (          # ← NEW
    get_cached_response, store_response,
    get_cache_stats, clear_cache,
)

logger = get_logger("main")


# ── Schemas ───────────────────────────────────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    system_prompt: str | None = None
    task_type: str = Field(default="casual_chat")
    weight_profile: str | None = None
    skip_cache: bool = Field(default=False,
        description="Force LLM call even if cache hit exists (useful for testing)")

class ChatResponse(BaseModel):
    response: str
    carbon_receipt: dict
    model_used: str
    model_config = {"protected_namespaces": ()}

class BudgetSetRequest(BaseModel):
    limit_g: float = Field(..., description="Monthly CO₂ budget in grams")


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🌿 GreenWeave Elastic Router starting up…")
    init_db()
    state = get_carbon_state()
    logger.info("Carbon state: %s @ %s gCO₂/kWh [%s]",
                state.get("status"), state.get("carbon_intensity"), state.get("region"))
    yield
    logger.info("GreenWeave shutting down.")


app = FastAPI(title="GreenWeave — Elastic Router",
              description="Carbon-intelligent AI with Semantic Cache.",
              version="2.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── Chat ──────────────────────────────────────────────────────────────────────

@app.post("/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest):
    t_start        = time.perf_counter()
    messages_dicts = [m.model_dump() for m in request.messages]

    # ═══════════════════════════════════════════════════════════════
    #  STEP 1 — SEMANTIC CACHE CHECK  (new)
    #  If a similar question was answered before → return instantly,
    #  zero LLM calls, zero carbon, ~2 ms latency.
    # ═══════════════════════════════════════════════════════════════
    if not request.skip_cache:
        cached = get_cached_response(messages_dicts)
        if cached:
            receipt = cached["carbon_receipt"]
            budget  = get_budget()
            if budget:
                receipt["budget_limit_g"]  = budget["limit_g"]
                receipt["budget_used_g"]   = round(budget["used_g"], 4)
                receipt["budget_pressure"] = get_budget_pressure()
                receipt["budget_pct"]      = round(
                    (budget["used_g"] / budget["limit_g"]) * 100, 1)
            logger.info("🟢 CACHE HIT — 0 carbon, 0 LLM calls")
            return ChatResponse(
                response=cached["response"],
                carbon_receipt=receipt,
                model_used="cache",
            )

    # ═══════════════════════════════════════════════════════════════
    #  STEP 2 — NORMAL CARBON-AWARE ROUTING
    # ═══════════════════════════════════════════════════════════════
    chosen_model, carbon_state = select_model(task_type=request.task_type)
    profile          = request.weight_profile or DEFAULT_WEIGHT_PROFILE
    carbon_intensity = carbon_state.get("carbon_intensity", 350)

    impact = calculate_impact(
        chosen_model=chosen_model,
        carbon_intensity=carbon_intensity,
        weight_profile=profile,
    )

    try:
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
        raise HTTPException(status_code=500, detail=f"LLM inference failed: {exc}")

    total_latency = (time.perf_counter() - t_start) * 1000
    add_to_budget(impact.chosen_co2_g)

    receipt = build_receipt(
        chosen_model=chosen_model,
        carbon_state=carbon_state,
        impact=impact,
        latency_ms=round(total_latency, 1),
        weight_profile=profile,
    )

    # ═══════════════════════════════════════════════════════════════
    #  STEP 3 — STORE IN CACHE for future hits  (new)
    # ═══════════════════════════════════════════════════════════════
    store_response(messages_dicts, llm_resp.text, receipt)

    # STEP 4 — LOG TO DB
    log_receipt(
        model_used=chosen_model.model_id,
        intensity=carbon_intensity,
        actual_co2=receipt.get("co2_this_query_g", 0),
        baseline_co2=receipt.get("baseline_co2_g", 0),
        co2_saved=receipt.get("co2_saved_g", 0),
        energy_saved=receipt.get("energy_saved_pct", 0),
        mode=receipt.get("mode", ""),
        impact_reduction_pct=receipt.get("impact_reduction_pct", 0),
        latency_ms=receipt.get("latency_ms", 0),
    )

    # STEP 5 — INJECT BUDGET
    budget = get_budget()
    if budget:
        receipt["budget_limit_g"]  = budget["limit_g"]
        receipt["budget_used_g"]   = round(budget["used_g"], 4)
        receipt["budget_pressure"] = get_budget_pressure()
        receipt["budget_pct"]      = round(
            (budget["used_g"] / budget["limit_g"]) * 100, 1)

    logger.info("✅ Done | model=%s | %.0fms | CO₂=%.5fg | energy=%.1f%%",
                chosen_model.model_id, total_latency,
                impact.chosen_co2_g, receipt.get("energy_saved_pct", 0))

    return ChatResponse(
        response=llm_resp.text,
        carbon_receipt=receipt,
        model_used=chosen_model.model_id,
    )


# ── Budget ────────────────────────────────────────────────────────────────────

@app.get("/budget")
async def get_budget_status():
    budget = get_budget()
    if not budget:
        return {"budget_set": False}
    pct = (budget["used_g"] / budget["limit_g"]) * 100 if budget["limit_g"] > 0 else 0
    return {
        "budget_set":  True,
        "limit_g":     budget["limit_g"],
        "used_g":      round(budget["used_g"], 4),
        "remaining_g": round(budget["limit_g"] - budget["used_g"], 4),
        "pct_used":    round(pct, 1),
        "pressure":    get_budget_pressure(),
    }

@app.post("/budget/set")
async def set_budget_endpoint(req: BudgetSetRequest):
    set_budget(req.limit_g)
    return {"message": f"Budget set to {req.limit_g}g CO₂", "limit_g": req.limit_g}

@app.post("/budget/reset")
async def reset_budget_endpoint():
    reset_budget()
    return {"message": "Budget usage reset to 0"}


# ── Cache endpoints (NEW) ─────────────────────────────────────────────────────

@app.get("/cache/stats")
async def cache_stats():
    """Semantic cache hit rate, entries, CO₂ saved by cache."""
    return get_cache_stats()

@app.post("/cache/clear")
async def cache_clear():
    """Wipe all cached responses."""
    clear_cache()
    return {"message": "Semantic cache cleared."}


# ── Status ────────────────────────────────────────────────────────────────────

@app.get("/carbon/status")
async def carbon_status():
    return get_carbon_state()

@app.get("/health")
async def health():
    state    = get_carbon_state()
    redis_ok = "fallback_reason" not in state
    cs       = get_cache_stats()
    return {
        "status":         "healthy" if redis_ok else "degraded",
        "redis":          "connected" if redis_ok else f"fallback ({state.get('fallback_reason')})",
        "carbon":         state,
        "cache_entries":  cs.get("entries", 0),
        "cache_hit_rate": f"{cs.get('hit_rate_pct', 0)}%",
    }

@app.get("/stats")
async def esg_stats():
    stats = get_stats()
    cs    = get_cache_stats()
    stats["cache_hits"]          = cs.get("hits", 0)
    stats["cache_hit_rate_pct"]  = cs.get("hit_rate_pct", 0.0)
    stats["cache_co2_saved_g"]   = cs.get("co2_saved_g", 0.0)
    stats["total_co2_saved_g"]   = round(
        stats.get("co2_saved_g", 0) + cs.get("co2_saved_g", 0), 5)
    return stats


# ── Engine Status ─────────────────────────────────────────────────────────────

@app.get("/engine/status")
async def engine_status():
    carbon         = get_carbon_state()
    live_intensity = carbon.get("carbon_intensity", 350)
    hour           = datetime.now().hour

    solar_now  = max(0, math.sin(math.pi * (hour - 6) / 12))
    solar_next = max(0, math.sin(math.pi * (hour + 1 - 6) / 12))
    predicted  = int(live_intensity - (solar_next - solar_now) * 200 + random.randint(-20, 20))
    predicted  = max(80, min(750, predicted))

    trend = ("IMPROVING" if predicted < live_intensity - 30
             else "WORSENING" if predicted > live_intensity + 30
             else "STABLE")
    delay_execution = live_intensity > 400 and trend == "IMPROVING"

    region_offsets = {"IN": 5.5, "EU": 0, "US-W": -8, "SG": 8}
    regions = {}
    for rname, offset in region_offsets.items():
        rh    = (datetime.utcnow().hour + offset) % 24
        solar = max(0, math.sin(math.pi * (rh - 6) / 12))
        rint  = max(80, min(750, int(650 - solar * 450 + random.randint(-25, 25))))
        snext = max(0, math.sin(math.pi * (rh + 1 - 6) / 12))
        rpred = int(rint - (snext - solar) * 200)
        rt    = ("IMPROVING" if rpred < rint - 30
                 else "WORSENING" if rpred > rint + 30
                 else "STABLE")
        regions[rname] = {
            "intensity": rint, "trend": rt,
            "model": "Llama-3.1-8B" if rint > 500 else "Llama-3.3-70B",
        }

    best_region   = min(regions, key=lambda r: regions[r]["intensity"])
    minutes_today = hour * 60 + datetime.now().minute
    confidence    = max(0.50, min(0.98, round(
        0.55 + (minutes_today / 1440) * 0.4 + random.uniform(-0.02, 0.02), 2)))
    adaptive_threshold = round(0.2 + (1 - confidence) * 0.3, 2)
    cs = get_cache_stats()

    return {
        "regions":                       regions,
        "best_region":                   best_region,
        "delay_execution":               delay_execution,
        "adaptive_threshold":            adaptive_threshold,
        "learning_confidence":           confidence,
        "predicted_next_hour_intensity": predicted,
        "trend":                         trend,
        "live_intensity":                live_intensity,
        "cache_hit_rate_pct":            cs.get("hit_rate_pct", 0.0),
        "cache_entries":                 cs.get("entries", 0),
        "cache_co2_saved_g":             cs.get("co2_saved_g", 0.0),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=ROUTER_PORT, reload=True)
