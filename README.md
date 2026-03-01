# 🌿 GreenWeave — Climate-Intelligent AI Infrastructure

> *The world's first carbon-aware AI inference middleware. Route smarter. Cache smarter. Schedule smarter.*

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://docker.com)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis)](https://redis.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 One-Command Launch

```bash
# 1. Clone
git clone https://github.com/Guruprasad0818/greenweave.git
cd greenweave

# 2. Set your API key
cp .env.example .env
# Edit .env → set GROQ_API_KEY=your_key_here

# 3. Launch everything
docker-compose up --build
```

| Service | URL | Description |
|---------|-----|-------------|
| 🌿 Dashboard | http://localhost:8501 | Main chat UI + Carbon receipts |
| 🏆 Leaderboard | http://localhost:8501/leaderboard | Team carbon competition |
| 🔔 Alerts | http://localhost:8501/alerts | Webhook alert management |
| 📊 ESG Report | http://localhost:8501/esg_report | Compliance dashboard |
| ⚡ Router API | http://localhost:8000 | FastAPI backend |
| 📖 API Docs | http://localhost:8000/docs | Interactive Swagger docs |
| 🧠 Cache Stats | http://localhost:8000/cache/stats | Semantic cache analytics |

---

## 🧠 What is GreenWeave?

AI systems are **carbon-blind** — they run the same heavy compute regardless of whether electricity comes from solar panels or coal plants.

GreenWeave is a **middleware layer** that sits between your application and your AI models. It makes every inference request carbon-aware — automatically, in real time, with zero code changes needed.

```python
# BEFORE — standard OpenAI
from openai import OpenAI

# AFTER — GreenWeave (change ONE line, zero other changes)
from greenweave_sdk import GreenWeave as OpenAI

client = OpenAI(api_key="sk-...", greenweave_url="http://localhost:8000")
response = client.chat.completions.create(model="gpt-4", messages=[...])

# Everything works identically — PLUS you get:
print(response.carbon_receipt.co2_saved_g)       # grams CO₂ saved
print(response.carbon_receipt.energy_saved_pct)  # % energy saved
print(response.carbon_receipt.cache_hit)          # True = 0 CO₂, ~2ms
```

---

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Your App / GreenWeave SDK (Module 2)               │
│         from greenweave_sdk import GreenWeave as OpenAI         │
└────────────────────────────┬────────────────────────────────────┘
                             │ POST /chat/completions
┌────────────────────────────▼────────────────────────────────────┐
│                    STEP 1: SEMANTIC CACHE (Module 1)            │
│         sentence-transformers · cosine similarity > 0.92        │
│                                                                 │
│   CACHE HIT  →  Return instantly  |  0.00000g CO₂  |  ~2ms  ✅  │
│   CACHE MISS →  Continue to router ↓                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                 STEP 2: ELASTIC ROUTER (FastAPI)                │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │  Grid Monitor   │  │ Predictive Engine │  │ Multi-Region  │  │
│  │  live gCO₂/kWh  │  │ forecasts 1hr     │  │ IN/EU/US-W/SG │  │
│  │  every 30s      │  │ solar model       │  │ picks cheapest│  │
│  └────────┬────────┘  └────────┬──────────┘  └──────┬────────┘  │
│           └───────────────────┬┴─────────────────────┘          │
│                               │                                 │
│          Impact = α·(Energy × CarbonIntensity) + β·AccuracyLoss │
│                               │                                 │
│   LOW grid  < 250 gCO₂/kWh  → Llama-3.3-70B  (full quality)   │
│   MED grid  250–500          → Llama-3.1-8B   (balanced)       │
│   HIGH grid > 500            → Llama-3.1-8B   (ECO_MAX)        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      GROQ API (LLM Inference)                   │
│                 Llama-3.3-70B  ·  Llama-3.1-8B                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              STEP 3: CARBON RECEIPT + ESG LOGGING               │
│   CO₂ emitted · CO₂ saved · energy% · model · grid intensity   │
│   SQLite DB · Alert Engine · Leaderboard update                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔥 Six Advanced Modules

### 🧠 Module 1 — Semantic Cache
Checks if a similar question was already answered before calling any LLM.

```
Query → embed with all-MiniLM-L6-v2 → compare against 1000 stored vectors
Similarity > 0.92 → return cached answer instantly
```

| Metric | Value |
|--------|-------|
| CO₂ per cache hit | **0.00000g** |
| Latency per cache hit | **~2ms** |
| Expected enterprise hit rate | **30–40%** |
| Energy saved | **100%** |

### 🔌 Module 2 — SDK Wrapper
Drop-in OpenAI replacement. Change **one line** of code.

```python
# That's literally it. The rest of your codebase is unchanged.
from greenweave_sdk import GreenWeave as OpenAI
```

```bash
pip install greenweave-sdk
python greenweave_sdk/sdk_demo.py  # see it in action
```

