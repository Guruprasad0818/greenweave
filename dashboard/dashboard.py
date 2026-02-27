# """
# GreenWeave — Module 4: Dashboard
# Climate AI Control Center — Carbon Budget + Predictive Carbon +
# Follow-the-Sun Multi-Region + Self-Learning Engine panels.
# """

# import time
# import requests
# import streamlit as st

# ROUTER_URL = "http://elastic_router:8000"

# st.set_page_config(
#     page_title="GreenWeave AI",
#     page_icon="🌿",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

# :root {
#     --green:      #00ff88;
#     --green-dim:  #00c46a;
#     --green-dark: #003d22;
#     --yellow:     #f5c542;
#     --red:        #ff4d4d;
#     --orange:     #ff8c00;
#     --blue:       #4da6ff;
#     --bg:         #080f0a;
#     --surface:    #0e1a10;
#     --surface2:   #142018;
#     --border:     #1e3024;
#     --text:       #c8e6d0;
#     --text-dim:   #6b8f72;
#     --mono:       'Space Mono', monospace;
#     --sans:       'DM Sans', sans-serif;
# }

# html, body, [data-testid="stAppViewContainer"] {
#     background: var(--bg) !important;
#     color: var(--text) !important;
#     font-family: var(--sans) !important;
# }
# [data-testid="stSidebar"] {
#     background: var(--surface) !important;
#     border-right: 1px solid var(--border) !important;
# }
# [data-testid="stHeader"] { background: transparent !important; }
# h1, h2, h3 { font-family: var(--mono) !important; color: var(--green) !important; }
# #MainMenu, footer, header { visibility: hidden; }

# .gw-card {
#     background: var(--surface);
#     border: 1px solid var(--border);
#     border-radius: 12px;
#     padding: 16px 20px;
#     margin-bottom: 14px;
#     position: relative;
#     overflow: hidden;
#     font-family: var(--sans);
#     font-size: 13px;
#     color: var(--text-dim);
# }
# .gw-card::before {
#     content: '';
#     position: absolute;
#     top: 0; left: 0; right: 0;
#     height: 2px;
#     background: linear-gradient(90deg, var(--green), transparent);
# }
# .gw-card.yellow::before { background: linear-gradient(90deg, #f5c542, transparent); }
# .gw-card.blue::before   { background: linear-gradient(90deg, #4da6ff, transparent); }
# .gw-card.orange::before { background: linear-gradient(90deg, #ff8c00, transparent); }

# .status-badge {
#     display: inline-flex;
#     align-items: center;
#     gap: 10px;
#     font-family: var(--mono);
#     font-size: 13px;
#     font-weight: 700;
#     padding: 8px 18px;
#     border-radius: 100px;
#     letter-spacing: 1px;
# }
# .status-LOW      { background: #00ff8820; color: #00ff88; border: 1px solid #00ff8840; }
# .status-MODERATE { background: #f5c54220; color: #f5c542; border: 1px solid #f5c54240; }
# .status-HIGH     { background: #ff4d4d20; color: #ff4d4d; border: 1px solid #ff4d4d40; }

# .pulse-dot { width: 10px; height: 10px; border-radius: 50%; animation: pulse 1.8s infinite; }
# .dot-LOW      { background: #00ff88; box-shadow: 0 0 8px #00ff88; }
# .dot-MODERATE { background: #f5c542; box-shadow: 0 0 8px #f5c542; }
# .dot-HIGH     { background: #ff4d4d; box-shadow: 0 0 8px #ff4d4d; }

# @keyframes pulse {
#     0%, 100% { opacity: 1; transform: scale(1); }
#     50%       { opacity: 0.4; transform: scale(0.85); }
# }

# .bubble-user {
#     background: var(--green-dark);
#     border: 1px solid #1e4a2a;
#     border-radius: 16px 16px 4px 16px;
#     padding: 14px 18px;
#     margin: 10px 0;
#     font-family: var(--sans);
#     font-size: 15px;
#     color: var(--text);
#     max-width: 80%;
#     margin-left: auto;
# }
# .bubble-ai {
#     background: var(--surface2);
#     border: 1px solid var(--border);
#     border-radius: 16px 16px 16px 4px;
#     padding: 14px 18px;
#     margin: 10px 0;
#     font-family: var(--sans);
#     font-size: 15px;
#     color: var(--text);
#     max-width: 90%;
#     line-height: 1.6;
# }
# .bubble-label {
#     font-family: var(--mono);
#     font-size: 10px;
#     letter-spacing: 1px;
#     color: var(--text-dim);
#     margin-bottom: 5px;
# }

# .receipt {
#     background: #050d07;
#     border: 1px solid var(--green-dark);
#     border-radius: 10px;
#     padding: 16px 20px;
#     margin-top: 12px;
#     font-family: var(--mono);
#     font-size: 12px;
# }
# .receipt-title {
#     color: var(--green);
#     font-size: 11px;
#     letter-spacing: 2px;
#     font-weight: 700;
#     margin-bottom: 12px;
#     text-transform: uppercase;
# }
# .receipt-row {
#     display: flex;
#     justify-content: space-between;
#     padding: 4px 0;
#     border-bottom: 1px dashed #1a2e1e;
#     color: var(--text-dim);
# }
# .receipt-row span:last-child { color: var(--text); }
# .receipt-row.highlight span:last-child { color: var(--green); font-weight: 700; }
# .receipt-row.warning span:last-child { color: #ff8c00; font-weight: 700; }
# .receipt-row.danger span:last-child { color: #ff4d4d; font-weight: 700; }

# .meter-wrap { margin: 16px 0 8px; }
# .meter-label { font-family: var(--mono); font-size: 11px; color: var(--text-dim); margin-bottom: 6px; letter-spacing: 1px; }
# .meter-track { height: 8px; background: #1a2e1e; border-radius: 100px; overflow: hidden; }
# .meter-fill { height: 100%; border-radius: 100px; transition: width 1s ease; }

# .stat-box {
#     background: var(--surface2);
#     border: 1px solid var(--border);
#     border-radius: 10px;
#     padding: 16px;
#     text-align: center;
# }
# .stat-value { font-family: var(--mono); font-size: 26px; font-weight: 700; color: var(--green); line-height: 1; }
# .stat-label { font-family: var(--sans); font-size: 12px; color: var(--text-dim); margin-top: 6px; }

