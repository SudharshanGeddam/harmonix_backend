"""
Pydantic schemas for package management endpoints.

Defines request and response models for package operations.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PackageStatus(str, Enum):
    """Valid package status values."""

    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DELAYED = "delayed"


class PackageCreate(BaseModel):
    """Request model for creating a new package."""

    package_id: str = Field(..., min_length=1, description="Unique package identifier")
    destination: str = Field(..., min_length=1, description="Delivery destination")
    status: PackageStatus = Field(..., description="Package status")


class PackageUpdate(BaseModel):
    """Request model for updating a package."""

    status: PackageStatus = Field(..., description="New package status")


class PackageResponse(BaseModel):
    """Response model for a package."""

    id: str = Field(..., description="Package UUID")
    package_id: str = Field(..., description="Unique package identifier")
    destination: str = Field(..., description="Delivery destination")
    status: PackageStatus = Field(..., description="Package status")
    last_updated: datetime = Field(..., description="Last update timestamp")


class PackagesListResponse(BaseModel):
    """Response model for listing packages."""

    packages: list[PackageResponse] = Field(..., description="List of packages")
    count: int = Field(..., description="Total number of packages")
