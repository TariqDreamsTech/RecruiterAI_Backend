from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model for authentication"""

    USER_TYPE_CHOICES = [
        ("recruiter", "Recruiter"),
        ("jobseeker", "Job Seeker"),
        ("admin", "Admin"),
    ]

    email = models.EmailField(_("email address"), unique=True)
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default="jobseeker"
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "user_type"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email
    
    # Payment-related properties and methods
    @property
    def has_active_subscription(self):
        """Check if user has an active subscription"""
        try:
            return (
                hasattr(self, 'customer') and 
                self.customer.subscriptions.filter(
                    status__in=['active', 'trialing']
                ).exists()
            )
        except:
            return False
    
    @property
    def active_subscription(self):
        """Get user's active subscription"""
        try:
            if hasattr(self, 'customer'):
                return self.customer.subscriptions.filter(
                    status__in=['active', 'trialing']
                ).first()
        except:
            pass
        return None
    
    @property
    def subscription_plan(self):
        """Get user's current subscription plan"""
        subscription = self.active_subscription
        return subscription.pricing_plan if subscription else None
    
    @property
    def is_on_trial(self):
        """Check if user is on trial"""
        subscription = self.active_subscription
        return subscription.is_trial if subscription else False
    
    @property
    def trial_days_remaining(self):
        """Get remaining trial days"""
        subscription = self.active_subscription
        return subscription.days_remaining_in_trial if subscription else 0
    
    @property
    def job_posts_remaining(self):
        """Get remaining job posts for current period"""
        subscription = self.active_subscription
        return subscription.job_posts_remaining if subscription else 0
    
    @property
    def job_posts_used(self):
        """Get used job posts for current period"""
        subscription = self.active_subscription
        return subscription.job_posts_used if subscription else 0
    
    def can_post_job(self):
        """Check if user can post a job"""
        if not self.has_active_subscription:
            return False
        
        subscription = self.active_subscription
        if subscription.is_trial:
            # During trial, allow 1 job post
            return subscription.job_posts_used < 1
        
        # For active subscriptions, check remaining posts
        return subscription.job_posts_remaining > 0
    
    def use_job_post(self):
        """Use one job post credit"""
        if self.can_post_job():
            subscription = self.active_subscription
            subscription.update_usage(1)
            return True
        return False
    
    def get_subscription_status(self):
        """Get detailed subscription status"""
        if not self.has_active_subscription:
            return {
                'has_subscription': False,
                'status': 'none',
                'plan': None,
                'trial': False,
                'trial_days_remaining': 0,
                'job_posts_remaining': 0,
                'job_posts_used': 0,
                'can_post': False
            }
        
        subscription = self.active_subscription
        return {
            'has_subscription': True,
            'status': subscription.status,
            'plan': subscription.pricing_plan.name,
            'plan_type': subscription.pricing_plan.plan_type,
            'trial': subscription.is_trial,
            'trial_days_remaining': subscription.days_remaining_in_trial,
            'job_posts_remaining': subscription.job_posts_remaining,
            'job_posts_used': subscription.job_posts_used,
            'job_posts_limit': subscription.pricing_plan.job_posts_per_year,
            'can_post': self.can_post_job(),
            'billing_interval': subscription.billing_interval,
            'current_period_end': subscription.current_period_end
        }


class UserProfile(models.Model):
    """Extended user profile information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)
    experience_years = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Profile"
