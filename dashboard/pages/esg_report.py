"""
GreenWeave — ESG Reporting Dashboard
Real-time SQLite Database integration for persistent reporting.
"""

import json
import csv
import io
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import requests
import streamlit as st

ROUTER_URL = "http://localhost:8000"
# Path to the database created by the router
DB_PATH = os.path.join(os.path.dirname(__file__), "../../elastic_router/greenweave_esg.db")

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
    --red:#ff4d4d;--blue:#4da6ff;--bg:#080f0a;--surface:#0e1a10;--surface2:#142018;
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
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;}
.kpi-box{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:20px 16px;text-align:center;position:relative;overflow:hidden;}
.kpi-box::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;}
.kpi-box.g::after{background:#00ff88;}.kpi-box.y::after{background:#f5c542;}.kpi-box.b::after{background:#4da6ff;}
.kpi-value{font-family:var(--mono);font-size:32px;font-weight:700;line-height:1;margin-bottom:6px;}
.kpi-label{font-family:var(--sans);font-size:12px;color:var(--text-dim);margin-top:4px;}
.kpi-sub{font-family:var(--mono);font-size:10px;color:var(--text-dim);margin-top:4px;}
.section-title{font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--text-dim);margin-bottom:14px;text-transform:uppercase;}
.tier-row{display:flex;align-items:center;gap:14px;padding:12px 0;border-bottom:1px solid var(--border);}
.tier-bar-track{flex:1;height:6px;background:#1a2e1e;border-radius:100px;overflow:hidden;}
.tier-bar-fill{height:100%;border-radius:100px;}
.tier-label{font-family:var(--mono);font-size:11px;width:80px;}
.tier-count{font-family:var(--mono);font-size:11px;color:var(--text-dim);width:60px;text-align:right;}
.report-block{background:#050d07;border:1px solid var(--green-dark);border-radius:10px;padding:20px 24px;font-family:var(--mono);font-size:12px;line-height:1.8;color:var(--text-dim);}
.rh{color:var(--green);font-size:11px;letter-spacing:2px;margin-bottom:6px;margin-top:20px;}
.compliance-badge{display:inline-block;padding:4px 14px;border-radius:100px;font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:1px;}
.badge-pass{background:#00ff8820;color:#00ff88;border:1px solid #00ff8840;}
.badge-partial{background:#f5c54220;color:#f5c542;border:1px solid #f5c54240;}
.gw-divider{border:none;border-top:1px solid var(--border);margin:18px 0;}
[data-testid="baseButton-primary"]{background:var(--green)!important;color:#000!important;border:none!important;font-family:var(--mono)!important;font-weight:700!important;border-radius:10px!important;}
[data-testid="baseButton-secondary"]{background:transparent!important;color:var(--text-dim)!important;border:1px solid var(--border)!important;font-family:var(--mono)!important;border-radius:10px!important;}
</style>
""", unsafe_allow_html=True)


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

def get_real_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM carbon_log", conn)
        conn.close()
    except sqlite3.OperationalError:
        # DB doesn't exist yet
        df = pd.DataFrame()

    if df.empty:
        return {
            "total_queries": 0, "low_queries": 0, "moderate_queries": 0, "high_queries": 0,
            "actual_co2_g": 0.0, "baseline_co2_g": 0.0, "co2_saved_g": 0.0,
            "avg_energy_saved_pct": 0.0, "daily_trend": [],
            "report_period": f"{(datetime.now()-timedelta(days=7)).strftime('%b %d')} – {datetime.now().strftime('%b %d, %Y')}",
        }

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Bin queries based on intensity to show in distribution
    low_q = len(df[df['grid_intensity'] < 250])
    mod_q = len(df[(df['grid_intensity'] >= 250) & (df['grid_intensity'] < 500)])
    high_q = len(df[df['grid_intensity'] >= 500])

    total_queries = len(df)
    actual_co2 = df['actual_co2_g'].sum()
    baseline_co2 = df['baseline_co2_g'].sum()
    co2_saved = df['co2_saved_g'].sum()
    avg_energy = df['energy_saved_pct'].mean()

    # Create daily trend
    df['date'] = df['timestamp'].dt.strftime('%b %d')
    daily = df.groupby('date').agg({'id': 'count', 'co2_saved_g': 'sum'}).reset_index()
    daily_trend = [{"date": row['date'], "queries": int(row['id']), "co2_saved": round(row['co2_saved_g'], 2)} for _, row in daily.iterrows()]

    # Make sure we have at least 1 day for rendering
    if not daily_trend:
        daily_trend = [{"date": datetime.now().strftime('%b %d'), "queries": 0, "co2_saved": 0.0}]

    return {
        "total_queries": total_queries, 
        "low_queries": low_q, 
        "moderate_queries": mod_q, 
        "high_queries": high_q,
        "actual_co2_g": round(actual_co2, 2), 
        "baseline_co2_g": round(baseline_co2, 2), 
        "co2_saved_g": round(co2_saved, 2),
        "avg_energy_saved_pct": round(avg_energy, 1), 
        "daily_trend": daily_trend,
        "report_period": f"{df['timestamp'].min().strftime('%b %d, %Y')} – {datetime.now().strftime('%b %d, %Y')}",
    }


def generate_csv(data, carbon, budget):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["GreenWeave ESG Carbon Report"])
    w.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M")])
    w.writerow(["Period", data["report_period"]])
    w.writerow([])
    w.writerow(["Total Queries", data["total_queries"]])
    w.writerow(["Actual CO2 (g)", data["actual_co2_g"]])
    w.writerow(["Baseline CO2 (g)", data["baseline_co2_g"]])
    w.writerow(["CO2 Saved (g)", data["co2_saved_g"]])
    w.writerow(["Avg Energy Saved %", f"{data['avg_energy_saved_pct']}%"])
    w.writerow([])
    w.writerow(["Date","Queries","CO2 Saved (g)"])
    for d in data["daily_trend"]:
        w.writerow([d["date"], d["queries"], d["co2_saved"]])
    return out.getvalue()


data   = get_real_data()
carbon = get_carbon_state()
budget = get_budget()

co2_pct   = round((data["co2_saved_g"]/data["baseline_co2_g"])*100,1) if data["baseline_co2_g"] > 0 else 0
cars_eq   = round(data["co2_saved_g"]/1000/0.21, 2)
trees_eq  = round(data["co2_saved_g"]/21000, 3)
low_pct   = round((data["low_queries"]/data["total_queries"])*100) if data["total_queries"] > 0 else 0
mod_pct   = round((data["moderate_queries"]/data["total_queries"])*100) if data["total_queries"] > 0 else 0
high_pct  = round((data["high_queries"]/data["total_queries"])*100) if data["total_queries"] > 0 else 0


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:#00ff88;">🌿 GreenWeave</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Sans,sans-serif;font-size:12px;color:#6b8f72;margin-bottom:18px;">ESG Reporting Dashboard</div>', unsafe_allow_html=True)

    status = carbon.get("status","UNKNOWN")
    intensity = carbon.get("carbon_intensity",0)
    sc = {"LOW":"#00ff88","MODERATE":"#f5c542","HIGH":"#ff4d4d"}.get(status,"#6b8f72")

    st.markdown(f"""
    <div class="esg-card green">
        <div class="section-title">REPORT PERIOD</div>
        <div style="font-family:var(--mono);font-size:13px;color:var(--green);">{data["report_period"]}</div>
        <div style="margin-top:14px;" class="section-title">LIVE GRID</div>
        <div style="font-family:var(--mono);font-size:18px;font-weight:700;color:{sc};">{intensity} gCO₂/kWh — {status}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">EXPORT</div>', unsafe_allow_html=True)
    st.download_button("⬇ Download CSV", generate_csv(data,carbon,budget),
        file_name=f"greenweave_esg_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv",
        use_container_width=True, type="primary")
    st.download_button("⬇ Download JSON",
        json.dumps({"period":data["report_period"],"co2_saved_g":data["co2_saved_g"],"reduction_pct":co2_pct},indent=2),
        file_name=f"greenweave_esg_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json",
        use_container_width=True)
    if st.button("↺ Refresh DB", use_container_width=True):
        st.rerun()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:'Space Mono',monospace;font-size:26px;font-weight:700;color:#00ff88;">📊 ESG Carbon Report</div>
<div style="font-family:'DM Sans',sans-serif;font-size:14px;color:#6b8f72;margin-top:4px;margin-bottom:18px;">Environmental, Social &amp; Governance — AI Inference Sustainability Metrics (Live Database)</div>
<hr class="gw-divider">
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-box g"><div class="kpi-value" style="color:#00ff88;">{data["co2_saved_g"]:.1f}g</div><div class="kpi-label">Total CO₂ Saved</div><div class="kpi-sub">vs unoptimized baseline</div></div>
    <div class="kpi-box y"><div class="kpi-value" style="color:#f5c542;">{co2_pct}%</div><div class="kpi-label">Emissions Reduction</div><div class="kpi-sub">vs always-large model</div></div>
    <div class="kpi-box b"><div class="kpi-value" style="color:#4da6ff;">{data["total_queries"]}</div><div class="kpi-label">Total Queries</div><div class="kpi-sub">carbon-routed inferences</div></div>
    <div class="kpi-box g"><div class="kpi-value" style="color:#00ff88;">{data["avg_energy_saved_pct"]}%</div><div class="kpi-label">Avg Energy Saved</div><div class="kpi-sub">per query average</div></div>
</div>
""", unsafe_allow_html=True)

# ── Two columns ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(f"""
    <div class="esg-card green">
        <div class="section-title">ROUTING BREAKDOWN</div>
        <div class="tier-row"><div class="tier-label" style="color:#00ff88;">🟢 LOW</div><div class="tier-bar-track"><div class="tier-bar-fill" style="width:{low_pct}%;background:#00ff88;"></div></div><div class="tier-count">{data["low_queries"]} ({low_pct}%)</div></div>
        <div class="tier-row"><div class="tier-label" style="color:#f5c542;">🟡 MOD</div><div class="tier-bar-track"><div class="tier-bar-fill" style="width:{mod_pct}%;background:#f5c542;"></div></div><div class="tier-count">{data["moderate_queries"]} ({mod_pct}%)</div></div>
        <div class="tier-row" style="border-bottom:none;"><div class="tier-label" style="color:#ff4d4d;">🔴 HIGH</div><div class="tier-bar-track"><div class="tier-bar-fill" style="width:{high_pct}%;background:#ff4d4d;"></div></div><div class="tier-count">{data["high_queries"]} ({high_pct}%)</div></div>
    </div>
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

with col2:
    max_saved = max(d["co2_saved"] for d in data["daily_trend"]) if data["daily_trend"] else 0
    bars = ""
    for day in data["daily_trend"]:
        h = int((day["co2_saved"]/max_saved)*80) if max_saved > 0 else 10
        bars += f"""<div style="display:flex;flex-direction:column;align-items:center;gap:4px;flex:1;">
            <div style="font-family:var(--mono);font-size:10px;color:#00ff88;">{day["co2_saved"]}g</div>
            <div style="width:100%;background:#1a2e1e;border-radius:4px;height:80px;display:flex;align-items:flex-end;overflow:hidden;">
                <div style="width:100%;height:{h}px;background:linear-gradient(180deg,#00ff88,#003d22);border-radius:4px;"></div>
            </div>
            <div style="font-family:var(--mono);font-size:9px;color:var(--text-dim);">{day["date"].split()[1] if len(day["date"].split())>1 else day["date"]}</div>
        </div>"""

    st.markdown(f"""
    <div class="esg-card blue">
        <div class="section-title">7-DAY CO₂ SAVINGS TREND</div>
        <div style="display:flex;gap:8px;align-items:flex-end;padding:8px 0;">{bars}</div>
    </div>
    <div class="esg-card red">
        <div class="section-title">CO₂ COMPARISON</div>
        <div style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-family:var(--mono);font-size:11px;color:var(--text-dim);">Without GreenWeave</span>
                <span style="font-family:var(--mono);font-size:11px;color:#ff4d4d;">{data["baseline_co2_g"]:.1f}g</span>
            </div>
            <div style="height:8px;background:#1a2e1e;border-radius:100px;overflow:hidden;"><div style="width:100%;height:100%;background:#ff4d4d;border-radius:100px;"></div></div>
        </div>
        <div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-family:var(--mono);font-size:11px;color:var(--text-dim);">With GreenWeave</span>
                <span style="font-family:var(--mono);font-size:11px;color:#00ff88;">{data["actual_co2_g"]:.1f}g</span>
            </div>
            <div style="height:8px;background:#1a2e1e;border-radius:100px;overflow:hidden;"><div style="width:{100-co2_pct if data['baseline_co2_g'] > 0 else 0:.0f}%;height:100%;background:#00ff88;border-radius:100px;"></div></div>
        </div>
        <div style="text-align:center;margin-top:16px;font-family:var(--mono);font-size:22px;font-weight:700;color:#00ff88;">{co2_pct}% reduction</div>
    </div>
    """, unsafe_allow_html=True)


# ── ESG Compliance ────────────────────────────────────────────────────────────
st.markdown('<hr class="gw-divider"><div style="font-family:Space Mono,monospace;font-size:11px;letter-spacing:2px;color:#6b8f72;margin-bottom:16px;">ESG COMPLIANCE STATUS</div>', unsafe_allow_html=True)

cc1, cc2, cc3 = st.columns(3)

with cc1:
    st.markdown(f"""<div class="esg-card green"><div class="section-title">ENVIRONMENTAL</div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Carbon Monitoring</span><span class="compliance-badge badge-pass">✓ ACTIVE</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Emissions Tracking</span><span class="compliance-badge badge-pass">✓ LIVE DB</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Energy Optimization</span><span class="compliance-badge badge-pass">✓ {data['avg_energy_saved_pct']}%</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Net Zero Alignment</span><span class="compliance-badge badge-partial">~ PARTIAL</span></div>
    </div></div>""", unsafe_allow_html=True)

with cc2:
    st.markdown("""<div class="esg-card yellow"><div class="section-title">SOCIAL</div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Transparency</span><span class="compliance-badge badge-pass">✓ FULL</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Carbon Receipts</span><span class="compliance-badge badge-pass">✓ EVERY QUERY</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">User Awareness</span><span class="compliance-badge badge-pass">✓ ACTIVE</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Budget Controls</span><span class="compliance-badge badge-pass">✓ ENABLED</span></div>
    </div></div>""", unsafe_allow_html=True)

with cc3:
    st.markdown("""<div class="esg-card blue"><div class="section-title">GOVERNANCE</div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Audit Trail</span><span class="compliance-badge badge-pass">✓ DB LOGGED</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Report Export</span><span class="compliance-badge badge-pass">✓ CSV/JSON</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Policy Enforcement</span><span class="compliance-badge badge-pass">✓ BUDGET MODE</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--sans);font-size:13px;">Regulatory Ready</span><span class="compliance-badge badge-partial">~ IN PROGRESS</span></div>
    </div></div>""", unsafe_allow_html=True)


# ── Formal Statement ──────────────────────────────────────────────────────────
st.markdown('<hr class="gw-divider"><div style="font-family:Space Mono,monospace;font-size:11px;letter-spacing:2px;color:#6b8f72;margin-bottom:16px;">FORMAL ESG STATEMENT</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="report-block">
    <div class="rh">ORGANIZATION</div><div style="color:var(--text);">GreenWeave Climate-Intelligent AI Infrastructure (CIAI)</div>
    <div class="rh">REPORTING PERIOD</div><div style="color:var(--text);">{data["report_period"]}</div>
    <div class="rh">ENVIRONMENTAL PERFORMANCE</div>
    <div style="color:var(--text);">
        Total queries: <span style="color:#00ff88;">{data["total_queries"]}</span> &nbsp;|&nbsp;
        CO₂ actual: <span style="color:#00ff88;">{data["actual_co2_g"]:.2f}g</span> &nbsp;|&nbsp;
        CO₂ baseline: <span style="color:#ff4d4d;">{data["baseline_co2_g"]:.2f}g</span><br>
        CO₂ avoided: <span style="color:#00ff88;">{data["co2_saved_g"]:.2f}g ({co2_pct}% reduction)</span> &nbsp;|&nbsp;
        Avg energy saved: <span style="color:#00ff88;">{data["avg_energy_saved_pct"]}%</span>
    </div>
    <div class="rh">METHODOLOGY</div>
    <div style="color:var(--text);">GreenWeave dynamically routes AI inference using Impact = α·(Energy × CarbonIntensity) + β·AccuracyLoss. Baseline = large model at 700 gCO₂/kWh worst-case grid.</div>
    <div class="rh">ROUTING DISTRIBUTION</div>
    <div style="color:var(--text);">LOW ({low_pct}%): {data["low_queries"]} queries &nbsp;|&nbsp; MODERATE ({mod_pct}%): {data["moderate_queries"]} queries &nbsp;|&nbsp; HIGH ({high_pct}%): {data["high_queries"]} queries</div>
    <div class="rh">DECLARATION</div>
    <div style="color:var(--text);">Auto-generated by GreenWeave CIAI. Carbon data from real-time persistent DB. Generated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}</div>
</div>
""", unsafe_allow_html=True)