"""
Category detection service for packages.

Provides rule-based automatic category detection based on structured signals.
Uses sender type, fragility, weight, and verification status.
"""

from typing import Optional


class CategoryDetector:
    """Detects package category from structured signals."""

    @staticmethod
    def detect(
        urgency: str,
        weight: Optional[float],
        fragile: Optional[bool],
        sender_type: Optional[str],
        zk_verified_sender: Optional[bool],
    ) -> Optional[str]:
        """
        Detect package category from structured signals.

        Inference rules (deterministic, priority-based):
        1. If zk_verified_sender is True AND sender_type in [hospital, ngo, govt]:
           → medicine
        2. Else if fragile is True AND weight is not null AND weight < 5:
           → medicine
        3. Else if sender_type == "luxury":
           → fancy
        4. Else if sender_type in ["retail", "warehouse"]:
           → clothes
        5. Else:
           → None

        Args:
            urgency: Package urgency (unused in detection, kept for compatibility)
            weight: Package weight in kg (nullable)
            fragile: Whether package is fragile (nullable)
            sender_type: Type of sender (hospital|ngo|govt|retail|luxury|warehouse|null)
            zk_verified_sender: Whether sender is ZK-verified (nullable)

        Returns:
            Category string ('medicine', 'clothes', 'fancy') or None if no match
        """
        # Rule 1: ZK-verified sender from institutional sources → medicine
        if (
            zk_verified_sender is True
            and sender_type in ["hospital", "ngo", "govt"]
        ):
            return "medicine"

        # Rule 2: Fragile lightweight items → medicine
        if fragile is True and weight is not None and weight < 5:
            return "medicine"

        # Rule 3: Luxury sender → fancy
        if sender_type == "luxury":
            return "fancy"

        # Rule 4: Retail/warehouse → clothes
        if sender_type in ["retail", "warehouse"]:
            return "clothes"

        # No category detected
        return None
