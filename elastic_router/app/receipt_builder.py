"""
GreenWeave — Receipt Builder
FIXED: Signature exactly matches main.py call:
    build_receipt(chosen_model, carbon_state, impact, latency_ms, weight_profile)
FIXED: energy_saved_pct uses energy comparison (not CO2), so it's never 0.
"""

# ─── Energy per model (Wh per query) ─────────────────────────────────────────
MODEL_ENERGY_WH = {
    "llama-3.3-70b-versatile":   4.0,
    "llama-3.3-70b-specdec":     3.6,
    "llama3-70b-8192":           4.0,
    "llama-3.1-70b-versatile":   3.8,
    "gemma2-9b-it":              1.5,
    "mixtral-8x7b-32768":        2.2,
    "llama-3.1-8b-instant":      0.8,
    "llama3-8b-8192":            0.8,
    "llama-3.2-3b-preview":      0.4,
    "llama-3.2-1b-preview":      0.2,
    "gemma-7b-it":               1.2,
}

# Worst-case baseline: large model on dirtiest grid
BASELINE_ENERGY_WH        = 4.0    # Llama 70B
BASELINE_CARBON_INTENSITY = 700.0  # gCO2/kWh


def _get_energy(model_id: str) -> float:
    """Wh per query — exact match first, then size-keyword fallback."""
    if model_id in MODEL_ENERGY_WH:
        return MODEL_ENERGY_WH[model_id]
    mid = model_id.lower()
    if "70b" in mid or "65b" in mid:      return 4.0
    if "8x7b" in mid or "34b" in mid:     return 2.2
    if "13b" in mid:                       return 2.0
    if "9b" in mid or "8b" in mid:         return 1.2
    if "7b" in mid:                        return 1.0
    if "3b" in mid or "2b" in mid:         return 0.4
    if "1b" in mid:                        return 0.2
    return 1.0  # safe default


def _derive_mode(model_id: str, carbon_status: str, weight_profile: str) -> str:
    mid = model_id.lower()
    if weight_profile == "ACCURACY_FIRST":
        return "ACCURACY_FIRST"
    if weight_profile == "ECO_FIRST":
        return "ECO_MAX" if carbon_status == "HIGH" else "ECO_LIGHT"
    # BALANCED
    if carbon_status == "LOW":
        return "STANDARD"
    if carbon_status == "HIGH":
        return "ECO_MAX" if ("8b" in mid or "3b" in mid or "1b" in mid) else "ECO_STANDARD"
    return "STANDARD"


def build_receipt(
    chosen_model,
    carbon_state: dict,
    impact,
    latency_ms: float,
    weight_profile: str = "BALANCED",
) -> dict:
    """
    Build a Carbon Receipt.

    Parameters match main.py exactly:
        chosen_model  — model object with .model_id attribute
        carbon_state  — dict from get_carbon_state(): {carbon_intensity, status, region}
        impact        — ImpactResult from calculate_impact(): has .chosen_co2_g
        latency_ms    — end-to-end latency in ms
        weight_profile — "BALANCED" | "ECO_FIRST" | "ACCURACY_FIRST"
    """
    model_id         = chosen_model.model_id
    carbon_intensity = float(carbon_state.get("carbon_intensity", 350))
    carbon_status    = carbon_state.get("status", "MODERATE")

    # ── Energy values ─────────────────────────────────────────────
    chosen_energy_wh   = _get_energy(model_id)
    baseline_energy_wh = BASELINE_ENERGY_WH

    # ── CO₂ values ────────────────────────────────────────────────
    # Use impact.chosen_co2_g if available, otherwise calculate from energy
    chosen_co2_g = getattr(impact, "chosen_co2_g", None)
    if chosen_co2_g is None or chosen_co2_g == 0:
        chosen_co2_g = (chosen_energy_wh / 1000.0) * carbon_intensity

    baseline_co2_g = (baseline_energy_wh / 1000.0) * BASELINE_CARBON_INTENSITY
    co2_saved_g    = max(0.0, baseline_co2_g - chosen_co2_g)

    # ── FIXED: energy_saved_pct ───────────────────────────────────
    # Compares the two models' energy consumption directly.
    # e.g. 8B (0.8 Wh) vs 70B (4.0 Wh) baseline = 80% saved ✅
    # Old code was comparing CO₂ values near 0 → always 0% ❌
    energy_saved_pct = max(
        0.0,
        ((baseline_energy_wh - chosen_energy_wh) / baseline_energy_wh) * 100.0,
    )

    # ── Impact reduction % ────────────────────────────────────────
    impact_reduction_pct = (
        (co2_saved_g / baseline_co2_g * 100.0) if baseline_co2_g > 0 else 0.0
    )

    mode = _derive_mode(model_id, carbon_status, weight_profile)

    return {
        # Routing
        "mode":                     mode,
        "model_used":               model_id,
        "model_name":               model_id,
        "weight_profile":           weight_profile,

        # Grid
        "grid_intensity_gco2_kwh":  round(carbon_intensity, 1),
        "grid_status":              carbon_status,

        # Energy
        "chosen_energy_wh":         round(chosen_energy_wh, 3),
        "baseline_energy_wh":       round(baseline_energy_wh, 3),

        # CO₂
        "co2_this_query_g":         round(chosen_co2_g, 5),
        "actual_co2_g":             round(chosen_co2_g, 5),
        "baseline_co2_g":           round(baseline_co2_g, 5),
        "co2_saved_g":              round(co2_saved_g, 4),

        # FIXED efficiency
        "energy_saved_pct":         round(energy_saved_pct, 1),
        "impact_reduction_pct":     round(impact_reduction_pct, 1),

        # Perf
        "latency_ms":               round(latency_ms, 1),
    }
