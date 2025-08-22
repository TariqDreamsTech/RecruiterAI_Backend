"""
Serializers for Supabase Authentication
"""

from rest_framework import serializers


class SupabaseRegistrationSerializer(serializers.Serializer):
    """Serializer for Supabase user registration"""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=6)
    username = serializers.CharField(required=False, max_length=150)
    user_type = serializers.ChoiceField(
        choices=[("recruiter", "Recruiter"), ("jobseeker", "Job Seeker")],
        required=False,
        default="jobseeker",
    )
    phone_number = serializers.CharField(required=False, max_length=15)
    full_name = serializers.CharField(required=False, max_length=255)


class SupabaseLoginSerializer(serializers.Serializer):
    """Serializer for Supabase user login"""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class SupabasePasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request"""

    email = serializers.EmailField(required=True)


class SupabaseUserUpdateSerializer(serializers.Serializer):
    """Serializer for updating user data via Supabase"""

    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False, min_length=6)
    phone = serializers.CharField(required=False, max_length=15)
    user_metadata = serializers.DictField(required=False)

    # User metadata fields
    username = serializers.CharField(required=False, max_length=150)
    user_type = serializers.ChoiceField(
        choices=[("recruiter", "Recruiter"), ("jobseeker", "Job Seeker")],
        required=False,
    )
    full_name = serializers.CharField(required=False, max_length=255)
    bio = serializers.CharField(required=False)
    location = serializers.CharField(required=False, max_length=100)
    website = serializers.URLField(required=False)
    linkedin_url = serializers.URLField(required=False)
    github_url = serializers.URLField(required=False)
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    experience_years = serializers.IntegerField(required=False, min_value=0)


class SupabaseOAuthSerializer(serializers.Serializer):
    """Serializer for OAuth authentication"""

    provider = serializers.ChoiceField(
        choices=[
            ("google", "Google"),
            ("github", "GitHub"),
            ("linkedin", "LinkedIn"),
            ("facebook", "Facebook"),
            ("twitter", "Twitter"),
        ],
        required=True,
    )
    redirect_to = serializers.URLField(required=False)


class SupabaseRefreshTokenSerializer(serializers.Serializer):
    """Serializer for refresh token"""

    refresh_token = serializers.CharField(required=True)


class SupabaseUserResponseSerializer(serializers.Serializer):
    """Serializer for Supabase user response"""

    id = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    email_confirmed_at = serializers.DateTimeField(read_only=True)
    phone = serializers.CharField(read_only=True)
    phone_confirmed_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    last_sign_in_at = serializers.DateTimeField(read_only=True)
    user_metadata = serializers.DictField(read_only=True)
    app_metadata = serializers.DictField(read_only=True)


class SupabaseAuthResponseSerializer(serializers.Serializer):
    """Serializer for Supabase authentication response"""

    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    expires_in = serializers.IntegerField(read_only=True)
    expires_at = serializers.IntegerField(read_only=True)
    token_type = serializers.CharField(read_only=True)
    user = SupabaseUserResponseSerializer(read_only=True)
    message = serializers.CharField(read_only=True)


class SupabaseLogoutSerializer(serializers.Serializer):
    """Serializer for logout request"""

    # Logout doesn't require any input fields for Supabase
    # The access token is handled via Authorization header
    pass
