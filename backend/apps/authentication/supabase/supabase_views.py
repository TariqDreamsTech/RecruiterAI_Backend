"""
Supabase Authentication Views
Django REST Framework views using Supabase Auth
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .supabase_auth import supabase_auth
from .supabase_serializers import (
    SupabaseRegistrationSerializer,
    SupabaseLoginSerializer,
    SupabasePasswordResetSerializer,
    SupabaseUserUpdateSerializer,
    SupabaseOAuthSerializer,
    SupabaseRefreshTokenSerializer,
    SupabaseAuthResponseSerializer,
    SupabaseUserResponseSerializer,
    SupabaseLogoutSerializer,
)


def get_auth_token_from_request(request):
    """Extract Bearer token from Authorization header"""
    auth_header = request.headers.get("Authorization", "")

    if auth_header.startswith("Bearer "):
        return auth_header[7:]  # Remove 'Bearer ' prefix
    elif auth_header and not auth_header.startswith("Bearer "):
        # If token is provided without Bearer prefix, assume it's the token
        return auth_header
    return None


@extend_schema(
    tags=["Supabase Authentication"],
    summary="Register New User",
    description="Register a new user using Supabase Auth with email verification",
    request=SupabaseRegistrationSerializer,
    responses={201: SupabaseAuthResponseSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def supabase_register(request):
    """Register a new user with Supabase Auth"""
    serializer = SupabaseRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.validated_data
        email = data["email"]
        password = data["password"]

        # Prepare user metadata
        user_metadata = {}
        if "username" in data:
            user_metadata["username"] = data["username"]
        if "user_type" in data:
            user_metadata["user_type"] = data["user_type"]
        if "phone_number" in data:
            user_metadata["phone_number"] = data["phone_number"]
        if "full_name" in data:
            user_metadata["full_name"] = data["full_name"]

        # Register with Supabase
        result = supabase_auth.sign_up(email, password, user_metadata)

        if result["success"]:
            # Handle both dict and object types for user data
            user_data = result["user"]
            if user_data and hasattr(user_data, "__dict__"):
                user_data = user_data.__dict__

            response_data = {
                "message": result["message"],
                "user": user_data,
            }

            if result["session"]:
                response_data.update(
                    {
                        "access_token": result["session"].access_token,
                        "refresh_token": result["session"].refresh_token,
                        "expires_in": result["session"].expires_in,
                        "expires_at": result["session"].expires_at,
                        "token_type": result["session"].token_type,
                    }
                )

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": result["error"], "message": result["message"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Supabase Authentication"],
    summary="User Login",
    description="Authenticate user with email and password using Supabase Auth",
    request=SupabaseLoginSerializer,
    responses={200: SupabaseAuthResponseSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def supabase_login(request):
    """Login user with Supabase Auth"""
    serializer = SupabaseLoginSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.validated_data
        email = data["email"]
        password = data["password"]

        # Login with Supabase
        result = supabase_auth.sign_in(email, password)

        if result["success"]:
            # Handle both dict and object types for user data
            user_data = result["user"]
            if user_data and hasattr(user_data, "__dict__"):
                user_data = user_data.__dict__

            response_data = {
                "message": result["message"],
                "user": user_data,
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
            }

            if result["session"]:
                response_data.update(
                    {
                        "expires_in": result["session"].expires_in,
                        "expires_at": result["session"].expires_at,
                        "token_type": result["session"].token_type,
                    }
                )

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": result["error"], "message": result["message"]},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Supabase Authentication"],
    summary="User Logout",
    description="Logout user and invalidate session",
    request=SupabaseLogoutSerializer,
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
)
@api_view(["POST"])
@permission_classes([AllowAny])  # We handle auth manually
def supabase_logout(request):
    """Logout user from Supabase Auth"""
    access_token = get_auth_token_from_request(request)

    if not access_token:
        return Response(
            {"error": "Authorization header with Bearer token required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Logout with Supabase
    result = supabase_auth.sign_out(access_token)

    if result["success"]:
        return Response({"message": result["message"]}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": result["error"], "message": result["message"]},
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(
    tags=["Supabase Authentication"],
    summary="Get User Profile",
    description="Get current user information from Supabase Auth",
    responses={200: SupabaseUserResponseSerializer},
)
@api_view(["GET"])
@permission_classes([AllowAny])  # We handle auth manually
def supabase_get_user(request):
    """Get current user from Supabase Auth"""
    access_token = get_auth_token_from_request(request)

    if not access_token:
        return Response(
            {"error": "Authorization header with Bearer token required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Get user from Supabase
    result = supabase_auth.get_user(access_token)

    if result["success"]:
        # Handle both dict and object types for user data
        user_data = result["user"]
        if user_data and hasattr(user_data, "__dict__"):
            user_data = user_data.__dict__

        return Response(
            {
                "user": user_data,
                "message": result["message"],
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"error": result["error"], "message": result["message"]},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@extend_schema(
    tags=["Supabase Authentication"],
    summary="Update User Profile",
    description="Update user information in Supabase Auth",
    request=SupabaseUserUpdateSerializer,
    responses={200: SupabaseUserResponseSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([AllowAny])  # We handle auth manually
def supabase_update_user(request):
    """Update user in Supabase Auth"""
    access_token = get_auth_token_from_request(request)

    if not access_token:
        return Response(
            {"error": "Authorization header with Bearer token required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    serializer = SupabaseUserUpdateSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.validated_data

        # Prepare update attributes
        attributes = {}

        # Direct attributes
        if "email" in data:
            attributes["email"] = data["email"]
        if "password" in data:
            attributes["password"] = data["password"]
        if "phone" in data:
            attributes["phone"] = data["phone"]

        # User metadata
        user_metadata = data.get("user_metadata", {})

        # Add metadata fields to user_metadata
        metadata_fields = [
            "username",
            "user_type",
            "full_name",
            "bio",
            "location",
            "website",
            "linkedin_url",
            "github_url",
            "skills",
            "experience_years",
        ]

        for field in metadata_fields:
            if field in data:
                user_metadata[field] = data[field]

        if user_metadata:
            attributes["data"] = user_metadata

        # Update user with Supabase
        result = supabase_auth.update_user(access_token, attributes)

        if result["success"]:
            # Handle both dict and object types for user data
            user_data = result["user"]
            if user_data and hasattr(user_data, "__dict__"):
                user_data = user_data.__dict__

            return Response(
                {
                    "user": user_data,
                    "message": result["message"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": result["error"], "message": result["message"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Supabase Authentication"],
    summary="Password Reset",
    description="Send password reset email via Supabase Auth",
    request=SupabasePasswordResetSerializer,
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def supabase_password_reset(request):
    """Send password reset email via Supabase Auth"""
    serializer = SupabasePasswordResetSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data["email"]

        # Send password reset email
        result = supabase_auth.reset_password(email)

        if result["success"]:
            return Response({"message": result["message"]}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": result["error"], "message": result["message"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Supabase Authentication"],
    summary="Refresh Token",
    description="Refresh access token using refresh token",
    request=SupabaseRefreshTokenSerializer,
    responses={200: SupabaseAuthResponseSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def supabase_refresh_token(request):
    """Refresh access token using refresh token"""
    serializer = SupabaseRefreshTokenSerializer(data=request.data)

    if serializer.is_valid():
        refresh_token = serializer.validated_data["refresh_token"]

        # Refresh session
        result = supabase_auth.refresh_session(refresh_token)

        if result["success"]:
            response_data = {
                "message": result["message"],
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
            }

            if result["session"]:
                response_data.update(
                    {
                        "expires_in": result["session"].expires_in,
                        "expires_at": result["session"].expires_at,
                        "token_type": result["session"].token_type,
                    }
                )

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": result["error"], "message": result["message"]},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Supabase Authentication"],
    summary="OAuth Login",
    description="Get OAuth URL for social login (Google, GitHub, etc.)",
    request=SupabaseOAuthSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {"url": {"type": "string"}, "message": {"type": "string"}},
        }
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def supabase_oauth_login(request):
    """Get OAuth URL for social login"""
    serializer = SupabaseOAuthSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.validated_data
        provider = data["provider"]
        redirect_to = data.get("redirect_to")

        # Get OAuth URL
        result = supabase_auth.sign_in_with_oauth(provider, redirect_to)

        if result["success"]:
            return Response(
                {"url": result["url"], "message": result["message"]},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": result["error"], "message": result["message"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Supabase Authentication"],
    summary="Verify Token",
    description="Verify if access token is valid",
    responses={
        200: {
            "type": "object",
            "properties": {"valid": {"type": "boolean"}, "message": {"type": "string"}},
        }
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])  # We handle auth manually
def supabase_verify_token(request):
    """Verify if access token is valid"""
    access_token = get_auth_token_from_request(request)

    if not access_token:
        return Response(
            {
                "valid": False,
                "message": "Authorization header with Bearer token required",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Verify token
    result = supabase_auth.verify_token(access_token)

    if result["success"]:
        return Response(
            {
                "valid": result["valid"],
                "message": result["message"],
                "user": result.get("user", {}),
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"valid": False, "error": result["error"], "message": result["message"]},
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(
    tags=["Supabase Authentication"],
    summary="Email Confirmation Callback",
    description="Handle email confirmation callback from Supabase with auto token fetch and user verification",
    parameters=[
        OpenApiParameter(
            name="token_hash",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Token hash from confirmation email",
            required=True,
        ),
        OpenApiParameter(
            name="type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Confirmation type (signup, recovery, etc.)",
            required=True,
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "user": {"type": "object"},
                "access_token": {"type": "string"},
                "refresh_token": {"type": "string"},
            }
        },
        400: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "error": {"type": "string"},
                "message": {"type": "string"},
            }
        }
    },
)
@api_view(["GET", "OPTIONS"])  # Add OPTIONS method for CORS preflight
@permission_classes([AllowAny])
@csrf_exempt
def email_confirmation_callback(request):
    """
    Handle email confirmation callback from Supabase
    This endpoint automatically fetches the access token and verifies the user
    """
    token_hash = request.GET.get("token_hash")
    confirmation_type = request.GET.get("type", "signup")
    
    if not token_hash:
        return Response(
            {
                "success": False,
                "error": "missing_token",
                "message": "Token hash is required for confirmation",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    try:
        # Verify the confirmation token with Supabase
        result = supabase_auth.verify_confirmation_token(token_hash, confirmation_type)
        
        if result["success"]:
            # Get user session and tokens
            session_result = supabase_auth.get_user_session(result["user_id"])
            
            if session_result["success"]:
                response_data = {
                    "success": True,
                    "message": "Email confirmed successfully! You can now log in to your account.",
                    "user": result.get("user", {}),
                    "access_token": session_result.get("access_token"),
                    "refresh_token": session_result.get("refresh_token"),
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # User confirmed but no session available
                return Response(
                    {
                        "success": True,
                        "message": "Email confirmation successful! Please log in to your account.",
                        "user": result.get("user", {}),
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {
                    "success": False,
                    "error": result.get("error", "verification_failed"),
                    "message": result.get("message", "Email confirmation failed"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
            
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "verification_error",
                "message": f"An error occurred during confirmation: {str(e)}",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    tags=["Supabase Authentication"],
    summary="CORS Test Endpoint",
    description="Simple endpoint to test CORS configuration",
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "cors_test": {"type": "boolean"},
            }
        }
    },
)
@api_view(["GET", "OPTIONS"])
@permission_classes([AllowAny])
def cors_test(request):
    """Simple endpoint to test CORS configuration"""
    return Response(
        {
            "message": "CORS is working!",
            "cors_test": True,
        },
        status=status.HTTP_200_OK,
    )
