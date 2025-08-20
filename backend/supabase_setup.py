#!/usr/bin/env python3
"""
Supabase Database Setup Script for RecruiterAI Backend
This script helps configure the project to use Supabase PostgreSQL database
"""

import os
import subprocess
import sys
from pathlib import Path


def test_supabase_connection():
    """Test connection to Supabase database"""
    print("🔌 Testing Supabase database connection...")
    
    try:
        import psycopg2
        
        # Test connection
        conn = psycopg2.connect(
            host='db.ummbhscjtbrynnicptpm.supabase.co',
            database='postgres',
            user='postgres',
            password='recruiterAI@12312',
            port='5432',
            sslmode='require'
        )
        
        # Test query
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        
        cur.close()
        conn.close()
        
        print(f"✅ Successfully connected to Supabase!")
        print(f"📊 Database version: {version[0]}")
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        return test_supabase_connection()
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False


def create_env_file():
    """Create .env file with Supabase configuration"""
    env_content = """# Django Settings
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings - Supabase PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=recruiterAI@12312
DB_HOST=db.ummbhscjtbrynnicptpm.supabase.co
DB_PORT=5432
DB_SSL_MODE=require

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS Settings (for file uploads)
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# AWS_STORAGE_BUCKET_NAME=your-bucket-name
# AWS_S3_REGION_NAME=your-region

# Redis Settings (for caching and background tasks)
# REDIS_URL=redis://localhost:6379/0

# API Keys
# OPENAI_API_KEY=your-openai-api-key
# LINKEDIN_API_KEY=your-linkedin-api-key
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with Supabase configuration")
    else:
        print("ℹ️  .env file already exists")


def run_migrations():
    """Run Django migrations"""
    print("\n🔄 Running Django migrations...")
    
    try:
        # Make migrations
        result = subprocess.run(
            ["python", "manage.py", "makemigrations"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print("✅ Created migrations successfully")
        
        # Run migrations
        result = subprocess.run(
            ["python", "manage.py", "migrate"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print("✅ Applied migrations successfully")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("🚀 Welcome to RecruiterAI Backend Supabase Setup!")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Test Supabase connection
    if not test_supabase_connection():
        print("❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Install dependencies if needed
    print("\n📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Run migrations
    if not run_migrations():
        print("❌ Failed to run migrations")
        sys.exit(1)
    
    # Create superuser prompt
    print("\n👤 Would you like to create a superuser account? (y/n): ", end="")
    create_superuser = input().lower().strip()
    
    if create_superuser in ['y', 'yes']:
        try:
            subprocess.run(["python", "manage.py", "createsuperuser"], check=True)
            print("✅ Superuser created successfully")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to create superuser. You can create one later with:")
            print("   python manage.py createsuperuser")
    
    print("\n🎉 Supabase setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the development server:")
    print("   python manage.py runserver")
    print("2. Access the admin interface:")
    print("   http://localhost:8000/admin/")
    print("3. View API documentation:")
    print("   http://localhost:8000/api/docs/")
    print("\nYour Django app is now connected to Supabase! 🚀")


if __name__ == "__main__":
    main()
