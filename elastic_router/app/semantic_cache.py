"""
GreenWeave — Module 1: Semantic Cache
════════════════════════════════════════════════════════════
Before every LLM call, checks if a similar question was already
answered. Cache hit = 0 LLM calls, 0 CO₂, ~2ms latency.

HOW IT WORKS:
  1. Convert user query to a 384-dim embedding vector
  2. Compare against all stored embeddings via cosine similarity
  3. If similarity > 0.92 → return cached answer instantly
  4. If miss → call LLM, store result for next time

INSTALL:
  pip install sentence-transformers numpy
"""

import json
import time
import hashlib
import logging
import numpy as np

logger = logging.getLogger("semantic_cache")

# ── Config ────────────────────────────────────────────────────────────────────
SIMILARITY_THRESHOLD = 0.92     # 0–1 score. 0.92 = must be very similar
MAX_CACHE_ENTRIES    = 1000     # oldest entries trimmed beyond this
CACHE_TTL            = 86400    # 24 hours in seconds

# Redis keys (db=1 so cache is isolated from main app on db=0)
KEY_EMBEDDINGS = "gw:cache:embeddings"   # list  → [{hash, vector}]
KEY_RESPONSES  = "gw:cache:responses"    # hash  → {hash: response_json}
KEY_STATS      = "gw:cache:stats"        # hash  → {hits, misses, total}

# Baseline CO₂ for a full large-model query (used to calculate savings)
BASELINE_CO2_G = 0.00280   # 4.0Wh × 700gCO₂/kWh ÷ 1000


# ── Lazy model loader ─────────────────────────────────────────────────────────
_model = None

def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model all-MiniLM-L6-v2 …")
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("✅ Semantic cache model ready.")
        except ImportError:
            logger.warning("sentence-transformers not installed — cache disabled. Run: pip install sentence-transformers")
            _model = False   # False = disabled permanently, don't retry
    return _model


# ── Redis helper ──────────────────────────────────────────────────────────────
def _redis():
    """Return Redis client on db=1, or None if unavailable."""
    for host in ("redis", "localhost"):
        try:
            import redis as r_lib
            client = r_lib.Redis(host=host, port=6379, db=1, decode_responses=True)
            client.ping()
            return client
        except Exception:
            continue
    return None


# ── Internals ─────────────────────────────────────────────────────────────────
def _messages_to_text(messages: list[dict]) -> str:
    """Flatten messages list → single string (user turns only)."""
    return " ".join(
        m.get("content", "") for m in messages if m.get("role") == "user"
    ).strip()


def _embed(text: str):
    model = _get_model()
    if not model:
        return None
    try:
        vec = model.encode(text, normalize_embeddings=True)
        return vec.astype(np.float32)
    except Exception as e:
        logger.error("Embed error: %s", e)
        return None


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))   # vectors are already normalised


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _inc_stat(r, key: str):
    try:
        r.hincrby(KEY_STATS, key, 1)
        r.expire(KEY_STATS, CACHE_TTL)
    except Exception:
        pass


# ── Public API ────────────────────────────────────────────────────────────────