# .budget-card {
#     background: var(--surface);
#     border: 1px solid var(--border);
#     border-radius: 12px;
#     padding: 18px 20px;
#     margin-bottom: 14px;
#     position: relative;
#     overflow: hidden;
# }
# .budget-card::before {
#     content: '';
#     position: absolute;
#     top: 0; left: 0; right: 0;
#     height: 2px;
#     background: linear-gradient(90deg, #f5c542, transparent);
# }

# .region-row {
#     display: flex;
#     justify-content: space-between;
#     align-items: center;
#     padding: 6px 0;
#     border-bottom: 1px solid var(--border);
#     font-family: var(--mono);
#     font-size: 11px;
# }
# .region-row:last-child { border-bottom: none; }

# [data-testid="stTextInput"] input {
#     background: var(--surface2) !important;
#     border: 1px solid var(--border) !important;
#     color: var(--text) !important;
#     border-radius: 10px !important;
#     font-family: var(--sans) !important;
# }
# [data-testid="stTextInput"] input:focus {
#     border-color: var(--green) !important;
#     box-shadow: 0 0 0 2px #00ff8820 !important;
# }
# [data-testid="baseButton-primary"] {
#     background: var(--green) !important;
#     color: #000 !important;
#     border: none !important;
#     font-family: var(--mono) !important;
#     font-weight: 700 !important;
#     border-radius: 10px !important;
# }
# [data-testid="baseButton-secondary"] {
#     background: transparent !important;
#     color: var(--text-dim) !important;
#     border: 1px solid var(--border) !important;
#     font-family: var(--mono) !important;
#     border-radius: 10px !important;
# }
# [data-testid="stSelectbox"] > div > div {
#     background: var(--surface2) !important;
#     border-color: var(--border) !important;
#     color: var(--text) !important;
# }
# [data-testid="stNumberInput"] input {
#     background: var(--surface2) !important;
#     border-color: var(--border) !important;
#     color: var(--text) !important;
#     border-radius: 10px !important;
# }

# ::-webkit-scrollbar { width: 4px; }
# ::-webkit-scrollbar-track { background: var(--bg); }
# ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

# .gw-divider { border: none; border-top: 1px solid var(--border); margin: 18px 0; }
# </style>
# """, unsafe_allow_html=True)


# # ─────────────────────────────────────────────────────────────────────────────
# #  Session State
# # ─────────────────────────────────────────────────────────────────────────────
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "total_co2_saved" not in st.session_state:
#     st.session_state.total_co2_saved = 0.0
# if "total_queries" not in st.session_state:
#     st.session_state.total_queries = 0
# if "total_energy_saved_pct" not in st.session_state:
#     st.session_state.total_energy_saved_pct = []


# # ─────────────────────────────────────────────────────────────────────────────
# #  Helpers
# # ─────────────────────────────────────────────────────────────────────────────
# def get_carbon_status():
#     try:
#         r = requests.get(f"{ROUTER_URL}/carbon/status", timeout=2)
#         return r.json()
#     except:
#         return {"status": "UNKNOWN", "carbon_intensity": 0, "region": "Offline"}

# def get_health():
#     try:
#         r = requests.get(f"{ROUTER_URL}/health", timeout=2)
#         return r.json()
#     except:
#         return {"status": "offline"}

# def get_budget():
#     try:
#         r = requests.get(f"{ROUTER_URL}/budget", timeout=2)
#         return r.json()
#     except:
#         return {"budget_set": False}

# def get_engine_status():
#     try:
#         r = requests.get(f"{ROUTER_URL}/engine/status", timeout=2)
#         return r.json()
#     except:
#         return {}

# def set_budget(limit_g: float):
#     requests.post(f"{ROUTER_URL}/budget/set", json={"limit_g": limit_g}, timeout=2)

# def reset_budget():
#     requests.post(f"{ROUTER_URL}/budget/reset", timeout=2)

# def send_message(messages, task_type, weight_profile):
#     payload = {"messages": messages, "task_type": task_type, "weight_profile": weight_profile}
#     r = requests.post(f"{ROUTER_URL}/chat/completions", json=payload, timeout=60)
#     r.raise_for_status()
#     return r.json()

# def status_color(status):
#     return {"LOW": "#00ff88", "MODERATE": "#f5c542", "HIGH": "#ff4d4d"}.get(status, "#6b8f72")

# def status_emoji(status):
#     return {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🔴"}.get(status, "⚪")

# def trend_color(t):
#     return {"IMPROVING": "#00ff88", "STABLE": "#f5c542", "WORSENING": "#ff4d4d"}.get(t, "#6b8f72")

# def trend_arrow(t):
#     return {"IMPROVING": "↓", "STABLE": "→", "WORSENING": "↑"}.get(t, "–")

# def budget_color(pct):
#     if pct >= 100: return "#ff4d4d"
#     if pct >= 90:  return "#ff4d4d"
#     if pct >= 70:  return "#ff8c00"
#     return "#00ff88"

# def pressure_label(pressure):
#     return {
#         "NONE":     "No Budget Set",
#         "LOW":      "✅ On Track",
#         "MEDIUM":   "⚠️ 70%+ Used",
#         "HIGH":     "🔴 90%+ Used — Downgrading Models",
#         "EXCEEDED": "🚫 Budget Exceeded — Minimum Mode",
#     }.get(pressure, pressure)


# # ─────────────────────────────────────────────────────────────────────────────
# #  Sidebar
# # ─────────────────────────────────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown('<div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:#00ff88;">🌿 GreenWeave</div>', unsafe_allow_html=True)
#     st.markdown('<div style="font-family:DM Sans,sans-serif;font-size:13px;color:#6b8f72;">Climate AI Control Center</div>', unsafe_allow_html=True)
#     st.markdown('<hr class="gw-divider">', unsafe_allow_html=True)

#     # ── Live Grid Status ──────────────────────────────────────────
#     carbon = get_carbon_status()
#     status = carbon.get("status", "UNKNOWN")
#     intensity = carbon.get("carbon_intensity", 0)
#     region = carbon.get("region", "Unknown")
#     fill_pct = min(100.0, (intensity / 800) * 100)

