"""
Stripe Payment Views
Django REST Framework views for Stripe payment operations
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from .stripe_service import stripe_service
from .serializers import (
    CreateProductSerializer,
    UpdateProductSerializer,
    StripeResponseSerializer,
    ProductListResponseSerializer,
    DeleteProductResponseSerializer,
    CreateSubscriptionSerializer,
    PricingPlansResponseSerializer,
    CreateSubscriptionResponseSerializer,
)


@extend_schema(
    tags=["Stripe Payments"],
    summary="Create Stripe Product",
    description="Create a new product in Stripe for payment processing",
    request=CreateProductSerializer,
    responses={201: StripeResponseSerializer, 400: StripeResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_product(request):
    """Create a new product in Stripe"""
    serializer = CreateProductSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.validated_data
        
        # Create product using Stripe service
        result = stripe_service.create_product(
            name=data["name"],
            description=data.get("description"),
            images=data.get("images"),
            metadata=data.get("metadata"),
            url=data.get("url"),
            active=data.get("active", True),
        )

        if result["success"]:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "success": False,
            "message": "Invalid data provided",
            "error": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@extend_schema(
    tags=["Stripe Payments"],
    summary="Get Stripe Product",
    description="Retrieve a product from Stripe by ID",
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Stripe product ID",
            required=True,
        )
    ],
    responses={200: StripeResponseSerializer, 404: StripeResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_product(request, product_id):
    """Retrieve a product from Stripe"""
    result = stripe_service.get_product(product_id)

    if result["success"]:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=["Stripe Payments"],
    summary="Update Stripe Product",
    description="Update an existing product in Stripe",
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Stripe product ID",
            required=True,
        )
    ],
    request=UpdateProductSerializer,
    responses={200: StripeResponseSerializer, 400: StripeResponseSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_product(request, product_id):
    """Update a product in Stripe"""
    serializer = UpdateProductSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.validated_data
        
        # Update product using Stripe service
        result = stripe_service.update_product(
            product_id=product_id,
            name=data.get("name"),
            description=data.get("description"),
            images=data.get("images"),
            metadata=data.get("metadata"),
            url=data.get("url"),
            active=data.get("active"),
        )

        if result["success"]:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "success": False,
            "message": "Invalid data provided",
            "error": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@extend_schema(
    tags=["Stripe Payments"],
    summary="List Stripe Products",
    description="List products from Stripe with pagination",
    parameters=[
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of products to retrieve (max 100)",
            required=False,
        ),
        OpenApiParameter(
            name="active",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter by active status",
            required=False,
        ),
        OpenApiParameter(
            name="starting_after",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Pagination cursor",
            required=False,
        ),
    ],
    responses={200: ProductListResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_products(request):
    """List products from Stripe"""
    limit = int(request.GET.get("limit", 10))
    active = request.GET.get("active")
    starting_after = request.GET.get("starting_after")

    # Convert active parameter to boolean if provided
    if active is not None:
        active = active.lower() in ["true", "1", "yes"]

    result = stripe_service.list_products(
        limit=limit,
        active=active,
        starting_after=starting_after,
    )

    return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Stripe Payments"],
    summary="Delete Stripe Product",
    description="Delete a product from Stripe",
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Stripe product ID",
            required=True,
        )
    ],
    responses={200: DeleteProductResponseSerializer, 400: DeleteProductResponseSerializer},
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_product(request, product_id):
    """Delete a product from Stripe"""
    result = stripe_service.delete_product(product_id)

    if result["success"]:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Stripe Payments"],
    summary="Get Stripe Configuration",
    description="Get Stripe publishable key and configuration",
    responses={
        200: {
            "type": "object",
            "properties": {
                "publishable_key": {"type": "string"},
                "success": {"type": "boolean"},
                "message": {"type": "string"},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_stripe_config(request):
    """Get Stripe configuration for frontend"""
    return Response(
        {
            "success": True,
            "publishable_key": stripe_service.publishable_key,
            "message": "Stripe configuration retrieved successfully",
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    tags=["Pricing Plans"],
    summary="Setup Pricing Plans",
    description="Setup RecruiterAI pricing plans in Stripe (Starter, Standard, Enterprise)",
    responses={200: PricingPlansResponseSerializer, 400: PricingPlansResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def setup_pricing_plans(request):
    """Setup the three pricing plans in Stripe"""
    result = stripe_service.setup_pricing_plans()
    
    if result["success"]:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Pricing Plans"],
    summary="Get Pricing Plans",
    description="Get all available pricing plans with their details",
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "plans": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "monthly_price": {"type": "number"},
                            "yearly_price": {"type": "number"},
                            "monthly_price_formatted": {"type": "string"},
                            "yearly_price_formatted": {"type": "string"},
                            "yearly_savings": {"type": "string"},
                            "features": {"type": "array", "items": {"type": "string"}},
                            "metadata": {"type": "object"}
                        }
                    }
                }
            }
        }
    },
)
@api_view(["GET"])
@permission_classes([])  # Public endpoint
def get_pricing_plans(request):
    """Get pricing plans information for the frontend"""
    plans_data = [
        {
            "name": "Starter",
            "description": "Perfect for small businesses",
            "monthly_price": 182.31,
            "yearly_price": 2187.77,
            "monthly_price_formatted": "$182.31/month",
            "yearly_price_formatted": "$2,187.77 a year",
            "yearly_savings": "Save 30%",
            "features": [
                "36 job posts per year",
                "Priority email support", 
                "Advanced analytics",
                "7-day free trial (1 job post)"
            ],
            "metadata": {
                "plan_type": "starter",
                "job_posts_per_year": 36,
                "support_level": "email",
                "trial_days": 7
            }
        },
        {
            "name": "Standard", 
            "description": "Perfect for growing teams",
            "monthly_price": 246.66,
            "yearly_price": 2959.92,
            "monthly_price_formatted": "$246.66/month",
            "yearly_price_formatted": "$2,959.92 a year",
            "yearly_savings": "Save 30%",
            "features": [
                "120 job posts per year",
                "Priority email support",
                "Advanced analytics", 
                "Team collaboration tools",
                "7-day free trial (1 job post)"
            ],
            "metadata": {
                "plan_type": "standard",
                "job_posts_per_year": 120,
                "support_level": "email",
                "trial_days": 7
            }
        },
        {
            "name": "Enterprise",
            "description": "Perfect for large organizations", 
            "monthly_price": 343.18,
            "yearly_price": 4118.15,
            "monthly_price_formatted": "$343.18/month",
            "yearly_price_formatted": "$4,118.15 a year",
            "yearly_savings": "Save 30%",
            "features": [
                "360 job posts per year",
                "Priority email support",
                "Advanced analytics",
                "Team collaboration tools", 
                "7-day free trial (1 job post)"
            ],
            "metadata": {
                "plan_type": "enterprise",
                "job_posts_per_year": 360,
                "support_level": "email",
                "trial_days": 7
            }
        }
    ]
    
    return Response(
        {
            "success": True,
            "plans": plans_data,
            "message": "Pricing plans retrieved successfully",
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    tags=["Subscriptions"],
    summary="Create Subscription",
    description="Create a new subscription with 7-day free trial",
    request=CreateSubscriptionSerializer,
    responses={201: CreateSubscriptionResponseSerializer, 400: CreateSubscriptionResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_subscription(request):
    """Create a subscription with free trial"""
    serializer = CreateSubscriptionSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.validated_data
        
        # Create customer first
        customer_result = stripe_service.create_customer(
            email=data["customer_email"],
            name=data.get("customer_name"),
            metadata=data.get("metadata", {})
        )
        
        if not customer_result["success"]:
            return Response(customer_result, status=status.HTTP_400_BAD_REQUEST)
        
        # Create subscription with trial
        subscription_result = stripe_service.create_subscription(
            customer_id=customer_result["customer"]["id"],
            price_id=data["price_id"],
            trial_period_days=data.get("trial_period_days", 7),
            metadata=data.get("metadata", {})
        )
        
        if subscription_result["success"]:
            response_data = {
                **subscription_result,
                "customer": customer_result["customer"]
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(subscription_result, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "success": False,
            "message": "Invalid data provided",
            "error": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@extend_schema(
    tags=["Subscriptions"],
    summary="Start Free Trial",
    description="Start a 7-day free trial for new users",
    request=CreateSubscriptionSerializer,
    responses={201: CreateSubscriptionResponseSerializer, 400: CreateSubscriptionResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_free_trial(request):
    """Start a free trial subscription"""
    serializer = CreateSubscriptionSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.validated_data
        
        # Force 7-day trial
        data["trial_period_days"] = 7
        
        # Add trial metadata
        metadata = data.get("metadata", {})
        metadata.update({
            "trial_type": "free_trial",
            "trial_started": "true",
            "user_id": str(request.user.id) if hasattr(request, 'user') else ""
        })
        
        # Create customer
        customer_result = stripe_service.create_customer(
            email=data["customer_email"],
            name=data.get("customer_name"),
            metadata=metadata
        )
        
        if not customer_result["success"]:
            return Response(customer_result, status=status.HTTP_400_BAD_REQUEST)
        
        # Create trial subscription
        subscription_result = stripe_service.create_subscription(
            customer_id=customer_result["customer"]["id"],
            price_id=data["price_id"],
            trial_period_days=7,
            metadata=metadata
        )
        
        if subscription_result["success"]:
            response_data = {
                **subscription_result,
                "customer": customer_result["customer"],
                "message": "Free trial started successfully! No payment required for 7 days."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(subscription_result, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "success": False,
            "message": "Invalid data provided",
            "error": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )
