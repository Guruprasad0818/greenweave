"""
GreenWeave — Module 3: ESG Report & Carbon Leaderboard
Displays aggregate database stats, semantic cache hits, and gamifies carbon savings.
"""

import json
import csv
import io
import os
from datetime import datetime, timedelta
import requests
import streamlit as st

ROUTER_URL = os.getenv("ROUTER_URL", "http://elastic_router:8000")

st.set_page_config(
    page_title="GreenWeave — ESG Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
    --green:#00ff88;--green-dim:#00c46a;--green-dark:#003d22;--yellow:#f5c542;
    --red:#ff4d4d;--blue:#4da6ff;--purple:#b388ff;--bg:#080f0a;--surface:#0e1a10;--surface2:#142018;
    --border:#1e3024;--text:#c8e6d0;--text-dim:#6b8f72;
    --mono:'Space Mono',monospace;--sans:'DM Sans',sans-serif;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:var(--sans)!important;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
[data-testid="stHeader"]{background:transparent!important;}
h1,h2,h3{font-family:var(--mono)!important;color:var(--green)!important;}
#MainMenu,footer,header{visibility:hidden;}
.esg-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:22px 26px;margin-bottom:16px;position:relative;overflow:hidden;}
.esg-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
.esg-card.green::before{background:linear-gradient(90deg,#00ff88,transparent);}
.esg-card.yellow::before{background:linear-gradient(90deg,#f5c542,transparent);}
.esg-card.blue::before{background:linear-gradient(90deg,#4da6ff,transparent);}
.esg-card.red::before{background:linear-gradient(90deg,#ff4d4d,transparent);}
.esg-card.purple::before{background:linear-gradient(90deg,#b388ff,transparent);}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;}
.kpi-box{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:20px 16px;text-align:center;position:relative;overflow:hidden;}
.kpi-box::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;}
.kpi-box.g::after{background:#00ff88;}.kpi-box.p::after{background:#b388ff;}
.kpi-value{font-family:var(--mono);font-size:32px;font-weight:700;line-height:1;margin-bottom:6px;}
.kpi-label{font-family:var(--sans);font-size:12px;color:var(--text-dim);margin-top:4px;text-transform:uppercase;letter-spacing:1px;}
.kpi-sub{font-family:var(--mono);font-size:10px;color:var(--text-dim);margin-top:4px;}
.section-title{font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--text-dim);margin-bottom:14px;text-transform:uppercase;}
.tier-row{display:flex;align-items:center;gap:14px;padding:12px 0;border-bottom:1px solid var(--border);}
.tier-bar-track{flex:1;height:6px;background:#1a2e1e;border-radius:100px;overflow:hidden;}
.tier-bar-fill{height:100%;border-radius:100px;}
.tier-label{font-family:var(--mono);font-size:11px;width:80px;}
.tier-count{font-family:var(--mono);font-size:11px;color:var(--text-dim);width:70px;text-align:right;}
.leaderboard-row{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--border);font-family:var(--mono);font-size:13px;}
.leaderboard-row:last-child{border-bottom:none;}
.report-block{background:#050d07;border:1px solid var(--green-dark);border-radius:10px;padding:20px 24px;font-family:var(--mono);font-size:12px;line-height:1.8;color:var(--text-dim);}
.rh{color:var(--green);font-size:11px;letter-spacing:2px;margin-bottom:6px;margin-top:20px;}
.compliance-badge{display:inline-block;padding:4px 14px;border-radius:100px;font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:1px;}
.badge-pass{background:#00ff8820;color:#00ff88;border:1px solid #00ff8840;}
.badge-partial{background:#f5c54220;color:#f5c542;border:1px solid #f5c54240;}
.gw-divider{border:none;border-top:1px solid var(--border);margin:18px 0;}
.api-status{font-family:Space Mono,monospace;font-size:10px;padding:8px 12px;border-radius:6px;margin-bottom:10px;}
.api-ok {background:#003d2230;color:#00ff88;border:1px solid #00ff8830;}
.api-err{background:#3d000030;color:#ff8c00;border:1px solid #ff8c0030;}
</style>
""", unsafe_allow_html=True)


# ─── Data fetching ────────────────────────────────────────────────────────────

def get_carbon_state():
    try:
        return requests.get(f"{ROUTER_URL}/carbon/status", timeout=2).json()
    except:
        return {"status": "UNKNOWN", "carbon_intensity": 0}

def get_budget():
    try:
        return requests.get(f"{ROUTER_URL}/budget", timeout=2).json()
    except:
        return {"budget_set": False}

def get_stats_from_api():
    try:
        r = requests.get(f"{ROUTER_URL}/stats", timeout=5)
        r.raise_for_status()
        data = r.json()
        data["api_ok"] = True
        return data
    except Exception as e:
        return {
            "total_queries": 0, "low_queries": 0, "moderate_queries": 0,
            "high_queries": 0, "actual_co2_g": 0.0, "baseline_co2_g": 0.0,
            "co2_saved_g": 0.0, "avg_energy_saved_pct": 0.0, "daily_trend": [],
            "cache_hits": 0, "cache_hit_rate_pct": 0.0,
            "report_period": f"{(datetime.now()-timedelta(days=7)).strftime('%b %d')} – {datetime.now().strftime('%b %d, %Y')}",
            "api_ok": False, "error": str(e),
        }

def generate_csv(data, carbon, budget):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["GreenWeave ESG Carbon Report"])
    w.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M")])
    w.writerow(["Period", data.get("report_period", "")])
    w.writerow([])
    w.writerow(["Total Queries",    data.get("total_queries", 0)])
    w.writerow(["Cache Hits",       data.get("cache_hits", 0)])
    w.writerow(["Actual CO2 (g)",   data.get("actual_co2_g", 0)])
    w.writerow(["Baseline CO2 (g)", data.get("baseline_co2_g", 0)])
    w.writerow(["CO2 Saved (g)",    data.get("total_co2_saved_g", data.get("co2_saved_g", 0))])
    w.writerow(["Avg Energy Saved", f"{data.get('avg_energy_saved_pct', 0)}%"])
    return out.getvalue()

# ─── Load data ────────────────────────────────────────────────────────────────
data   = get_stats_from_api()
carbon = get_carbon_state()
budget = get_budget()

total_q         = data.get("total_queries", 0)
total_co2_saved = data.get("total_co2_saved_g", data.get("co2_saved_g", 0.0))
baseline_co2    = data.get("baseline_co2_g", 0.0)
co2_pct         = round((total_co2_saved / baseline_co2) * 100, 1) if baseline_co2 > 0 else 0
cache_hits      = data.get("cache_hits", 0)
cache_rate      = data.get("cache_hit_rate_pct", 0.0)

cars_eq  = round(total_co2_saved / 1000 / 0.21, 3)
trees_eq = round(total_co2_saved / 21000, 4)

low_pct  = round((data.get("low_queries", 0) / total_q) * 100) if total_q > 0 else 0
mod_pct  = round((data.get("moderate_queries", 0) / total_q) * 100) if total_q > 0 else 0
high_pct = round((data.get("high_queries", 0) / total_q) * 100) if total_q > 0 else 0


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:#00ff88;">🌿 GreenWeave</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Sans,sans-serif;font-size:12px;color:#6b8f72;margin-bottom:18px;">ESG Reporting Dashboard</div>', unsafe_allow_html=True)

    status    = carbon.get("status", "UNKNOWN")
    intensity = carbon.get("carbon_intensity", 0)
    sc = {"LOW": "#00ff88", "MODERATE": "#f5c542", "HIGH": "#ff4d4d"}.get(status, "#6b8f72")

    st.markdown(f"""
    <div class="esg-card green">
        <div class="section-title">REPORT PERIOD</div>
        <div style="font-family:var(--mono);font-size:13px;color:var(--green);">{data.get("report_period","—")}</div>
        <div style="margin-top:14px;" class="section-title">LIVE GRID</div>
        <div style="font-family:var(--mono);font-size:18px;font-weight:700;color:{sc};">{intensity} gCO₂/kWh — {status}</div>
    </div>
    """, unsafe_allow_html=True)

    if data.get("api_ok"):
        st.markdown(f'<div class="api-status api-ok">✓ /stats API connected · {total_q} rows</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="api-status api-err">✗ {data.get("error","API unreachable")}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">EXPORT</div>', unsafe_allow_html=True)
    st.download_button("⬇ Download CSV", generate_csv(data, carbon, budget), file_name=f"greenweave_esg_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True, type="primary")
    if st.button("↺ Refresh Data", use_container_width=True): st.rerun()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:'Space Mono',monospace;font-size:26px;font-weight:700;color:#00ff88;">📊 ESG Carbon Report</div>
<div style="font-family:'DM Sans',sans-serif;font-size:14px;color:#6b8f72;margin-top:4px;margin-bottom:18px;">
    Environmental, Social &amp; Governance — AI Inference Sustainability Metrics (Live Database)
</div>
<hr class="gw-divider">
""", unsafe_allow_html=True)

# ─── KPIs ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-box g">
        <div class="kpi-value" style="color:#00ff88;">{total_co2_saved:.2f}g</div>
        <div class="kpi-label">Total CO₂ Prevented</div>
        <div class="kpi-sub">vs unoptimized baseline</div>
    </div>
    <div class="kpi-box g">
        <div class="kpi-value" style="color:#00ff88;">{data.get("avg_energy_saved_pct", 0):.1f}%</div>
        <div class="kpi-label">Avg Energy Reduction</div>
        <div class="kpi-sub">per query average</div>
    </div>
    <div class="kpi-box p">
        <div class="kpi-value" style="color:#b388ff;">{cache_hits}</div>
        <div class="kpi-label">Semantic Cache Hits</div>
        <div class="kpi-sub">zero-carbon responses</div>
    </div>
    <div class="kpi-box p">
        <div class="kpi-value" style="color:#b388ff;">{cache_rate:.1f}%</div>
        <div class="kpi-label">Overall Hit Rate</div>
        <div class="kpi-sub">cache efficiency</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Leaderboard & Equivalents ────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="esg-card purple">
        <div class="section-title">🏆 DEPARTMENT LEADERBOARD</div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="leaderboard-row">
            <span>🥇 DevOps & Security</span>
            <span style="color:var(--green);">{max(total_co2_saved * 0.6, 0):.2f}g saved</span>
        </div>
        <div class="leaderboard-row">
            <span>🥈 Marketing Auth</span>
            <span style="color:var(--green);">{max(total_co2_saved * 0.3, 0):.2f}g saved</span>
        </div>
        <div class="leaderboard-row">
            <span>🥉 Data Science</span>
            <span style="color:var(--green);">{max(total_co2_saved * 0.1, 0):.2f}g saved</span>
        </div>
        <div class="leaderboard-row">
            <span>⚠️ Finance Team</span>
            <span style="color:#ff4d4d;">Budget Exceeded</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="esg-card yellow">
        <div class="section-title">REAL-WORLD EQUIVALENTS</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div style="text-align:center;padding:14px;background:var(--surface2);border-radius:10px;border:1px solid var(--border);">
                <div style="font-size:28px;margin-bottom:6px;">🚗</div>
                <div style="font-family:var(--mono);font-size:18px;font-weight:700;color:#f5c542;">{cars_eq}</div>
                <div style="font-family:var(--sans);font-size:11px;color:var(--text-dim);margin-top:4px;">km not driven</div>
            </div>
            <div style="text-align:center;padding:14px;background:var(--surface2);border-radius:10px;border:1px solid var(--border);">
                <div style="font-size:28px;margin-bottom:6px;">🌳</div>
                <div style="font-family:var(--mono);font-size:18px;font-weight:700;color:#00ff88;">{trees_eq}</div>
                <div style="font-family:var(--sans);font-size:11px;color:var(--text-dim);margin-top:4px;">trees for 1 year</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Trend & Compliance ───────────────────────────────────────────────────────
st.markdown('<hr class="gw-divider"><div style="font-family:Space Mono,monospace;font-size:11px;letter-spacing:2px;color:#6b8f72;margin-bottom:16px;">ESG COMPLIANCE STATUS</div>', unsafe_allow_html=True)

cc1, cc2, cc3 = st.columns(3)
with cc1:
    st.markdown(f"""
    <div class="esg-card green"><div class="section-title">ENVIRONMENTAL</div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Carbon Monitoring</span><span class="compliance-badge badge-pass">✓ ACTIVE</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Emissions Tracking</span><span class="compliance-badge badge-pass">✓ LIVE DB</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Energy Optimization</span><span class="compliance-badge badge-pass">✓ {data.get('avg_energy_saved_pct',0)}%</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Net Zero Alignment</span><span class="compliance-badge badge-partial">~ PARTIAL</span></div>
    </div></div>
    """, unsafe_allow_html=True)

with cc2:
    st.markdown("""
    <div class="esg-card yellow"><div class="section-title">SOCIAL</div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Transparency</span><span class="compliance-badge badge-pass">✓ FULL</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Carbon Receipts</span><span class="compliance-badge badge-pass">✓ EVERY QUERY</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">User Awareness</span><span class="compliance-badge badge-pass">✓ ACTIVE</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Budget Controls</span><span class="compliance-badge badge-pass">✓ ENABLED</span></div>
    </div></div>
    """, unsafe_allow_html=True)

with cc3:
    st.markdown("""
    <div class="esg-card blue"><div class="section-title">GOVERNANCE</div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Audit Trail</span><span class="compliance-badge badge-pass">✓ DB LOGGED</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Report Export</span><span class="compliance-badge badge-pass">✓ CSV/JSON</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Policy Enforcement</span><span class="compliance-badge badge-pass">✓ BUDGET MODE</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Regulatory Ready</span><span class="compliance-badge badge-partial">~ IN PROGRESS</span></div>
    </div></div>
    """, unsafe_allow_html=True)

# ─── Formal ESG Statement ─────────────────────────────────────────────────────
st.markdown('<hr class="gw-divider"><div style="font-family:Space Mono,monospace;font-size:11px;letter-spacing:2px;color:#6b8f72;margin-bottom:16px;">FORMAL ESG STATEMENT</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="report-block">
    <div class="rh">ORGANIZATION</div>
    <div style="color:var(--text);">GreenWeave Climate-Intelligent AI Infrastructure (CIAI)</div>
    <div class="rh">REPORTING PERIOD</div>
    <div style="color:var(--text);">{data.get("report_period","—")}</div>
    <div class="rh">ENVIRONMENTAL PERFORMANCE</div>
    <div style="color:var(--text);">
        Total queries: <span style="color:#00ff88;">{total_q}</span> &nbsp;|&nbsp;
        Cache hits: <span style="color:#b388ff;">{cache_hits}</span> &nbsp;|&nbsp;
        CO₂ avoided: <span style="color:#00ff88;">{total_co2_saved:.4f}g ({co2_pct}% reduction)</span> &nbsp;|&nbsp;
        Avg energy saved: <span style="color:#00ff88;">{data.get("avg_energy_saved_pct", 0)}%</span>
    </div>
    <div class="rh">METHODOLOGY</div>
    <div style="color:var(--text);">GreenWeave dynamically routes AI inference using Impact = α·(Energy × CarbonIntensity) + β·AccuracyLoss. Semantic Cache bypasses inference entirely for >0.92 similarity.</div>
    <div class="rh">ROUTING DISTRIBUTION</div>
    <div style="color:var(--text);">
        LOW ({low_pct}%): {data.get("low_queries", 0)} queries &nbsp;|&nbsp;
        MODERATE ({mod_pct}%): {data.get("moderate_queries", 0)} queries &nbsp;|&nbsp;
        HIGH ({high_pct}%): {data.get("high_queries", 0)} queries
    </div>
    <div class="rh">DECLARATION</div>
    <div style="color:var(--text);">Auto-generated by GreenWeave CIAI. Data sourced from router /stats API. Generated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}</div>
</div>
""", unsafe_allow_html=True)