#     st.markdown(f"""
#     <div class="gw-card">
#         <div style="font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--text-dim);margin-bottom:12px;">LIVE GRID STATUS</div>
#         <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
#             <div class="pulse-dot dot-{status}"></div>
#             <span class="status-badge status-{status}">{status_emoji(status)} {status}</span>
#         </div>
#         <div class="meter-wrap">
#             <div class="meter-label">GRID INTENSITY</div>
#             <div class="meter-track">
#                 <div class="meter-fill" style="width:{fill_pct:.1f}%;background:linear-gradient(90deg,#ff4d4d,#f5c542,#00ff88);"></div>
#             </div>
#         </div>
#         <div style="font-family:var(--mono);font-size:20px;font-weight:700;color:{status_color(status)};margin-top:10px;">
#             {intensity} <span style="font-size:12px;color:var(--text-dim)">gCO₂/kWh</span>
#         </div>
#         <div style="font-family:var(--sans);font-size:11px;color:var(--text-dim);margin-top:6px;">📍 {region}</div>
#     </div>
#     """, unsafe_allow_html=True)

#     # ── Intelligent Engine Panel ──────────────────────────────────
#     engine = get_engine_status()
#     if engine:
#         best_region = engine.get("best_region", "-")
#         delay       = engine.get("delay_execution", False)
#         adaptive    = engine.get("adaptive_threshold", 0)
#         confidence  = engine.get("learning_confidence", 0)
#         trend       = engine.get("trend", "STABLE")
#         predicted   = engine.get("predicted_next_hour_intensity", intensity)
#         regions     = engine.get("regions", {})
#         delay_color = "#ff8c00" if delay else "#00ff88"
#         delay_text  = "⏳ WAITING FOR CLEAN GRID" if delay else "⚡ EXECUTING NOW"

#         st.markdown(f"""
#         <div class="gw-card blue">
#             <div style="font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--text-dim);margin-bottom:12px;">🌍 INTELLIGENT ENGINE</div>
#             <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);">
#                 <span>Carbon Trend</span>
#                 <span style="color:{trend_color(trend)};font-family:var(--mono);">{trend_arrow(trend)} {trend}</span>
#             </div>
#             <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);">
#                 <span>Predicted Next Hour</span>
#                 <span style="color:#4da6ff;font-family:var(--mono);">{predicted} gCO₂</span>
#             </div>
#             <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);">
#                 <span>Best Region</span>
#                 <span style="color:#00ff88;font-family:var(--mono);">🌱 {best_region}</span>
#             </div>
#             <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);">
#                 <span>Delay Execution</span>
#                 <span style="color:{delay_color};font-family:var(--mono);font-size:10px;">{delay_text}</span>
#             </div>
#             <div style="display:flex;justify-content:space-between;padding:5px 0;">
#                 <span>Adaptive Threshold</span>
#                 <span style="color:#00ff88;font-family:var(--mono);">{adaptive}</span>
#             </div>
#             <div style="margin-top:12px;">
#                 <div style="font-family:var(--mono);font-size:10px;color:var(--text-dim);margin-bottom:6px;">SELF-LEARNING CONFIDENCE</div>
#                 <div class="meter-track">
#                     <div class="meter-fill" style="width:{confidence*100:.0f}%;background:linear-gradient(90deg,#003d22,#00ff88);"></div>
#                 </div>
#                 <div style="text-align:right;font-size:11px;color:#00ff88;margin-top:4px;">{confidence*100:.0f}%</div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#         # ── Multi-Region Comparison ───────────────────────────────
#         if regions:
#             st.markdown("""
#             <div class="gw-card orange">
#                 <div style="font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--text-dim);margin-bottom:8px;">🌎 MULTI-REGION COMPARISON</div>
#             </div>
#             """, unsafe_allow_html=True)
#             for r_name, r_data in regions.items():
#                 r_int   = r_data.get("intensity", 0)
#                 r_trend = r_data.get("trend", "STABLE")
#                 is_best = "⭐ " if r_name == best_region else ""
#                 name_color = "#00ff88" if r_name == best_region else "var(--text)"
#                 st.markdown(f"""
#                 <div style="display:flex;justify-content:space-between;align-items:center;
#                     padding:6px 0;border-bottom:1px solid #1e3024;font-family:'Space Mono',monospace;font-size:11px;">
#                     <span style="color:{name_color};">{is_best}{r_name}</span>
#                     <span style="color:#c8e6d0;">{r_int} gCO₂</span>
#                     <span style="color:{trend_color(r_trend)};">{trend_arrow(r_trend)} {r_trend}</span>
#                 </div>
#                 """, unsafe_allow_html=True)

#     # ── Carbon Budget Mode ────────────────────────────────────────
#     st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;letter-spacing:2px;color:#f5c542;margin-bottom:10px;">⚡ CARBON BUDGET MODE</div>', unsafe_allow_html=True)

#     budget = get_budget()
#     budget_set = budget.get("budget_set", False)

#     if budget_set:
#         limit     = budget.get("limit_g", 0)
#         used      = budget.get("used_g", 0)
#         remaining = budget.get("remaining_g", 0)
#         pct       = budget.get("pct_used", 0)
#         pressure  = budget.get("pressure", "NONE")
#         b_color   = budget_color(pct)

#         st.markdown(f"""
#         <div class="budget-card">
#             <div style="font-family:var(--mono);font-size:10px;letter-spacing:2px;color:#f5c542;margin-bottom:12px;">MONTHLY BUDGET</div>
#             <div class="meter-wrap">
#                 <div class="meter-label">USAGE: {pct:.1f}%</div>
#                 <div class="meter-track">
#                     <div class="meter-fill" style="width:{min(pct,100):.1f}%;background:{b_color};"></div>
#                 </div>
#             </div>
#             <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px;">
#                 <div class="stat-box">
#                     <div class="stat-value" style="font-size:16px;color:{b_color};">{used:.2f}g</div>
#                     <div class="stat-label">Used</div>
#                 </div>
#                 <div class="stat-box">
#                     <div class="stat-value" style="font-size:16px;">{remaining:.2f}g</div>
#                     <div class="stat-label">Remaining</div>
#                 </div>
#             </div>
#             <div style="font-family:var(--mono);font-size:11px;color:{b_color};margin-top:12px;text-align:center;">
#                 {pressure_label(pressure)}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#         if st.button("↺ Reset Usage", use_container_width=True):
#             reset_budget()
#             st.rerun()
#         if st.button("✕ Remove Budget", use_container_width=True):
#             reset_budget()
#             st.rerun()
#     else:
#         st.markdown('<div style="font-family:DM Sans,sans-serif;font-size:12px;color:#6b8f72;margin-bottom:10px;">Set a monthly CO₂ limit. GreenWeave will automatically route to smaller models as you approach the limit.</div>', unsafe_allow_html=True)
#         budget_limit = st.number_input(
#             "Budget (grams CO₂)",
#             min_value=100.0, max_value=100000.0, value=2000.0, step=100.0,
#             label_visibility="collapsed",
#         )
#         if st.button("🎯 Set Budget", type="primary", use_container_width=True):
#             set_budget(budget_limit)
#             st.success(f"Budget set: {budget_limit}g CO₂")
#             st.rerun()

