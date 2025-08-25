from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import json
import logging

from .models import (
    Job, JobApplication, JobCategory, JobSkill, 
    JobTemplate, UnipileWebhook
)
from .serializers import (
    JobListSerializer, JobDetailSerializer, JobCreateUpdateSerializer,
    JobPublishSerializer, JobApplicationSerializer, JobApplicationManageSerializer,
    JobTemplateSerializer, CreateJobFromTemplateSerializer, UnipileAccountSerializer,
    UnipileWebhookSerializer, JobStatsSerializer, JobSearchSerializer,
    LinkedInJobCreateSerializer, LinkedInJobPublishSerializer, LinkedInJobResponseSerializer,
    JobCategorySerializer, JobSkillSerializer, JobCategoryCreateUpdateSerializer, JobSkillCreateUpdateSerializer
)
from .unipile_service import UnipileService, process_webhook_payload


logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job postings"""
    queryset = Job.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'job_type', 'experience_level', 'category', 'is_remote']
    search_fields = ['title', 'company_name', 'description', 'location']
    ordering_fields = ['created_at', 'published_at', 'application_deadline', 'view_count']
    ordering = ['-created_at']
    
    @extend_schema(tags=["Job Management"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Management"])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Management"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Management"])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Management"])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Management"])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return JobCreateUpdateSerializer
        return JobDetailSerializer
    
    def get_queryset(self):
        queryset = Job.objects.select_related('category', 'recruiter').prefetch_related('skills')
        
        # Filter by recruiter for authenticated users
        if self.request.user.is_authenticated and self.action in ['list', 'retrieve']:
            # Recruiters see their own jobs + published jobs from others
            if hasattr(self.request.user, 'is_recruiter') and self.request.user.is_recruiter:
                queryset = queryset.filter(
                    Q(recruiter=self.request.user) | Q(status='published')
                )
            else:
                # Regular users only see published jobs
                queryset = queryset.filter(status='published')
        else:
            # Anonymous users only see published jobs
            queryset = queryset.filter(status='published')
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count for published jobs
        if instance.status == 'published':
            instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @extend_schema(
        tags=["Job Management"],
        summary="Publish job",
        description="Publish a job and optionally post to LinkedIn",
        request=JobPublishSerializer,
        responses={200: JobDetailSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def publish(self, request, pk=None):
        """Publish a job and optionally post to LinkedIn"""
        job = self.get_object()
        
        if job.recruiter != request.user:
            return Response(
                {'error': 'You can only publish your own jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = JobPublishSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Publish the job
        job.status = 'published'
        job.published_at = timezone.now()
        job.save()
        
        # Post to LinkedIn if requested
        if serializer.validated_data.get('post_to_linkedin'):
            success = self._post_to_linkedin(job, serializer.validated_data)
            if not success:
                return Response(
                    {'error': 'Job published but LinkedIn posting failed'},
                    status=status.HTTP_207_MULTI_STATUS
                )
        
        return Response(JobDetailSerializer(job).data)
    
    def _post_to_linkedin(self, job, data):
        """Post job to LinkedIn via Unipile"""
        try:
            unipile = UnipileService()
            account_id = data.get('linkedin_account_id')
            
            # Prepare job data for LinkedIn posting
            job_data = {
                'title': job.title,
                'company_name': job.company_name,
                'location': job.location,
                'job_type': job.job_type,
                'description': job.description,
                'responsibilities': job.responsibilities,
                'requirements': job.requirements,
                'nice_to_have': job.nice_to_have,
                'salary_range': job.salary_range,
                'auto_rejection_template': data.get('auto_rejection_template', ''),
                'screening_questions': data.get('screening_questions', []),
            }
            
            # Create LinkedIn job posting
            response = unipile.create_linkedin_job_posting(account_id, job_data)
            
            if response and response.get('job_id'):
                job_id = response['job_id']
                
                # Auto-publish if requested (default to free posting)
                publish_options = data.get('publish_options', {'free': True})
                publish_response = unipile.publish_linkedin_job(account_id, job_id, publish_options)
                
                # Update job record
                job.posted_to_linkedin = True
                job.unipile_account_id = account_id
                job.unipile_post_id = job_id
                job.linkedin_posted_at = timezone.now()
                
                if publish_response:
                    job.linkedin_post_url = publish_response.get('url', '')
                
                job.save()
                return True
            
        except Exception as e:
            logger.error(f"Failed to post job {job.id} to LinkedIn: {e}")
        
        return False
    
    @extend_schema(
        tags=["Job Management"],
        summary="Get job statistics",
        description="Get statistics for recruiter's jobs",
        responses={200: JobStatsSerializer}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get job statistics for the current recruiter"""
        user_jobs = Job.objects.filter(recruiter=request.user)
        
        stats = {
            'total_jobs': user_jobs.count(),
            'published_jobs': user_jobs.filter(status='published').count(),
            'draft_jobs': user_jobs.filter(status='draft').count(),
            'total_applications': JobApplication.objects.filter(job__recruiter=request.user).count(),
            'new_applications_today': JobApplication.objects.filter(
                job__recruiter=request.user,
                applied_at__date=timezone.now().date()
            ).count(),
            'total_views': user_jobs.aggregate(total=Sum('view_count'))['total'] or 0,
            'posted_to_linkedin': user_jobs.filter(posted_to_linkedin=True).count(),
        }
        
        serializer = JobStatsSerializer(stats)
        return Response(serializer.data)
    
    @extend_schema(
        tags=["Job Search"],
        summary="Search jobs",
        description="Advanced job search with filters",
        parameters=[
            OpenApiParameter('query', OpenApiTypes.STR, description='Search query'),
            OpenApiParameter('category', OpenApiTypes.INT, description='Category ID'),
            OpenApiParameter('job_type', OpenApiTypes.STR, description='Job type'),
            OpenApiParameter('location', OpenApiTypes.STR, description='Location'),
            OpenApiParameter('is_remote', OpenApiTypes.BOOL, description='Remote jobs only'),
        ],
        responses={200: JobListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced job search"""
        serializer = JobSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()
        filters = serializer.validated_data
        
        # Apply filters
        if filters.get('query'):
            query = filters['query']
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(company_name__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
            )
        
        if filters.get('category'):
            queryset = queryset.filter(category=filters['category'])
        
        if filters.get('job_type'):
            queryset = queryset.filter(job_type=filters['job_type'])
        
        if filters.get('experience_level'):
            queryset = queryset.filter(experience_level=filters['experience_level'])
        
        if filters.get('location'):
            queryset = queryset.filter(location__icontains=filters['location'])
        
        if filters.get('is_remote') is not None:
            queryset = queryset.filter(is_remote=filters['is_remote'])
        
        if filters.get('salary_min'):
            queryset = queryset.filter(salary_min__gte=filters['salary_min'])
        
        if filters.get('salary_max'):
            queryset = queryset.filter(salary_max__lte=filters['salary_max'])
        
        if filters.get('skills'):
            queryset = queryset.filter(skills__in=filters['skills']).distinct()
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobListSerializer(queryset, many=True)
        return Response(serializer.data)


class JobApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job applications"""
    queryset = JobApplication.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'applied_via']
    ordering_fields = ['applied_at', 'status_updated_at']
    ordering = ['-applied_at']
    
    @extend_schema(tags=["Job Applications"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Applications"])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Applications"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Applications"])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Applications"])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Applications"])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve'] and self.request.user.is_authenticated:
            # Recruiters see management view, applicants see basic view
            return JobApplicationManageSerializer
        return JobApplicationSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Recruiters see applications for their jobs
            return JobApplication.objects.filter(job__recruiter=self.request.user)
        return JobApplication.objects.none()
    
    def get_permissions(self):
        if self.action == 'create':
            # Anyone can apply to jobs
            permission_classes = [AllowAny]
        else:
            # Only authenticated users can view/manage applications
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @extend_schema(
        tags=["Job Applications"],
        summary="Update application status",
        description="Update the status of a job application",
        request={'type': 'object', 'properties': {'status': {'type': 'string'}, 'notes': {'type': 'string'}}}
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """Update application status"""
        application = self.get_object()
        
        if application.job.recruiter != request.user:
            return Response(
                {'error': 'You can only update applications for your jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if new_status not in dict(JobApplication.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = new_status
        if notes:
            application.recruiter_notes = notes
        application.save()
        
        serializer = JobApplicationManageSerializer(application)
        return Response(serializer.data)


class JobTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job templates"""
    serializer_class = JobTemplateSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    @extend_schema(tags=["Job Templates"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Templates"])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Templates"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Templates"])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Templates"])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(tags=["Job Templates"])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        return JobTemplate.objects.filter(recruiter=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user)
    
    @extend_schema(
        tags=["Job Templates"],
        summary="Create job from template",
        description="Create a new job using a template",
        request=CreateJobFromTemplateSerializer,
        responses={201: JobDetailSerializer}
    )
    @action(detail=False, methods=['post'])
    def create_job(self, request):
        """Create a job from template"""
        serializer = CreateJobFromTemplateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        template = serializer.context['template']
        
        # Check template ownership
        if template.recruiter != request.user:
            return Response(
                {'error': 'You can only use your own templates'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create job from template
        job = template.create_job_from_template(**serializer.validated_data)
        
        return Response(
            JobDetailSerializer(job).data,
            status=status.HTTP_201_CREATED
        )


# Unipile Integration Views
@extend_schema(
    tags=["LinkedIn Integration"],
    summary="Get Unipile accounts",
    description="Get all connected Unipile accounts",
    responses={200: UnipileAccountSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unipile_accounts(request):
    """Get connected Unipile accounts"""
    try:
        unipile = UnipileService()
        accounts = unipile.get_accounts()
        serializer = UnipileAccountSerializer(accounts, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Failed to get Unipile accounts: {e}")
        return Response(
            {'error': 'Failed to fetch accounts'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=["LinkedIn Integration"],
    summary="Get LinkedIn accounts",
    description="Get connected LinkedIn accounts only",
    responses={200: UnipileAccountSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_linkedin_accounts(request):
    """Get LinkedIn accounts only"""
    try:
        unipile = UnipileService()
        accounts = unipile.get_linkedin_accounts()
        serializer = UnipileAccountSerializer(accounts, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Failed to get LinkedIn accounts: {e}")
        return Response(
            {'error': 'Failed to fetch LinkedIn accounts'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=["LinkedIn Integration"],
    summary="Setup Unipile webhooks",
    description="Setup all required webhooks for Unipile integration",
    responses={200: {'type': 'object'}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_webhooks(request):
    """Setup Unipile webhooks"""
    try:
        unipile = UnipileService()
        results = unipile.setup_webhooks()
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        return Response({
            'message': f'Setup {success_count}/{total_count} webhooks successfully',
            'results': results
        })
    except Exception as e:
        logger.error(f"Failed to setup webhooks: {e}")
        return Response(
            {'error': 'Failed to setup webhooks'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=["LinkedIn Job Management"],
    summary="Create LinkedIn job posting",
    description="Create a job posting directly on LinkedIn using Unipile API",
    request=LinkedInJobCreateSerializer,
    responses={
        200: LinkedInJobResponseSerializer,
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        404: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        500: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    },
    examples=[
        OpenApiExample(
            'Complete Example',
            summary='Complete LinkedIn job posting request',
            description='Example with all optional fields',
            value={
                'job_id': '123',
                'linkedin_account_id': 'account_67890',
                'location_id': 'linkedin_location_id_here',  # Get from /api/jobs/linkedin/search-parameters/?type=LOCATION
                'auto_rejection_template': 'Thank you for your application. Unfortunately, your profile does not match our current requirements.',
                'screening_questions': [
                    {
                        'question': 'How many years of Python experience do you have?',
                        'required': True,
                        'type': 'text'
                    },
                    {
                        'question': 'Are you authorized to work in the US?',
                        'required': True,
                        'type': 'boolean'
                    }
                ],
                'publish_options': {
                    'free': True
                },
                'nice_to_have': 'Experience with cloud platforms, Docker knowledge, open source contributions',
                'category': 1,
                'skills': [1, 2, 3, 4]
            },
            request_only=True
        ),
        OpenApiExample(
            'Minimal Example',
            summary='Minimal LinkedIn job posting request',
            description='Example with only required fields',
            value={
                'job_id': '123',
                'linkedin_account_id': 'account_67890'
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_linkedin_job(request):
    """Create a job posting on LinkedIn"""
    try:
        job_id = request.data.get('job_id')
        linkedin_account_id = request.data.get('linkedin_account_id')
        
        if not job_id or not linkedin_account_id:
            return Response(
                {'error': 'job_id and linkedin_account_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the job
        try:
            job = Job.objects.get(id=job_id, recruiter=request.user)
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        unipile = UnipileService()
        
        # Get additional data from request
        nice_to_have_override = request.data.get('nice_to_have', '')
        category_id = request.data.get('category')
        skill_ids = request.data.get('skills', [])
        location_id = request.data.get('location_id')  # LinkedIn location ID
        
        # Validate location_id is not a placeholder
        if location_id and location_id.startswith('location_') and location_id != 'location_123':
            # This is a placeholder, we need a real LinkedIn location ID
            return Response(
                {
                    'error': 'Invalid location_id',
                    'details': f'"{location_id}" is a placeholder. You need to get a real LinkedIn location ID from /api/jobs/linkedin/search-parameters/?type=LOCATION'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get category and skills if provided
        category_name = ''
        skills_list = []
        
        if category_id:
            try:
                category = JobCategory.objects.get(id=category_id)
                category_name = category.name
            except JobCategory.DoesNotExist:
                pass
        
        if skill_ids:
            skills = JobSkill.objects.filter(id__in=skill_ids)
            skills_list = [skill.name for skill in skills]
        
        # Prepare job data
        job_data = {
            'title': job.title,
            'company_name': job.company_name,
            'location': location_id or job.location,  # Use LinkedIn location ID if provided
            'job_type': job.job_type,
            'description': job.description,
            'responsibilities': job.responsibilities,
            'requirements': job.requirements,
            'nice_to_have': nice_to_have_override or job.nice_to_have,
            'salary_range': job.salary_range,
            'category_name': category_name,
            'skills_list': skills_list,
            'auto_rejection_template': request.data.get('auto_rejection_template', ''),
            'screening_questions': request.data.get('screening_questions', []),
        }
        
        # Create LinkedIn job posting
        try:
            response = unipile.create_linkedin_job_posting(linkedin_account_id, job_data)
            
            if response and response.get('job_id'):
                # Update job record
                job.posted_to_linkedin = True
                job.unipile_account_id = linkedin_account_id
                job.unipile_post_id = response['job_id']
                job.linkedin_posted_at = timezone.now()
                job.save()
                
                return Response({
                    'success': True,
                    'message': 'LinkedIn job posting created successfully',
                    'linkedin_job_id': response['job_id'],
                    'publish_options': response.get('publish_options', {})
                })
            else:
                # Log the job data for debugging
                logger.error(f"Failed to create LinkedIn job posting. Job data: {job_data}")
                return Response(
                    {
                        'error': 'Failed to create LinkedIn job posting',
                        'details': 'Check the logs for more information. Common issues: missing required fields, invalid account ID, or Unipile API errors.'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Exception during LinkedIn job creation: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {
                    'error': 'Exception during LinkedIn job creation',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f"Failed to create LinkedIn job: {e}")
        return Response(
            {'error': 'Failed to create LinkedIn job posting'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=["LinkedIn Job Management"],
    summary="Publish LinkedIn job",
    description="Publish a LinkedIn job posting that was created as a draft",
    request=LinkedInJobPublishSerializer,
    responses={
        200: LinkedInJobResponseSerializer,
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        500: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    },
    examples=[
        OpenApiExample(
            'Free Posting',
            summary='Publish with free option',
            description='Publish job using free posting option',
            value={
                'linkedin_job_id': 'linkedin_job_abc123',
                'linkedin_account_id': 'account_67890',
                'publish_options': {
                    'free': True
                }
            },
            request_only=True
        ),
        OpenApiExample(
            'Promoted Posting',
            summary='Publish with promoted option',
            description='Publish job with promoted posting and budget',
            value={
                'linkedin_job_id': 'linkedin_job_abc123',
                'linkedin_account_id': 'account_67890',
                'publish_options': {
                    'promoted': {
                        'daily_budget': 50.0,
                        'currency': 'USD'
                    }
                }
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_linkedin_job(request):
    """Publish a LinkedIn job posting"""
    try:
        linkedin_job_id = request.data.get('linkedin_job_id')
        linkedin_account_id = request.data.get('linkedin_account_id')
        publish_options = request.data.get('publish_options', {'free': True})
        
        if not linkedin_job_id or not linkedin_account_id:
            return Response(
                {'error': 'linkedin_job_id and linkedin_account_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        unipile = UnipileService()
        response = unipile.publish_linkedin_job(linkedin_account_id, linkedin_job_id, publish_options)
        
        if response:
            # Update job record if we can find it
            try:
                job = Job.objects.get(unipile_post_id=linkedin_job_id, recruiter=request.user)
                job.linkedin_post_url = response.get('url', '')
                job.save()
            except Job.DoesNotExist:
                pass  # Job might not be in our database
            
            return Response({
                'success': True,
                'message': 'LinkedIn job published successfully',
                'job_url': response.get('url', ''),
                'published_at': timezone.now().isoformat()
            })
        else:
            return Response(
                {'error': 'Failed to publish LinkedIn job'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f"Failed to publish LinkedIn job: {e}")
        return Response(
            {'error': 'Failed to publish LinkedIn job'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=["LinkedIn Job Management"],
    summary="List LinkedIn jobs",
    description="List all LinkedIn job postings for an account",
    parameters=[
        OpenApiParameter('account_id', OpenApiTypes.STR, description='LinkedIn account ID', required=True),
        OpenApiParameter('limit', OpenApiTypes.INT, description='Number of jobs to return', required=False),
    ],
    responses={200: {'type': 'object'}}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_linkedin_jobs(request):
    """List LinkedIn job postings"""
    try:
        account_id = request.query_params.get('account_id')
        limit = int(request.query_params.get('limit', 20))
        
        if not account_id:
            return Response(
                {'error': 'account_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        unipile = UnipileService()
        jobs = unipile.list_linkedin_jobs(account_id, limit)
        
        return Response({
            'success': True,
            'jobs': jobs,
            'count': len(jobs)
        })
        
    except Exception as e:
        logger.error(f"Failed to list LinkedIn jobs: {e}")
        return Response(
            {'error': 'Failed to list LinkedIn jobs'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=["LinkedIn Job Management"],
    summary="Get LinkedIn job details",
    description="Get details of a specific LinkedIn job posting",
    parameters=[
        OpenApiParameter('account_id', OpenApiTypes.STR, description='LinkedIn account ID', required=True),
        OpenApiParameter('job_id', OpenApiTypes.STR, description='LinkedIn job ID', required=True),
    ],
    responses={200: {'type': 'object'}}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_linkedin_job_details(request):
    """Get LinkedIn job details"""
    try:
        account_id = request.query_params.get('account_id')
        job_id = request.query_params.get('job_id')
        
        if not account_id or not job_id:
            return Response(
                {'error': 'account_id and job_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        unipile = UnipileService()
        job_details = unipile.get_linkedin_job(account_id, job_id)
        
        if job_details:
            return Response({
                'success': True,
                'job': job_details
            })
        else:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
    except Exception as e:
        logger.error(f"Failed to get LinkedIn job details: {e}")
        return Response(
            {'error': 'Failed to get LinkedIn job details'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=["LinkedIn Job Management"],
    summary="Get job applicants",
    description="Get applicants for a LinkedIn job posting",
    parameters=[
        OpenApiParameter('account_id', OpenApiTypes.STR, description='LinkedIn account ID', required=True),
        OpenApiParameter('job_id', OpenApiTypes.STR, description='LinkedIn job ID', required=True),
    ],
    responses={200: {'type': 'object'}}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_linkedin_job_applicants(request):
    """Get LinkedIn job applicants"""
    try:
        account_id = request.query_params.get('account_id')
        job_id = request.query_params.get('job_id')
        
        if not account_id or not job_id:
            return Response(
                {'error': 'account_id and job_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        unipile = UnipileService()
        applicants = unipile.get_job_applicants(account_id, job_id)
        
        return Response({
            'success': True,
            'applicants': applicants,
            'count': len(applicants)
        })
        
    except Exception as e:
        logger.error(f"Failed to get job applicants: {e}")
        return Response(
            {'error': 'Failed to get job applicants'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=["LinkedIn Job Management"],
    summary="Get LinkedIn search parameters",
    description="Get LinkedIn search parameters (locations, job titles, companies)",
    parameters=[
        OpenApiParameter('account_id', OpenApiTypes.STR, description='LinkedIn account ID', required=True),
        OpenApiParameter('type', OpenApiTypes.STR, description='Parameter type (LOCATION, JOB_TITLE, COMPANY)', required=False),
        OpenApiParameter('query', OpenApiTypes.STR, description='Search query for parameters', required=False),
    ],
    responses={200: {'type': 'object'}}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_linkedin_search_parameters(request):
    """Get LinkedIn search parameters"""
    try:
        account_id = request.query_params.get('account_id')
        param_type = request.query_params.get('type', 'LOCATION')
        query = request.query_params.get('query', '')
        
        if not account_id:
            return Response(
                {'error': 'account_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        unipile = UnipileService()
        
        if query:
            parameters = unipile.search_linkedin_locations(account_id, query)
        else:
            parameters = unipile.get_linkedin_search_parameters(account_id, param_type)
        
        return Response({
            'success': True,
            'parameters': parameters,
            'count': len(parameters),
            'type': param_type
        })
        
    except Exception as e:
        logger.error(f"Failed to get LinkedIn search parameters: {e}")
        return Response(
            {'error': 'Failed to get LinkedIn search parameters'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Webhook Handlers
@csrf_exempt
def webhook_account_status(request):
    """Handle account status webhooks"""
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    elif request.method == "POST":
        return _handle_webhook(request, 'account_status')
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def webhook_messaging(request):
    """Handle messaging webhooks"""
    if request.method == "OPTIONS":
        return JsonResponse({}, status=200)
    
    return _handle_webhook(request, 'messaging')


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def webhook_mailing(request):
    """Handle mailing webhooks"""
    if request.method == "OPTIONS":
        return JsonResponse({}, status=200)
    
    return _handle_webhook(request, 'mailing')


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def webhook_mail_tracking(request):
    """Handle mail tracking webhooks"""
    if request.method == "OPTIONS":
        return JsonResponse({}, status=200)
    
    return _handle_webhook(request, 'mail_tracking')


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def webhook_users_relations(request):
    """Handle users relations webhooks"""
    if request.method == "OPTIONS":
        return JsonResponse({}, status=200)
    
    return _handle_webhook(request, 'users_relations')


def _handle_webhook(request, webhook_type):
    """Common webhook handler"""
    try:
        # Log the raw request for debugging
        logger.info(f"Received {webhook_type} webhook")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request body: {request.body.decode('utf-8')}")
        
        payload = json.loads(request.body.decode('utf-8'))
        
        # Extract event information (flexible field mapping)
        event_id = payload.get('id') or payload.get('event_id') or f"webhook_{webhook_type}_{timezone.now().timestamp()}"
        event_type = payload.get('event_type') or payload.get('type') or f"{webhook_type}_event"
        account_id = payload.get('account_id') or payload.get('accountId') or payload.get('data', {}).get('account_id', '')
        
        # Store webhook event
        webhook = UnipileWebhook.objects.create(
            webhook_type=webhook_type,
            event_id=event_id,
            account_id=account_id,
            event_type=event_type,
            payload=payload
        )
        
        logger.info(f"Stored webhook {webhook.id} - Type: {webhook_type}, Event: {event_type}")
        
        # Process webhook
        try:
            success = process_webhook_payload(webhook_type, payload)
            if success:
                webhook.mark_processed()
                logger.info(f"Successfully processed webhook {webhook.id}")
            else:
                webhook.mark_processed(error="Processing failed")
                logger.warning(f"Failed to process webhook {webhook.id}")
        except Exception as e:
            webhook.mark_processed(error=str(e))
            logger.error(f"Error processing webhook {webhook.id}: {e}")
        
        return JsonResponse({
            'status': 'received',
            'webhook_id': str(webhook.id),
            'event_type': event_type
        }, status=200)
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in {webhook_type} webhook: {e}"
        logger.error(error_msg)
        return JsonResponse({'error': 'Invalid JSON', 'details': str(e)}, status=400)
    except Exception as e:
        error_msg = f"Error handling {webhook_type} webhook: {e}"
        logger.error(error_msg)
        return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)


# Public API Views
@extend_schema(
    tags=["Public API"],
    summary="Get job categories",
    description="Get all active job categories",
    responses={200: {'type': 'array', 'items': {'$ref': '#/components/schemas/JobCategory'}}}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_job_categories(request):
    """Get all job categories"""
    from .serializers import JobCategorySerializer
    categories = JobCategory.objects.filter(is_active=True)
    serializer = JobCategorySerializer(categories, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=["Public API"],
    summary="Get job skills",
    description="Get all active job skills",
    responses={200: {'type': 'array', 'items': {'$ref': '#/components/schemas/JobSkill'}}}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_job_skills(request):
    """Get all job skills"""
    from .serializers import JobSkillSerializer
    skills = JobSkill.objects.filter(is_active=True)
    serializer = JobSkillSerializer(skills, many=True)
    return Response(serializer.data)


# Category and Skills Management
@extend_schema(
    tags=["Category Management"],
    summary="Create job category",
    description="Create a new job category",
    request=JobCategoryCreateUpdateSerializer,
    responses={
        201: JobCategorySerializer,
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    },
    examples=[
        OpenApiExample(
            'Software Development',
            summary='Create Software Development category',
            description='Example for creating a software development category',
            value={
                'name': 'Software Development',
                'description': 'Jobs related to software development, programming, and engineering'
            },
            request_only=True
        ),
        OpenApiExample(
            'Marketing',
            summary='Create Marketing category',
            description='Example for creating a marketing category',
            value={
                'name': 'Digital Marketing',
                'description': 'Jobs related to digital marketing, SEO, content creation, and brand management'
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job_category(request):
    """Create a new job category"""
    serializer = JobCategoryCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        category = serializer.save()
        response_serializer = JobCategorySerializer(category)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Category Management"],
    summary="Update job category",
    description="Update an existing job category",
    request=JobCategoryCreateUpdateSerializer,
    responses={
        200: JobCategorySerializer,
        404: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    }
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_job_category(request, category_id):
    """Update a job category"""
    try:
        category = JobCategory.objects.get(id=category_id)
    except JobCategory.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    
    partial = request.method == 'PATCH'
    serializer = JobCategoryCreateUpdateSerializer(category, data=request.data, partial=partial)
    if serializer.is_valid():
        updated_category = serializer.save()
        response_serializer = JobCategorySerializer(updated_category)
        return Response(response_serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Category Management"],
    summary="Delete job category",
    description="Delete a job category",
    responses={204: None}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job_category(request, category_id):
    """Delete a job category"""
    try:
        category = JobCategory.objects.get(id=category_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except JobCategory.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=["Skills Management"],
    summary="Create job skill",
    description="Create a new job skill",
    request=JobSkillCreateUpdateSerializer,
    responses={
        201: JobSkillSerializer,
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    },
    examples=[
        OpenApiExample(
            'Python Skill',
            summary='Create Python programming skill',
            description='Example for creating a Python skill with category',
            value={
                'name': 'Python',
                'category': 1
            },
            request_only=True
        ),
        OpenApiExample(
            'General Skill',
            summary='Create skill without category',
            description='Example for creating a skill without specific category',
            value={
                'name': 'Project Management'
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job_skill(request):
    """Create a new job skill"""
    serializer = JobSkillCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        skill = serializer.save()
        response_serializer = JobSkillSerializer(skill)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Skills Management"],
    summary="Update job skill",
    description="Update an existing job skill",
    request=JobSkillCreateUpdateSerializer,
    responses={
        200: JobSkillSerializer,
        404: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    }
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_job_skill(request, skill_id):
    """Update a job skill"""
    try:
        skill = JobSkill.objects.get(id=skill_id)
    except JobSkill.DoesNotExist:
        return Response({'error': 'Skill not found'}, status=status.HTTP_404_NOT_FOUND)
    
    partial = request.method == 'PATCH'
    serializer = JobSkillCreateUpdateSerializer(skill, data=request.data, partial=partial)
    if serializer.is_valid():
        updated_skill = serializer.save()
        response_serializer = JobSkillSerializer(updated_skill)
        return Response(response_serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Skills Management"],
    summary="Delete job skill",
    description="Delete a job skill",
    responses={204: None}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job_skill(request, skill_id):
    """Delete a job skill"""
    try:
        skill = JobSkill.objects.get(id=skill_id)
        skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except JobSkill.DoesNotExist:
        return Response({'error': 'Skill not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=["Skills Management"],
    summary="Get skills by category",
    description="Get all skills filtered by category",
    parameters=[
        OpenApiParameter('category_id', OpenApiTypes.INT, description='Category ID', required=True),
    ],
    responses={200: {'type': 'array', 'items': {'$ref': '#/components/schemas/JobSkill'}}}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_skills_by_category(request, category_id):
    """Get skills by category"""
    try:
        category = JobCategory.objects.get(id=category_id)
        skills = JobSkill.objects.filter(category=category, is_active=True)
        serializer = JobSkillSerializer(skills, many=True)
        return Response(serializer.data)
    except JobCategory.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
