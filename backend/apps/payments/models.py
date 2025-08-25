from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class PricingPlan(models.Model):
    """Model to store pricing plan information"""
    
    PLAN_TYPE_CHOICES = [
        ('starter', 'Starter'),
        ('standard', 'Standard'),
        ('enterprise', 'Enterprise'),
    ]
    
    BILLING_INTERVAL_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Plan name (e.g., Starter)")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, unique=True)
    description = models.TextField(help_text="Plan description")
    
    # Pricing
    monthly_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Monthly price in USD"
    )
    yearly_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Yearly price in USD"
    )
    
    # Stripe IDs
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_monthly_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_yearly_price_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Plan limits and features
    job_posts_per_year = models.PositiveIntegerField(help_text="Number of job posts allowed per year")
    trial_days = models.PositiveIntegerField(default=7, help_text="Trial period in days")
    support_level = models.CharField(max_length=50, default="email", help_text="Level of support provided")
    
    # Features (stored as JSON)
    features = models.JSONField(default=list, help_text="List of plan features")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False, help_text="Mark as popular plan")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Pricing Plan")
        verbose_name_plural = _("Pricing Plans")
        ordering = ['monthly_price']
    
    def __str__(self):
        return f"{self.name} Plan - ${self.monthly_price}/month"
    
    @property
    def yearly_savings_percentage(self):
        """Calculate yearly savings percentage"""
        monthly_yearly_cost = self.monthly_price * 12
        if monthly_yearly_cost > 0:
            savings = ((monthly_yearly_cost - self.yearly_price) / monthly_yearly_cost) * 100
            return round(savings, 0)
        return 0
    
    @property
    def yearly_savings_amount(self):
        """Calculate yearly savings amount in USD"""
        return (self.monthly_price * 12) - self.yearly_price


class Customer(models.Model):
    """Model to store customer information for Stripe integration"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    
    # Contact information
    email = models.EmailField()
    name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Billing address
    billing_address_line1 = models.CharField(max_length=255, blank=True, null=True)
    billing_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    billing_city = models.CharField(max_length=100, blank=True, null=True)
    billing_state = models.CharField(max_length=100, blank=True, null=True)
    billing_postal_code = models.CharField(max_length=20, blank=True, null=True)
    billing_country = models.CharField(max_length=2, blank=True, null=True)  # ISO country code
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Customer: {self.email} ({self.stripe_customer_id})"


class Subscription(models.Model):
    """Model to store subscription information"""
    
    STATUS_CHOICES = [
        ('trialing', 'Trialing'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
        ('incomplete', 'Incomplete'),
        ('incomplete_expired', 'Incomplete Expired'),
        ('paused', 'Paused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='subscriptions')
    pricing_plan = models.ForeignKey(PricingPlan, on_delete=models.PROTECT, related_name='subscriptions')
    
    # Stripe information
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_price_id = models.CharField(max_length=255)
    
    # Subscription details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    billing_interval = models.CharField(max_length=10, choices=PricingPlan.BILLING_INTERVAL_CHOICES)
    
    # Pricing
    unit_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in USD")
    currency = models.CharField(max_length=3, default='usd')
    
    # Periods
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    
    # Trial information
    trial_start = models.DateTimeField(blank=True, null=True)
    trial_end = models.DateTimeField(blank=True, null=True)
    
    # Usage tracking
    job_posts_used = models.PositiveIntegerField(default=0)
    job_posts_remaining = models.PositiveIntegerField(default=0)
    
    # Cancellation
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.email} - {self.pricing_plan.name} ({self.status})"
    
    @property
    def is_active(self):
        """Check if subscription is active or trialing"""
        return self.status in ['active', 'trialing']
    
    @property
    def is_trial(self):
        """Check if subscription is in trial period"""
        return self.status == 'trialing'
    
    @property
    def days_remaining_in_trial(self):
        """Calculate days remaining in trial"""
        if self.trial_end and self.is_trial:
            from django.utils import timezone
            remaining = self.trial_end - timezone.now()
            return max(0, remaining.days)
        return 0
    
    def update_usage(self, posts_used=1):
        """Update job posts usage"""
        self.job_posts_used += posts_used
        self.job_posts_remaining = max(0, self.pricing_plan.job_posts_per_year - self.job_posts_used)
        self.save(update_fields=['job_posts_used', 'job_posts_remaining', 'updated_at'])
    
    def reset_usage(self):
        """Reset usage counters (called on renewal)"""
        self.job_posts_used = 0
        self.job_posts_remaining = self.pricing_plan.job_posts_per_year
        self.save(update_fields=['job_posts_used', 'job_posts_remaining', 'updated_at'])


class PaymentMethod(models.Model):
    """Model to store payment method information"""
    
    TYPE_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('bank_account', 'Bank Account'),
        ('paypal', 'PayPal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payment_methods')
    
    # Stripe information
    stripe_payment_method_id = models.CharField(max_length=255, unique=True)
    
    # Payment method details
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_default = models.BooleanField(default=False)
    
    # Card details (if type is card)
    card_brand = models.CharField(max_length=20, blank=True, null=True)  # visa, mastercard, etc.
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    card_exp_month = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    card_exp_year = models.PositiveIntegerField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.type == 'card' and self.card_last4:
            return f"{self.card_brand.title()} ending in {self.card_last4}"
        return f"{self.get_type_display()} - {self.stripe_payment_method_id}"


class Invoice(models.Model):
    """Model to store invoice information"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('void', 'Void'),
        ('uncollectible', 'Uncollectible'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    
    # Stripe information
    stripe_invoice_id = models.CharField(max_length=255, unique=True)
    
    # Invoice details
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Amounts (in cents to match Stripe)
    amount_due = models.PositiveIntegerField(help_text="Amount due in cents")
    amount_paid = models.PositiveIntegerField(default=0, help_text="Amount paid in cents")
    subtotal = models.PositiveIntegerField(help_text="Subtotal in cents")
    tax = models.PositiveIntegerField(default=0, help_text="Tax amount in cents")
    total = models.PositiveIntegerField(help_text="Total amount in cents")
    
    currency = models.CharField(max_length=3, default='usd')
    
    # Dates
    invoice_date = models.DateTimeField()
    due_date = models.DateTimeField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # URLs
    hosted_invoice_url = models.URLField(blank=True, null=True)
    invoice_pdf_url = models.URLField(blank=True, null=True)
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"Invoice {self.invoice_number or self.stripe_invoice_id} - {self.customer.email}"
    
    @property
    def amount_due_dollars(self):
        """Convert amount due from cents to dollars"""
        return self.amount_due / 100
    
    @property
    def total_dollars(self):
        """Convert total from cents to dollars"""
        return self.total / 100