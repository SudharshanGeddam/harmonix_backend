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


class SenderType(str, Enum):
    """Valid sender type values."""

    HOSPITAL = "hospital"
    NGO = "ngo"
    GOVT = "govt"
    RETAIL = "retail"
    LUXURY = "luxury"
    WAREHOUSE = "warehouse"
    BUSINESS = "business"


class PackageCreate(BaseModel):
    """Request model for creating a new package."""

    package_id: str = Field(..., min_length=1, description="Unique package identifier")
    destination: str = Field(..., min_length=1, description="Delivery destination")
    status: PackageStatus = Field(..., description="Package status")
    urgency: PackageUrgency = Field(..., description="Package urgency level")
    description: Optional[str] = Field(
        None, description="Package description (for backward compatibility)"
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description is not empty string."""
        if v is not None and isinstance(v, str) and v.strip() == "":
            return None
        return v


class PackageProcessSignals(BaseModel):
    """Request model for processing package with structured signals.
    
    All fields are optional. At least one field should be provided for meaningful processing.
    Missing fields will be treated as None.
    """

    weight: Optional[float] = Field(
        None, ge=0, description="Package weight in kg"
    )
    fragile: Optional[bool] = Field(
        None, description="Whether package is fragile"
    )
    sender_type: Optional[SenderType] = Field(
        None, description="Type of sender (hospital|ngo|govt|retail|luxury|warehouse|business)"
    )
    zk_verified_sender: Optional[bool] = Field(
        None, description="Whether sender is ZK-verified"
    )
    claimed_product_type: Optional[str] = Field(
        None, description="Claimed product type for ZK verification (not stored for privacy)"
    )
    
    class Config:
        """Pydantic config for flexible input."""
        extra = "ignore"  # Ignore extra fields from frontend
        json_schema_extra = {
            "examples": [
                {
                    "weight": 2.5,
                    "fragile": True,
                    "sender_type": "hospital",
                    "claimed_product_type": "medical_supplies",
                    "zk_verified_sender": None
                },
                {
                    "weight": 5.0,
                    "fragile": False,
                    "sender_type": "ngo"
                },
                {
                    "claimed_product_type": "medicine"
                }
            ]
        }


class PackageUpdate(BaseModel):
    """Request model for updating a package."""

    status: Optional[str] = Field(None, description="New package status")
    
    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize status value."""
        if v is None:
            return None
        
        # Convert to lowercase for case-insensitive matching
        v_lower = str(v).lower().strip()
        
        # Map to valid enum values
        valid_statuses = {"in_transit", "delivered", "delayed"}
        if v_lower in valid_statuses:
            return v_lower
        
        # If not valid, raise error with helpful message
        raise ValueError(
            f"Invalid status '{v}'. Must be one of: {', '.join(valid_statuses)}"
        )


class PackageCategoryUpdate(BaseModel):
    """Request model for updating a package's category."""

    category: PackageCategory = Field(..., description="Package category")


class PackageResponse(BaseModel):
    """Response model for a package."""

    id: str = Field(..., description="Package UUID")
    package_id: str = Field(..., description="Unique package identifier")
    destination: str = Field(..., description="Delivery destination")
    status: PackageStatus = Field(..., description="Package status")
    urgency: Optional[PackageUrgency] = Field(None, description="Package urgency level")
    description: Optional[str] = Field(None, description="Package description")
    weight: Optional[float] = Field(None, description="Package weight in kg")
    fragile: Optional[bool] = Field(None, description="Whether package is fragile")
    sender_type: Optional[str] = Field(None, description="Type of sender")
    zk_verified_sender: Optional[bool] = Field(
        None, description="Whether sender is ZK-verified"
    )
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
