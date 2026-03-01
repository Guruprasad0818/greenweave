"""
GreenWeave — Module 5: The Green Queue
Demonstrates Compute Time-Shifting for heavy asynchronous AI workloads.
"""
import time
import requests
from datetime import datetime

ROUTER_URL = "http://localhost:8000"
# Set a strict carbon budget. If the grid is dirtier than this, WE WAIT.
MAX_CARBON_THRESHOLD = 350  

def check_grid():
    try:
        resp = requests.get(f"{ROUTER_URL}/carbon/status", timeout=2).json()
        return resp.get("carbon_intensity", 999), resp.get("region", "UNKNOWN")
    except:
        return 999, "UNKNOWN"

def process_heavy_job():
    print("\n" + "🟢"*30)
    print("☀️ SOLAR/WIND SURGE DETECTED! GRID IS CLEAN!")
    print("🟢"*30)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Waking up AI cluster...")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing 500 queued PDF summaries...")
    time.sleep(2)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Job complete. 100% Green Energy utilized.")
    print("🟢"*30 + "\n")

print("⏳ GreenWeave Asynchronous Task Queue started...")
print("📦 Job Received: Summarize 500 Financial PDFs (Estimated Compute Time: 4 Hours)")
print(f"⚙️ Policy: Wait for grid intensity to drop below {MAX_CARBON_THRESHOLD} gCO₂/kWh.\n")

queued = True
attempt = 1

while queued:
    intensity, region = check_grid()
    
    print(f"--- Attempt {attempt} ---")
    print(f"🌍 Current Grid ({region}): {intensity} gCO₂/kWh")
    
    if intensity <= MAX_CARBON_THRESHOLD:
        process_heavy_job()
        queued = False
    else:
        print(f"🛑 Grid is too dirty (Coal-heavy). Holding task in queue to prevent emissions.")
        print(f"💤 Sleeping for 5 seconds before checking again...\n")
        time.sleep(5)
        attempt += 1
        
        # HACKATHON DEMO TRICK: 
        # On the 3rd attempt, we simulate the sun coming out to force the job to run 
        # so you don't have to wait all day during your live pitch!
        if attempt == 4:
            print("🌤️ [SIMULATION] Fast-forwarding time to 2:00 PM (Peak Solar hours)...")
            MAX_CARBON_THRESHOLD = 1000 # Artificially raise threshold to force execution