class RegionRouter:
    """
    Intelligent region selection based on lowest carbon intensity.
    """

    def select_best_region(self, region_data: dict) -> dict:
        """
        Select region with lowest carbon intensity.

        Returns:
        {
            "best_region": "DE",
            "intensity": 180
        }
        """

        if not region_data:
            raise ValueError("No region data available")

        # Find region with minimum carbon intensity
        best_region = min(region_data, key=region_data.get)

        return {
            "best_region": best_region,
            "intensity": region_data[best_region]
        }