from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Job, JobApplication, JobCategory, JobSkill, 
    JobTemplate, UnipileWebhook
)


User = get_user_model()


class JobSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSkill
        fields = ['id', 'name', 'slug', 'category', 'is_active', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class JobSkillCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating job skills"""
    name = serializers.CharField(
        max_length=100,
        help_text="Skill name (e.g., 'Python', 'React', 'Project Management')"
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=JobCategory.objects.filter(is_active=True),
        required=False,
        help_text="Category ID (optional)"
    )
    
    class Meta:
        model = JobSkill
        fields = ['name', 'category']
        
    def create(self, validated_data):
        validated_data['is_active'] = True
        return super().create(validated_data)


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class JobCategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating job categories"""
    name = serializers.CharField(
        max_length=100,
        help_text="Category name (e.g., 'Software Development')"
    )
    description = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Brief description of the category"
    )
    
    class Meta:
        model = JobCategory
        fields = ['name', 'description']
        
    def create(self, validated_data):
        validated_data['is_active'] = True
        return super().create(validated_data)


class JobListSerializer(serializers.ModelSerializer):
    """Serializer for job listing (minimal fields)"""
    category = JobCategorySerializer(read_only=True)
    skills = JobSkillSerializer(many=True, read_only=True)
    recruiter_name = serializers.CharField(source='recruiter.get_full_name', read_only=True)
    salary_range = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    can_apply = serializers.BooleanField(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company_name', 'location', 'is_remote',
            'job_type', 'experience_level', 'salary_range', 'category', 'skills',
            'recruiter_name', 'published_at', 'application_deadline', 'view_count',
            'application_count', 'is_active', 'can_apply', 'status'
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed job view"""
    category = JobCategorySerializer(read_only=True)
    skills = JobSkillSerializer(many=True, read_only=True)
    recruiter_name = serializers.CharField(source='recruiter.get_full_name', read_only=True)
    recruiter_email = serializers.EmailField(source='recruiter.email', read_only=True)
    salary_range = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    can_apply = serializers.BooleanField(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company_name', 'description', 'responsibilities',
            'requirements', 'nice_to_have', 'location', 'is_remote', 'job_type',
            'experience_level', 'salary_min', 'salary_max', 'salary_currency',
            'salary_period', 'salary_range', 'category', 'skills', 'application_deadline',
            'application_email', 'application_url', 'recruiter_name', 'recruiter_email',
            'published_at', 'expires_at', 'view_count', 'application_count',
            'is_active', 'can_apply', 'status', 'posted_to_linkedin', 'linkedin_post_url'
        ]


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating jobs"""
    skills = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=JobSkill.objects.filter(is_active=True),
        required=False
    )
    
    class Meta:
        model = Job
        fields = [
            'title', 'company_name', 'description', 'responsibilities', 'requirements',
            'nice_to_have', 'category', 'skills', 'job_type', 'experience_level',
            'location', 'is_remote', 'salary_min', 'salary_max', 'salary_currency',
            'salary_period', 'application_deadline', 'application_email', 'application_url',
            'status', 'expires_at'
        ]
    
    def validate(self, data):
        # Validate salary range
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError({
                'salary_max': 'Maximum salary must be greater than minimum salary.'
            })
        
        # Validate application deadline
        application_deadline = data.get('application_deadline')
        expires_at = data.get('expires_at')
        
        if application_deadline and expires_at and application_deadline > expires_at:
            raise serializers.ValidationError({
                'application_deadline': 'Application deadline must be before job expiry date.'
            })
        
        return data