### 🏆 Module 3 — Carbon Leaderboard
Multi-team competitive dashboard. Gamifies sustainability at the enterprise level.

```python
# Tag any request with your team name
client = GreenWeave(api_key="sk-...", team="engineering")

# Or via HTTP header
curl -H "X-GreenWeave-Team: engineering" http://localhost:8000/chat/completions
```

Live rankings update per query. Weekly trophy 🏆 to the winning team.

### 🔔 Module 4 — Carbon Alert Webhook
Auto-fires Slack/webhook alerts when grid intensity crosses thresholds.

| Level | Threshold | Action |
|-------|-----------|--------|
| 🟢 ALL_CLEAR | < 250 gCO₂/kWh | Full model quality restored |
| 🟡 WARNING | > 400 gCO₂/kWh | Switched to ECO_STANDARD |
| 🔴 CRITICAL | > 550 gCO₂/kWh | ECO_MAX activated, Slack fired |

```bash
# Register a Slack webhook — then it's fully automatic
POST /alerts/webhooks/add
{"name": "sustainability-team", "url": "https://hooks.slack.com/...", "type": "slack"}
```

### ⏳ Module 5 — Green Queue *(coming soon)*
Carbon-aware batch scheduler. Holds non-urgent jobs until the grid is clean.

### 🔬 Module 6 — Quality Validator *(coming soon)*
Async sampling validates routing decisions with real empirical accuracy data.

---

## ⚡ Carbon Routing Logic

| Grid Status | Intensity | Model | Energy | CO₂ (700g grid) |
|-------------|-----------|-------|--------|-----------------|
| 🟢 LOW | < 250 gCO₂/kWh | Llama-3.3-70B | 4.0 Wh | 2.80g |
| 🟡 MODERATE | 250–500 gCO₂/kWh | Llama-3.1-8B | 0.8 Wh | 0.56g |
| 🔴 HIGH | > 500 gCO₂/kWh | Llama-3.1-8B | 0.8 Wh | 0.56g |
| 🧠 CACHE HIT | any | none | 0 Wh | **0.00000g** |

**Result: 70–88% CO₂ reduction per query vs unoptimised baseline.**  
**With 30–40% cache hit rate: 93–98% effective reduction.**

---

## 📁 Project Structure

```
greenweave/
│
├── docker-compose.yml             # One-command launch
├── .env.example                   # API key template
├── README.md
│
├── grid_monitor/                  # Carbon data ingestion
│   ├── app/
│   │   ├── carbon_service.py      # Live grid intensity (Electricity Maps API)
│   │   ├── redis_service.py       # Writes grid_status to Redis
│   │   ├── main.py
│   │   └── config.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── elastic_router/                # Core routing brain
│   ├── app/
│   │   ├── main.py                # FastAPI entry point + all endpoints
│   │   ├── semantic_cache.py      # ← Module 1: Vector similarity cache
│   │   ├── alert_engine.py        # ← Module 4: Webhook alert system
│   │   ├── router_logic.py        # Carbon-aware model selection
│   │   ├── impact_model.py        # α·Energy·Carbon + β·AccuracyLoss
│   │   ├── receipt_builder.py     # Carbon receipt generator
│   │   ├── database.py            # SQLite ESG logging
│   │   ├── llm_client.py          # Groq API calls
│   │   ├── redis_service.py       # Grid state reader
│   │   └── config.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── dashboard/                     # Streamlit frontend
│   ├── dashboard.py               # Main chat UI + carbon receipts
│   ├── pages/
│   │   ├── esg_report.py          # ESG compliance dashboard
│   │   ├── leaderboard.py         # ← Module 3: Team carbon competition
│   │   └── alerts.py              # ← Module 4: Webhook management UI
│   ├── Dockerfile
│   └── requirements.txt
│
└── greenweave_sdk/                # ← Module 2: Drop-in OpenAI SDK
    ├── __init__.py                # GreenWeave client class
    ├── models.py                  # OpenAI-compatible response types
    ├── setup.py                   # pip install greenweave-sdk
    ├── sdk_demo.py                # Live demo script
    └── README.md
```

---

## 🌍 Impact at Scale

| Scenario | Without GreenWeave | Routing Only | Routing + Cache |
|----------|--------------------|--------------|-----------------|
| 1 query (HIGH grid) | 2.8g CO₂ | 0.56g CO₂ | 0.00g CO₂ (if cached) |
| 1M queries/day | 2.8 tons | 0.20–0.56 tons | **0.05–0.20 tons** |
| Annual | ~1,000 tons | ~120–200 tons | **~20–75 tons** |
| Equivalent | – | 4–6 cars off road | **20–40 cars off road** |

---

## 🔧 API Reference