#     st.markdown('<hr class="gw-divider">', unsafe_allow_html=True)

#     # ── Session Impact ────────────────────────────────────────────
#     avg_energy = (
#         sum(st.session_state.total_energy_saved_pct) / len(st.session_state.total_energy_saved_pct)
#         if st.session_state.total_energy_saved_pct else 0
#     )
#     st.markdown(f"""
#     <div class="gw-card">
#         <div style="font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--text-dim);margin-bottom:14px;">SESSION IMPACT</div>
#         <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
#             <div class="stat-box">
#                 <div class="stat-value">{st.session_state.total_queries}</div>
#                 <div class="stat-label">Queries</div>
#             </div>
#             <div class="stat-box">
#                 <div class="stat-value">{st.session_state.total_co2_saved:.3f}</div>
#                 <div class="stat-label">gCO₂ saved</div>
#             </div>
#             <div class="stat-box" style="grid-column:span 2;">
#                 <div class="stat-value">{avg_energy:.0f}%</div>
#                 <div class="stat-label">Avg energy saved</div>
#             </div>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

#     st.markdown('<hr class="gw-divider">', unsafe_allow_html=True)

#     # ── Routing Settings ──────────────────────────────────────────
#     st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;letter-spacing:2px;color:#6b8f72;margin-bottom:10px;">ROUTING SETTINGS</div>', unsafe_allow_html=True)
#     task_type      = st.selectbox("Task Type", ["casual_chat", "summarization", "coding", "legal_drafting", "medical"])
#     weight_profile = st.selectbox("Weight Profile", ["BALANCED", "ECO_FIRST", "ACCURACY_FIRST"])

#     st.markdown('<hr class="gw-divider">', unsafe_allow_html=True)

#     health    = get_health()
#     router_ok = health.get("status") != "offline"
#     redis_ok  = "connected" in str(health.get("redis", ""))
#     engine_ok = bool(engine)

#     st.markdown(f"""
#     <div style="font-family:Space Mono,monospace;font-size:11px;">
#         <div style="display:flex;justify-content:space-between;padding:4px 0;color:#6b8f72;">
#             <span>ROUTER</span>
#             <span style="color:{'#00ff88' if router_ok else '#ff4d4d'}">{'● ONLINE' if router_ok else '● OFFLINE'}</span>
#         </div>
#         <div style="display:flex;justify-content:space-between;padding:4px 0;color:#6b8f72;">
#             <span>REDIS</span>
#             <span style="color:{'#00ff88' if redis_ok else '#f5c542'}">{'● CONNECTED' if redis_ok else '● FALLBACK'}</span>
#         </div>
#         <div style="display:flex;justify-content:space-between;padding:4px 0;color:#6b8f72;">
#             <span>ENGINE</span>
#             <span style="color:{'#00ff88' if engine_ok else '#ff4d4d'}">{'● ACTIVE' if engine_ok else '● OFFLINE'}</span>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

#     if st.button("↺  Refresh Status", use_container_width=True):
#         st.rerun()
#     if st.button("🗑  Clear Chat", use_container_width=True):
#         st.session_state.messages = []
#         st.session_state.total_co2_saved = 0.0
#         st.session_state.total_queries = 0
#         st.session_state.total_energy_saved_pct = []
#         st.rerun()


# # ─────────────────────────────────────────────────────────────────────────────
# #  Main Chat Area
# # ─────────────────────────────────────────────────────────────────────────────
# st.markdown("""
# <div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">
#     <div>
#         <div style="font-family:'Space Mono',monospace;font-size:28px;font-weight:700;color:#00ff88;line-height:1;">🌿 GreenWeave</div>
#         <div style="font-family:'DM Sans',sans-serif;font-size:14px;color:#6b8f72;margin-top:4px;">
#             Climate AI Control Center &nbsp;·&nbsp; Predictive · Multi-Region · Self-Learning
#         </div>
#     </div>
# </div>
# <hr class="gw-divider">
# """, unsafe_allow_html=True)

# if not st.session_state.messages:
#     st.markdown("""
#     <div style="text-align:center;padding:60px 20px;color:#6b8f72;">
#         <div style="font-size:48px;margin-bottom:16px;">🌿</div>
#         <div style="font-family:Space Mono,monospace;font-size:14px;color:#00ff88;margin-bottom:8px;">GREENWEAVE READY</div>
#         <div style="font-family:DM Sans,sans-serif;font-size:13px;max-width:440px;margin:0 auto;line-height:1.7;">
#             Every response is routed using predictive carbon intelligence,
#             multi-region comparison, and self-learning adaptive thresholds.
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

# for msg in st.session_state.messages:
#     if msg["role"] == "user":
#         st.markdown(f'<div class="bubble-label" style="text-align:right;">YOU</div><div class="bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
#     elif msg["role"] == "assistant":
#         receipt      = msg.get("receipt", {})
#         mode         = receipt.get("mode", "")
#         model_name   = receipt.get("model_name", receipt.get("model_used", ""))
#         co2_saved    = receipt.get("co2_saved_g", 0)
#         energy_pct   = receipt.get("energy_saved_pct", 0)
#         intensity_val = receipt.get("grid_intensity_gco2_kwh", 0)
#         impact_red   = receipt.get("impact_reduction_pct", 0)
#         latency      = receipt.get("latency_ms", 0)
#         co2_this     = receipt.get("co2_this_query_g", 0)
#         b_limit      = receipt.get("budget_limit_g")
#         b_used       = receipt.get("budget_used_g")
#         b_pct        = receipt.get("budget_pct")
#         b_pressure   = receipt.get("budget_pressure", "NONE")

#         st.markdown(f'<div class="bubble-label">GREENWEAVE AI</div><div class="bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)

#         if receipt:
#             budget_row = ""
#             if b_limit:
#                 b_color_class = "danger" if b_pct >= 90 else ("warning" if b_pct >= 70 else "highlight")
#                 budget_row = f'<div class="receipt-row" style="margin-top:8px;border-top:1px solid #1e3024;padding-top:8px;"><span>Budget Used</span><span>{b_used:.4f}g / {b_limit}g</span></div><div class="receipt-row {b_color_class}"><span>Budget %</span><span>{b_pct:.1f}% — {pressure_label(b_pressure)}</span></div>'

