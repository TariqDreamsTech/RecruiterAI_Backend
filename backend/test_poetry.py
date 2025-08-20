#!/usr/bin/env python3
"""
Poetry Test Script for RecruiterAI Backend
Run this script to test your Poetry setup and Supabase connection
"""

import os
import sys
import subprocess
from pathlib import Path


def test_poetry_installation():
    """Test if Poetry is properly installed"""
    print("🧪 Testing Poetry Installation")
    print("=" * 40)
    
    try:
        result = subprocess.run(["poetry", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Poetry is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Poetry is not working properly")
            return False
    except FileNotFoundError:
        print("❌ Poetry not found. Please install it first:")
        print("   pip install poetry")
        return False


def test_poetry_dependencies():
    """Test if Poetry dependencies are installed"""
    print("\n📦 Testing Poetry Dependencies")
    print("=" * 40)
    
    try:
        # Check if virtual environment exists
        result = subprocess.run(["poetry", "env", "info"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Poetry virtual environment is set up")
        else:
            print("❌ Poetry virtual environment not found")
            return False
        
        # Check installed packages
        result = subprocess.run(["poetry", "show"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies are installed")
            return True
        else:
            print("❌ Failed to check dependencies")
            return False
            
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False


def test_django_with_poetry():
    """Test Django using Poetry"""
    print("\n🐍 Testing Django with Poetry")
    print("=" * 40)
    
    try:
        # Test Django version
        result = subprocess.run(
            ["poetry", "run", "python", "-c", "import django; print(django.get_version())"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Django is working: {result.stdout.strip()}")
            return True
        else:
            print("❌ Django test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Django: {e}")
        return False


def test_supabase_connection():
    """Test Supabase connection using Poetry"""
    print("\n🔌 Testing Supabase Connection with Poetry")
    print("=" * 40)
    
    try:
        # Test database connection
        result = subprocess.run([
            "poetry", "run", "python", "test_supabase.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Supabase connection test passed")
            return True
        else:
            print("❌ Supabase connection test failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Supabase connection: {e}")
        return False


def show_poetry_commands():
    """Show useful Poetry commands"""
    print("\n📚 Useful Poetry Commands")
    print("=" * 40)
    print("poetry install                    # Install all dependencies")
    print("poetry install --with dev         # Install dev dependencies")
    print("poetry add <package>              # Add a dependency")
    print("poetry add --group dev <package>  # Add dev dependency")
    print("poetry remove <package>           # Remove a dependency")
    print("poetry update                     # Update dependencies")
    print("poetry run python manage.py <cmd> # Run Django commands")
    print("poetry shell                      # Activate virtual environment")
    print("poetry show                       # Show installed packages")
    print("poetry env info                   # Show environment info")


def main():
    """Main test function"""
    print("🚀 Poetry Setup Test for RecruiterAI Backend")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Check if pyproject.toml exists
    if not Path('pyproject.toml').exists():
        print("❌ Error: pyproject.toml not found. Please run poetry_setup.py first.")
        sys.exit(1)
    
    tests_passed = 0
    total_tests = 4
    
    # Run tests
    if test_poetry_installation():
        tests_passed += 1
    
    if test_poetry_dependencies():
        tests_passed += 1
    
    if test_django_with_poetry():
        tests_passed += 1
    
    if test_supabase_connection():
        tests_passed += 1
    
    # Show results
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! Your Poetry setup is working perfectly!")
        print("\nYou can now:")
        print("1. Start the development server:")
        print("   poetry run python manage.py runserver")
        print("2. Access the admin interface:")
        print("   http://localhost:8000/admin/")
        print("3. View API documentation:")
        print("   http://localhost:8000/api/docs/")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed.")
        print("Please check the errors above and fix them.")
    
    # Show Poetry commands
    show_poetry_commands()


if __name__ == "__main__":
    main()

