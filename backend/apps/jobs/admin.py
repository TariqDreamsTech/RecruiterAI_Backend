from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Job, JobApplication, JobCategory, JobSkill, 
    JobTemplate, UnipileWebhook
)


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'job_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    def job_count(self, obj):
        return obj.jobs.count()
    job_count.short_description = 'Jobs Count'


@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'is_active', 'job_count', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def job_count(self, obj):
        return obj.jobs.count()
    job_count.short_description = 'Jobs Count'


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ['applied_at', 'status_updated_at']
    fields = ['applicant_name', 'applicant_email', 'status', 'applied_via', 'applied_at']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company_name', 'recruiter', 'status', 'job_type', 
        'location', 'view_count', 'application_count', 'posted_to_linkedin', 
        'published_at', 'created_at'
    ]
    list_filter = [
        'status', 'job_type', 'experience_level', 'is_remote', 
        'posted_to_linkedin', 'category', 'created_at', 'published_at'
    ]
    search_fields = ['title', 'company_name', 'description', 'location']
    readonly_fields = [
        'id', 'slug', 'view_count', 'application_count', 'published_at',
        'linkedin_posted_at', 'created_at', 'updated_at'
    ]
    filter_horizontal = ['skills']
    inlines = [JobApplicationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'recruiter', 'title', 'slug', 'company_name', 'status')
        }),
        ('Job Details', {
            'fields': ('description', 'responsibilities', 'requirements', 'nice_to_have')
        }),
        ('Categories & Skills', {
            'fields': ('category', 'skills')
        }),
        ('Job Characteristics', {
            'fields': ('job_type', 'experience_level', 'location', 'is_remote')
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'salary_period')
        }),
        ('Application Details', {
            'fields': ('application_deadline', 'application_email', 'application_url', 'expires_at')
        }),
        ('LinkedIn Integration', {
            'fields': (
                'posted_to_linkedin', 'linkedin_post_id', 'linkedin_post_url', 
                'linkedin_posted_at', 'unipile_account_id', 'unipile_post_id'
            )
        }),
        ('Statistics', {
            'fields': ('view_count', 'application_count')
        }),
        ('Timestamps', {
            'fields': ('published_at', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recruiter', 'category')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'applicant_name', 'applicant_email', 'job_title', 'company_name',
        'status', 'applied_via', 'applied_at'
    ]
    list_filter = ['status', 'applied_via', 'applied_at', 'job__category']
    search_fields = [
        'applicant_name', 'applicant_email', 'job__title', 
        'job__company_name', 'cover_letter'
    ]
    readonly_fields = ['id', 'applied_at', 'status_updated_at']
    
    fieldsets = (
        ('Application Info', {
            'fields': ('id', 'job', 'status', 'applied_via', 'applied_at', 'status_updated_at')
        }),
        ('Applicant Details', {
            'fields': (
                'applicant_name', 'applicant_email', 'applicant_phone',
                'applicant_linkedin', 'applicant_portfolio'
            )
        }),
        ('Application Content', {
            'fields': ('cover_letter', 'resume_file', 'resume_text')
        }),
        ('Recruiter Notes', {
            'fields': ('recruiter_notes', 'interview_feedback', 'rejection_reason')
        }),
    )
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job Title'
    
    def company_name(self, obj):
        return obj.job.company_name
    company_name.short_description = 'Company'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job')


@admin.register(JobTemplate)
class JobTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'recruiter', 'default_job_type', 'default_experience_level',
        'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'default_job_type', 'default_experience_level', 'created_at']
    search_fields = ['name', 'description', 'title_template']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Template Info', {
            'fields': ('id', 'recruiter', 'name', 'description', 'is_active')
        }),
        ('Template Content', {
            'fields': (
                'title_template', 'description_template', 'responsibilities_template',
                'requirements_template', 'nice_to_have_template'
            )
        }),
        ('Default Values', {
            'fields': ('default_category', 'default_job_type', 'default_experience_level')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recruiter', 'default_category')


@admin.register(UnipileWebhook)
class UnipileWebhookAdmin(admin.ModelAdmin):
    list_display = [
        'event_id', 'webhook_type', 'event_type', 'account_id',
        'processed', 'created_at', 'processed_at'
    ]
    list_filter = ['webhook_type', 'event_type', 'processed', 'created_at']
    search_fields = ['event_id', 'account_id', 'event_type']
    readonly_fields = [
        'id', 'event_id', 'payload', 'created_at', 'processed_at',
        'processing_error'
    ]
    
    fieldsets = (
        ('Webhook Info', {
            'fields': (
                'id', 'webhook_type', 'event_id', 'event_type', 
                'account_id', 'processed', 'processed_at'
            )
        }),
        ('Payload', {
            'fields': ('payload_display',),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('processing_error',)
        }),
        ('Related Objects', {
            'fields': ('related_job', 'related_user')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def payload_display(self, obj):
        import json
        return format_html(
            '<pre>{}</pre>',
            json.dumps(obj.payload, indent=2) if obj.payload else 'No payload'
        )
    payload_display.short_description = 'Payload'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('related_job', 'related_user')


# Custom admin actions
@admin.action(description='Publish selected jobs')
def publish_jobs(modeladmin, request, queryset):
    updated = queryset.filter(status='draft').update(
        status='published',
        published_at=timezone.now()
    )
    modeladmin.message_user(
        request, 
        f'{updated} jobs were successfully published.'
    )

@admin.action(description='Mark applications as reviewed')
def mark_reviewed(modeladmin, request, queryset):
    updated = queryset.filter(status='submitted').update(
        status='under_review'
    )
    modeladmin.message_user(
        request,
        f'{updated} applications were marked as reviewed.'
    )

# Add actions to admin
JobAdmin.actions = [publish_jobs]
JobApplicationAdmin.actions = [mark_reviewed]
