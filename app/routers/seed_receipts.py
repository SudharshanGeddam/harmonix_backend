"""
Demo seed endpoint for populating receipts table with realistic data.

⚠️  Demo seed endpoint — remove in production

Provides one-time seeding of the receipts table with varied demo data
for testing ethical receipt documentation.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.core.database import get_supabase_client
from app.schemas.receipts import ReceiptResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/seed", tags=["seed"])

TABLE_NAME = "receipts"


class DemoReceiptData:
    """Holds demo receipt data for seeding."""

    def __init__(
        self,
        receipt_id: str,
        package_id: str,
        proof_summary: str,
        status: str,
    ):
        self.receipt_id = receipt_id
        self.package_id = package_id
        self.proof_summary = proof_summary
        self.status = status


def _get_demo_receipts() -> list[DemoReceiptData]:
    """
    Generate demo receipts with varied combinations.

    Includes:
    - verified receipts for hospital packages
    - pending receipts for ngo deliveries
    - verified receipts for luxury items
    - mixed statuses for different package types
    """
    return [
        # 1. Hospital Package - Verified Receipt
        DemoReceiptData(
            receipt_id="RECEIPT-001-HOSPITAL",
            package_id="DEMO-001-HOSPITAL-CRIT",
            proof_summary="Emergency medical supplies verified by City Hospital. Delivery confirmed with signature from ER Director. Ethically sourced from WHO-approved supplier.",
            status="verified",
        ),
        # 2. NGO Package - Pending Receipt
        DemoReceiptData(
            receipt_id="RECEIPT-002-NGO",
            package_id="DEMO-002-NGO-CRIT",
            proof_summary="Disaster relief supplies awaiting verification. Sent to Relief NGO, verification documents submitted.",
            status="pending",
        ),
        # 3. NGO Community Health - Verified Receipt
        DemoReceiptData(
            receipt_id="RECEIPT-003-COMMUNITY-NGO",
            package_id="DEMO-003-NGO-PREF",
            proof_summary="Community health supplies verified by Community Health NGO. Rural center received package. Ethical sourcing verified from certified suppliers.",
            status="verified",
        ),
        # 4. Warehouse - Pending Receipt
        DemoReceiptData(
            receipt_id="RECEIPT-004-WAREHOUSE",
            package_id="DEMO-004-WAREHOUSE-FLEX",
            proof_summary="Storage facility received goods. Verification in progress for regional warehouse inventory.",
            status="pending",
        ),
        # 5. Retail - Verified Receipt
        DemoReceiptData(
            receipt_id="RECEIPT-005-RETAIL",
            package_id="DEMO-005-RETAIL-DELAYED",
            proof_summary="Retail store received clothing shipment. Verified delivery with photos. Fair-trade sourcing confirmed.",
            status="verified",
        ),
        # 6. Luxury - Verified Receipt
        DemoReceiptData(
            receipt_id="RECEIPT-006-LUXURY",
            package_id="DEMO-006-LUXURY-DELIVERED",
            proof_summary="Luxury boutique received exclusive collection. Quality inspection completed. Ethically produced by certified artisans.",
            status="verified",
        ),
        # 7. Government Health Center - Pending Receipt
        DemoReceiptData(
            receipt_id="RECEIPT-007-GOVT",
            package_id="DEMO-007-GOVT-CRIT",
            proof_summary="Government health center medical shipment awaiting final verification. Initial inspection passed.",
            status="pending",
        ),
        # 8. Fashion Retail - Verified Receipt
        DemoReceiptData(
            receipt_id="RECEIPT-008-FASHION",
            package_id="DEMO-008-RETAIL-PREF",
            proof_summary="Fashion retail received seasonal collection. Verified delivery from ethical supplier. Labor conditions certified as fair.",
            status="verified",
        ),
        # 9. Art Gallery - Verified Receipt
        DemoReceiptData(
            receipt_id="RECEIPT-009-GALLERY",
            package_id="DEMO-009-LUXURY-FLEX",
            proof_summary="Art gallery received cultural items. Artwork authenticated and ethically sourced from established artists.",
            status="verified",
        ),
        # 10. Medical NGO - Pending Receipt
        DemoReceiptData(
            receipt_id="RECEIPT-010-MEDICAL-NGO",
            package_id="DEMO-010-NGO-CRIT-MED",
            proof_summary="Medical emergency supplies sent to NGO emergency response unit. Verification documents being processed.",
            status="pending",
        ),
    ]


@router.post(
    "/receipts",
    response_model=list[ReceiptResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Seed Demo Receipts",
)
async def seed_receipts():
    """
    Populate receipts table with demo data.

    Inserts 10 demo receipts with varied statuses (verified/pending)
    and proof summaries for ethical receipt documentation.
    Each receipt is linked to a corresponding demo package.

    Safety:
    - Does NOT reinsert if receipt_id already exists (checks before insert)

    Returns:
        List of created ReceiptResponse objects

    Raises:
        HTTPException: If database error occurs
    """
    try:
        client = get_supabase_client()
        demo_receipts = _get_demo_receipts()
        created_receipts = []

        for demo_rcpt in demo_receipts:
            # Check if receipt_id already exists
            existing = client.table(TABLE_NAME).select("id").eq(
                "receipt_id", demo_rcpt.receipt_id
            ).execute()

            if existing.data:
                logger.info(
                    f"Receipt {demo_rcpt.receipt_id} already exists, skipping."
                )
                continue

            # Prepare receipt data for insertion
            receipt_data = {
                "receipt_id": demo_rcpt.receipt_id,
                "package_id": demo_rcpt.package_id,
                "proof_summary": demo_rcpt.proof_summary,
                "status": demo_rcpt.status,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Insert into database
            response = client.table(TABLE_NAME).insert(receipt_data).execute()

            if response.data:
                created_receipts.append(ReceiptResponse(**response.data[0]))
                logger.info(
                    f"Created demo receipt {demo_rcpt.receipt_id} "
                    f"(status={demo_rcpt.status}, package={demo_rcpt.package_id})"
                )

        if not created_receipts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="All demo receipts already exist in database",
            )

        logger.info(
            f"Seeding complete: {len(created_receipts)} receipts created"
        )
        return created_receipts

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Failed to seed receipts: {str(e)}", exc_info=True)

        # Handle table not found
        if "could not find the table" in error_msg or "pgrst205" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Receipts table not configured. Please set up the database schema.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to seed receipts",
        )
