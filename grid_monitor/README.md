# GreenWeave – Grid Monitor Module

This service polls Electricity Maps API for real-time carbon intensity and stores categorized results in Redis.

## Features

- Retry mechanism (3 attempts)
- Redis TTL expiration
- Environment-based configuration
- Structured logging
- Production-ready modular design

## Run

1. Install dependencies:
   pip install -r requirements.txt

2. Start Redis:
   docker run -d -p 6379:6379 --name greenweave-redis redis

3. Run worker:
   python -m app.main

## Redis Key

grid_status

Example:

{
  "region": "IN-SO",
  "carbon_intensity": 642,
  "status": "HIGH",
  "timestamp_utc": "2026-02-26T12:00:00"
}