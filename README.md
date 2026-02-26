# 🌿 GreenWeave — Climate-Intelligent AI Infrastructure

> *The climate intelligence layer that enables sustainable, carbon-aware AI inference worldwide.*

---

## 🚀 One-Command Launch (Docker)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/greenweave.git
cd greenweave

# 2. Add your API key to .env
# Edit .env and set GROQ_API_KEY=your_key_here

# 3. Launch everything
docker-compose up --build
```

| Service | URL |
|---------|-----|
| 🌿 Dashboard | http://localhost:8501 |
| ⚡ Router API | http://localhost:8000 |
| 📖 API Docs | http://localhost:8000/docs |

---

## 🧠 What is GreenWeave?

AI systems are **carbon-blind** — they run the same heavy compute regardless of whether electricity comes from solar panels or coal plants.

GreenWeave fixes this by dynamically routing AI inference to the most climate-appropriate model based on:

- **Real-time grid carbon intensity** (gCO₂/kWh)
- **Task accuracy requirements** (coding vs casual chat)
- **Enterprise carbon budgets**

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User / Frontend                   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│           Module 4: Streamlit Dashboard              │
│    Chat UI · Carbon Receipt · Live Grid Meter        │
└──────────────────────┬──────────────────────────────┘
                       │  POST /chat/completions
┌──────────────────────▼──────────────────────────────┐
│          Module 2: Elastic Router (FastAPI)          │
│   Reads Redis → Picks Model → Calculates Impact      │
└──────────┬───────────────────────────┬──────────────┘
           │                           │
    HIGH carbon                    LOW carbon
    (fossil grid)                  (renewables)
           │                           │
    Llama-3.1-8B               Llama-3.3-70B
    (fast, efficient)          (full precision)
           │                           │
┌──────────▼───────────────────────────▼──────────────┐
│                    Groq API                          │
└─────────────────────────────────────────────────────┘
           ▲
           │ reads carbon state (<1ms)
┌──────────┴──────────────────────────────────────────┐
│         Module 1: Grid Monitor                       │
│   Simulates carbon intensity → Stores in Redis       │
└─────────────────────────────────────────────────────┘
```

---

## ⚡ Carbon Routing Logic

| Grid Status | Intensity | Model | Energy |
|-------------|-----------|-------|--------|
| 🟢 LOW | < 200 gCO₂/kWh | Llama-3.3-70B | 4.0 Wh |
| 🟡 MODERATE | 200–500 gCO₂/kWh | Llama-3.3-70B | 2.2 Wh |
| 🔴 HIGH | > 500 gCO₂/kWh | Llama-3.1-8B | 1.2 Wh |

**Result: 45–70% energy reduction per query vs always using the full model on a dirty grid.**

---

## 📁 Project Structure

```
GREENWEAVE/
│
├── grid_monitor/                  # Module 1: Carbon data ingestion
│   ├── app/
│   │   ├── __init__.py
│   │   ├── carbon_service.py      # Simulates real-time carbon intensity
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── main.py
│   │   └── redis_service.py       # Writes grid_status to Redis
│   ├── Dockerfile
│   └── requirements.txt
│
├── elastic_router/                # Module 2: Carbon-aware routing brain
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py              # Thresholds, model table, α/β weights
│   │   ├── impact_model.py        # α·Energy·Carbon + β·AccuracyLoss
│   │   ├── llm_client.py          # Groq API calls
│   │   ├── logger.py
│   │   ├── main.py                # FastAPI entry point
│   │   ├── receipt_builder.py     # Builds Carbon Receipt
│   │   ├── redis_service.py       # Reads grid_status from Redis
│   │   └── router_logic.py        # THE BRAIN: picks the right model
│   ├── Dockerfile
│   └── requirements.txt
│
├── dashboard/                     # Module 4: Streamlit UI
│   ├── dashboard.py               # Full chat UI + carbon receipt
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml             # One-command launch
├── .env                           # API keys & config
└── README.md
```

---

## 🛠 Manual Setup (without Docker)

```bash
# Terminal 1 — Grid Monitor
cd grid_monitor
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m app.main

# Terminal 2 — Elastic Router
cd elastic_router
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.main

# Terminal 3 — Dashboard
cd dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run dashboard.py
```

---

## 🌍 Impact at Scale

| Scenario | Without GreenWeave | With GreenWeave |
|----------|-------------------|-----------------|
| 1 query (HIGH grid) | 2.8 g CO₂ | 0.84 g CO₂ |
| 1M queries/day | 2.8 tons CO₂ | 0.32–0.84 tons |
| Annual | ~1,000 tons CO₂ | ~120–300 tons |

**Equivalent to removing 4–6 cars from roads per million queries.**

---

## 🔧 Environment Variables

```dotenv
# Grid Monitor
REDIS_HOST=localhost
REDIS_PORT=6379
LOW_THRESHOLD=150
MODERATE_THRESHOLD=400
POLL_INTERVAL=300
REDIS_TTL=600
LOG_LEVEL=INFO

# Elastic Router
GROQ_API_
ROUTER_PORT=8000
MAX_TOKENS=1024
WEIGHT_PROFILE=BALANCED    # BALANCED | ECO_FIRST | ACCURACY_FIRST
```

---

## 🏆 Built For

Hackathons · Climate Tech · Sustainable AI · ESG Compliance

---

*GreenWeave — Because every query has a carbon cost.*
