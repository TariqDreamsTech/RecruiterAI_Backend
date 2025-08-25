from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid


User = get_user_model()


class JobCategory(models.Model):
    """Job categories for organizing job postings"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Category"
        verbose_name_plural = "Job Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class JobSkill(models.Model):
    """Skills that can be associated with jobs"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=[
        ('technical', 'Technical'),
        ('soft', 'Soft Skills'),
        ('language', 'Language'),
        ('certification', 'Certification'),
        ('other', 'Other')
    ], default='technical')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Job Skill"
        verbose_name_plural = "Job Skills"
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class Job(models.Model):
    """Main job posting model"""
    JOB_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]

    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('principal', 'Principal'),
        ('executive', 'Executive'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    company_name = models.CharField(max_length=200)
    
    # Job Details
    description = models.TextField(help_text="Detailed job description")
    responsibilities = models.TextField(help_text="Key responsibilities and duties")
    requirements = models.TextField(help_text="Required qualifications and skills")
    nice_to_have = models.TextField(blank=True, null=True, help_text="Preferred qualifications")
    
    # Categories and Skills
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(JobSkill, blank=True, related_name='jobs')
    
    # Job Characteristics
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='mid')
    
    # Location
    location = models.CharField(max_length=200, help_text="City, Country or Remote")
    is_remote = models.BooleanField(default=False)
    
    # Compensation
    salary_min = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    salary_max = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    salary_currency = models.CharField(max_length=3, default='USD', help_text="Currency code (USD, EUR, etc.)")
    salary_period = models.CharField(max_length=20, choices=[
        ('hourly', 'Per Hour'),
        ('daily', 'Per Day'),
        ('weekly', 'Per Week'),
        ('monthly', 'Per Month'),
        ('yearly', 'Per Year'),
    ], default='yearly')
    
    # Application Details
    application_deadline = models.DateTimeField(null=True, blank=True)
    application_email = models.EmailField(null=True, blank=True)
    application_url = models.URLField(null=True, blank=True, validators=[URLValidator()])
    
    # Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # LinkedIn Integration
    posted_to_linkedin = models.BooleanField(default=False)
    linkedin_post_id = models.CharField(max_length=200, null=True, blank=True)
    linkedin_post_url = models.URLField(null=True, blank=True)
    linkedin_posted_at = models.DateTimeField(null=True, blank=True)
    
    # Unipile Integration
    unipile_account_id = models.CharField(max_length=200, null=True, blank=True)
    unipile_post_id = models.CharField(max_length=200, null=True, blank=True)
    
    # Tracking
    view_count = models.PositiveIntegerField(default=0)
    application_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['recruiter', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['job_type', 'experience_level']),
        ]

    def __str__(self):
        return f"{self.title} at {self.company_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import random
            base_slug = slugify(f"{self.title}-{self.company_name}")
            self.slug = f"{base_slug}-{random.randint(1000, 9999)}"
        
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Check if job is currently active and accepting applications"""
        if self.status != 'published':
            return False
        
        now = timezone.now()
        if self.application_deadline and now > self.application_deadline:
            return False
        
        if self.expires_at and now > self.expires_at:
            return False
        
        return True

    @property
    def salary_range(self):
        """Get formatted salary range"""
        if not self.salary_min and not self.salary_max:
            return None
        
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,} - {self.salary_max:,} {self.salary_period}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,}+ {self.salary_period}"
        else:
            return f"Up to {self.salary_currency} {self.salary_max:,} {self.salary_period}"

    def increment_view_count(self):
        """Increment the view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def can_apply(self):
        """Check if applications are still being accepted"""
        return self.is_active and (not self.application_deadline or timezone.now() < self.application_deadline)


class JobApplication(models.Model):
    """Job applications from candidates"""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interviewed', 'Interviewed'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
        ('withdrawn', 'Withdrawn'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant_name = models.CharField(max_length=200)
    applicant_email = models.EmailField()
    applicant_phone = models.CharField(max_length=20, blank=True, null=True)
    applicant_linkedin = models.URLField(blank=True, null=True)
    applicant_portfolio = models.URLField(blank=True, null=True)
    
    # Application Content
    cover_letter = models.TextField(blank=True, null=True)
    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)
    resume_text = models.TextField(blank=True, null=True, help_text="Extracted text from resume")
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    applied_via = models.CharField(max_length=50, choices=[
        ('website', 'Company Website'),
        ('linkedin', 'LinkedIn'),
        ('email', 'Email'),
        ('other', 'Other'),
    ], default='website')
    
    # Notes and Feedback
    recruiter_notes = models.TextField(blank=True, null=True)
    interview_feedback = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    status_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ['-applied_at']
        unique_together = ['job', 'applicant_email']
        indexes = [
            models.Index(fields=['job', 'status']),
            models.Index(fields=['status', 'applied_at']),
        ]

    def __str__(self):
        return f"Application from {self.applicant_name} for {self.job.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Increment application count on job
            self.job.application_count += 1
            self.job.save(update_fields=['application_count'])


class UnipileWebhook(models.Model):
    """Track webhook events from Unipile"""
    WEBHOOK_TYPES = [
        ('account_status', 'Account Status Update'),
        ('messaging', 'Messaging Events'),
        ('mailing', 'Mailing Events'),
        ('mail_tracking', 'Mail Tracking Events'),
        ('users_relations', 'Users Relations Events'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook_type = models.CharField(max_length=20, choices=WEBHOOK_TYPES)
    event_id = models.CharField(max_length=200, unique=True)
    account_id = models.CharField(max_length=200, null=True, blank=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(null=True, blank=True)
    
    # Related objects
    related_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    related_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Unipile Webhook"
        verbose_name_plural = "Unipile Webhooks"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook_type', 'processed']),
            models.Index(fields=['account_id', 'event_type']),
        ]

    def __str__(self):
        return f"{self.webhook_type} - {self.event_type} ({self.event_id})"

    def mark_processed(self, error=None):
        """Mark webhook as processed"""
        self.processed = True
        self.processed_at = timezone.now()
        if error:
            self.processing_error = str(error)
        self.save(update_fields=['processed', 'processed_at', 'processing_error'])


class JobTemplate(models.Model):
    """Reusable job posting templates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_templates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True, help_text="Template description")
    
    # Template Content
    title_template = models.CharField(max_length=200)
    description_template = models.TextField()
    responsibilities_template = models.TextField()
    requirements_template = models.TextField()
    nice_to_have_template = models.TextField(blank=True, null=True)
    
    # Default Values
    default_category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    default_job_type = models.CharField(max_length=20, choices=Job.JOB_TYPES, default='full_time')
    default_experience_level = models.CharField(max_length=20, choices=Job.EXPERIENCE_LEVELS, default='mid')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Template"
        verbose_name_plural = "Job Templates"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (by {self.recruiter.username})"

    def create_job_from_template(self, **overrides):
        """Create a new job from this template"""
        job_data = {
            'recruiter': self.recruiter,
            'title': self.title_template,
            'description': self.description_template,
            'responsibilities': self.responsibilities_template,
            'requirements': self.requirements_template,
            'nice_to_have': self.nice_to_have_template,
            'category': self.default_category,
            'job_type': self.default_job_type,
            'experience_level': self.default_experience_level,
            'status': 'draft',
        }
        
        # Apply any overrides
        job_data.update(overrides)
        
        return Job.objects.create(**job_data)
