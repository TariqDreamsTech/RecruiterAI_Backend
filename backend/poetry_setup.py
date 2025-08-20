#!/usr/bin/env python3
"""
Poetry Setup Script for RecruiterAI Backend
This script helps set up the project using Poetry for dependency management
"""

import os
import subprocess
import sys
from pathlib import Path


def check_poetry_installed():
    """Check if Poetry is installed"""
    try:
        result = subprocess.run(["poetry", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Poetry is installed: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def install_poetry():
    """Install Poetry if not already installed"""
    print("📦 Installing Poetry...")
    
    try:
        # Install Poetry using the official installer
        subprocess.run([
            sys.executable, "-m", "pip", "install", "poetry"
        ], check=True)
        
        # Verify installation
        result = subprocess.run(["poetry", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Poetry installed successfully: {result.stdout.strip()}")
            return True
        else:
            print("❌ Poetry installation failed")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Poetry: {e}")
        return False


def setup_poetry_project():
    """Set up Poetry project"""
    print("🔧 Setting up Poetry project...")
    
    try:
        # Install dependencies
        subprocess.run(["poetry", "install"], check=True)
        print("✅ Dependencies installed successfully")
        
        # Install development dependencies
        subprocess.run(["poetry", "install", "--with", "dev"], check=True)
        print("✅ Development dependencies installed successfully")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
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
DB_PASSWORD=
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


def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'media',
        'media/profile_pictures',
        'media/company_logos',
        'media/resumes',
        'staticfiles'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")


def run_migrations():
    """Run Django migrations using Poetry"""
    print("\n🔄 Running Django migrations...")
    
    try:
        # Make migrations
        subprocess.run(["poetry", "run", "python", "manage.py", "makemigrations"], check=True)
        print("✅ Created migrations successfully")
        
        # Run migrations
        subprocess.run(["poetry", "run", "python", "manage.py", "migrate"], check=True)
        print("✅ Applied migrations successfully")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        return False


def setup_pre_commit():
    """Set up pre-commit hooks"""
    print("\n🔧 Setting up pre-commit hooks...")
    
    try:
        subprocess.run(["poetry", "run", "pre-commit", "install"], check=True)
        print("✅ Pre-commit hooks installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install pre-commit hooks. You can install them later with:")
        print("   poetry run pre-commit install")
        return False


def main():
    """Main setup function"""
    print("🚀 Welcome to RecruiterAI Backend Poetry Setup!")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Check if pyproject.toml exists
    if not Path('pyproject.toml').exists():
        print("❌ Error: pyproject.toml not found. Please ensure Poetry is configured.")
        sys.exit(1)
    
    # Check/Install Poetry
    if not check_poetry_installed():
        print("📦 Poetry not found. Installing...")
        if not install_poetry():
            print("❌ Failed to install Poetry. Please install it manually:")
            print("   pip install poetry")
            sys.exit(1)
    
    # Set up Poetry project
    if not setup_poetry_project():
        print("❌ Failed to set up Poetry project")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Create necessary directories
    create_directories()
    
    # Run migrations
    if not run_migrations():
        print("❌ Failed to run migrations")
        sys.exit(1)
    
    # Set up pre-commit hooks
    setup_pre_commit()
    
    # Create superuser prompt
    print("\n👤 Would you like to create a superuser account? (y/n): ", end="")
    create_superuser = input().lower().strip()
    
    if create_superuser in ['y', 'yes']:
        try:
            subprocess.run(["poetry", "run", "python", "manage.py", "createsuperuser"], check=True)
            print("✅ Superuser created successfully")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to create superuser. You can create one later with:")
            print("   poetry run python manage.py createsuperuser")
    
    print("\n🎉 Poetry setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the development server:")
    print("   poetry run python manage.py runserver")
    print("2. Access the admin interface:")
    print("   http://localhost:8000/admin/")
    print("3. View API documentation:")
    print("   http://localhost:8000/api/docs/")
    print("\nPoetry commands:")
    print("  poetry add <package>          # Add a dependency")
    print("  poetry add --group dev <package>  # Add dev dependency")
    print("  poetry run python manage.py <command>  # Run Django commands")
    print("  poetry shell                  # Activate virtual environment")
    print("\nYour Django app is now set up with Poetry! 🚀")


if __name__ == "__main__":
    main()

