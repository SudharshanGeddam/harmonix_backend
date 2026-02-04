"""
Pydantic schemas for package management endpoints.

Defines request and response models for package operations.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PackageStatus(str, Enum):
    """Valid package status values."""

    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DELAYED = "delayed"


class PackageUrgency(str, Enum):
    """Valid package urgency values."""

    CRITICAL = "critical"
    PREFERRED = "preferred"
    FLEXIBLE = "flexible"


class PackageCategory(str, Enum):
    """Valid package category values."""

    MEDICINE = "medicine"
    CLOTHES = "clothes"
    FANCY = "fancy"


class PackagePriority(str, Enum):
    """Valid package priority values."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PackageCreate(BaseModel):
    """Request model for creating a new package."""

    package_id: str = Field(..., min_length=1, description="Unique package identifier")
    destination: str = Field(..., min_length=1, description="Delivery destination")
    status: PackageStatus = Field(..., description="Package status")
    urgency: PackageUrgency = Field(..., description="Package urgency level")
    description: Optional[str] = Field(
        None, description="Package description for category detection"
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description is not empty string."""
        if v is not None and isinstance(v, str) and v.strip() == "":
            return None
        return v


class PackageUpdate(BaseModel):
    """Request model for updating a package."""

    status: PackageStatus = Field(..., description="New package status")


class PackageCategoryUpdate(BaseModel):
    """Request model for updating a package's category."""

    category: PackageCategory = Field(..., description="Package category")


class PackageResponse(BaseModel):
    """Response model for a package."""

    id: str = Field(..., description="Package UUID")
    package_id: str = Field(..., description="Unique package identifier")
    destination: str = Field(..., description="Delivery destination")
    status: PackageStatus = Field(..., description="Package status")
    urgency: PackageUrgency = Field(..., description="Package urgency level")
    description: Optional[str] = Field(None, description="Package description")
    category: Optional[str] = Field(
        None, description="Detected or manual package category"
    )
    priority_label: Optional[str] = Field(
        None, description="Computed priority label"
    )
    last_updated: datetime = Field(..., description="Last update timestamp")


class PackagesListResponse(BaseModel):
    """Response model for listing packages."""

    packages: list[PackageResponse] = Field(..., description="List of packages")
    count: int = Field(..., description="Total number of packages")
