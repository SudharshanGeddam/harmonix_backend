"""
Category detection service for packages.

Provides rule-based automatic category detection based on package description.
"""

from typing import Optional


class CategoryDetector:
    """Detects package category from description using keyword matching."""

    # Category keywords
    MEDICINE_KEYWORDS = [
        "medicine",
        "tablet",
        "drug",
        "medical",
        "first aid",
        "antibiotic",
    ]
    CLOTHES_KEYWORDS = ["shirt", "jeans", "clothes", "fabric", "t-shirt", "dress"]
    FANCY_KEYWORDS = ["jewelry", "watch", "luxury", "perfume", "cosmetic"]

    @staticmethod
    def detect(description: Optional[str]) -> Optional[str]:
        """
        Detect package category from description.

        Uses keyword matching with priority: medicine > clothes > fancy.

        Args:
            description: Package description text (case-insensitive matching)

        Returns:
            Category string ('medicine', 'clothes', 'fancy') or None if no match
        """
        if not description or not isinstance(description, str):
            return None

        # Normalize description to lowercase for matching
        description_lower = description.lower()

        # Check for medicine keywords
        for keyword in CategoryDetector.MEDICINE_KEYWORDS:
            if keyword in description_lower:
                return "medicine"

        # Check for clothes keywords
        for keyword in CategoryDetector.CLOTHES_KEYWORDS:
            if keyword in description_lower:
                return "clothes"

        # Check for fancy keywords
        for keyword in CategoryDetector.FANCY_KEYWORDS:
            if keyword in description_lower:
                return "fancy"

        # No category detected
        return None
