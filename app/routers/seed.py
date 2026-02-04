"""
Demo seed endpoint for populating packages table with realistic data.

⚠️  Demo seed endpoint — remove in production

Provides one-time seeding of the packages table with varied demo data
for testing category detection and priority computation.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.core.database import get_supabase_client
from app.schemas.packages import PackageResponse
from app.services.category_detector import CategoryDetector
from app.services.priority_engine import PriorityEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/seed", tags=["seed"])

TABLE_NAME = "packages"


class DemoPackageData:
    """Holds demo package data for seeding."""

    def __init__(
        self,
        package_id: str,
        destination: str,
        urgency: str,
        status: str,
        weight: Optional[float],
        fragile: Optional[bool],
        sender_type: Optional[str],
    ):
        self.package_id = package_id
        self.destination = destination
        self.urgency = urgency
        self.status = status
        self.weight = weight
        self.fragile = fragile
        self.sender_type = sender_type


def _get_demo_packages() -> list[DemoPackageData]:
    """
    Generate demo packages with varied combinations.

    Includes:
    - critical + hospital + fragile → high priority
    - preferred + ngo → medium
    - flexible + warehouse → low
    - delayed + critical
    - delivered + low priority
    """
    return [
        # 1. Critical + Hospital + Fragile → high priority
        DemoPackageData(
            package_id="DEMO-001-HOSPITAL-CRIT",
            destination="City Hospital, Emergency Ward",
            urgency="critical",
            status="in_transit",
            weight=2.5,
            fragile=True,
            sender_type="hospital",
        ),
        # 2. Critical + NGO → medium priority
        DemoPackageData(
            package_id="DEMO-002-NGO-CRIT",
            destination="Relief NGO, Disaster Zone",
            urgency="critical",
            status="in_transit",
            weight=8.0,
            fragile=False,
            sender_type="ngo",
        ),
        # 3. Preferred + NGO → medium priority
        DemoPackageData(
            package_id="DEMO-003-NGO-PREF",
            destination="Community Health NGO, Rural Center",
            urgency="preferred",
            status="in_transit",
            weight=5.5,
            fragile=True,
            sender_type="ngo",
        ),
        # 4. Flexible + Warehouse → low priority
        DemoPackageData(
            package_id="DEMO-004-WAREHOUSE-FLEX",
            destination="Regional Warehouse, Storage Zone",
            urgency="flexible",
            status="in_transit",
            weight=15.0,
            fragile=False,
            sender_type="warehouse",
        ),
        # 5. Delayed + Critical → medium priority (critical + clothes)
        DemoPackageData(
            package_id="DEMO-005-RETAIL-DELAYED",
            destination="Retail Store, Downtown",
            urgency="critical",
            status="delayed",
            weight=3.0,
            fragile=False,
            sender_type="retail",
        ),
        # 6. Delivered + Low priority (flexible)
        DemoPackageData(
            package_id="DEMO-006-LUXURY-DELIVERED",
            destination="Luxury Boutique, Upscale District",
            urgency="flexible",
            status="delivered",
            weight=1.2,
            fragile=True,
            sender_type="luxury",
        ),
        # 7. Critical + Govt + Fragile → high priority (medicine)
        DemoPackageData(
            package_id="DEMO-007-GOVT-CRIT",
            destination="Government Health Center, Central",
            urgency="critical",
            status="in_transit",
            weight=3.5,
            fragile=True,
            sender_type="govt",
        ),
        # 8. Preferred + Retail → low priority (clothes)
        DemoPackageData(
            package_id="DEMO-008-RETAIL-PREF",
            destination="Fashion Retail, Shopping Mall",
            urgency="preferred",
            status="in_transit",
            weight=2.0,
            fragile=False,
            sender_type="retail",
        ),
        # 9. Flexible + Luxury → low priority (fancy)
        DemoPackageData(
            package_id="DEMO-009-LUXURY-FLEX",
            destination="Art Gallery, Cultural Center",
            urgency="flexible",
            status="in_transit",
            weight=0.8,
            fragile=True,
            sender_type="luxury",
        ),
        # 10. Critical + NGO + Hospital → high priority (medicine)
        DemoPackageData(
            package_id="DEMO-010-NGO-CRIT-MED",
            destination="Medical NGO, Emergency Response",
            urgency="critical",
            status="in_transit",
            weight=4.2,
            fragile=True,
            sender_type="ngo",
        ),
    ]


@router.post(
    "/packages",
    response_model=list[PackageResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Seed Demo Packages",
)
async def seed_packages():
    """
    Populate packages table with demo data.

    Inserts 8–10 demo packages with varied urgency, status, and sender types.
    Each package:
    - Includes structured signals (weight, fragile, sender_type)
    - Runs through category detection
    - Computes priority_label based on urgency + category

    Safety:
    - Does NOT reinsert if package_id already exists (checks before insert)

    Returns:
        List of created PackageResponse objects

    Raises:
        HTTPException: If database error occurs
    """
    try:
        client = get_supabase_client()
        demo_packages = _get_demo_packages()
        created_packages = []

        for demo_pkg in demo_packages:
            # Check if package_id already exists
            existing = client.table(TABLE_NAME).select("id").eq(
                "package_id", demo_pkg.package_id
            ).execute()

            if existing.data:
                logger.info(
                    f"Package {demo_pkg.package_id} already exists, skipping."
                )
                continue

            # Detect category using structured signals
            category = CategoryDetector.detect(
                urgency=demo_pkg.urgency,
                weight=demo_pkg.weight,
                fragile=demo_pkg.fragile,
                sender_type=demo_pkg.sender_type,
                zk_verified_sender=None,
            )

            # Compute priority_label based on urgency + category
            priority_label = None
            if category:
                priority_label = PriorityEngine.compute(
                    demo_pkg.urgency, category
                )

            # Prepare package data for insertion
            package_data = {
                "package_id": demo_pkg.package_id,
                "destination": demo_pkg.destination,
                "status": demo_pkg.status,
                "urgency": demo_pkg.urgency,
                "weight": demo_pkg.weight,
                "fragile": demo_pkg.fragile,
                "sender_type": demo_pkg.sender_type,
                "zk_verified_sender": None,
                "category": category,
                "priority_label": priority_label,
                "description": f"Demo package: {demo_pkg.sender_type}",
                "last_updated": datetime.utcnow().isoformat(),
            }

            # Insert into database
            response = client.table(TABLE_NAME).insert(package_data).execute()

            if response.data:
                created_packages.append(PackageResponse(**response.data[0]))
                logger.info(
                    f"Created demo package {demo_pkg.package_id} "
                    f"(category={category}, priority={priority_label})"
                )

        if not created_packages:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="All demo packages already exist in database",
            )

        logger.info(
            f"Seeding complete: {len(created_packages)} packages created"
        )
        return created_packages

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Failed to seed packages: {str(e)}", exc_info=True)

        # Handle table not found
        if "could not find the table" in error_msg or "pgrst205" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Packages table not configured. Please set up the database schema.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to seed packages",
        )
