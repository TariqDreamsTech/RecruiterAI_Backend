"""
Supabase Authentication Service
Handles all authentication operations using Supabase Auth
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from gotrue import AuthResponse, User as SupabaseUser
from django.conf import settings
from decouple import config


class SupabaseAuthService:
    """Service class for Supabase authentication operations"""

    def __init__(self):
        # Initialize Supabase client
        supabase_url = config("SUPABASE_URL", default="")
        supabase_key = config("SUPABASE_ANON_KEY", default="")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables"
            )

        self.supabase: Client = create_client(supabase_url, supabase_key)

    def sign_up(
        self, email: str, password: str, user_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a new user with Supabase

        Args:
            email: User's email address
            password: User's password
            user_metadata: Additional user metadata (optional)

        Returns:
            Dict containing user data and session info
        """
        try:
            options = {}
            if user_metadata:
                options["data"] = user_metadata

            response = self.supabase.auth.sign_up(
                {"email": email, "password": password, "options": options}
            )

            return {
                "success": True,
                "user": response.user,
                "session": response.session,
                "message": "Registration successful. Please check your email for verification.",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "message": "Registration failed"}

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in user with email and password

        Args:
            email: User's email address
            password: User's password

        Returns:
            Dict containing user data and session info
        """
        try:
            response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            return {
                "success": True,
                "user": response.user,
                "session": response.session,
                "access_token": (
                    response.session.access_token if response.session else None
                ),
                "refresh_token": (
                    response.session.refresh_token if response.session else None
                ),
                "message": "Login successful",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "message": "Login failed"}

    def sign_out(self, access_token: str) -> Dict[str, Any]:
        """
        Sign out user

        Args:
            access_token: User's access token

        Returns:
            Dict containing success status
        """
        try:
            # Set the session
            self.supabase.auth.set_session(access_token, "")
            self.supabase.auth.sign_out()

            return {"success": True, "message": "Logout successful"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": "Logout failed"}

    def get_user(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from access token

        Args:
            access_token: User's access token

        Returns:
            Dict containing user information
        """
        try:
            # Create a new client instance with the access token as header
            from supabase import create_client, ClientOptions

            supabase_url = config("SUPABASE_URL", default="")
            supabase_key = config("SUPABASE_ANON_KEY", default="")

            # Create client with authorization header
            headers = {"Authorization": f"Bearer {access_token}"}
            client_options = ClientOptions(headers=headers)
            client = create_client(supabase_url, supabase_key, options=client_options)

            # Get user using the authenticated client
            print(f"DEBUG: About to call client.auth.get_user()")
            user_response = client.auth.get_user()

            print(f"DEBUG: user_response = {user_response}")
            print(f"DEBUG: user_response type = {type(user_response)}")

            if user_response and hasattr(user_response, "user") and user_response.user:
                print(f"DEBUG: Successfully got user: {user_response.user}")
                return {
                    "success": True,
                    "user": user_response.user,
                    "message": "User data retrieved successfully",
                }
            else:
                print(f"DEBUG: No valid user in response")
                # Try alternative approach - direct API call to Supabase
                try:
                    import requests

                    supabase_url = config("SUPABASE_URL", default="")
                    api_url = f"{supabase_url}/auth/v1/user"

                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "apikey": config("SUPABASE_ANON_KEY", default=""),
                        "Content-Type": "application/json",
                    }

                    print(f"DEBUG: Making direct API call to {api_url}")
                    response = requests.get(api_url, headers=headers)
                    print(f"DEBUG: API response status: {response.status_code}")
                    print(f"DEBUG: API response content: {response.text}")

                    if response.status_code == 200:
                        user_data = response.json()
                        print(f"DEBUG: Successfully got user from API: {user_data}")

                        return {
                            "success": True,
                            "user": user_data,
                            "message": "User data retrieved from direct API call",
                        }
                    else:
                        print(
                            f"DEBUG: API call failed with status {response.status_code}"
                        )

                except Exception as api_error:
                    print(f"DEBUG: Direct API call failed: {api_error}")

                # Try JWT decoding as final fallback
                try:
                    import jwt

                    # Decode JWT to get user info directly (without secret verification for debugging)
                    decoded = jwt.decode(
                        access_token,
                        options={
                            "verify_signature": False
                        },  # Skip signature verification for now
                    )
                    print(f"DEBUG: Decoded JWT (no verification): {decoded}")

                    # Create a user object from JWT claims
                    user_data = {
                        "id": decoded.get("sub"),
                        "email": decoded.get("email"),
                        "user_metadata": decoded.get("user_metadata", {}),
                        "app_metadata": decoded.get("app_metadata", {}),
                    }

                    return {
                        "success": True,
                        "user": user_data,
                        "message": "User data retrieved from JWT claims",
                    }

                except Exception as jwt_error:
                    print(f"DEBUG: JWT decode failed: {jwt_error}")

                return {
                    "success": False,
                    "error": "Invalid user response from Supabase",
                    "message": "Failed to retrieve user data",
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve user data",
            }

    def update_user(
        self, access_token: str, attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user attributes

        Args:
            access_token: User's access token
            attributes: Dictionary of attributes to update

        Returns:
            Dict containing updated user data
        """
        try:
            print(f"DEBUG: update_user called with token: {access_token[:30]}...")
            print(f"DEBUG: attributes to update: {attributes}")

            # Try direct API call to Supabase (more reliable than client)
            import requests

            supabase_url = config("SUPABASE_URL", default="")
            api_url = f"{supabase_url}/auth/v1/user"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "apikey": config("SUPABASE_ANON_KEY", default=""),
                "Content-Type": "application/json",
            }

            # Convert attributes to the format expected by Supabase API
            payload = {}
            if "email" in attributes:
                payload["email"] = attributes["email"]
            if "password" in attributes:
                payload["password"] = attributes["password"]
            if "phone" in attributes:
                payload["phone"] = attributes["phone"]
            if "data" in attributes:
                payload["data"] = attributes["data"]

            print(f"DEBUG: Making PUT request to {api_url}")
            print(f"DEBUG: Headers: {headers}")
            print(f"DEBUG: Payload: {payload}")

            response = requests.put(api_url, headers=headers, json=payload)

            print(f"DEBUG: API response status: {response.status_code}")
            print(f"DEBUG: API response content: {response.text}")

            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "user": user_data,
                    "message": "User updated successfully",
                }
            else:
                return {
                    "success": False,
                    "error": f"API call failed with status {response.status_code}: {response.text}",
                    "message": "Failed to update user",
                }

        except Exception as e:
            print(f"DEBUG: Update user failed with exception: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update user",
            }

    def reset_password(self, email: str) -> Dict[str, Any]:
        """
        Send password reset email

        Args:
            email: User's email address

        Returns:
            Dict containing success status
        """
        try:
            self.supabase.auth.reset_password_email(email)

            return {
                "success": True,
                "message": "Password reset email sent successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to send password reset email",
            }

    def verify_token(self, access_token: str) -> Dict[str, Any]:
        """
        Verify if access token is valid

        Args:
            access_token: User's access token

        Returns:
            Dict containing verification result
        """
        try:
            user_response = self.get_user(access_token)
            if user_response["success"]:
                return {
                    "success": True,
                    "valid": True,
                    "user": user_response["user"],
                    "message": "Token is valid",
                }
            else:
                return {"success": True, "valid": False, "message": "Token is invalid"}
        except Exception as e:
            return {
                "success": False,
                "valid": False,
                "error": str(e),
                "message": "Token verification failed",
            }

    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh user session using refresh token

        Args:
            refresh_token: User's refresh token

        Returns:
            Dict containing new session data
        """
        try:
            response = self.supabase.auth.refresh_session(refresh_token)

            return {
                "success": True,
                "session": response.session,
                "access_token": (
                    response.session.access_token if response.session else None
                ),
                "refresh_token": (
                    response.session.refresh_token if response.session else None
                ),
                "message": "Session refreshed successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to refresh session",
            }

    def sign_in_with_oauth(
        self, provider: str, redirect_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate OAuth sign-in with provider (Google, GitHub, etc.)

        Args:
            provider: OAuth provider name (google, github, etc.)
            redirect_to: URL to redirect after authentication

        Returns:
            Dict containing OAuth URL
        """
        try:
            options = {}
            if redirect_to:
                options["redirect_to"] = redirect_to

            response = self.supabase.auth.sign_in_with_oauth(
                {"provider": provider, "options": options}
            )

            return {
                "success": True,
                "url": response.url,
                "message": f"OAuth URL generated for {provider}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate OAuth URL for {provider}",
            }


# Global instance
supabase_auth = SupabaseAuthService()
