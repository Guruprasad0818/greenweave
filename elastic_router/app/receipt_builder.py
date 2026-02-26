"""
GreenWeave — Elastic Router
Receipt Builder: Packages the routing decision + impact data
into the Carbon Receipt that gets returned alongside every AI response.

Example output:
{
    "mode": "High Carbon Mode 🔴",
    "model_used": "llama-3-8b-8192",
    "model_name": "Llama-3-8B Quantized (Groq)",
    "carbon_status": "HIGH",
    "grid_intensity_gco2_kwh": 642,
    "region": "South India Grid",
    "co2_this_query_g": 0.00084,
    "co2_saved_g": 0.00196,
    "energy_saved_pct": 70.0,
    "accuracy_score": 0.7,
    "impact_reduction_pct": 63.4,
    "weight_profile": "BALANCED",
    "latency_ms": 320.5
}
"""

from app.config import ModelConfig
from app.impact_model import ImpactResult
from app.logger import get_logger

logger = get_logger("receipt_builder")

# Status → human-readable mode label + emoji
MODE_LABELS: dict[str, str] = {
    "LOW":      "Low Carbon Mode 🟢",
    "MODERATE": "Moderate Carbon Mode 🟡",
    "HIGH":     "High Carbon Mode 🔴",
}


def build_receipt(
    chosen_model: ModelConfig,
    carbon_state: dict,
    impact: ImpactResult,
    latency_ms: float,
    weight_profile: str,
) -> dict:
    """
    Construct the Carbon Receipt dict appended to every API response.

    Args:
        chosen_model:   the ModelConfig that was used
        carbon_state:   raw dict from redis_service.get_carbon_state()
        impact:         ImpactResult from impact_model.calculate_impact()
        latency_ms:     end-to-end response latency from llm_client
        weight_profile: name of the α/β weight profile used
    """
    status = carbon_state.get("status", "UNKNOWN")
    mode_label = MODE_LABELS.get(status, f"{status} Carbon Mode")

    receipt = {
        # ── Mode & Model ─────────────────────────────────────────
        "mode": mode_label,
        "model_used": chosen_model.model_id,
        "model_name": chosen_model.name,

        # ── Grid Data ────────────────────────────────────────────
        "carbon_status": status,
        "grid_intensity_gco2_kwh": carbon_state.get("carbon_intensity"),
        "region": carbon_state.get("region", "Unknown"),
        "grid_timestamp": carbon_state.get("timestamp"),

        # ── CO₂ & Energy ─────────────────────────────────────────
        "co2_this_query_g": impact.chosen_co2_g,
        "co2_saved_g": impact.co2_saved_g,
        "energy_saved_wh": impact.energy_saved_wh,
        "energy_saved_pct": impact.energy_saved_pct,

        # ── Accuracy ─────────────────────────────────────────────
        "accuracy_score": impact.accuracy_score,
        "accuracy_loss": impact.accuracy_loss,

        # ── Impact Score ─────────────────────────────────────────
        "impact_score_chosen": impact.chosen_impact,
        "impact_score_baseline": impact.baseline_impact,
        "impact_reduction_pct": impact.impact_reduction_pct,
        "weight_profile": weight_profile,

        # ── Performance ──────────────────────────────────────────
        "latency_ms": latency_ms,

        # ── Fallback flag (helpful for debugging) ─────────────────
        "used_fallback": "fallback_reason" in carbon_state,
        "fallback_reason": carbon_state.get("fallback_reason"),
    }

    logger.debug(
        "Carbon Receipt built | mode=%s | CO₂ saved=%.5f g | energy saved=%.1f%%",
        mode_label, impact.co2_saved_g, impact.energy_saved_pct,
    )

    return receipt
