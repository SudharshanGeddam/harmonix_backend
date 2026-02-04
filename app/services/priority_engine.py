"""
Priority evaluation service for packages.

Computes priority labels based on urgency and category.
"""

from typing import Optional


class PriorityEngine:
    """Evaluates package priority based on urgency and category."""

    @staticmethod
    def compute(urgency: str, category: Optional[str]) -> Optional[str]:
        """
        Compute priority label from urgency and category.

        Priority rules:
        - If category is None → return None
        - critical + medicine → high
        - critical + clothes → medium
        - critical + fancy → low
        - preferred + medicine → medium
        - preferred + clothes → low
        - preferred + fancy → low
        - flexible + any → low

        Args:
            urgency: Package urgency ('critical', 'preferred', 'flexible')
            category: Package category ('medicine', 'clothes', 'fancy', or None)

        Returns:
            Priority label ('high', 'medium', 'low') or None if category is None
        """
        if category is None:
            return None

        # critical + medicine → high
        if urgency == "critical" and category == "medicine":
            return "high"

        # critical + clothes → medium
        if urgency == "critical" and category == "clothes":
            return "medium"

        # critical + fancy → low
        if urgency == "critical" and category == "fancy":
            return "low"

        # preferred + medicine → medium
        if urgency == "preferred" and category == "medicine":
            return "medium"

        # preferred + clothes → low
        if urgency == "preferred" and category == "clothes":
            return "low"

        # preferred + fancy → low
        if urgency == "preferred" and category == "fancy":
            return "low"

        # flexible + any → low
        if urgency == "flexible":
            return "low"

        # Fallback (should not reach here with valid inputs)
        return None