### Chat
```bash
POST /chat/completions
{
  "messages": [{"role": "user", "content": "Hello"}],
  "task_type": "casual_chat",       # casual_chat | coding | medical | legal_drafting
  "weight_profile": "BALANCED",     # BALANCED | ECO_FIRST | ACCURACY_FIRST
  "skip_cache": false               # true to bypass semantic cache
}
```

### Cache
```bash
GET  /cache/stats     # hit rate, entries, CO₂ saved by cache
POST /cache/clear     # wipe all cached responses
```

### Budget
```bash
GET  /budget          # current usage vs limit
POST /budget/set      # {"limit_g": 2000}
POST /budget/reset    # reset usage to 0
```

### Alerts
```bash
GET  /alerts/webhooks           # list registered webhooks
POST /alerts/webhooks/add       # {"name": "slack", "url": "...", "type": "slack"}
POST /alerts/webhooks/remove    # {"name": "slack"}
POST /alerts/webhooks/test      # fire test alert immediately
GET  /alerts/history            # recent alert log
```

### Stats & Status
```bash
GET /stats              # full ESG aggregate data
GET /carbon/status      # live grid intensity
GET /engine/status      # predictive engine + multi-region + cache stats
GET /health             # system health check
GET /leaderboard        # team rankings
```

---

## 🛠 Manual Setup (without Docker)

```bash
# 1. Redis (required)
docker run -d -p 6379:6379 redis:7-alpine

# 2. Grid Monitor
cd grid_monitor
pip install -r requirements.txt
python -m app.main

# 3. Elastic Router
cd elastic_router
pip install -r requirements.txt
# Install semantic cache dependency:
pip install sentence-transformers numpy
python -m app.main

# 4. Dashboard
cd dashboard
pip install -r requirements.txt
streamlit run dashboard.py

# 5. SDK (optional)
cd greenweave_sdk
pip install -e .
python sdk_demo.py
```

---

## 🔑 Environment Variables

```dotenv
# Required
GROQ_API_KEY=gsk_your_groq_key_here

# Optional — real grid data (https://api.electricitymap.org)
ELECTRICITY_MAPS_API_KEY=your_key_here

# Router config (defaults shown)
ROUTER_PORT=8000
DEFAULT_WEIGHT_PROFILE=BALANCED
DB_PATH=/data/greenweave_esg.db
REDIS_HOST=redis
REDIS_PORT=6379
```

---

## 🧪 Running the SDK Demo

```bash
cd greenweave_sdk
pip install -e .
python sdk_demo.py
```

Expected output:
```
📤 Query 1: First time asking — routes to optimal model
  ⚡ ECO_LIGHT | Model: llama-3.1-8b | CO₂: 0.00014g | Saved: +0.0027g | 82% | 840ms

📤 Query 2: Similar question — SEMANTIC CACHE INTERCEPTS IT
  🧠 CACHE HIT | CO₂: 0.00000g | Energy saved: 100% | 2ms ⚡
```

---

## 🏆 Competitive Advantage

| Feature | AWS Bedrock | Azure OpenAI | LangChain | **GreenWeave** |
|---------|-------------|--------------|-----------|----------------|
| Real-time carbon routing | ❌ | ❌ | ❌ | ✅ |
| Semantic cache (0 CO₂ hits) | ❌ | ❌ | ❌ | ✅ |
| Carbon budget enforcement | ❌ | ❌ | ❌ | ✅ |
| Drop-in OpenAI SDK | ❌ | ❌ | ❌ | ✅ |
| Team carbon leaderboard | ❌ | ❌ | ❌ | ✅ |
| Real-time Slack alerts | ❌ | ❌ | ❌ | ✅ |
| Multi-region carbon routing | ❌ | ❌ | ❌ | ✅ |
| ESG compliance reports | ❌ | Partial | ❌ | ✅ |
| Self-learning confidence | ❌ | ❌ | ❌ | ✅ |

---

## 📈 Business Model

**SDK-Led Growth** (same strategy as Stripe, Twilio, Datadog)
1. Developer discovers via `pip install greenweave-sdk`
2. Zero switching cost — drop-in OpenAI replacement
3. Free tier → Paid ESG analytics → Enterprise licensing

**Revenue Streams**
- **SaaS API**: Per-1,000 carbon-optimised inferences
- **Enterprise Licensing**: Custom ESG reporting & compliance dashboards
- **Budget Enforcement SLA**: Guaranteed carbon budgets with overrun protection

**TAM**: Global AI inference spend projected at **$150B+ by 2030**.  
Every dollar spent on AI inference is a GreenWeave opportunity.

---

## 🏅 Built For

**AI4Dev '26 Hackathon** · Team PS100060 · PSG College of Technology

**Problem Domains**: Responsible AI · Resource Optimization · Sustainable Development · Climate Action

---

*🌿 GreenWeave — Because every query has a carbon cost. Don't choose between powerful AI and a livable planet.*
