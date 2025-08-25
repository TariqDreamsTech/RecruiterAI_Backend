"""
Serializers for Stripe Payment APIs
"""

from rest_framework import serializers


class CreateProductSerializer(serializers.Serializer):
    """Serializer for creating a Stripe product"""
    
    name = serializers.CharField(
        max_length=255,
        help_text="Product name"
    )
    description = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        help_text="Product description"
    )
    images = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        allow_empty=True,
        max_length=8,
        help_text="List of product image URLs (max 8)"
    )
    metadata = serializers.DictField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
        help_text="Additional metadata for the product"
    )
    url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Product URL"
    )
    active = serializers.BooleanField(
        default=True,
        help_text="Whether the product is active"
    )


class UpdateProductSerializer(serializers.Serializer):
    """Serializer for updating a Stripe product"""
    
    name = serializers.CharField(
        max_length=255,
        required=False,
        help_text="Product name"
    )
    description = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        help_text="Product description"
    )
    images = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        allow_empty=True,
        max_length=8,
        help_text="List of product image URLs (max 8)"
    )
    metadata = serializers.DictField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
        help_text="Additional metadata for the product"
    )
    url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Product URL"
    )
    active = serializers.BooleanField(
        required=False,
        help_text="Whether the product is active"
    )


class ProductResponseSerializer(serializers.Serializer):
    """Serializer for Stripe product response"""
    
    id = serializers.CharField(help_text="Stripe product ID")
    name = serializers.CharField(help_text="Product name")
    description = serializers.CharField(help_text="Product description", allow_null=True)
    images = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of product image URLs"
    )
    metadata = serializers.DictField(help_text="Product metadata")
    url = serializers.CharField(help_text="Product URL", allow_null=True)
    active = serializers.BooleanField(help_text="Whether the product is active")
    created = serializers.IntegerField(help_text="Unix timestamp when created")
    updated = serializers.IntegerField(help_text="Unix timestamp when updated")


class StripeResponseSerializer(serializers.Serializer):
    """Generic Stripe API response serializer"""
    
    success = serializers.BooleanField(help_text="Whether the operation was successful")
    message = serializers.CharField(help_text="Response message")
    product = ProductResponseSerializer(required=False, help_text="Product data")
    error = serializers.CharField(required=False, help_text="Error message if failed")


class ProductListResponseSerializer(serializers.Serializer):
    """Serializer for listing Stripe products response"""
    
    success = serializers.BooleanField(help_text="Whether the operation was successful")
    message = serializers.CharField(help_text="Response message")
    products = ProductResponseSerializer(many=True, help_text="List of products")
    has_more = serializers.BooleanField(help_text="Whether there are more products")
    error = serializers.CharField(required=False, help_text="Error message if failed")


class DeleteProductResponseSerializer(serializers.Serializer):
    """Serializer for delete product response"""
    
    success = serializers.BooleanField(help_text="Whether the operation was successful")
    message = serializers.CharField(help_text="Response message")
    deleted = serializers.BooleanField(required=False, help_text="Whether the product was deleted")
    product_id = serializers.CharField(required=False, help_text="ID of the deleted product")
    error = serializers.CharField(required=False, help_text="Error message if failed")


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer for creating a subscription"""
    
    customer_email = serializers.EmailField(help_text="Customer email address")
    customer_name = serializers.CharField(
        max_length=255,
        required=False,
        help_text="Customer name"
    )
    price_id = serializers.CharField(help_text="Stripe price ID")
    trial_period_days = serializers.IntegerField(
        default=7,
        min_value=0,
        max_value=365,
        help_text="Number of trial days (default: 7)"
    )
    metadata = serializers.DictField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
        help_text="Additional metadata"
    )


class PricingPlanSerializer(serializers.Serializer):
    """Serializer for pricing plan data"""
    
    plan_name = serializers.CharField(help_text="Plan name")
    product = ProductResponseSerializer(help_text="Product details")
    monthly_price = serializers.DictField(help_text="Monthly price details")
    yearly_price = serializers.DictField(help_text="Yearly price details")
    features = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of plan features"
    )


class PricingPlansResponseSerializer(serializers.Serializer):
    """Serializer for pricing plans response"""
    
    success = serializers.BooleanField(help_text="Whether the operation was successful")
    message = serializers.CharField(help_text="Response message")
    plans = PricingPlanSerializer(many=True, help_text="List of pricing plans")
    error = serializers.CharField(required=False, help_text="Error message if failed")


class SubscriptionResponseSerializer(serializers.Serializer):
    """Serializer for subscription response"""
    
    id = serializers.CharField(help_text="Subscription ID")
    customer = serializers.CharField(help_text="Customer ID")
    status = serializers.CharField(help_text="Subscription status")
    current_period_start = serializers.IntegerField(help_text="Current period start timestamp")
    current_period_end = serializers.IntegerField(help_text="Current period end timestamp")
    trial_start = serializers.IntegerField(help_text="Trial start timestamp", allow_null=True)
    trial_end = serializers.IntegerField(help_text="Trial end timestamp", allow_null=True)
    metadata = serializers.DictField(help_text="Subscription metadata")


class CreateSubscriptionResponseSerializer(serializers.Serializer):
    """Serializer for create subscription response"""
    
    success = serializers.BooleanField(help_text="Whether the operation was successful")
    message = serializers.CharField(help_text="Response message")
    subscription = SubscriptionResponseSerializer(required=False, help_text="Subscription details")
    customer = serializers.DictField(required=False, help_text="Customer details")
    error = serializers.CharField(required=False, help_text="Error message if failed")
