"""
GreenWeave — Elastic Router
Config: Carbon thresholds, model routing table, impact weights
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the root GREENWEAVE folder (one level up from elastic_router)
_root = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=_root / ".env")


# ─────────────────────────────────────────────
#  Carbon Intensity Thresholds  (gCO₂/kWh)
# ─────────────────────────────────────────────
CARBON_LOW_THRESHOLD: int = 200
CARBON_HIGH_THRESHOLD: int = 500

REDIS_CARBON_KEY: str = os.getenv("REDIS_CARBON_KEY", "carbon:south_india")
REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD", None)


# ─────────────────────────────────────────────
#  Model Routing Table
# ─────────────────────────────────────────────

@dataclass
class ModelConfig:
    name: str
    provider: str
    model_id: str
    energy_wh: float
    accuracy_score: float
    api_key_env: str


MODEL_ROUTES: dict[str, ModelConfig] = {
    "LOW": ModelConfig(
        name="Llama-3-70B (Groq)",
        provider="groq",
        model_id="llama-3.3-70b-versatile",
        energy_wh=4.0,
        accuracy_score=1.0,
        api_key_env="GROQ_API_KEY",
    ),
    "MODERATE": ModelConfig(
        name="Llama-3-70B (Groq)",
        provider="groq",
       model_id="llama-3.3-70b-versatile",
        energy_wh=2.2,
        accuracy_score=0.85,
        api_key_env="GROQ_API_KEY",
    ),
    "HIGH": ModelConfig(
        name="Llama-3-8B Quantized (Groq)",
        provider="groq",
        model_id="llama-3.3-70b-versatile",
        energy_wh=1.2,
        accuracy_score=0.70,
        api_key_env="GROQ_API_KEY",
    ),
}

BASELINE_MODEL: ModelConfig = MODEL_ROUTES["LOW"]


# ─────────────────────────────────────────────
#  Impact Model Weights  (α and β)
# ─────────────────────────────────────────────

@dataclass
class ImpactWeights:
    alpha: float
    beta: float

WEIGHT_PROFILES: dict[str, ImpactWeights] = {
    "BALANCED":        ImpactWeights(alpha=0.5, beta=0.5),
    "ECO_FIRST":       ImpactWeights(alpha=0.8, beta=0.2),
    "ACCURACY_FIRST":  ImpactWeights(alpha=0.2, beta=0.8),
}

DEFAULT_WEIGHT_PROFILE: str = os.getenv("WEIGHT_PROFILE", "BALANCED")


# ─────────────────────────────────────────────
#  API Keys
# ─────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "") 
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
      # ← paste your key in .env
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

API_KEY_MAP: dict[str, str] = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "GROQ_API_KEY": GROQ_API_KEY,
    "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
}


# ─────────────────────────────────────────────
#  Router Settings
# ─────────────────────────────────────────────
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 1024))
ROUTER_PORT: int = int(os.getenv("ROUTER_PORT", 8000))
FALLBACK_CARBON_STATUS: str = "MODERATE"