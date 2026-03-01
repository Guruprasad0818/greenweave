# 🌿 GreenWeave SDK

> **Drop-in OpenAI replacement. One line change. Your entire app becomes carbon-aware.**

## Install

```bash
pip install greenweave-sdk
# or from source:
pip install -e ./greenweave_sdk
```

## Usage

```python
# BEFORE — standard OpenAI
from openai import OpenAI
client = OpenAI(api_key="sk-...")

# AFTER — GreenWeave (change ONE line)
from greenweave_sdk import GreenWeave as OpenAI
client = OpenAI(api_key="sk-...", greenweave_url="http://localhost:8000")

# Everything below is IDENTICAL — zero breaking changes
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)  # ✅ works exactly like OpenAI

# Bonus: carbon data on every response
print(response.carbon_receipt.co2_saved_g)      # grams CO₂ saved
print(response.carbon_receipt.energy_saved_pct) # % energy saved
print(response.carbon_receipt.cache_hit)         # True if served from cache
```

## What happens behind the scenes

```
Your app calls .create()
        ↓
GreenWeave SDK intercepts
        ↓
Check Semantic Cache (similarity > 0.92?)
  YES → return instantly, 0 CO₂, ~2ms ✅
  NO  ↓
Check live grid carbon intensity
        ↓
Route to optimal model:
  LOW grid  (< 250 gCO₂/kWh) → Llama 70B (full quality)
  MED grid  (250-500)         → Llama 8B  (balanced)
  HIGH grid (> 500)           → Llama 3B  (eco max)
        ↓
Return OpenAI-compatible response + carbon receipt
```

## Carbon Receipt

Every response includes a `carbon_receipt` object:

```python
response.carbon_receipt.mode                    # "ECO_LIGHT", "STANDARD", "SEMANTIC_CACHE"
response.carbon_receipt.model_used              # actual model that ran
response.carbon_receipt.grid_intensity_gco2_kwh # live grid carbon
response.carbon_receipt.co2_this_query_g        # CO₂ emitted this query
response.carbon_receipt.co2_saved_g             # CO₂ saved vs baseline
response.carbon_receipt.energy_saved_pct        # % energy saved
response.carbon_receipt.cache_hit               # True = 0 CO₂, ~2ms
response.carbon_receipt.latency_ms              # total latency
```

## Advanced Options

```python
client = OpenAI(
    api_key="sk-...",
    greenweave_url="http://localhost:8000",
    team="engineering",        # team name for leaderboard
    verbose=True,              # print carbon receipt to terminal
    timeout=60,                # request timeout in seconds
)

# Force task-specific routing
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    task_type="coding",          # casual_chat | coding | medical | legal_drafting
    weight_profile="ECO_FIRST",  # BALANCED | ECO_FIRST | ACCURACY_FIRST
    skip_cache=False,            # set True to bypass cache (testing)
)

# Direct utility methods
client.get_carbon_status()   # live grid intensity
client.get_cache_stats()     # cache hit rate, CO₂ saved
client.get_esg_stats()       # full ESG aggregate data
client.set_carbon_budget(2000)  # set 2kg monthly CO₂ budget
```

## Demo

```bash
python sdk_demo.py
```

Expected output:
```
📤 Query 1: First time asking — routes to optimal model
  ⚡ ECO_LIGHT | Model: llama-3.1-8b-instant | CO₂: 0.00014g | Saved: +0.0027g | 80% | 842ms

📤 Query 2: Similar question — SEMANTIC CACHE INTERCEPTS IT
  🧠 CACHE HIT | CO₂: 0.00000g | Energy saved: 100% | 2ms
```

## Why This Matters

Any company using OpenAI today — **zero code changes required beyond one import**.
GreenWeave integrates into existing AI infrastructure in under 60 seconds.

---
*Built for AI4Dev Hackathon | Team PS100060 | GreenWeave*
