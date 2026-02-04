"""
Authentication router using Supabase Auth.

Implements signup and login endpoints for user authentication.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from supabase_auth.errors import AuthApiError

from app.core.database import get_supabase_client
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    SignupResponse,
    UserResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Signup",
)
async def signup(request: SignupRequest):
    """
    Create a new user account.

    Args:
        request: Signup request with email and password

    Returns:
        SignupResponse with created user info

    Raises:
        HTTPException: If email already exists or validation fails
    """
    try:
        client = get_supabase_client()

        # Sign up user with Supabase Auth
        response = client.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
            }
        )

        # Extract user info
        user = response.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account",
            )

        return SignupResponse(
            user=UserResponse(id=user.id, email=user.email or request.email),
            message="User created successfully",
        )

    except HTTPException:
        raise
    except AuthApiError as e:
        error_msg = str(e).lower()
        logger.warning(f"Supabase Auth error during signup: {str(e)}")

        # # Handle rate limiting
        # if "rate limit" in error_msg:
        #     raise HTTPException(
        #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        #         detail="Too many signup attempts. Please try again later.",
        #     )

        # Handle duplicate email
        if "user already exists" in error_msg or "duplicate" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # Handle validation errors
        if "invalid" in error_msg or "password" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password format",
            )

        # Generic Auth error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Signup error: {str(e)}", exc_info=True)

        # Handle duplicate email
        if "user already exists" in error_msg or "duplicate" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # Handle validation errors
        if "invalid" in error_msg or "password" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password format",
            )

        # Network/connection errors
        if (
            "connect" in error_msg
            or "connection" in error_msg
            or "getaddrinfo" in error_msg
        ):
            logger.warning(
                "Signup: Supabase connection failed. Verify SUPABASE_URL is correct."
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase service unavailable. Verify SUPABASE_URL in .env file.",
            )

        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account",
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
)
async def login(request: LoginRequest):
    """
    Authenticate a user and return tokens.

    Args:
        request: Login request with email and password

    Returns:
        LoginResponse with access token, refresh token, and user info

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        client = get_supabase_client()

        # Authenticate with Supabase Auth
        response = client.auth.sign_in_with_password(
            {
                "email": request.email,
                "password": request.password,
            }
        )

        # Extract tokens and user info
        session = response.session
        user = response.user

        if not session or not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return LoginResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token or "",
            user=UserResponse(id=user.id, email=user.email or request.email),
            token_type="bearer",
        )

    except HTTPException:
        raise
    except AuthApiError as e:
        error_msg = str(e).lower()
        logger.warning(f"Supabase Auth error during login: {str(e)}")

        # # Handle rate limiting
        # if "rate limit" in error_msg:
        #     raise HTTPException(
        #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        #         detail="Too many login attempts. Please try again later.",
        #     )

        # Handle invalid credentials
        if "invalid" in error_msg or "credentials" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Generic Auth error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Login error: {str(e)}", exc_info=True)

        # Handle invalid credentials
        if "invalid" in error_msg or "credentials" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Network/connection errors
        if (
            "connect" in error_msg
            or "connection" in error_msg
            or "getaddrinfo" in error_msg
        ):
            logger.warning(
                "Login: Supabase connection failed. Verify SUPABASE_URL is correct."
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase service unavailable. Verify SUPABASE_URL in .env file.",
            )

        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed",
        )
