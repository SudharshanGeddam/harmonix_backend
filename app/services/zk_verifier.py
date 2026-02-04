"""
Zero-Knowledge Verification Service for Medical Products.

Provides ZK-style verification that a claimed product is in the WHO registry
without revealing the actual product details.
"""

from typing import Optional

from app.services.who_registry import WHO_APPROVED_PRODUCTS


class ZKVerifier:
    """
    Verifies medical product claims against WHO registry.

    Simulates Zero-Knowledge verification:
    - Checks if a claimed product type is in the WHO approved list
    - Returns boolean (verified or not)
    - Does not store or leak product details
    """

    @staticmethod
    def verify(claimed_product_type: Optional[str]) -> bool:
        """
        Verify a claimed product type is WHO-approved.

        This simulates ZK verification against a trusted authority:
        - Input: A claimed product type from the sender
        - Process: Check against WHO approved products registry
        - Output: Boolean verification result
        - Privacy: Product type claim is not stored or logged

        Args:
            claimed_product_type: Product type claimed by sender (case-insensitive)

        Returns:
            True if product is in WHO registry, False otherwise
        """
        if not claimed_product_type or not isinstance(claimed_product_type, str):
            return False

        # Normalize to lowercase for comparison
        normalized_claim = claimed_product_type.lower().strip()

        # Check against WHO approved products
        # This simulates verification against a trusted authority
        # No sensitive data is revealed in this process
        is_verified = normalized_claim in WHO_APPROVED_PRODUCTS

        return is_verified
