from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import PricingPlan, Customer, Subscription, PaymentMethod, Invoice


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    """Admin interface for Pricing Plans"""
    
    list_display = [
        'name', 'plan_type', 'monthly_price', 'yearly_price', 
        'yearly_savings_display', 'job_posts_per_year', 'is_active', 'is_popular'
    ]
    list_filter = ['plan_type', 'is_active', 'is_popular']
    search_fields = ['name', 'description']
    ordering = ['monthly_price']
    readonly_fields = ['id', 'created_at', 'updated_at', 'yearly_savings_display', 'yearly_savings_amount']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'description')
        }),
        ('Pricing', {
            'fields': ('monthly_price', 'yearly_price', 'yearly_savings_display', 'yearly_savings_amount')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_product_id', 'stripe_monthly_price_id', 'stripe_yearly_price_id'),
            'classes': ('collapse',)
        }),
        ('Plan Features', {
            'fields': ('job_posts_per_year', 'trial_days', 'support_level', 'features')
        }),
        ('Status', {
            'fields': ('is_active', 'is_popular')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def yearly_savings_display(self, obj):
        """Display yearly savings percentage"""
        return f"{obj.yearly_savings_percentage}% (${obj.yearly_savings_amount})"
    yearly_savings_display.short_description = "Yearly Savings"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin interface for Customers"""
    
    list_display = [
        'email', 'name', 'user_link', 'stripe_customer_id', 
        'active_subscriptions_count', 'created_at'
    ]
    list_filter = ['created_at', 'billing_country']
    search_fields = ['email', 'name', 'stripe_customer_id', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'user_link', 'active_subscriptions_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_link', 'email', 'name', 'phone')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_customer_id',)
        }),
        ('Billing Address', {
            'fields': (
                'billing_address_line1', 'billing_address_line2', 
                'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'active_subscriptions_count'),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        """Link to related user"""
        if obj.user:
            url = reverse('admin:authentication_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_link.short_description = "User"
    
    def active_subscriptions_count(self, obj):
        """Count of active subscriptions"""
        return obj.subscriptions.filter(status__in=['active', 'trialing']).count()
    active_subscriptions_count.short_description = "Active Subscriptions"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscriptions"""
    
    list_display = [
        'customer_email', 'pricing_plan', 'status', 'billing_interval',
        'trial_status', 'usage_display', 'current_period_end', 'created_at'
    ]
    list_filter = [
        'status', 'billing_interval', 'pricing_plan__plan_type', 
        'created_at', 'cancel_at_period_end'
    ]
    search_fields = [
        'customer__email', 'stripe_subscription_id', 
        'pricing_plan__name', 'customer__user__email'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'trial_status', 
        'usage_display', 'days_remaining_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'pricing_plan', 'status', 'billing_interval')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id', 'stripe_price_id')
        }),
        ('Pricing', {
            'fields': ('unit_amount', 'currency')
        }),
        ('Periods', {
            'fields': ('current_period_start', 'current_period_end')
        }),
        ('Trial Information', {
            'fields': ('trial_start', 'trial_end', 'trial_status', 'days_remaining_display')
        }),
        ('Usage Tracking', {
            'fields': ('job_posts_used', 'job_posts_remaining', 'usage_display')
        }),
        ('Cancellation', {
            'fields': ('cancel_at_period_end', 'canceled_at')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def customer_email(self, obj):
        """Display customer email"""
        return obj.customer.email
    customer_email.short_description = "Customer"
    
    def trial_status(self, obj):
        """Display trial status"""
        if obj.is_trial:
            days_left = obj.days_remaining_in_trial
            color = 'green' if days_left > 3 else 'orange' if days_left > 0 else 'red'
            return format_html(
                '<span style="color: {};">Trial ({} days left)</span>', 
                color, days_left
            )
        return 'Not on trial'
    trial_status.short_description = "Trial Status"
    
    def usage_display(self, obj):
        """Display usage information"""
        percentage = (obj.job_posts_used / obj.pricing_plan.job_posts_per_year) * 100 if obj.pricing_plan.job_posts_per_year > 0 else 0
        color = 'green' if percentage < 50 else 'orange' if percentage < 80 else 'red'
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color, obj.job_posts_used, obj.pricing_plan.job_posts_per_year, round(percentage, 1)
        )
    usage_display.short_description = "Usage"
    
    def days_remaining_display(self, obj):
        """Display days remaining in current period"""
        if obj.current_period_end:
            remaining = (obj.current_period_end - timezone.now()).days
            return f"{remaining} days" if remaining > 0 else "Expired"
        return "-"
    days_remaining_display.short_description = "Days Remaining"


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin interface for Payment Methods"""
    
    list_display = [
        'customer_email', 'type', 'card_display', 'is_default', 
        'is_active', 'created_at'
    ]
    list_filter = ['type', 'is_default', 'is_active', 'card_brand']
    search_fields = ['customer__email', 'stripe_payment_method_id', 'card_last4']
    readonly_fields = ['id', 'created_at', 'updated_at', 'card_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'type', 'is_default', 'is_active')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_method_id',)
        }),
        ('Card Details', {
            'fields': ('card_brand', 'card_last4', 'card_exp_month', 'card_exp_year', 'card_display')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def customer_email(self, obj):
        """Display customer email"""
        return obj.customer.email
    customer_email.short_description = "Customer"
    
    def card_display(self, obj):
        """Display card information"""
        if obj.type == 'card' and obj.card_last4:
            exp = f"{obj.card_exp_month:02d}/{obj.card_exp_year}" if obj.card_exp_month and obj.card_exp_year else "N/A"
            return f"{obj.card_brand.title()} •••• {obj.card_last4} ({exp})"
        return f"{obj.get_type_display()}"
    card_display.short_description = "Card Details"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin interface for Invoices"""
    
    list_display = [
        'invoice_number_display', 'customer_email', 'status', 
        'total_display', 'invoice_date', 'due_date', 'paid_at'
    ]
    list_filter = ['status', 'invoice_date', 'currency']
    search_fields = [
        'stripe_invoice_id', 'invoice_number', 'customer__email', 
        'subscription__pricing_plan__name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'total_display', 
        'amount_due_display', 'invoice_number_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'subscription', 'status', 'invoice_number_display')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_invoice_id',)
        }),
        ('Amounts', {
            'fields': (
                'amount_due_display', 'amount_paid', 'subtotal', 
                'tax', 'total_display', 'currency'
            )
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date', 'paid_at')
        }),
        ('URLs', {
            'fields': ('hosted_invoice_url', 'invoice_pdf_url'),
            'classes': ('collapse',)
        }),
        ('Details', {
            'fields': ('description', 'metadata'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def customer_email(self, obj):
        """Display customer email"""
        return obj.customer.email
    customer_email.short_description = "Customer"
    
    def invoice_number_display(self, obj):
        """Display invoice number or Stripe ID"""
        return obj.invoice_number or obj.stripe_invoice_id
    invoice_number_display.short_description = "Invoice Number"
    
    def total_display(self, obj):
        """Display total amount in dollars"""
        return f"${obj.total_dollars:.2f}"
    total_display.short_description = "Total"
    
    def amount_due_display(self, obj):
        """Display amount due in dollars"""
        return f"${obj.amount_due_dollars:.2f}"
    amount_due_display.short_description = "Amount Due"
# Note: Stripe products are managed directly in Stripe, 
# so no Django models are needed for basic product management.
