"""
URL Configuration for Stripe Payments
"""

from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    # Product management endpoints
    path("products/", views.list_products, name="list_products"),
    path("products/create/", views.create_product, name="create_product"),
    path("products/<str:product_id>/", views.get_product, name="get_product"),
    path("products/<str:product_id>/update/", views.update_product, name="update_product"),
    path("products/<str:product_id>/delete/", views.delete_product, name="delete_product"),
    
    # Pricing plans endpoints
    path("pricing/plans/", views.get_pricing_plans, name="get_pricing_plans"),
    path("pricing/setup/", views.setup_pricing_plans, name="setup_pricing_plans"),
    
    # Subscription endpoints
    path("subscriptions/create/", views.create_subscription, name="create_subscription"),
    path("subscriptions/trial/", views.start_free_trial, name="start_free_trial"),
    
    # Configuration endpoint
    path("config/", views.get_stripe_config, name="stripe_config"),
]
