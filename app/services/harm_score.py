"""
Harm Score calculation service for ethical receipts.

Provides disaster severity assessment based on disaster type.
Harm Score represents urgency/severity of disaster at delivery destination.

Scale: 0-100 (higher = greater urgency)
"""

from typing import Optional


class HarmScoreCalculator:
    """Calculates harm score based on disaster type."""

    @staticmethod
    def calculate(disaster_type: Optional[str]) -> int:
        """
        Calculate harm score from disaster type.

        Harm Score represents disaster severity at destination.
        Higher score indicates greater urgency for delivery.

        Rules (deterministic):
        - earthquake → 95 (most severe)
        - flood → 90
        - cyclone → 85
        - landslide → 80
        - storm → 70
        - none / unknown / null → 10 (baseline)

        Args:
            disaster_type: Type of disaster (case-insensitive)
                          Examples: "flood", "cyclone", "earthquake", "landslide", "storm"

        Returns:
            Harm score as integer (0-100)

        Example:
            score = HarmScoreCalculator.calculate("flood")  # Returns 90
            score = HarmScoreCalculator.calculate(None)      # Returns 10
        """
        if not disaster_type or not isinstance(disaster_type, str):
            return 10  # Baseline score for no disaster

        # Normalize to lowercase for comparison
        normalized_type = disaster_type.lower().strip()

        # Disaster type → harm score mapping
        disaster_scores = {
            "earthquake": 95,
            "flood": 90,
            "cyclone": 85,
            "landslide": 80,
            "storm": 70,
        }

        # Return score if found, otherwise baseline
        return disaster_scores.get(normalized_type, 10)
