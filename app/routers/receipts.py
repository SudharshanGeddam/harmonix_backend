"""
Receipts router for managing ethical receipt data using Supabase.

Implements CRUD operations for receipts with harm score calculation.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.core.database import get_supabase_client
from app.schemas.receipts import (
    ReceiptCreate,
    ReceiptResponse,
    ReceiptStatus,
    ReceiptsListResponse,
)
from app.services.harm_score import HarmScoreCalculator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/receipts", tags=["receipts"])

TABLE_NAME = "receipts"


@router.get(
    "",
    response_model=ReceiptsListResponse,
    status_code=status.HTTP_200_OK,
    summary="List All Receipts",
)
async def list_receipts():
    """
    Retrieve all receipts ordered by timestamp descending.

    Returns:
        ReceiptsListResponse with list of receipts and count

    Raises:
        HTTPException: If database query fails
    """
    try:
        client = get_supabase_client()

        # Fetch all receipts ordered by timestamp descending
        response = client.table(TABLE_NAME).select("*").order(
            "timestamp", desc=True
        ).execute()

        receipts = [ReceiptResponse(**rcpt) for rcpt in response.data]

        return ReceiptsListResponse(receipts=receipts, count=len(receipts))

    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Failed to list receipts: {str(e)}", exc_info=True)

        # Handle table not found
        if "could not find the table" in error_msg or "pgrst205" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Receipts table not configured. Please set up the database schema.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve receipts",
        )


@router.post(
    "",
    response_model=ReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Receipt",
)
async def create_receipt(request: ReceiptCreate):
    """
    Create a new receipt with harm score calculation.

    Args:
        request: Receipt creation data with optional disaster_type

    Returns:
        ReceiptResponse with created receipt and calculated harm_score

    Raises:
        HTTPException: If receipt creation fails
    """
    try:
        client = get_supabase_client()

        # Calculate harm score from disaster type
        harm_score = HarmScoreCalculator.calculate(request.disaster_type)

        # Prepare receipt data
        receipt_data = {
            "receipt_id": request.receipt_id,
            "package_id": request.package_id,
            "proof_summary": request.proof_summary,
            "status": request.status.value,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Insert receipt into database
        response = client.table(TABLE_NAME).insert(receipt_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create receipt",
            )

        # Add harm_score to response (calculated, not from DB)
        created_receipt = response.data[0]
        created_receipt["harm_score"] = harm_score

        logger.info(
            f"Created receipt {request.receipt_id} "
            f"(disaster={request.disaster_type}, harm_score={harm_score})"
        )

        created_receipt = response.data[0]
        return ReceiptResponse(**created_receipt)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Failed to create receipt: {str(e)}", exc_info=True)

        # Handle table not found
        if "could not find the table" in error_msg or "pgrst205" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Receipts table not configured. Please set up the database schema.",
            )

        # Handle unique constraint violation on receipt_id
        if "unique" in error_msg or "duplicate" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Receipt ID already exists",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create receipt",
        )