#             html_block = f"""
# <div class="receipt">
# <div class="receipt-title">⚡ Carbon Receipt</div>
# <div class="receipt-row highlight"><span>Mode</span><span>{mode}</span></div>
# <div class="receipt-row"><span>Model Used</span><span>{model_name}</span></div>
# <div class="receipt-row"><span>Grid Intensity</span><span>{intensity_val} gCO₂/kWh</span></div>
# <div class="receipt-row"><span>CO₂ This Query</span><span>{co2_this:.5f} g</span></div>
# <div class="receipt-row highlight"><span>CO₂ Saved</span><span>+{co2_saved:.4f} g</span></div>
# <div class="receipt-row highlight"><span>Energy Saved</span><span>{energy_pct:.0f}%</span></div>
# <div class="receipt-row"><span>Impact Reduction</span><span>{impact_red:.1f}%</span></div>
# <div class="receipt-row"><span>Latency</span><span>{latency:.0f} ms</span></div>
# {budget_row}
# <div class="meter-wrap" style="margin-top:14px;">
# <div class="meter-label">ENERGY EFFICIENCY</div>
# <div class="meter-track">
# <div class="meter-fill" style="width:{energy_pct}%;background:linear-gradient(90deg,#003d22,#00ff88);"></div>
# </div>
# <div style="text-align:right;font-size:11px;color:#00ff88;margin-top:4px;">{energy_pct:.0f}% saved vs full model on dirty grid</div>
# </div>
# </div>
# """
#             st.markdown(html_block, unsafe_allow_html=True)


# # ─────────────────────────────────────────────────────────────────────────────
# #  Input
# # ─────────────────────────────────────────────────────────────────────────────
# st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
# col1, col2 = st.columns([5, 1])
# with col1:
#     user_input = st.text_input(
#         label="prompt",
#         label_visibility="collapsed",
#         placeholder="Ask anything — GreenWeave routes using predictive carbon intelligence…",
#         key="user_input",
#     )
# with col2:
#     send = st.button("Send →", type="primary", use_container_width=True)

# if send and user_input.strip():
#     st.session_state.messages.append({"role": "user", "content": user_input.strip()})

#     api_messages = [
#         {"role": m["role"], "content": m["content"]}
#         for m in st.session_state.messages
#         if m["role"] in ("user", "assistant")
#     ]

#     with st.spinner("🌿 Routing via predictive carbon intelligence…"):
#         try:
#             result        = send_message(api_messages, task_type, weight_profile)
#             response_text = result.get("response", "")
#             receipt       = result.get("carbon_receipt", {})

#             st.session_state.messages.append({
#                 "role": "assistant",
#                 "content": response_text,
#                 "receipt": receipt,
#             })

#             st.session_state.total_queries += 1
#             st.session_state.total_co2_saved += receipt.get("co2_saved_g", 0)
#             st.session_state.total_energy_saved_pct.append(receipt.get("energy_saved_pct", 0))
            
#             st.rerun()

#         except requests.exceptions.ConnectionError:
#             st.error("⚠️ Cannot reach the Elastic Router at elastic_router:8000")
#         except Exception as e:
#             st.error(f"⚠️ Error: {str(e)}")
"""
GreenWeave — Module 4: Dashboard
Climate AI Control Center — Carbon Budget + Predictive Carbon +
Follow-the-Sun Multi-Region + Self-Learning Engine panels.
"""

import time
import requests
import streamlit as st

ROUTER_URL = "http://elastic_router:8000"

