"""
Pydantic schemas for receipt management endpoints.

Defines request and response models for receipt operations.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ReceiptStatus(str, Enum):
    """Valid receipt status values."""

    VERIFIED = "verified"
    PENDING = "pending"


class ReceiptCreate(BaseModel):
    """Request model for creating a new receipt."""

    receipt_id: str = Field(..., min_length=1, description="Unique receipt identifier")
    package_id: str = Field(..., min_length=1, description="Associated package ID")
    proof_summary: str = Field(..., min_length=1, description="Summary of ethical proof")
    status: ReceiptStatus = Field(..., description="Receipt status")


class ReceiptResponse(BaseModel):
    """Response model for a receipt."""

    id: str = Field(..., description="Receipt UUID")
    receipt_id: str = Field(..., description="Unique receipt identifier")
    package_id: str = Field(..., description="Associated package ID")
    proof_summary: str = Field(..., description="Summary of ethical proof")
    status: ReceiptStatus = Field(..., description="Receipt status")
    timestamp: datetime = Field(..., description="Creation timestamp")


class ReceiptsListResponse(BaseModel):
    """Response model for listing receipts."""

    receipts: list[ReceiptResponse] = Field(..., description="List of receipts")
    count: int = Field(..., description="Total number of receipts")
