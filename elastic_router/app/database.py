"""
GreenWeave — Database
SQLite persistent storage for ESG reporting.
DB_PATH defaults to the same folder as this file so
elastic_router always finds it.
"""

import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger("database")

# Store DB in same folder as this file (elastic_router/app/)
DB_PATH = os.getenv(
    "DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "greenweave_esg.db"),
)


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the carbon_log table if it does not already exist."""
    try:
        conn = get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS carbon_log (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp           TEXT    NOT NULL,
                model_used          TEXT    NOT NULL,
                mode                TEXT    DEFAULT '',
                grid_intensity      REAL    DEFAULT 0,
                actual_co2_g        REAL    DEFAULT 0,
                baseline_co2_g      REAL    DEFAULT 0,
                co2_saved_g         REAL    DEFAULT 0,
                energy_saved_pct    REAL    DEFAULT 0,
                impact_reduction_pct REAL   DEFAULT 0,
                latency_ms          REAL    DEFAULT 0,
                prompt_tokens       INTEGER DEFAULT 0,
                completion_tokens   INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
        logger.info("DB initialised at %s", DB_PATH)
    except Exception as e:
        logger.error("DB init failed: %s", e)


def log_receipt(
    model_used: str,
    intensity: float,
    actual_co2: float,
    baseline_co2: float,
    co2_saved: float,
    energy_saved: float,
    mode: str = "",
    impact_reduction_pct: float = 0.0,
    latency_ms: float = 0.0,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
):
    """Insert one row into carbon_log."""
    try:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO carbon_log (
                timestamp, model_used, mode,
                grid_intensity, actual_co2_g, baseline_co2_g,
                co2_saved_g, energy_saved_pct, impact_reduction_pct,
                latency_ms, prompt_tokens, completion_tokens
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                datetime.utcnow().isoformat(),
                model_used, mode,
                round(intensity, 2),
                round(actual_co2, 6),
                round(baseline_co2, 6),
                round(co2_saved, 6),
                round(energy_saved, 2),
                round(impact_reduction_pct, 2),
                round(latency_ms, 1),
                prompt_tokens,
                completion_tokens,
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("log_receipt failed: %s", e)


def get_stats() -> dict:
    """
    Return aggregated ESG stats directly from the DB.
    Called by the /stats API endpoint so the dashboard
    doesn't need to touch the DB file at all.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM carbon_log")
        total = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT
                COALESCE(SUM(actual_co2_g), 0),
                COALESCE(SUM(baseline_co2_g), 0),
                COALESCE(SUM(co2_saved_g), 0),
                COALESCE(AVG(energy_saved_pct), 0),
                MIN(timestamp),
                MAX(timestamp)
            FROM carbon_log
        """)
        row = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM carbon_log WHERE grid_intensity < 250")
        low_q = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM carbon_log WHERE grid_intensity >= 250 AND grid_intensity < 500")
        mod_q = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM carbon_log WHERE grid_intensity >= 500")
        high_q = cur.fetchone()[0] or 0

        # Daily trend (last 7 days)
        cur.execute("""
            SELECT
                DATE(timestamp) as day,
                COUNT(*) as queries,
                COALESCE(SUM(co2_saved_g), 0) as co2_saved
            FROM carbon_log
            WHERE timestamp >= DATE('now', '-7 days')
            GROUP BY day
            ORDER BY day ASC
        """)
        daily_rows = cur.fetchall()
        conn.close()

        # Format daily trend
        daily_trend = [
            {
                "date": row[0],
                "queries": int(row[1]),
                "co2_saved": round(float(row[2]), 4),
            }
            for row in daily_rows
        ]

        act   = float(row[0])
        bas   = float(row[1])
        saved = float(row[2])
        avg_e = float(row[3])

        # Fallback: if energy_saved_pct was stored as 0 (old data), derive from CO2
        if avg_e == 0.0 and bas > 0:
            avg_e = round(((bas - act) / bas) * 100.0, 1)

        ts_min = row[4] or ""
        if ts_min:
            try:
                from datetime import datetime as dt
                ts_min = dt.fromisoformat(ts_min).strftime("%b %d, %Y")
            except Exception:
                pass

        return {
            "total_queries":        total,
            "low_queries":          low_q,
            "moderate_queries":     mod_q,
            "high_queries":         high_q,
            "actual_co2_g":         round(act, 4),
            "baseline_co2_g":       round(bas, 4),
            "co2_saved_g":          round(saved, 4),
            "avg_energy_saved_pct": round(avg_e, 1),
            "daily_trend":          daily_trend,
            "report_period":        f"{ts_min} – now",
            "db_path":              DB_PATH,
        }

    except Exception as e:
        logger.error("get_stats failed: %s", e)
        return {
            "total_queries": 0, "low_queries": 0, "moderate_queries": 0,
            "high_queries": 0, "actual_co2_g": 0.0, "baseline_co2_g": 0.0,
            "co2_saved_g": 0.0, "avg_energy_saved_pct": 0.0,
            "daily_trend": [], "report_period": "No data yet",
            "error": str(e),
        }
