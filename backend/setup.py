#!/usr/bin/env python3
"""
Setup script for RecruiterAI Backend
This script helps with initial project setup and configuration
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


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


def setup_environment():
    """Set up environment file"""
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if not env_file.exists() and env_example.exists():
        print("\n📝 Setting up environment file...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Generate a random secret key
        import secrets
        secret_key = secrets.token_urlsafe(50)
        content = content.replace('your-secret-key-here', secret_key)
        
        # Update Supabase database configuration
        content = content.replace('DB_PASSWORD=recruiterAI@12312', 'DB_PASSWORD=recru')
        content = content.replace('DB_HOST=db.ummbhscjtbrynnicptpm.supabase.co', 'DB_HOST=db.ummbhscjtbrynnicptpm.supabase.co')
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Environment file created with generated secret key and Supabase configuration")
    else:
        print("ℹ️  Environment file already exists or env.example not found")


def main():
    """Main setup function"""
    print("🚀 Welcome to RecruiterAI Backend Setup!")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Create necessary directories
    print("\n📁 Creating necessary directories...")
    create_directories()
    
    # Set up environment
    setup_environment()
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Run migrations
    if not run_command("python manage.py makemigrations", "Creating initial migrations"):
        print("❌ Failed to create migrations.")
        sys.exit(1)
    
    if not run_command("python manage.py migrate", "Running migrations"):
        print("❌ Failed to run migrations.")
        sys.exit(1)
    
    # Create superuser prompt
    print("\n👤 Would you like to create a superuser account? (y/n): ", end="")
    create_superuser = input().lower().strip()
    
    if create_superuser in ['y', 'yes']:
        if not run_command("python manage.py createsuperuser", "Creating superuser"):
            print("⚠️  Failed to create superuser. You can create one later with:")
            print("   python manage.py createsuperuser")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate your virtual environment:")
    print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("2. Start the development server:")
    print("   python manage.py runserver")
    print("3. Access the admin interface:")
    print("   http://localhost:8000/admin/")
    print("4. View API documentation:")
    print("   http://localhost:8000/api/docs/")
    print("\nHappy coding! 🚀")


if __name__ == "__main__":
    main()