class JobPublishSerializer(serializers.Serializer):
    """Serializer for publishing jobs to LinkedIn"""
    post_to_linkedin = serializers.BooleanField(default=False)
    linkedin_account_id = serializers.CharField(required=False, allow_blank=True)
    custom_message = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    
    def validate(self, data):
        if data.get('post_to_linkedin') and not data.get('linkedin_account_id'):
            raise serializers.ValidationError({
                'linkedin_account_id': 'LinkedIn account ID is required when posting to LinkedIn.'
            })
        return data


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for job applications"""
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company_name', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_title', 'job_company', 'applicant_name', 'applicant_email',
            'applicant_phone', 'applicant_linkedin', 'applicant_portfolio', 'cover_letter',
            'resume_file', 'status', 'applied_via', 'applied_at'
        ]
        read_only_fields = ['id', 'applied_at', 'status']
    
    def validate(self, data):
        job = data.get('job')
        applicant_email = data.get('applicant_email')
        
        # Check if job accepts applications
        if job and not job.can_apply():
            raise serializers.ValidationError({
                'job': 'This job is no longer accepting applications.'
            })
        
        # Check for duplicate applications (if updating existing)
        if not self.instance:  # Only for new applications
            existing = JobApplication.objects.filter(
                job=job, 
                applicant_email=applicant_email
            ).exists()
            
            if existing:
                raise serializers.ValidationError({
                    'applicant_email': 'You have already applied to this job.'
                })
        
        return data


class JobApplicationManageSerializer(serializers.ModelSerializer):
    """Serializer for recruiters to manage applications"""
    applicant_name = serializers.CharField(read_only=True)
    applicant_email = serializers.EmailField(read_only=True)
    applied_at = serializers.DateTimeField(read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job_title', 'applicant_name', 'applicant_email', 'applicant_phone',
            'applicant_linkedin', 'applicant_portfolio', 'cover_letter', 'resume_file',
            'status', 'applied_via', 'recruiter_notes', 'interview_feedback',
            'rejection_reason', 'applied_at', 'status_updated_at'
        ]
        read_only_fields = ['id', 'applied_at']


class JobTemplateSerializer(serializers.ModelSerializer):
    """Serializer for job templates"""
    default_category = JobCategorySerializer(read_only=True)
    default_category_id = serializers.PrimaryKeyRelatedField(
        queryset=JobCategory.objects.filter(is_active=True),
        source='default_category',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = JobTemplate
        fields = [
            'id', 'name', 'description', 'title_template', 'description_template',
            'responsibilities_template', 'requirements_template', 'nice_to_have_template',
            'default_category', 'default_category_id', 'default_job_type', 'default_experience_level',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateJobFromTemplateSerializer(serializers.Serializer):
    """Serializer for creating job from template"""
    template_id = serializers.UUIDField()
    title = serializers.CharField(max_length=200, required=False)
    company_name = serializers.CharField(max_length=200)
    location = serializers.CharField(max_length=200, required=False)
    salary_min = serializers.IntegerField(required=False, min_value=0)
    salary_max = serializers.IntegerField(required=False, min_value=0)
    
    def validate_template_id(self, value):
        try:
            template = JobTemplate.objects.get(id=value, is_active=True)
            self.context['template'] = template
            return value
        except JobTemplate.DoesNotExist:
            raise serializers.ValidationError("Template not found or inactive.")


class UnipileAccountSerializer(serializers.Serializer):
    """Serializer for Unipile account data"""
    id = serializers.CharField()
    type = serializers.CharField()
    name = serializers.CharField()
    created_at = serializers.DateTimeField()
    sources = serializers.ListField(child=serializers.DictField(), required=False)
    
    def to_representation(self, instance):
        """Convert Unipile API response to expected format"""
        data = super().to_representation(instance)
        
        # Map fields for backwards compatibility
        data['provider'] = data.get('type', '')
        data['username'] = data.get('name', '')
        data['display_name'] = data.get('name', '')
        data['connected_at'] = data.get('created_at', '')
        
        # Extract status from sources
        sources = data.get('sources', [])
        if sources and len(sources) > 0:
            data['status'] = sources[0].get('status', 'Unknown')
        else:
            data['status'] = 'Unknown'
        
        return data


class UnipileWebhookSerializer(serializers.ModelSerializer):
    """Serializer for webhook events"""
    class Meta:
        model = UnipileWebhook
        fields = [
            'id', 'webhook_type', 'event_id', 'account_id', 'event_type',
            'payload', 'processed', 'processing_error', 'created_at', 'processed_at'
        ]
        read_only_fields = ['id', 'created_at', 'processed_at']


class JobStatsSerializer(serializers.Serializer):
    """Serializer for job statistics"""
    total_jobs = serializers.IntegerField()
    published_jobs = serializers.IntegerField()
    draft_jobs = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    new_applications_today = serializers.IntegerField()
    total_views = serializers.IntegerField()
    posted_to_linkedin = serializers.IntegerField()


class JobSearchSerializer(serializers.Serializer):
    """Serializer for job search parameters"""
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=JobCategory.objects.filter(is_active=True),
        required=False
    )
    job_type = serializers.ChoiceField(choices=Job.JOB_TYPES, required=False)
    experience_level = serializers.ChoiceField(choices=Job.EXPERIENCE_LEVELS, required=False)
    location = serializers.CharField(required=False, allow_blank=True)
    is_remote = serializers.BooleanField(required=False)
    salary_min = serializers.IntegerField(required=False, min_value=0)
    salary_max = serializers.IntegerField(required=False, min_value=0)
    skills = serializers.PrimaryKeyRelatedField(
        queryset=JobSkill.objects.filter(is_active=True),
        many=True,
        required=False
    )


class ScreeningQuestionSerializer(serializers.Serializer):
    """Serializer for screening questions"""
    question = serializers.CharField(
        max_length=500,
        help_text="The screening question text"
    )
    required = serializers.BooleanField(
        default=True,
        help_text="Whether this question is required"
    )
    type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('boolean', 'Yes/No'),
            ('multiple_choice', 'Multiple Choice')
        ],
        default='text',
        help_text="Question type"
    )


class PublishOptionsSerializer(serializers.Serializer):
    """Serializer for LinkedIn job publishing options"""
    free = serializers.BooleanField(
        default=True,
        help_text="Use free posting option"
    )
    promoted = serializers.DictField(
        required=False,
        help_text="Promoted posting options with budget",
        child=serializers.CharField()
    )


class LinkedInJobCreateSerializer(serializers.Serializer):
    """Serializer for creating LinkedIn job posting"""
    job_id = serializers.CharField(
        max_length=50,
        help_text="Job ID from our database (required)"
    )
    linkedin_account_id = serializers.CharField(
        max_length=100,
        help_text="LinkedIn account ID from Unipile (required)"
    )
    location_id = serializers.CharField(
        max_length=100,
        required=False,
        help_text="LinkedIn location ID (get from /api/jobs/linkedin/search-parameters/?type=LOCATION)"
    )
    auto_rejection_template = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Auto rejection message template for applicants who fail screening"
    )
    screening_questions = ScreeningQuestionSerializer(
        many=True,
        required=False,
        help_text="Array of screening questions for applicants"
    )
    publish_options = PublishOptionsSerializer(
        required=False,
        help_text="Publishing options (free or promoted posting)"
    )
    nice_to_have = serializers.CharField(
        max_length=2000,
        required=False,
        help_text="Nice to have requirements or skills"
    )
    category = serializers.IntegerField(
        required=False,
        help_text="Job category ID"
    )
    skills = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Array of skill IDs"
    )


class LinkedInJobPublishSerializer(serializers.Serializer):
    """Serializer for publishing LinkedIn job"""
    linkedin_job_id = serializers.CharField(
        max_length=100,
        help_text="LinkedIn job ID returned from create job endpoint (required)"
    )
    linkedin_account_id = serializers.CharField(
        max_length=100,
        help_text="LinkedIn account ID from Unipile (required)"
    )
    publish_options = PublishOptionsSerializer(
        required=False,
        help_text="Publishing options (free or promoted posting)"
    )


class LinkedInJobResponseSerializer(serializers.Serializer):
    """Serializer for LinkedIn job creation response"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    linkedin_job_id = serializers.CharField(required=False)
    publish_options = serializers.DictField(required=False)
    job_url = serializers.URLField(required=False)
    published_at = serializers.DateTimeField(required=False)
