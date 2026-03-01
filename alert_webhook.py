"""
GreenWeave — Module 4: Carbon Alert Webhook
Simulates an enterprise Slack/Teams integration for DevOps monitoring.
"""
import time
import requests
from datetime import datetime

# We use localhost because we will run this outside of Docker
ROUTER_URL = "http://localhost:8000"
THRESHOLD = 400  # Alert if gCO2 goes above this (your grid is currently in the 400s!)

def print_slack_alert(region, intensity, status):
    print("\n" + "🔴"*30)
    print("🚨 [INCOMING ENTERPRISE WEBHOOK ALERT] 🚨")
    print("🔴"*30)
    print(f"🏢 Integration: Microsoft Teams / Slack")
    print(f"📍 Channel:   #devops-infrastructure")
    print(f"⏰ Time:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    print(f"⚠️ WARNING: Carbon Intensity Spike Detected!")
    print(f"🌍 Region:    {region}")
    print(f"💨 Intensity: {intensity} gCO₂/kWh ({status})")
    print(f"🛡️ ACTION TAKEN: GreenWeave has automatically engaged 'Budget Protection Mode'.")
    print(f"   Non-urgent traffic is being delayed and routed to the Green Queue.")
    print("-" * 60 + "\n")

print("🤖 GreenWeave Webhook Monitor starting...")
print(f"👀 Watching API: {ROUTER_URL}/carbon/status")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        try:
            # Poll the live router API
            response = requests.get(f"{ROUTER_URL}/carbon/status", timeout=2)
            data = response.json()
            
            intensity = data.get("carbon_intensity", 0)
            region = data.get("region", "UNKNOWN")
            status = data.get("status", "UNKNOWN")
            
            # Hackathon Demo trigger: If it goes over threshold, FIRE THE ALERT!
            if intensity > THRESHOLD:
                print_slack_alert(region, intensity, status)
                print("🛑 Alert fired! Pausing monitor for 30 seconds to avoid channel spam...")
                time.sleep(30)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Grid Check: {intensity} gCO₂ in {region} -> STABLE. No alerts.")
                
        except requests.exceptions.ConnectionError:
            print("⏳ Waiting for GreenWeave Router to come online...")
            
        time.sleep(5)  # Check every 5 seconds
        
except KeyboardInterrupt:
    print("\n🛑 Webhook Monitor stopped.")