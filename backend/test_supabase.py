#!/usr/bin/env python3
"""
Test script to verify Supabase database connection
Run this script to test if your Django app can connect to Supabase
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

def test_database_connection():
    """Test Django database connection"""
    from django.db import connection
    
    try:
        # Test the connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Successfully connected to Supabase!")
            print(f"📊 Database version: {version[0]}")
            
            # Test Django models
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user_count = User.objects.count()
            print(f"👥 Users in database: {user_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_django_models():
    """Test if Django models can be imported"""
    try:
        from apps.authentication.models import User, UserProfile
        from apps.users.models import UserActivity, UserNotification
        from apps.recruiters.models import Company, RecruiterProfile, JobPost
        from apps.jobs.models import JobCategory, JobSearch, JobBookmark, JobRecommendation
        from apps.applications.models import JobApplication, ApplicationStatus, Interview, ApplicationNote
        
        print("✅ All Django models imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import Django models: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Supabase Database Connection")
    print("=" * 50)
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection test failed")
        sys.exit(1)
    
    # Test Django models
    if not test_django_models():
        print("\n❌ Django models test failed")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Your Django app is ready to use with Supabase.")
    print("\nYou can now:")
    print("1. Run migrations: python manage.py migrate")
    print("2. Create superuser: python manage.py createsuperuser")
    print("3. Start server: python manage.py runserver")

if __name__ == "__main__":
    main()
