import random
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed


class CarbonService:

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_intensity(self) -> int:
        """
        Simulated real-time carbon intensity (Free version)
        """

        # Simulate realistic carbon values
        intensity = random.randint(100, 800)

        print("Simulated API call successful")

        return intensity

    def categorize(self, intensity: int) -> str:

        if intensity <= 200:
            return "LOW"
        elif intensity <= 500:
            return "MODERATE"
        else:
            return "HIGH"

    def build_payload(self, intensity: int, status: str) -> dict:

        return {
            "region": "IN",
            "carbon_intensity": intensity,
            "status": status,
            "timestamp_utc": datetime.utcnow().isoformat()
        }