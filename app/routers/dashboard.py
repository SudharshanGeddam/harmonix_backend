"""
Dashboard router for metrics and analytics using Supabase.

Provides aggregated metrics about packages and deliveries.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardMetrics(BaseModel):
    """Response model for dashboard metrics."""

    total_packages: int = Field(..., description="Total number of packages")
    active_routes: int = Field(
        ..., description="Number of packages in transit"
    )
    alerts_count: int = Field(
        ..., description="Number of packages delayed"
    )
    completed_deliveries: int = Field(
        ..., description="Number of packages delivered"
    )


@router.get(
    "/metrics",
    response_model=DashboardMetrics,
    status_code=status.HTTP_200_OK,
    summary="Get Dashboard Metrics",
)
async def get_dashboard_metrics():
    """
    Retrieve aggregated metrics for the dashboard.

    Returns aggregated counts of packages by status:
    - total_packages: All packages
    - active_routes: Packages in transit
    - alerts_count: Delayed packages
    - completed_deliveries: Delivered packages

    Returns:
        DashboardMetrics with all metric counts

    Raises:
        HTTPException: If metrics retrieval fails
    """
    try:
        client = get_supabase_client()

        # Get total packages count
        total_response = client.table("packages").select(
            "id", count="exact"
        ).execute()
        total_packages = total_response.count

        # Get active routes (in_transit)
        active_response = client.table("packages").select(
            "id", count="exact"
        ).eq("status", "in_transit").execute()
        active_routes = active_response.count

        # Get alerts (delayed)
        alerts_response = client.table("packages").select(
            "id", count="exact"
        ).eq("status", "delayed").execute()
        alerts_count = alerts_response.count

        # Get completed deliveries
        completed_response = client.table("packages").select(
            "id", count="exact"
        ).eq("status", "delivered").execute()
        completed_deliveries = completed_response.count

        return DashboardMetrics(
            total_packages=total_packages,
            active_routes=active_routes,
            alerts_count=alerts_count,
            completed_deliveries=completed_deliveries,
        )

    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Failed to retrieve dashboard metrics: {str(e)}", exc_info=True)

        # Handle table not found
        if "could not find the table" in error_msg or "pgrst205" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Packages table not configured. Please set up the database schema.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metrics",
        )
