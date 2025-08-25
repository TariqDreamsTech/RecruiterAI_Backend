#!/usr/bin/env python3
"""
Test script for job posting system and LinkedIn integration
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('UNIPILE_API_KEY', 'P0P4J3SX.MX5Dvt2lWBiny9TDqdfRp88uKBEcRFk6TWuMi+5bXiY=')
os.environ.setdefault('UNIPILE_BASE_URL', 'https://api10.unipile.com:14090/api/v1')
os.environ.setdefault('UNIPILE_WEBHOOK_URL', 'https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks')

django.setup()

from apps.jobs.unipile_service import UnipileService
from apps.jobs.models import JobCategory, JobSkill
from django.contrib.auth import get_user_model

User = get_user_model()

def test_unipile_service():
    """Test Unipile service integration"""
    print("🧪 Testing Unipile Service...")
    
    try:
        service = UnipileService()
        
        # Test getting all accounts
        print("📡 Testing get_accounts()...")
        accounts = service.get_accounts()
        print(f"✅ Found {len(accounts)} accounts")
        
        for account in accounts:
            print(f"  - {account.get('name', 'Unknown')} ({account.get('type', 'Unknown')})")
            print(f"    ID: {account.get('id', 'N/A')}")
            print(f"    Status: {account.get('sources', [{}])[0].get('status', 'Unknown') if account.get('sources') else 'No sources'}")
        
        # Test LinkedIn accounts specifically
        print("\n📡 Testing get_linkedin_accounts()...")
        linkedin_accounts = service.get_linkedin_accounts()
        print(f"✅ Found {len(linkedin_accounts)} LinkedIn accounts")
        
        if linkedin_accounts:
            account = linkedin_accounts[0]
            account_id = account.get('id')
            print(f"  Using account: {account.get('name')} (ID: {account_id})")
            
            # Test job posting format
            print("\n📡 Testing job post formatting...")
            job_data = {
                'title': 'Senior Python Developer',
                'company_name': 'Tech Innovations Inc.',
                'location': 'San Francisco, CA',
                'job_type': 'full_time',
                'description': 'We are seeking a talented Senior Python Developer to join our dynamic team. The ideal candidate will have extensive experience in Django, REST APIs, and cloud technologies.'
            }
            
            formatted_content = service._format_job_for_linkedin(job_data)
            print("✅ Formatted job post:")
            print("=" * 50)
            print(formatted_content)
            print("=" * 50)
            
        else:
            print("⚠️  No LinkedIn accounts found for testing")
            
    except Exception as e:
        print(f"❌ Error testing Unipile service: {e}")

def test_database_models():
    """Test database models and relationships"""
    print("\n🧪 Testing Database Models...")
    
    try:
        # Test JobCategory
        print("📊 Testing JobCategory model...")
        category, created = JobCategory.objects.get_or_create(
            slug='software-development',
            defaults={
                'name': 'Software Development',
                'description': 'Software engineering and development roles'
            }
        )
        print(f"✅ JobCategory: {category.name} ({'created' if created else 'exists'})")
        
        # Test JobSkill
        print("📊 Testing JobSkill model...")
        skills_data = [
            ('python', 'Python', 'technical'),
            ('django', 'Django', 'technical'),
            ('rest-api', 'REST API', 'technical'),
            ('teamwork', 'Teamwork', 'soft'),
        ]
        
        for slug, name, skill_category in skills_data:
            skill, created = JobSkill.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'category': skill_category
                }
            )
            print(f"  - {skill.name} ({'created' if created else 'exists'})")
        
        # Test User model (for recruiter)
        print("📊 Testing User model...")
        user, created = User.objects.get_or_create(
            username='test_recruiter',
            defaults={
                'email': 'recruiter@test.com',
                'first_name': 'Test',
                'last_name': 'Recruiter'
            }
        )
        print(f"✅ User: {user.get_full_name()} ({'created' if created else 'exists'})")
        
        print("✅ All database models working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing database models: {e}")

def test_job_creation():
    """Test job creation with sample data"""
    print("\n🧪 Testing Job Creation...")
    
    try:
        from apps.jobs.models import Job
        
        # Get or create test data
        category = JobCategory.objects.get(slug='software-development')
        user = User.objects.get(username='test_recruiter')
        python_skill = JobSkill.objects.get(slug='python')
        django_skill = JobSkill.objects.get(slug='django')
        
        # Create a test job
        job, created = Job.objects.get_or_create(
            slug='senior-python-developer-tech-innovations',
            defaults={
                'recruiter': user,
                'title': 'Senior Python Developer',
                'company_name': 'Tech Innovations Inc.',
                'description': 'We are seeking a talented Senior Python Developer...',
                'responsibilities': '• Develop and maintain Django applications\n• Design REST APIs\n• Collaborate with cross-functional teams',
                'requirements': '• 5+ years Python experience\n• Strong Django knowledge\n• Experience with REST APIs',
                'nice_to_have': '• AWS experience\n• Docker knowledge\n• Agile/Scrum experience',
                'category': category,
                'job_type': 'full_time',
                'experience_level': 'senior',
                'location': 'San Francisco, CA',
                'is_remote': False,
                'salary_min': 120000,
                'salary_max': 180000,
                'salary_currency': 'USD',
                'salary_period': 'yearly',
                'application_email': 'hiring@techinnovations.com',
                'status': 'draft'
            }
        )
        
        if created:
            # Add skills to the job
            job.skills.add(python_skill, django_skill)
            print(f"✅ Created job: {job.title}")
        else:
            print(f"✅ Job exists: {job.title}")
        
        print(f"  - Company: {job.company_name}")
        print(f"  - Location: {job.location}")
        print(f"  - Salary: {job.salary_range}")
        print(f"  - Status: {job.status}")
        print(f"  - Skills: {', '.join([skill.name for skill in job.skills.all()])}")
        print(f"  - Active: {job.is_active}")
        print(f"  - Can Apply: {job.can_apply()}")
        
    except Exception as e:
        print(f"❌ Error testing job creation: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing RecruiterAI Job Posting System")
    print("=" * 60)
    
    test_unipile_service()
    test_database_models()
    test_job_creation()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n📝 Next steps:")
    print("1. Run migrations: python manage.py makemigrations && python manage.py migrate")
    print("2. Create superuser: python manage.py createsuperuser")
    print("3. Start server: python manage.py runserver")
    print("4. Test API endpoints at: http://localhost:8000/api/docs/")

if __name__ == "__main__":
    main()
