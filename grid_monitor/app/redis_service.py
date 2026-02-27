import redis
import json
from app.config import Settings


class RedisService:

    def __init__(self):
        self.client = redis.Redis(
            host=Settings.REDIS_HOST,
            port=Settings.REDIS_PORT,
            decode_responses=True
        )

    # ----------------------------
    # Health
    # ----------------------------
    def health_check(self):
        return self.client.ping()

    # ----------------------------
    # Current Grid Status
    # ----------------------------
    def store_grid_status(self, payload: dict):
        self.client.set(
            "grid_status",
            json.dumps(payload),
            ex=Settings.REDIS_TTL
        )

    def get_grid_status(self):
        data = self.client.get("grid_status")
        if data:
            return json.loads(data)
        return None

    # ----------------------------
    # Carbon History (NEW)
    # ----------------------------
    def store_carbon_history(self, intensity: int):
        """
        Store rolling last 24 carbon intensity values
        """
        self.client.lpush("carbon_history", intensity)
        self.client.ltrim("carbon_history", 0, 23)

    def get_recent_carbon_history(self, count: int = 6):
        """
        Fetch recent carbon values for prediction
        """
        values = self.client.lrange("carbon_history", 0, count - 1)
        return [int(v) for v in values if v]

    # ----------------------------
    # Impact History (Future use)
    # ----------------------------
    def store_impact_score(self, score: float):
        self.client.lpush("impact_history", score)
        self.client.ltrim("impact_history", 0, 100)

    def get_recent_impact_scores(self, count: int = 20):
        values = self.client.lrange("impact_history", 0, count - 1)
        return [float(v) for v in values if v]