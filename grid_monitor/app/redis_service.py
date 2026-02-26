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

    def health_check(self):
        return self.client.ping()

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