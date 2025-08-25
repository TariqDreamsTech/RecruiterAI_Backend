#!/usr/bin/env python3
"""
Test script for LinkedIn job posting via Unipile API
"""

import os
import django
import sys
import json

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('UNIPILE_API_KEY', 'P0P4J3SX.MX5Dvt2lWBiny9TDqdfRp88uKBEcRFk6TWuMi+5bXiY=')
os.environ.setdefault('UNIPILE_BASE_URL', 'https://api10.unipile.com:14090/api/v1')

django.setup()

from apps.jobs.unipile_service import UnipileService
from apps.jobs.models import Job, JobCategory, JobSkill
from django.contrib.auth import get_user_model

User = get_user_model()

def test_linkedin_job_posting():
    """Test LinkedIn job posting functionality"""
    print("🧪 Testing LinkedIn Job Posting via Unipile")
    print("=" * 60)
    
    try:
        # Initialize Unipile service
        unipile = UnipileService()
        
        # Get LinkedIn accounts
        print("📡 Getting LinkedIn accounts...")
        linkedin_accounts = unipile.get_linkedin_accounts()
        
        if not linkedin_accounts:
            print("❌ No LinkedIn accounts found. Please connect a LinkedIn account first.")
            return False
        
        account = linkedin_accounts[0]
        account_id = account.get('id')
        account_name = account.get('name', 'Unknown')
        
        print(f"✅ Using LinkedIn account: {account_name} (ID: {account_id})")
        
        # Create test job data
        job_data = {
            'title': 'Senior Python Developer - Test Job',
            'company_name': 'Tech Innovations Inc.',
            'location': 'San Francisco, CA',
            'job_type': 'full_time',
            'description': 'We are seeking a talented Senior Python Developer to join our dynamic team. This is a test job posting created via Unipile API integration.',
            'responsibilities': """• Develop and maintain Django applications
• Design and implement REST APIs
• Collaborate with cross-functional teams
• Write clean, maintainable code
• Participate in code reviews""",
            'requirements': """• 5+ years of Python development experience
• Strong knowledge of Django framework
• Experience with REST API development
• Familiarity with PostgreSQL
• Understanding of Git version control""",
            'nice_to_have': """• AWS cloud experience
• Docker and containerization knowledge
• Experience with React/Vue.js
• Knowledge of Agile/Scrum methodologies
• Open source contributions""",
            'salary_range': 'USD 120,000 - 180,000 yearly',
            'auto_rejection_template': 'Thank you for your application. Unfortunately, your profile does not match our current requirements.',
            'screening_questions': [
                {
                    'question': 'How many years of Python experience do you have?',
                    'required': True,
                    'type': 'text'
                },
                {
                    'question': 'Are you authorized to work in the United States?',
                    'required': True,
                    'type': 'boolean'
                }
            ]
        }
        
        print("\n📝 Test Job Data:")
        print(f"  - Title: {job_data['title']}")
        print(f"  - Company: {job_data['company_name']}")
        print(f"  - Location: {job_data['location']}")
        print(f"  - Type: {job_data['job_type']}")
        print(f"  - Workplace: {unipile._map_workplace_type(job_data['job_type'])}")
        print(f"  - Employment: {unipile._map_employment_status(job_data['job_type'])}")
        
        # Test job description formatting
        print("\n🎨 Testing job description formatting...")
        formatted_description = unipile._format_job_description_for_linkedin(job_data)
        print("✅ Job description formatted successfully")
        print(f"Description length: {len(formatted_description)} characters")
        
        # Create LinkedIn job posting
        print("\n🚀 Creating LinkedIn job posting...")
        create_response = unipile.create_linkedin_job_posting(account_id, job_data)
        
        if create_response and create_response.get('job_id'):
            linkedin_job_id = create_response['job_id']
            print(f"✅ LinkedIn job created successfully!")
            print(f"  - LinkedIn Job ID: {linkedin_job_id}")
            print(f"  - Object: {create_response.get('object', 'N/A')}")
            
            # Show publish options
            publish_options = create_response.get('publish_options', {})
            if publish_options:
                print("\n💰 Publishing Options:")
                
                free_option = publish_options.get('free', {})
                if free_option:
                    print("  Free Posting:")
                    print(f"    - Eligible: {free_option.get('eligible', 'N/A')}")
                    print(f"    - Estimated Monthly Applicants: {free_option.get('estimated_monthly_applicants', 'N/A')}")
                    if free_option.get('ineligible_reason'):
                        print(f"    - Ineligible Reason: {free_option['ineligible_reason']}")
                
                promoted_option = publish_options.get('promoted', {})
                if promoted_option:
                    print("  Promoted Posting:")
                    print(f"    - Estimated Monthly Applicants: {promoted_option.get('estimated_monthly_applicants', 'N/A')}")
                    print(f"    - Currency: {promoted_option.get('currency', 'N/A')}")
                    
                    daily_budget = promoted_option.get('daily_budget', {})
                    if daily_budget:
                        print(f"    - Daily Budget: ${daily_budget.get('min', 0)} - ${daily_budget.get('max', 0)} (Recommended: ${daily_budget.get('recommended', 0)})")
            
            # Test publishing (free option)
            print("\n📤 Publishing job (free option)...")
            publish_response = unipile.publish_linkedin_job(account_id, linkedin_job_id, {'mode': 'FREE'})
            
            if publish_response:
                print("✅ Job published successfully!")
                print(f"  - Job URL: {publish_response.get('url', 'N/A')}")
                print(f"  - Published at: {publish_response.get('published_at', 'N/A')}")
                
                # Test getting job details
                print("\n📋 Getting job details...")
                job_details = unipile.get_linkedin_job(account_id, linkedin_job_id)
                
                if job_details:
                    print("✅ Job details retrieved successfully!")
                    print(f"  - Status: {job_details.get('status', 'N/A')}")
                    print(f"  - Applications: {job_details.get('applicant_count', 0)}")
                else:
                    print("⚠️  Could not retrieve job details")
                
                # Test listing jobs
                print("\n📋 Listing LinkedIn jobs...")
                job_list = unipile.list_linkedin_jobs(account_id, limit=5)
                print(f"✅ Found {len(job_list)} LinkedIn jobs")
                
                # Test getting applicants (will be empty for new job)
                print("\n👥 Getting job applicants...")
                applicants = unipile.get_job_applicants(account_id, linkedin_job_id)
                print(f"✅ Found {len(applicants)} applicants")
                
                return True
                
            else:
                print("❌ Failed to publish job")
                return False
        else:
            print("❌ Failed to create LinkedIn job posting")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_job_mapping():
    """Test job type mapping functions"""
    print("\n🧪 Testing Job Type Mappings")
    print("=" * 40)
    
    unipile = UnipileService()
    
    job_types = ['full_time', 'part_time', 'contract', 'freelance', 'internship', 'remote', 'hybrid']
    
    print("Job Type → Workplace | Employment Status")
    print("-" * 40)
    
    for job_type in job_types:
        workplace = unipile._map_workplace_type(job_type)
        employment = unipile._map_employment_status(job_type)
        print(f"{job_type:12} → {workplace:8} | {employment}")

def test_html_formatting():
    """Test HTML formatting for job descriptions"""
    print("\n🧪 Testing HTML Formatting")
    print("=" * 40)
    
    unipile = UnipileService()
    
    test_text = """• Develop and maintain applications
• Work with databases
• Write documentation
This is a regular paragraph.
• Another bullet point
• Final point"""
    
    formatted = unipile._format_text_to_html(test_text)
    print("Original text:")
    print(test_text)
    print("\nFormatted HTML:")
    print(formatted)

def main():
    """Run all tests"""
    print("🚀 LinkedIn Job Posting Test Suite")
    print("=" * 80)
    
    # Test mappings first
    test_job_mapping()
    
    # Test HTML formatting
    test_html_formatting()
    
    # Test actual job posting
    success = test_linkedin_job_posting()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 All tests completed successfully!")
        print("\n📝 Next steps:")
        print("1. Check LinkedIn to verify the job was posted")
        print("2. Test the API endpoints via Swagger UI")
        print("3. Configure webhook account status notifications")
        print("4. Test job application workflow")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Unipile API key is valid")
        print("2. Check LinkedIn account connection status")
        print("3. Verify account permissions for job posting")

if __name__ == "__main__":
    main()
