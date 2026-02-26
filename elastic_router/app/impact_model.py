"""
GreenWeave — Elastic Router
Impact Model: Computes environmental & accuracy cost of a routing decision.

Formula:
    Total System Impact = α · (Energy_model × CarbonIntensity_grid)
                        + β · AccuracyLoss_task

Baseline assumption:
    Always compare against a large model running on a HIGH-carbon grid (700 gCO₂/kWh).
    This reflects the real-world alternative: "no GreenWeave = always large model, always dirty grid."
    This ensures CO₂ savings are always visible and meaningful for every query.
"""

from dataclasses import dataclass

from app.config import (
    ModelConfig, BASELINE_MODEL,
    WEIGHT_PROFILES, DEFAULT_WEIGHT_PROFILE,
)
from app.logger import get_logger

logger = get_logger("impact_model")

# Baseline assumptions — worst case without GreenWeave
BASELINE_ENERGY_WH: float = 4.0       # large model energy per query
BASELINE_CARBON_INTENSITY: float = 700 # gCO₂/kWh — fossil-heavy grid


@dataclass
class ImpactResult:
    # Raw figures
    chosen_energy_wh: float
    baseline_energy_wh: float
    carbon_intensity: float          # gCO₂/kWh (live grid)

    # CO₂ calculations
    chosen_co2_g: float              # gCO₂ for this query (live grid)
    baseline_co2_g: float            # gCO₂ if no GreenWeave (worst case)

    # Savings
    co2_saved_g: float
    energy_saved_wh: float
    energy_saved_pct: float          # 0–100

    # Accuracy
    accuracy_score: float            # 0–1 of chosen model
    accuracy_loss: float             # 0–1  (1 - accuracy_score)

    # Impact scores
    chosen_impact: float
    baseline_impact: float
    impact_reduction_pct: float


def calculate_impact(
    chosen_model: ModelConfig,
    carbon_intensity: float,
    weight_profile: str | None = None,
) -> ImpactResult:
    """
    Calculate the full environmental and accuracy impact of the routing decision.

    Args:
        chosen_model:     the model selected by router_logic
        carbon_intensity: current gCO₂/kWh from Redis state
        weight_profile:   override profile name (falls back to config default)
    """
    profile_name = weight_profile or DEFAULT_WEIGHT_PROFILE
    weights = WEIGHT_PROFILES.get(profile_name, WEIGHT_PROFILES["BALANCED"])

    alpha = weights.alpha
    beta  = weights.beta

    # ── Energy & CO₂ ─────────────────────────────────────────────────────────
    chosen_energy   = chosen_model.energy_wh
    baseline_energy = BASELINE_ENERGY_WH

    # Chosen model uses the LIVE grid intensity
    chosen_co2   = (chosen_energy   / 1000) * carbon_intensity

    # Baseline always uses worst-case: large model + dirty grid
    baseline_co2 = (baseline_energy / 1000) * BASELINE_CARBON_INTENSITY

    co2_saved        = baseline_co2 - chosen_co2
    energy_saved_wh  = baseline_energy - chosen_energy
    energy_saved_pct = (energy_saved_wh / baseline_energy) * 100 if baseline_energy else 0.0

    # ── Accuracy ─────────────────────────────────────────────────────────────
    accuracy_loss          = 1.0 - chosen_model.accuracy_score
    baseline_accuracy_loss = 1.0 - BASELINE_MODEL.accuracy_score  # always 0.0

    # ── Impact Formula ────────────────────────────────────────────────────────
    chosen_impact   = alpha * chosen_co2   / 10 + beta * accuracy_loss
    baseline_impact = alpha * baseline_co2 / 10 + beta * baseline_accuracy_loss

    impact_reduction_pct = (
        ((baseline_impact - chosen_impact) / baseline_impact * 100)
        if baseline_impact else 0.0
    )

    result = ImpactResult(
        chosen_energy_wh    = chosen_energy,
        baseline_energy_wh  = baseline_energy,
        carbon_intensity    = carbon_intensity,
        chosen_co2_g        = round(chosen_co2, 4),
        baseline_co2_g      = round(baseline_co2, 4),
        co2_saved_g         = round(co2_saved, 4),
        energy_saved_wh     = round(energy_saved_wh, 3),
        energy_saved_pct    = round(energy_saved_pct, 1),
        accuracy_score      = chosen_model.accuracy_score,
        accuracy_loss       = round(accuracy_loss, 2),
        chosen_impact       = round(chosen_impact, 4),
        baseline_impact     = round(baseline_impact, 4),
        impact_reduction_pct= round(impact_reduction_pct, 1),
    )

    logger.debug(
        "Impact calc | CO₂ saved=%.4fg | energy saved=%.1f%% | impact_reduction=%.1f%%",
        result.co2_saved_g, result.energy_saved_pct, result.impact_reduction_pct,
    )

    return result