def get_cached_response(messages: list[dict]) -> dict | None:
    """
    Returns cached {response, carbon_receipt} dict if hit, else None.
    Drop-in check before every LLM call in main.py.
    """
    r = _redis()
    if not r:
        return None

    text = _messages_to_text(messages)
    if not text:
        return None

    query_vec = _embed(text)
    if query_vec is None:
        return None

    t0 = time.perf_counter()

    try:
        stored = r.lrange(KEY_EMBEDDINGS, 0, -1)
        if not stored:
            _inc_stat(r, "misses")
            return None

        best_score, best_hash = 0.0, None
        for entry_json in stored:
            try:
                e     = json.loads(entry_json)
                score = _cosine(query_vec, np.array(e["vector"], dtype=np.float32))
                if score > best_score:
                    best_score, best_hash = score, e["hash"]
            except Exception:
                continue

        if best_score >= SIMILARITY_THRESHOLD and best_hash:
            raw = r.hget(KEY_RESPONSES, best_hash)
            if raw:
                cached     = json.loads(raw)
                latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                _inc_stat(r, "hits")

                logger.info("🟢 CACHE HIT | sim=%.4f | %.1fms", best_score, latency_ms)

                receipt = {
                    "mode":                    "SEMANTIC_CACHE",
                    "model_used":              "cache",
                    "model_name":              "Semantic Cache",
                    "grid_intensity_gco2_kwh": cached.get("grid_intensity", 0),
                    "co2_this_query_g":        0.0,
                    "actual_co2_g":            0.0,
                    "baseline_co2_g":          BASELINE_CO2_G,
                    "co2_saved_g":             BASELINE_CO2_G,
                    "energy_saved_pct":        100.0,
                    "impact_reduction_pct":    100.0,
                    "latency_ms":              latency_ms,
                    "cache_hit":               True,
                    "similarity_score":        round(best_score, 4),
                }
                return {
                    "response":       cached["response"],
                    "carbon_receipt": receipt,
                    "model_used":     "cache",
                    "cache_hit":      True,
                }

        _inc_stat(r, "misses")
        return None

    except Exception as e:
        logger.error("Cache lookup error: %s", e)
        return None


def store_response(messages: list[dict], response: str, receipt: dict):
    """
    Save a query+response into the cache after every successful LLM call.
    """
    r = _redis()
    if not r:
        return

    text = _messages_to_text(messages)
    if not text:
        return

    vec = _embed(text)
    if vec is None:
        return

    try:
        h = _hash(text)

        # Store embedding
        r.rpush(KEY_EMBEDDINGS, json.dumps({"hash": h, "vector": vec.tolist()}))
        r.expire(KEY_EMBEDDINGS, CACHE_TTL)

        # Trim to max size
        length = r.llen(KEY_EMBEDDINGS)
        if length > MAX_CACHE_ENTRIES:
            r.ltrim(KEY_EMBEDDINGS, length - MAX_CACHE_ENTRIES, -1)

        # Store response
        payload = {
            "response":       response,
            "grid_intensity": receipt.get("grid_intensity_gco2_kwh", 0),
        }
        r.hset(KEY_RESPONSES, h, json.dumps(payload))
        r.expire(KEY_RESPONSES, CACHE_TTL)

        _inc_stat(r, "total")
        logger.info("💾 Cached | hash=%s | '%s…'", h, text[:40])

    except Exception as e:
        logger.error("Cache store error: %s", e)


def get_cache_stats() -> dict:
    """Return stats dict for dashboard display."""
    r = _redis()
    if not r:
        return {"hits": 0, "misses": 0, "total_stored": 0,
                "entries": 0, "hit_rate_pct": 0.0, "co2_saved_g": 0.0}
    try:
        raw     = r.hgetall(KEY_STATS)
        hits    = int(raw.get("hits",   0))
        misses  = int(raw.get("misses", 0))
        total   = int(raw.get("total",  0))
        entries = r.llen(KEY_EMBEDDINGS)
        checked = hits + misses
        hit_rate = round((hits / checked) * 100, 1) if checked > 0 else 0.0
        return {
            "hits":         hits,
            "misses":       misses,
            "total_stored": total,
            "entries":      entries,
            "hit_rate_pct": hit_rate,
            "co2_saved_g":  round(hits * BASELINE_CO2_G, 5),
        }
    except Exception as e:
        logger.error("get_cache_stats error: %s", e)
        return {"hits": 0, "misses": 0, "total_stored": 0,
                "entries": 0, "hit_rate_pct": 0.0, "co2_saved_g": 0.0}


def clear_cache():
    """Wipe all cached entries."""
    r = _redis()
    if r:
        r.delete(KEY_EMBEDDINGS, KEY_RESPONSES, KEY_STATS)
        logger.info("🗑️ Cache cleared.")
# Pre-load the model on startup to avoid async HTTP client closures
_get_model()