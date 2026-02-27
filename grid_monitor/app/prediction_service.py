import statistics


class PredictionService:

    def __init__(self, redis_service):
        self.redis = redis_service

    def calculate_trend(self):
        #history = self.redis.get_recent_history(6)
        history = self.redis.get_recent_carbon_history(6)

        if len(history) < 3:
            return {
                "trend": "INSUFFICIENT_DATA",
                "confidence": 0
            }

        latest = history[0]
        oldest = history[-1]

        delta = latest - oldest

        # Trend classification
        if delta < -20:
            trend = "IMPROVING"      # carbon decreasing
        elif delta > 20:
            trend = "WORSENING"
        else:
            trend = "STABLE"

        confidence = min(abs(delta) / 100, 1.0)

        return {
            "trend": trend,
            "confidence": round(confidence, 2)
        }

    def should_delay_execution(self):
        result = self.calculate_trend()

        if result["trend"] == "IMPROVING" and result["confidence"] > 0.3:
            return True

        return False