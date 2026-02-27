import random
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed


class CarbonService:
    """
    Carbon data provider (Simulated version)

    Phase 1: Single region monitoring
    Phase 2: Multi-region carbon routing
    """

    # ==============================================
    # SINGLE REGION (Module 1)
    # ==============================================

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_intensity(self) -> int:
        """
        Simulated real-time carbon intensity
        """
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

    def build_payload(self, intensity: int, status: str, region: str = "IN") -> dict:
        return {
            "region": region,
            "carbon_intensity": intensity,
            "status": status,
            "timestamp_utc": datetime.utcnow().isoformat()
        }

    # ==============================================
    # MULTI-REGION (Module 2)
    # ==============================================

    def fetch_multi_region_intensity(self) -> dict:
        """
        Simulate carbon intensity across global regions
        This mimics a real distributed carbon API setup
        """

        regions = ["IN", "DE", "US", "SG"]

        region_data = {}

        for region in regions:
            region_data[region] = random.randint(100, 800)

        return region_data