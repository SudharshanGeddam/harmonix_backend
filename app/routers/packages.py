"""
Packages router for managing package data using Supabase.

Implements CRUD operations for packages.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.core.database import get_supabase_client
from app.schemas.packages import (
    PackageCreate,
    PackageResponse,
    PackageStatus,
    PackageUpdate,
    PackagesListResponse,
)

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
        request: Package creation data

    Returns:
        PackageResponse with created package

    Raises:
        HTTPException: If package creation fails
    """
    try:
        client = get_supabase_client()

        # Prepare package data
        package_data = {
            "package_id": request.package_id,
            "destination": request.destination,
            "status": request.status.value,
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
