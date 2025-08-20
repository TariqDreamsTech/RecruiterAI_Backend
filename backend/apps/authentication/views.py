from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, PasswordChangeSerializer
)
from .models import User, UserProfile


@extend_schema(
    tags=['Authentication'],
    summary='User Registration',
    description='Register a new user account',
    examples=[
        OpenApiExample(
            'Recruiter Registration',
            value={
                'email': 'recruiter@example.com',
                'username': 'recruiter123',
                'password': 'strongpassword123',
                'password_confirm': 'strongpassword123',
                'user_type': 'recruiter',
                'phone_number': '+1234567890'
            }
        ),
        OpenApiExample(
            'Job Seeker Registration',
            value={
                'email': 'jobseeker@example.com',
                'username': 'jobseeker123',
                'password': 'strongpassword123',
                'password_confirm': 'strongpassword123',
                'user_type': 'jobseeker',
                'phone_number': '+1234567890'
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='User Login',
    description='Authenticate user and return access token',
    examples=[
        OpenApiExample(
            'Login Example',
            value={
                'email': 'user@example.com',
                'password': 'userpassword123'
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='User Logout',
    description='Logout user and invalidate token'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """User logout endpoint"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    summary='Get User Profile',
    description='Retrieve current user profile information'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get current user profile"""
    user = request.user
    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    summary='Update User Profile',
    description='Update current user profile information'
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Update current user profile"""
    user = request.user
    user_serializer = UserSerializer(user, data=request.data, partial=True)
    
    if user_serializer.is_valid():
        user_serializer.save()
        
        # Update profile if profile data is provided
        if 'profile' in request.data:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile_serializer = UserProfileSerializer(profile, data=request.data['profile'], partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
        
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    
    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Change Password',
    description='Change user password'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Verify User',
    description='Verify user account (admin only)'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_user(request, user_id):
    """Verify user account (admin only)"""
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        user.is_verified = True
        user.save()
        return Response({'message': 'User verified successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
