import sqlite3
import os

DB_PATH = "greenweave_esg.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS carbon_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  model_used TEXT, 
                  grid_intensity REAL, 
                  actual_co2_g REAL,
                  baseline_co2_g REAL,
                  co2_saved_g REAL, 
                  energy_saved_pct REAL)''')
    conn.commit()
    conn.close()

def log_receipt(model_used, intensity, actual_co2, baseline_co2, co2_saved, energy_saved):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO carbon_log 
                 (model_used, grid_intensity, actual_co2_g, baseline_co2_g, co2_saved_g, energy_saved_pct) 
                 VALUES (?, ?, ?, ?, ?, ?)""", 
              (model_used, intensity, actual_co2, baseline_co2, co2_saved, energy_saved))
    conn.commit()
    conn.close()