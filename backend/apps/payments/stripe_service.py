"""
Stripe Service for handling payment operations
"""

import stripe
from typing import Dict, Any, Optional
from django.conf import settings
from decouple import config


class StripeService:
    """Service class for Stripe payment operations"""

    def __init__(self):
        # Initialize Stripe with secret key
        stripe.api_key = config("STRIPE_SECRET_KEY", default="")
        self.publishable_key = config("STRIPE_PUBLISHABLE_KEY", default="")
        
        if not stripe.api_key:
            raise ValueError("STRIPE_SECRET_KEY must be set in environment variables")

    def create_product(
        self,
        name: str,
        description: Optional[str] = None,
        images: Optional[list] = None,
        metadata: Optional[Dict[str, str]] = None,
        url: Optional[str] = None,
        active: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new product in Stripe

        Args:
            name: Product name
            description: Product description
            images: List of image URLs
            metadata: Additional metadata for the product
            url: Product URL
            active: Whether the product is active

        Returns:
            Dict containing product data or error
        """
        try:
            # Prepare product data
            product_data = {
                "name": name,
                "active": active,
            }

            if description:
                product_data["description"] = description
            
            if images:
                product_data["images"] = images
            
            if metadata:
                product_data["metadata"] = metadata
            
            if url:
                product_data["url"] = url

            # Create product in Stripe
            product = stripe.Product.create(**product_data)

            return {
                "success": True,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "images": product.images,
                    "metadata": product.metadata,
                    "url": product.url,
                    "active": product.active,
                    "created": product.created,
                    "updated": product.updated,
                },
                "message": "Product created successfully",
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create product in Stripe",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "An unexpected error occurred",
            }

    def get_product(self, product_id: str) -> Dict[str, Any]:
        """
        Retrieve a product from Stripe

        Args:
            product_id: Stripe product ID

        Returns:
            Dict containing product data or error
        """
        try:
            product = stripe.Product.retrieve(product_id)

            return {
                "success": True,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "images": product.images,
                    "metadata": product.metadata,
                    "url": product.url,
                    "active": product.active,
                    "created": product.created,
                    "updated": product.updated,
                },
                "message": "Product retrieved successfully",
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve product from Stripe",
            }

    def update_product(
        self,
        product_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        images: Optional[list] = None,
        metadata: Optional[Dict[str, str]] = None,
        url: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Update a product in Stripe

        Args:
            product_id: Stripe product ID
            name: Product name
            description: Product description
            images: List of image URLs
            metadata: Additional metadata for the product
            url: Product URL
            active: Whether the product is active

        Returns:
            Dict containing updated product data or error
        """
        try:
            # Prepare update data
            update_data = {}

            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if images is not None:
                update_data["images"] = images
            if metadata is not None:
                update_data["metadata"] = metadata
            if url is not None:
                update_data["url"] = url
            if active is not None:
                update_data["active"] = active

            # Update product in Stripe
            product = stripe.Product.modify(product_id, **update_data)

            return {
                "success": True,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "images": product.images,
                    "metadata": product.metadata,
                    "url": product.url,
                    "active": product.active,
                    "created": product.created,
                    "updated": product.updated,
                },
                "message": "Product updated successfully",
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update product in Stripe",
            }

    def list_products(
        self,
        limit: int = 10,
        active: Optional[bool] = None,
        starting_after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List products from Stripe

        Args:
            limit: Number of products to retrieve (max 100)
            active: Filter by active status
            starting_after: Pagination cursor

        Returns:
            Dict containing list of products or error
        """
        try:
            # Prepare list parameters
            list_params = {"limit": min(limit, 100)}

            if active is not None:
                list_params["active"] = active
            if starting_after:
                list_params["starting_after"] = starting_after

            # List products from Stripe
            products = stripe.Product.list(**list_params)

            return {
                "success": True,
                "products": [
                    {
                        "id": product.id,
                        "name": product.name,
                        "description": product.description,
                        "images": product.images,
                        "metadata": product.metadata,
                        "url": product.url,
                        "active": product.active,
                        "created": product.created,
                        "updated": product.updated,
                    }
                    for product in products.data
                ],
                "has_more": products.has_more,
                "message": "Products retrieved successfully",
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list products from Stripe",
            }

    def delete_product(self, product_id: str) -> Dict[str, Any]:
        """
        Delete a product from Stripe

        Args:
            product_id: Stripe product ID

        Returns:
            Dict containing deletion result or error
        """
        try:
            product = stripe.Product.delete(product_id)

            return {
                "success": True,
                "deleted": product.deleted,
                "product_id": product.id,
                "message": "Product deleted successfully",
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete product from Stripe",
            }

    def create_price(
        self,
        product_id: str,
        unit_amount: int,
        currency: str = "usd",
        recurring_interval: str = "month",
        nickname: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a price for a product in Stripe

        Args:
            product_id: Stripe product ID
            unit_amount: Price in cents
            currency: Currency code (default: usd)
            recurring_interval: Billing interval (month/year)
            nickname: Price nickname
            metadata: Additional metadata

        Returns:
            Dict containing price data or error
        """
        try:
            price_data = {
                "product": product_id,
                "unit_amount": unit_amount,
                "currency": currency,
                "recurring": {"interval": recurring_interval},
            }

            if nickname:
                price_data["nickname"] = nickname
            if metadata:
                price_data["metadata"] = metadata

            price = stripe.Price.create(**price_data)

            return {
                "success": True,
                "price": {
                    "id": price.id,
                    "product": price.product,
                    "unit_amount": price.unit_amount,
                    "currency": price.currency,
                    "recurring": price.recurring,
                    "nickname": price.nickname,
                    "metadata": price.metadata,
                    "active": price.active,
                },
                "message": "Price created successfully",
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create price in Stripe",
            }

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_period_days: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a subscription in Stripe

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            trial_period_days: Number of trial days
            metadata: Additional metadata

        Returns:
            Dict containing subscription data or error
        """
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
            }

            if trial_period_days:
                subscription_data["trial_period_days"] = trial_period_days
            if metadata:
                subscription_data["metadata"] = metadata

            subscription = stripe.Subscription.create(**subscription_data)

            return {
                "success": True,
                "subscription": {
                    "id": subscription.id,
                    "customer": subscription.customer,
                    "status": subscription.status,
                    "current_period_start": subscription.current_period_start,
                    "current_period_end": subscription.current_period_end,
                    "trial_start": subscription.trial_start,
                    "trial_end": subscription.trial_end,
                    "metadata": subscription.metadata,
                },
                "message": "Subscription created successfully",
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create subscription in Stripe",
            }

    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a customer in Stripe

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata

        Returns:
            Dict containing customer data or error
        """
        try:
            customer_data = {"email": email}

            if name:
                customer_data["name"] = name
            if metadata:
                customer_data["metadata"] = metadata

            customer = stripe.Customer.create(**customer_data)

            return {
                "success": True,
                "customer": {
                    "id": customer.id,
                    "email": customer.email,
                    "name": customer.name,
                    "metadata": customer.metadata,
                },
                "message": "Customer created successfully",
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create customer in Stripe",
            }

    def setup_pricing_plans(self) -> Dict[str, Any]:
        """
        Set up the three pricing plans for RecruiterAI

        Returns:
            Dict containing setup results
        """
        try:
            plans = []
            
            # Define pricing plans
            pricing_plans = [
                {
                    "name": "Starter",
                    "description": "Perfect for small businesses",
                    "features": [
                        "36 job posts per year",
                        "Priority email support", 
                        "Advanced analytics",
                        "7-day free trial (1 job post)"
                    ],
                    "monthly_price": 18231,  # $182.31 in cents
                    "yearly_price": 218777,  # $2,187.77 in cents
                    "metadata": {
                        "plan_type": "starter",
                        "job_posts_per_year": "36",
                        "support_level": "email",
                        "trial_days": "7"
                    }
                },
                {
                    "name": "Standard", 
                    "description": "Perfect for growing teams",
                    "features": [
                        "120 job posts per year",
                        "Priority email support",
                        "Advanced analytics", 
                        "Team collaboration tools",
                        "7-day free trial (1 job post)"
                    ],
                    "monthly_price": 24666,  # $246.66 in cents
                    "yearly_price": 295992,  # $2,959.92 in cents
                    "metadata": {
                        "plan_type": "standard",
                        "job_posts_per_year": "120",
                        "support_level": "email",
                        "trial_days": "7"
                    }
                },
                {
                    "name": "Enterprise",
                    "description": "Perfect for large organizations", 
                    "features": [
                        "360 job posts per year",
                        "Priority email support",
                        "Advanced analytics",
                        "Team collaboration tools", 
                        "7-day free trial (1 job post)"
                    ],
                    "monthly_price": 34318,  # $343.18 in cents
                    "yearly_price": 411815,  # $4,118.15 in cents
                    "metadata": {
                        "plan_type": "enterprise",
                        "job_posts_per_year": "360", 
                        "support_level": "email",
                        "trial_days": "7"
                    }
                }
            ]

            for plan_data in pricing_plans:
                # Create product
                product_result = self.create_product(
                    name=f"RecruiterAI {plan_data['name']} Plan",
                    description=plan_data['description'],
                    metadata=plan_data['metadata']
                )
                
                if not product_result["success"]:
                    continue

                product_id = product_result["product"]["id"]
                
                # Create monthly price
                monthly_price_result = self.create_price(
                    product_id=product_id,
                    unit_amount=plan_data['monthly_price'],
                    recurring_interval="month",
                    nickname=f"{plan_data['name']} Monthly",
                    metadata={**plan_data['metadata'], "billing_interval": "monthly"}
                )
                
                # Create yearly price (30% discount)
                yearly_price_result = self.create_price(
                    product_id=product_id,
                    unit_amount=plan_data['yearly_price'],
                    recurring_interval="year", 
                    nickname=f"{plan_data['name']} Yearly",
                    metadata={**plan_data['metadata'], "billing_interval": "yearly"}
                )

                plans.append({
                    "plan_name": plan_data['name'],
                    "product": product_result["product"],
                    "monthly_price": monthly_price_result.get("price"),
                    "yearly_price": yearly_price_result.get("price"),
                    "features": plan_data['features']
                })

            return {
                "success": True,
                "plans": plans,
                "message": "Pricing plans setup completed",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to setup pricing plans",
            }


# Global instance
stripe_service = StripeService()
