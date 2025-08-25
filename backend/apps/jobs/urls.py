from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'jobs', views.JobViewSet, basename='job')
router.register(r'applications', views.JobApplicationViewSet, basename='application')
router.register(r'templates', views.JobTemplateViewSet, basename='template')

app_name = 'jobs'

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Unipile Integration URLs
    path('unipile/accounts/', views.get_unipile_accounts, name='unipile-accounts'),
    path('unipile/linkedin-accounts/', views.get_linkedin_accounts, name='linkedin-accounts'),
    path('unipile/setup-webhooks/', views.setup_webhooks, name='setup-webhooks'),
    
    # LinkedIn Job Management URLs
    path('linkedin/create-job/', views.create_linkedin_job, name='create-linkedin-job'),
    path('linkedin/publish-job/', views.publish_linkedin_job, name='publish-linkedin-job'),
    path('linkedin/jobs/', views.list_linkedin_jobs, name='list-linkedin-jobs'),
    path('linkedin/job-details/', views.get_linkedin_job_details, name='linkedin-job-details'),
    path('linkedin/job-applicants/', views.get_linkedin_job_applicants, name='linkedin-job-applicants'),
    path('linkedin/search-parameters/', views.get_linkedin_search_parameters, name='linkedin-search-parameters'),
    
    # Webhook URLs (for Unipile callbacks)
    path('webhooks/account-status/', views.webhook_account_status, name='webhook-account-status'),
    path('webhooks/messaging/', views.webhook_messaging, name='webhook-messaging'),
    path('webhooks/mailing/', views.webhook_mailing, name='webhook-mailing'),
    path('webhooks/mail-tracking/', views.webhook_mail_tracking, name='webhook-mail-tracking'),
    path('webhooks/users-relations/', views.webhook_users_relations, name='webhook-users-relations'),
    
    # Public API URLs
    path('categories/', views.get_job_categories, name='job-categories'),
    path('skills/', views.get_job_skills, name='job-skills'),
    
    # Category Management URLs
    path('categories/create/', views.create_job_category, name='create-job-category'),
    path('categories/<int:category_id>/update/', views.update_job_category, name='update-job-category'),
    path('categories/<int:category_id>/delete/', views.delete_job_category, name='delete-job-category'),
    
    # Skills Management URLs
    path('skills/create/', views.create_job_skill, name='create-job-skill'),
    path('skills/<int:skill_id>/update/', views.update_job_skill, name='update-job-skill'),
    path('skills/<int:skill_id>/delete/', views.delete_job_skill, name='delete-job-skill'),
    path('skills/by-category/<int:category_id>/', views.get_skills_by_category, name='skills-by-category'),
]
