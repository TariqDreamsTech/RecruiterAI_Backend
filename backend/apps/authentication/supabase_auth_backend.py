"""
Custom authentication backend for Supabase JWT tokens
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
import jwt
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class SupabaseJWTAuthentication(BaseAuthentication):
    """
    Custom authentication backend that validates Supabase JWT tokens
    and creates/retrieves Django User objects
    """
    
    def authenticate(self, request):
        """
        Authenticate request using Supabase JWT token
        Returns (user, auth) tuple or None
        """
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
            
        # Extract token from Bearer header
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        elif auth_header.startswith('eyJ'):  # Direct JWT token
            token = auth_header
        else:
            return None
        
        try:
            # Decode JWT without verification (for development)
            # In production, you should verify the signature
            decoded = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            
            # Get user data from JWT
            user_id = decoded.get('sub')
            email = decoded.get('email')
            user_metadata = decoded.get('user_metadata', {})
            
            if not user_id or not email:
                raise AuthenticationFailed('Invalid token: missing user data')
            
            # Get or create Django user
            user = self.get_or_create_user(user_id, email, user_metadata)
            
            return (user, token)
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def get_or_create_user(self, user_id, email, user_metadata):
        """
        Get or create Django user from Supabase user data
        """
        try:
            # Try to find user by email first
            user = User.objects.get(email=email)
            
            # Update user metadata if changed
            self.update_user_from_metadata(user, user_metadata)
            
            return user
            
        except User.DoesNotExist:
            # Create new user
            username = user_metadata.get('username', email.split('@')[0])
            full_name = user_metadata.get('full_name', '')
            
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User.objects.create(
                username=username,
                email=email,
                first_name=full_name.split(' ')[0] if full_name else '',
                last_name=' '.join(full_name.split(' ')[1:]) if ' ' in full_name else '',
                is_active=True
            )
            
            # Set additional user metadata
            self.update_user_from_metadata(user, user_metadata)
            
            logger.info(f"Created new user from Supabase: {email}")
            return user
    
    def update_user_from_metadata(self, user, user_metadata):
        """
        Update Django user with Supabase metadata
        """
        updated = False
        
        # Update phone number if available
        phone = user_metadata.get('phone_number')
        if phone and hasattr(user, 'phone') and user.phone != phone:
            user.phone = phone
            updated = True
        
        # Update user type if available
        user_type = user_metadata.get('user_type')
        if user_type and hasattr(user, 'user_type') and user.user_type != user_type:
            user.user_type = user_type
            updated = True
        
        if updated:
            user.save()
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'Bearer'


class OptionalSupabaseJWTAuthentication(SupabaseJWTAuthentication):
    """
    Optional authentication that doesn't fail if no token is provided
    Useful for endpoints that support both authenticated and anonymous access
    """
    
    def authenticate(self, request):
        result = super().authenticate(request)
        
        # If no authentication provided, return AnonymousUser
        if result is None:
            return (AnonymousUser(), None)
        
        return result
