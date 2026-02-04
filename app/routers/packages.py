"""
Packages router for managing package data using Supabase.

Implements CRUD operations for packages with urgency-based prioritization
and automatic category detection.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.core.database import get_supabase_client
from app.schemas.packages import (
    PackageCreate,
    PackageCategoryUpdate,
    PackageResponse,
    PackageStatus,
    PackageUpdate,
    PackagesListResponse,
)
from app.services.category_detector import CategoryDetector
from app.services.priority_engine import PriorityEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/packages", tags=["packages"])

TABLE_NAME = "packages"


@router.get(
    "",
    response_model=PackagesListResponse,
    status_code=status.HTTP_200_OK,
    summary="List All Packages",
)
async def list_packages():
    """
    Retrieve all packages ordered by last_updated descending.

    Returns:
        PackagesListResponse with list of packages and count

    Raises:
        HTTPException: If database query fails
    """
    try:
        client = get_supabase_client()

        # Fetch all packages ordered by last_updated descending
        response = client.table(TABLE_NAME).select("*").order(
            "last_updated", desc=True
        ).execute()

        packages = [PackageResponse(**pkg) for pkg in response.data]

        return PackagesListResponse(packages=packages, count=len(packages))

    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Failed to list packages: {str(e)}", exc_info=True)

        # Handle table not found
        if "could not find the table" in error_msg or "pgrst205" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Packages table not configured. Please set up the database schema.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve packages",
        )


@router.post(
    "",
    response_model=PackageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Package",
)
async def create_package(request: PackageCreate):
    """
    Create a new package.

    Args:
        request: Package creation data with urgency and description

    Returns:
        PackageResponse with created package
        Note: category and priority_label will be null on creation

    Raises:
        HTTPException: If package creation fails
    """
    try:
        client = get_supabase_client()

        # Prepare package data (category and priority_label are null on creation)
        package_data = {
            "package_id": request.package_id,
            "destination": request.destination,
            "status": request.status.value,
            "urgency": request.urgency.value,
            "description": request.description,
            "category": None,
            "priority_label": None,
            "last_updated": datetime.utcnow().isoformat(),
        }

        # Insert package into database
        response = client.table(TABLE_NAME).insert(package_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create package",
            )

        created_package = response.data[0]
        return PackageResponse(**created_package)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Failed to create package: {str(e)}", exc_info=True)

        # Handle table not found
        if "could not find the table" in error_msg or "pgrst205" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Packages table not configured. Please set up the database schema.",
            )

        # Handle unique constraint violation on package_id
        if "unique" in error_msg or "duplicate" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Package ID already exists",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create package",
        )


@router.patch(
    "/{package_uuid}",
    response_model=PackageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Package Status",
)
async def update_package(package_uuid: str, request: PackageUpdate):
    """
    Update a package's status.

    Args:
        package_uuid: Package UUID
        request: Status update data

    Returns:
        PackageResponse with updated package

    Raises:
        HTTPException: If package not found or update fails
    """
    try:
        client = get_supabase_client()

        # Prepare update data
        update_data = {
            "status": request.status.value,
            "last_updated": datetime.utcnow().isoformat(),
        }

        # Update package
        response = client.table(TABLE_NAME).update(update_data).eq(
            "id", package_uuid
        ).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found",
            )

        updated_package = response.data[0]
        return PackageResponse(**updated_package)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Failed to update package: {str(e)}", exc_info=True)

        # Handle table not found
        if "could not find the table" in error_msg or "pgrst205" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Packages table not configured. Please set up the database schema.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update package",
        )

@router.patch(
    "/{package_uuid}/process",
    response_model=PackageResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Package for Category and Priority",
)
async def process_package(package_uuid: str):
    """
    Process package: detect category from description and compute priority.

    Workflow:
    1. Fetch package by id
    2. Run category detection on description
    3. If category detected:
       - Compute priority_label
       - Update category and priority_label
    4. If not detected:
       - Leave both as null

    Args:
        package_uuid: Package UUID

    Returns:
        PackageResponse with updated package

    Raises:
        HTTPException: If package not found or update fails
    """
    try:
        client = get_supabase_client()

        # Fetch package by id
        fetch_response = client.table(TABLE_NAME).select("*").eq(
            "id", package_uuid
        ).execute()

        if not fetch_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found",
            )

        package = fetch_response.data[0]

        # Detect category from description
        detected_category = CategoryDetector.detect(package.get("description"))

        # Compute priority_label if category is detected
        priority_label = None
        if detected_category:
            urgency = package.get("urgency")
            priority_label = PriorityEngine.compute(urgency, detected_category)

        # Prepare update data
        update_data = {
            "category": detected_category,
            "priority_label": priority_label,
            "last_updated": datetime.utcnow().isoformat(),
        }

        # Update package
        update_response = client.table(TABLE_NAME).update(update_data).eq(
            "id", package_uuid
        ).execute()

        if not update_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update package after processing",
            )

        updated_package = update_response.data[0]
        return PackageResponse(**updated_package)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Failed to process package: {str(e)}", exc_info=True)

        # Handle table not found
        if "could not find the table" in error_msg or "pgrst205" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Packages table not configured. Please set up the database schema.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process package",
        )


@router.patch(
    "/{package_uuid}/category",
    response_model=PackageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Package Category and Priority",
)
async def update_package_category(
    package_uuid: str, request: PackageCategoryUpdate
):
    """
    Manually set package category and compute priority.

    Workflow:
    1. Update category
    2. Compute priority_label from urgency and category
    3. Save both

    Args:
        package_uuid: Package UUID
        request: Category update data

    Returns:
        PackageResponse with updated package

    Raises:
        HTTPException: If package not found or update fails
    """
    try:
        client = get_supabase_client()

        # Fetch package to get urgency
        fetch_response = client.table(TABLE_NAME).select("*").eq(
            "id", package_uuid
        ).execute()

        if not fetch_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found",
            )

        package = fetch_response.data[0]
        urgency = package.get("urgency")

        # Compute priority label from urgency and new category
        priority_label = PriorityEngine.compute(urgency, request.category.value)

        # Prepare update data
        update_data = {
            "category": request.category.value,
            "priority_label": priority_label,
            "last_updated": datetime.utcnow().isoformat(),
        }

        # Update package
        update_response = client.table(TABLE_NAME).update(update_data).eq(
            "id", package_uuid
        ).execute()

        if not update_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update package category",
            )

        updated_package = update_response.data[0]
        return PackageResponse(**updated_package)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Failed to update package category: {str(e)}", exc_info=True)

        # Handle table not found
        if "could not find the table" in error_msg or "pgrst205" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Packages table not configured. Please set up the database schema.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update package category",
        )