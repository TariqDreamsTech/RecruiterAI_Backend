"""
URL Configuration for Supabase Authentication
"""

from django.urls import path
from . import supabase_views

app_name = "supabase_auth"

urlpatterns = [
    # Authentication endpoints
    path("register/", supabase_views.supabase_register, name="register"),
    path("login/", supabase_views.supabase_login, name="login"),
    path("logout/", supabase_views.supabase_logout, name="logout"),
    # User management
    path("user/", supabase_views.supabase_get_user, name="get_user"),
    path("user/update/", supabase_views.supabase_update_user, name="update_user"),
    # Password management
    path(
        "password/reset/", supabase_views.supabase_password_reset, name="password_reset"
    ),
    # Token management
    path("token/refresh/", supabase_views.supabase_refresh_token, name="refresh_token"),
    path("token/verify/", supabase_views.supabase_verify_token, name="verify_token"),
    # OAuth
    path("oauth/", supabase_views.supabase_oauth_login, name="oauth_login"),
    # Email confirmation
]
