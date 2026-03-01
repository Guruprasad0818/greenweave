"""
GreenWeave SDK — Live Demo Script
══════════════════════════════════
Run this during your hackathon presentation to show judges:
  1. One-line integration
  2. Carbon receipt on every response
  3. Cache hit showing 0 CO₂

HOW TO RUN:
    python sdk_demo.py

REQUIREMENTS:
    pip install requests
    GreenWeave router must be running at localhost:8000
"""

# ════════════════════════════════════════════════════════════════
#  THE ONE-LINE CHANGE — This is the entire pitch
# ════════════════════════════════════════════════════════════════

# BEFORE — standard OpenAI (comment this out to switch)
# from openai import OpenAI
# client = OpenAI(api_key="sk-your-key-here")

# AFTER — GreenWeave (one line changed, everything else identical)
from greenweave_sdk import GreenWeave as OpenAI

client = OpenAI(
    api_key="sk-not-needed",               # kept for API compatibility
    greenweave_url="http://localhost:8000", # your GreenWeave router
    team="engineering",                     # for leaderboard tracking
    verbose=True,                           # print carbon receipt to terminal
)

print("=" * 60)
print("  🌿 GreenWeave SDK Demo")
print("=" * 60)

# ── Demo 1: Normal carbon-routed query ───────────────────────────
print("\n📤 Query 1: First time asking — routes to optimal model\n")

response = client.chat.completions.create(
    model="gpt-4",                    # ← ignored, GreenWeave picks the model
    messages=[
        {"role": "user", "content": "Write a Python function to check if a number is prime"}
    ],
    task_type="coding",               # ← GreenWeave uses this for routing
    weight_profile="BALANCED",
)

# ✅ Identical to OpenAI — existing code works unchanged
print("RESPONSE:")
print(response.choices[0].message.content[:300] + "...\n")

# ✅ Bonus: carbon data attached to every response
r = response.carbon_receipt
print(f"CARBON RECEIPT:")
print(f"  Mode:         {r.mode}")
print(f"  Model used:   {r.model_used}")
print(f"  CO₂ emitted:  {r.co2_this_query_g:.5f} g")
print(f"  CO₂ saved:    {r.co2_saved_g:.4f} g")
print(f"  Energy saved: {r.energy_saved_pct:.0f}%")
print(f"  Latency:      {r.latency_ms:.0f} ms")
print(f"  Cache hit:    {r.cache_hit}")

# ── Demo 2: Cache hit — THE WOW MOMENT ───────────────────────────
print("\n" + "=" * 60)
print("📤 Query 2: Similar question — SEMANTIC CACHE INTERCEPTS IT")
print("=" * 60 + "\n")

response2 = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Python code to check if a number is a prime number"}
    ],
    task_type="coding",
)

r2 = response2.carbon_receipt
print("CARBON RECEIPT:")
if r2.cache_hit:
    print(f"  🧠 SEMANTIC CACHE HIT!")
    print(f"  CO₂ emitted:    0.00000 g  ← ZERO")
    print(f"  Energy saved:   100%       ← ZERO INFERENCE")
    print(f"  Latency:        {r2.latency_ms:.0f} ms       ← INSTANT")
    print(f"  Similarity:     {r2.similarity_score:.4f}    ← matched previous query")
    print(f"\n  ✅ No LLM was called. No carbon was emitted.")
else:
    print(f"  Mode: {r2.mode} | CO₂: {r2.co2_this_query_g:.5f}g | {r2.latency_ms:.0f}ms")

# ── Demo 3: ESG stats ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("📊 Session ESG Stats")
print("=" * 60)
stats = client.get_esg_stats()
print(f"  Total queries:    {stats.get('total_queries', 0)}")
print(f"  CO₂ saved:        {stats.get('co2_saved_g', 0):.4f} g")
print(f"  Avg energy saved: {stats.get('avg_energy_saved_pct', 0):.1f}%")
print(f"  Cache hit rate:   {stats.get('cache_hit_rate_pct', 0):.1f}%")

# ── Demo 4: Grid status ───────────────────────────────────────────
print("\n" + "=" * 60)
print("🌍 Live Grid Carbon Status")
print("=" * 60)
grid = client.get_carbon_status()
print(f"  Region:    {grid.get('region', 'Unknown')}")
print(f"  Intensity: {grid.get('carbon_intensity', 0)} gCO₂/kWh")
print(f"  Status:    {grid.get('status', 'UNKNOWN')}")

print("\n" + "=" * 60)
print("  ✅ That's GreenWeave. One import. Zero other changes.")
print("  Every AI app can be carbon-aware in under 60 seconds.")
print("=" * 60 + "\n")