st.set_page_config(
    page_title="GreenWeave AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --green:      #00ff88;
    --green-dim:  #00c46a;
    --green-dark: #003d22;
    --yellow:     #f5c542;
    --red:        #ff4d4d;
    --orange:     #ff8c00;
    --blue:       #4da6ff;
    --bg:         #080f0a;
    --surface:    #0e1a10;
    --surface2:   #142018;
    --border:     #1e3024;
    --text:       #c8e6d0;
    --text-dim:   #6b8f72;
    --mono:       'Space Mono', monospace;
    --sans:       'DM Sans', sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
h1, h2, h3 { font-family: var(--mono) !important; color: var(--green) !important; }
#MainMenu, footer, header { visibility: hidden; }

.gw-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
    font-family: var(--sans);
    font-size: 13px;
    color: var(--text-dim);
}
.gw-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--green), transparent);
}
.gw-card.yellow::before { background: linear-gradient(90deg, #f5c542, transparent); }
.gw-card.blue::before   { background: linear-gradient(90deg, #4da6ff, transparent); }
.gw-card.orange::before { background: linear-gradient(90deg, #ff8c00, transparent); }

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-family: var(--mono);
    font-size: 13px;
    font-weight: 700;
    padding: 8px 18px;
    border-radius: 100px;
    letter-spacing: 1px;
}
.status-LOW      { background: #00ff8820; color: #00ff88; border: 1px solid #00ff8840; }
.status-MODERATE { background: #f5c54220; color: #f5c542; border: 1px solid #f5c54240; }
.status-HIGH     { background: #ff4d4d20; color: #ff4d4d; border: 1px solid #ff4d4d40; }

.pulse-dot { width: 10px; height: 10px; border-radius: 50%; animation: pulse 1.8s infinite; }
.dot-LOW      { background: #00ff88; box-shadow: 0 0 8px #00ff88; }
.dot-MODERATE { background: #f5c542; box-shadow: 0 0 8px #f5c542; }
.dot-HIGH     { background: #ff4d4d; box-shadow: 0 0 8px #ff4d4d; }

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.85); }
}

.bubble-user {
    background: var(--green-dark);
    border: 1px solid #1e4a2a;
    border-radius: 16px 16px 4px 16px;
    padding: 14px 18px;
    margin: 10px 0;
    font-family: var(--sans);
    font-size: 15px;
    color: var(--text);
    max-width: 80%;
    margin-left: auto;
}
.bubble-ai {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 16px 16px 16px 4px;
    padding: 14px 18px;
    margin: 10px 0;
    font-family: var(--sans);
    font-size: 15px;
    color: var(--text);
    max-width: 90%;
    line-height: 1.6;
}
.bubble-label {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 1px;
    color: var(--text-dim);
    margin-bottom: 5px;
}

.receipt {
    background: #050d07;
    border: 1px solid var(--green-dark);
    border-radius: 10px;
    padding: 16px 20px;
    margin-top: 12px;
    font-family: var(--mono);
    font-size: 12px;
}
.receipt-title {
    color: var(--green);
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 700;
    margin-bottom: 12px;
    text-transform: uppercase;
}
.receipt-row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px dashed #1a2e1e;
    color: var(--text-dim);
}
.receipt-row span:last-child { color: var(--text); }
.receipt-row.highlight span:last-child { color: var(--green); font-weight: 700; }
.receipt-row.warning span:last-child { color: #ff8c00; font-weight: 700; }
.receipt-row.danger span:last-child { color: #ff4d4d; font-weight: 700; }

.meter-wrap { margin: 16px 0 8px; }
.meter-label { font-family: var(--mono); font-size: 11px; color: var(--text-dim); margin-bottom: 6px; letter-spacing: 1px; }
.meter-track { height: 8px; background: #1a2e1e; border-radius: 100px; overflow: hidden; }
.meter-fill { height: 100%; border-radius: 100px; transition: width 1s ease; }

.stat-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.stat-value { font-family: var(--mono); font-size: 26px; font-weight: 700; color: var(--green); line-height: 1; }
.stat-label { font-family: var(--sans); font-size: 12px; color: var(--text-dim); margin-top: 6px; }

.budget-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
}
.budget-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #f5c542, transparent);
}

.region-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid var(--border);
    font-family: var(--mono);
    font-size: 11px;
}
.region-row:last-child { border-bottom: none; }

[data-testid="stTextInput"] input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-family: var(--sans) !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 2px #00ff8820 !important;
}
[data-testid="baseButton-primary"] {
    background: var(--green) !important;
    color: #000 !important;
    border: none !important;
    font-family: var(--mono) !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
}
[data-testid="baseButton-secondary"] {
    background: transparent !important;
    color: var(--text-dim) !important;
    border: 1px solid var(--border) !important;
    font-family: var(--mono) !important;
    border-radius: 10px !important;
}
[data-testid="stSelectbox"] > div > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}
[data-testid="stNumberInput"] input {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

.gw-divider { border: none; border-top: 1px solid var(--border); margin: 18px 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Session State
# ─────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_co2_saved" not in st.session_state:
    st.session_state.total_co2_saved = 0.0
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "total_energy_saved_pct" not in st.session_state:
    st.session_state.total_energy_saved_pct = []


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────
def get_carbon_status():
    try:
        r = requests.get(f"{ROUTER_URL}/carbon/status", timeout=2)
        return r.json()
    except:
        return {"status": "UNKNOWN", "carbon_intensity": 0, "region": "Offline"}

def get_health():
    try:
        r = requests.get(f"{ROUTER_URL}/health", timeout=2)
        return r.json()
    except:
        return {"status": "offline"}

def get_budget():
    try:
        r = requests.get(f"{ROUTER_URL}/budget", timeout=2)
        return r.json()
    except:
        return {"budget_set": False}

def get_engine_status():
    try:
        r = requests.get(f"{ROUTER_URL}/engine/status", timeout=2)
        return r.json()
    except:
        return {}

def set_budget(limit_g: float):
    requests.post(f"{ROUTER_URL}/budget/set", json={"limit_g": limit_g}, timeout=2)

def reset_budget():
    # Force usage to 0 by re-setting the same limit!
    b = get_budget()
    if b and b.get("limit_g", 0) > 0:
        set_budget(b["limit_g"])

def remove_budget():
    # Force router to disable budget mode by setting limit to 0
    set_budget(0.0)

def send_message(messages, task_type, weight_profile):
    payload = {"messages": messages, "task_type": task_type, "weight_profile": weight_profile}
    r = requests.post(f"{ROUTER_URL}/chat/completions", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def status_color(status):
    return {"LOW": "#00ff88", "MODERATE": "#f5c542", "HIGH": "#ff4d4d"}.get(status, "#6b8f72")

def status_emoji(status):
    return {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🔴"}.get(status, "⚪")

def trend_color(t):
    return {"IMPROVING": "#00ff88", "STABLE": "#f5c542", "WORSENING": "#ff4d4d"}.get(t, "#6b8f72")

def trend_arrow(t):
    return {"IMPROVING": "↓", "STABLE": "→", "WORSENING": "↑"}.get(t, "–")

def budget_color(pct):
    if pct >= 100: return "#ff4d4d"
    if pct >= 90:  return "#ff4d4d"
    if pct >= 70:  return "#ff8c00"
    return "#00ff88"

def pressure_label(pressure):
    return {
        "NONE":     "No Budget Set",
        "LOW":      "✅ On Track",
        "MEDIUM":   "⚠️ 70%+ Used",
        "HIGH":     "🔴 90%+ Used — Downgrading Models",
        "EXCEEDED": "🚫 Budget Exceeded — Minimum Mode",
    }.get(pressure, pressure)


# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:#00ff88;">🌿 GreenWeave</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Sans,sans-serif;font-size:13px;color:#6b8f72;">Climate AI Control Center</div>', unsafe_allow_html=True)
    st.markdown('<hr class="gw-divider">', unsafe_allow_html=True)

    # ── Live Grid Status ──────────────────────────────────────────
    carbon = get_carbon_status()
    status = carbon.get("status", "UNKNOWN")
    intensity = carbon.get("carbon_intensity", 0)
    region = carbon.get("region", "Unknown")
    fill_pct = min(100.0, (intensity / 800) * 100)

    st.markdown(f"""
    <div class="gw-card">
        <div style="font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--text-dim);margin-bottom:12px;">LIVE GRID STATUS</div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
            <div class="pulse-dot dot-{status}"></div>
            <span class="status-badge status-{status}">{status_emoji(status)} {status}</span>
        </div>
        <div class="meter-wrap">
            <div class="meter-label">GRID INTENSITY</div>
            <div class="meter-track">
                <div class="meter-fill" style="width:{fill_pct:.1f}%;background:linear-gradient(90deg,#ff4d4d,#f5c542,#00ff88);"></div>
            </div>
        </div>
        <div style="font-family:var(--mono);font-size:20px;font-weight:700;color:{status_color(status)};margin-top:10px;">
            {intensity} <span style="font-size:12px;color:var(--text-dim)">gCO₂/kWh</span>
        </div>
        <div style="font-family:var(--sans);font-size:11px;color:var(--text-dim);margin-top:6px;">📍 {region}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Intelligent Engine Panel ──────────────────────────────────
    engine = get_engine_status()
    if engine:
        best_region = engine.get("best_region", "-")
        delay       = engine.get("delay_execution", False)
        adaptive    = engine.get("adaptive_threshold", 0)
        confidence  = engine.get("learning_confidence", 0)
        trend       = engine.get("trend", "STABLE")
        predicted   = engine.get("predicted_next_hour_intensity", intensity)
        regions     = engine.get("regions", {})
        delay_color = "#ff8c00" if delay else "#00ff88"
        delay_text  = "⏳ WAITING FOR CLEAN GRID" if delay else "⚡ EXECUTING NOW"

        st.markdown(f"""
        <div class="gw-card blue">
            <div style="font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--text-dim);margin-bottom:12px;">🌍 INTELLIGENT ENGINE</div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);">
                <span>Carbon Trend</span>
                <span style="color:{trend_color(trend)};font-family:var(--mono);">{trend_arrow(trend)} {trend}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);">
                <span>Predicted Next Hour</span>
                <span style="color:#4da6ff;font-family:var(--mono);">{predicted} gCO₂</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);">
                <span>Best Region</span>
                <span style="color:#00ff88;font-family:var(--mono);">🌱 {best_region}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);">
                <span>Delay Execution</span>
                <span style="color:{delay_color};font-family:var(--mono);font-size:10px;">{delay_text}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;">
                <span>Adaptive Threshold</span>
                <span style="color:#00ff88;font-family:var(--mono);">{adaptive}</span>
            </div>
            <div style="margin-top:12px;">
                <div style="font-family:var(--mono);font-size:10px;color:var(--text-dim);margin-bottom:6px;">SELF-LEARNING CONFIDENCE</div>
                <div class="meter-track">
                    <div class="meter-fill" style="width:{confidence*100:.0f}%;background:linear-gradient(90deg,#003d22,#00ff88);"></div>
                </div>
                <div style="text-align:right;font-size:11px;color:#00ff88;margin-top:4px;">{confidence*100:.0f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Multi-Region Comparison ───────────────────────────────
        if regions:
            st.markdown("""
            <div class="gw-card orange">
                <div style="font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--text-dim);margin-bottom:8px;">🌎 MULTI-REGION COMPARISON</div>
            </div>
            """, unsafe_allow_html=True)
            for r_name, r_data in regions.items():
                r_int   = r_data.get("intensity", 0)
                r_trend = r_data.get("trend", "STABLE")
                is_best = "⭐ " if r_name == best_region else ""
                name_color = "#00ff88" if r_name == best_region else "var(--text)"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:6px 0;border-bottom:1px solid #1e3024;font-family:'Space Mono',monospace;font-size:11px;">
                    <span style="color:{name_color};">{is_best}{r_name}</span>
                    <span style="color:#c8e6d0;">{r_int} gCO₂</span>
                    <span style="color:{trend_color(r_trend)};">{trend_arrow(r_trend)} {r_trend}</span>
                </div>
                """, unsafe_allow_html=True)

    # ── Carbon Budget Mode ────────────────────────────────────────
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;letter-spacing:2px;color:#f5c542;margin-bottom:10px;">⚡ CARBON BUDGET MODE</div>', unsafe_allow_html=True)

    budget = get_budget()
    budget_set = budget.get("budget_set", False)
    current_limit = budget.get("limit_g", 0)

    if budget_set and current_limit > 0:
        limit     = budget.get("limit_g", 0)
        used      = budget.get("used_g", 0)
        remaining = budget.get("remaining_g", 0)
        pct       = budget.get("pct_used", 0)
        pressure  = budget.get("pressure", "NONE")
        b_color   = budget_color(pct)

        st.markdown(f"""
        <div class="budget-card">
            <div style="font-family:var(--mono);font-size:10px;letter-spacing:2px;color:#f5c542;margin-bottom:12px;">MONTHLY BUDGET</div>
            <div class="meter-wrap">
                <div class="meter-label">USAGE: {pct:.1f}%</div>
                <div class="meter-track">
                    <div class="meter-fill" style="width:{min(pct,100):.1f}%;background:{b_color};"></div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px;">
                <div class="stat-box">
                    <div class="stat-value" style="font-size:16px;color:{b_color};">{used:.2f}g</div>
                    <div class="stat-label">Used</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="font-size:16px;">{remaining:.2f}g</div>
                    <div class="stat-label">Remaining</div>
                </div>
            </div>
            <div style="font-family:var(--mono);font-size:11px;color:{b_color};margin-top:12px;text-align:center;">
                {pressure_label(pressure)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("↺ Reset Usage", use_container_width=True):
            reset_budget()
            st.rerun()
        if st.button("✕ Remove Budget", use_container_width=True):
            remove_budget()
            st.rerun()
    else:
        st.markdown('<div style="font-family:DM Sans,sans-serif;font-size:12px;color:#6b8f72;margin-bottom:10px;">Set a monthly CO₂ limit. GreenWeave will automatically route to smaller models as you approach the limit.</div>', unsafe_allow_html=True)
        budget_limit = st.number_input(
            "Budget (grams CO₂)",
            min_value=100.0, max_value=100000.0, value=2000.0, step=100.0,
            label_visibility="collapsed",
        )
        if st.button("🎯 Set Budget", type="primary", use_container_width=True):
            set_budget(budget_limit)
            st.success(f"Budget set: {budget_limit}g CO₂")
            st.rerun()

    st.markdown('<hr class="gw-divider">', unsafe_allow_html=True)

    # ── Session Impact ────────────────────────────────────────────
    avg_energy = (
        sum(st.session_state.total_energy_saved_pct) / len(st.session_state.total_energy_saved_pct)
        if st.session_state.total_energy_saved_pct else 0
    )
    st.markdown(f"""
    <div class="gw-card">
        <div style="font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--text-dim);margin-bottom:14px;">SESSION IMPACT</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div class="stat-box">
                <div class="stat-value">{st.session_state.total_queries}</div>
                <div class="stat-label">Queries</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{st.session_state.total_co2_saved:.3f}</div>
                <div class="stat-label">gCO₂ saved</div>
            </div>
            <div class="stat-box" style="grid-column:span 2;">
                <div class="stat-value">{avg_energy:.0f}%</div>
                <div class="stat-label">Avg energy saved</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="gw-divider">', unsafe_allow_html=True)

    # ── Routing Settings ──────────────────────────────────────────
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;letter-spacing:2px;color:#6b8f72;margin-bottom:10px;">ROUTING SETTINGS</div>', unsafe_allow_html=True)
    task_type      = st.selectbox("Task Type", ["casual_chat", "summarization", "coding", "legal_drafting", "medical"])
    weight_profile = st.selectbox("Weight Profile", ["BALANCED", "ECO_FIRST", "ACCURACY_FIRST"])

    st.markdown('<hr class="gw-divider">', unsafe_allow_html=True)

    health    = get_health()
    router_ok = health.get("status") != "offline"
    redis_ok  = "connected" in str(health.get("redis", ""))
    engine_ok = bool(engine)

    st.markdown(f"""
    <div style="font-family:Space Mono,monospace;font-size:11px;">
        <div style="display:flex;justify-content:space-between;padding:4px 0;color:#6b8f72;">
            <span>ROUTER</span>
            <span style="color:{'#00ff88' if router_ok else '#ff4d4d'}">{'● ONLINE' if router_ok else '● OFFLINE'}</span>
        </div>
        <div style="display:flex;justify-content:space-between;padding:4px 0;color:#6b8f72;">
            <span>REDIS</span>
            <span style="color:{'#00ff88' if redis_ok else '#f5c542'}">{'● CONNECTED' if redis_ok else '● FALLBACK'}</span>
        </div>
        <div style="display:flex;justify-content:space-between;padding:4px 0;color:#6b8f72;">
            <span>ENGINE</span>
            <span style="color:{'#00ff88' if engine_ok else '#ff4d4d'}">{'● ACTIVE' if engine_ok else '● OFFLINE'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↺  Refresh Status", use_container_width=True):
        st.rerun()
    if st.button("🗑  Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_co2_saved = 0.0
        st.session_state.total_queries = 0
        st.session_state.total_energy_saved_pct = []
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  Main Chat Area
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">
    <div>
        <div style="font-family:'Space Mono',monospace;font-size:28px;font-weight:700;color:#00ff88;line-height:1;">🌿 GreenWeave</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:14px;color:#6b8f72;margin-top:4px;">
            Climate AI Control Center &nbsp;·&nbsp; Predictive · Multi-Region · Self-Learning
        </div>
    </div>
</div>
<hr class="gw-divider">
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#6b8f72;">
        <div style="font-size:48px;margin-bottom:16px;">🌿</div>
        <div style="font-family:Space Mono,monospace;font-size:14px;color:#00ff88;margin-bottom:8px;">GREENWEAVE READY</div>
        <div style="font-family:DM Sans,sans-serif;font-size:13px;max-width:440px;margin:0 auto;line-height:1.7;">
            Every response is routed using predictive carbon intelligence,
            multi-region comparison, and self-learning adaptive thresholds.
        </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="bubble-label" style="text-align:right;">YOU</div><div class="bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        receipt      = msg.get("receipt", {})
        mode         = receipt.get("mode", "")
        model_name   = receipt.get("model_name", receipt.get("model_used", ""))
        co2_saved    = receipt.get("co2_saved_g", 0)
        energy_pct   = receipt.get("energy_saved_pct", 0)
        intensity_val = receipt.get("grid_intensity_gco2_kwh", 0)
        impact_red   = receipt.get("impact_reduction_pct", 0)
        latency      = receipt.get("latency_ms", 0)
        co2_this     = receipt.get("co2_this_query_g", 0)
        b_limit      = receipt.get("budget_limit_g")
        b_used       = receipt.get("budget_used_g")
        b_pct        = receipt.get("budget_pct")
        b_pressure   = receipt.get("budget_pressure", "NONE")

        st.markdown(f'<div class="bubble-label">GREENWEAVE AI</div><div class="bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)

        if receipt:
            budget_row = ""
            if b_limit:
                b_color_class = "danger" if b_pct >= 90 else ("warning" if b_pct >= 70 else "highlight")
                budget_row = f'<div class="receipt-row" style="margin-top:8px;border-top:1px solid #1e3024;padding-top:8px;"><span>Budget Used</span><span>{b_used:.4f}g / {b_limit}g</span></div><div class="receipt-row {b_color_class}"><span>Budget %</span><span>{b_pct:.1f}% — {pressure_label(b_pressure)}</span></div>'

            html_block = f"""
<div class="receipt">
<div class="receipt-title">⚡ Carbon Receipt</div>
<div class="receipt-row highlight"><span>Mode</span><span>{mode}</span></div>
<div class="receipt-row"><span>Model Used</span><span>{model_name}</span></div>
<div class="receipt-row"><span>Grid Intensity</span><span>{intensity_val} gCO₂/kWh</span></div>
<div class="receipt-row"><span>CO₂ This Query</span><span>{co2_this:.5f} g</span></div>
<div class="receipt-row highlight"><span>CO₂ Saved</span><span>+{co2_saved:.4f} g</span></div>
<div class="receipt-row highlight"><span>Energy Saved</span><span>{energy_pct:.0f}%</span></div>
<div class="receipt-row"><span>Impact Reduction</span><span>{impact_red:.1f}%</span></div>
<div class="receipt-row"><span>Latency</span><span>{latency:.0f} ms</span></div>
{budget_row}
<div class="meter-wrap" style="margin-top:14px;">
<div class="meter-label">ENERGY EFFICIENCY</div>
<div class="meter-track">
<div class="meter-fill" style="width:{energy_pct}%;background:linear-gradient(90deg,#003d22,#00ff88);"></div>
</div>
<div style="text-align:right;font-size:11px;color:#00ff88;margin-top:4px;">{energy_pct:.0f}% saved vs full model on dirty grid</div>
</div>
</div>
"""
            st.markdown(html_block, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Input
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        label="prompt",
        label_visibility="collapsed",
        placeholder="Ask anything — GreenWeave routes using predictive carbon intelligence…",
        key="user_input",
    )
with col2:
    send = st.button("Send →", type="primary", use_container_width=True)

if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})

    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
        if m["role"] in ("user", "assistant")
    ]

    with st.spinner("🌿 Routing via predictive carbon intelligence…"):
        try:
            result        = send_message(api_messages, task_type, weight_profile)
            response_text = result.get("response", "")
            receipt       = result.get("carbon_receipt", {})

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "receipt": receipt,
            })

            st.session_state.total_queries += 1
            st.session_state.total_co2_saved += receipt.get("co2_saved_g", 0)
            st.session_state.total_energy_saved_pct.append(receipt.get("energy_saved_pct", 0))
            
            st.rerun()

        except requests.exceptions.ConnectionError:
            st.error("⚠️ Cannot reach the Elastic Router at elastic_router:8000")
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")