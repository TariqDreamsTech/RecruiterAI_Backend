#!/usr/bin/env python3
"""
Seed script to create initial job categories and skills
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from apps.jobs.models import JobCategory, JobSkill

def create_categories_and_skills():
    """Create initial job categories and skills"""
    print("🌱 Seeding job categories and skills...")
    
    # Create categories
    categories_data = [
        {
            'name': 'Software Development',
            'description': 'Jobs related to software development, programming, and engineering',
            'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'Django', 'PostgreSQL', 'Git', 'AWS', 'Docker', 'REST APIs']
        },
        {
            'name': 'Data Science',
            'description': 'Jobs related to data analysis, machine learning, and AI',
            'skills': ['Python', 'R', 'SQL', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Jupyter', 'Statistics']
        },
        {
            'name': 'Product Management',
            'description': 'Jobs related to product strategy, planning, and management',
            'skills': ['Product Strategy', 'Agile', 'Scrum', 'Market Research', 'User Stories', 'Roadmapping', 'Analytics', 'Stakeholder Management']
        },
        {
            'name': 'Design',
            'description': 'Jobs related to UI/UX design, graphic design, and creative roles',
            'skills': ['UI/UX Design', 'Figma', 'Adobe Creative Suite', 'Sketch', 'Prototyping', 'User Research', 'Design Systems', 'Wireframing']
        },
        {
            'name': 'Marketing',
            'description': 'Jobs related to digital marketing, content creation, and brand management',
            'skills': ['Digital Marketing', 'SEO', 'SEM', 'Social Media', 'Content Marketing', 'Google Analytics', 'Email Marketing', 'Brand Management']
        },
        {
            'name': 'Sales',
            'description': 'Jobs related to sales, business development, and customer relations',
            'skills': ['Sales', 'CRM', 'Lead Generation', 'Negotiation', 'Business Development', 'Customer Relations', 'Salesforce', 'Cold Calling']
        },
        {
            'name': 'DevOps',
            'description': 'Jobs related to infrastructure, deployment, and system administration',
            'skills': ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 'Terraform', 'Linux', 'Monitoring', 'Security', 'Cloud Computing']
        },
        {
            'name': 'Quality Assurance',
            'description': 'Jobs related to software testing and quality assurance',
            'skills': ['Manual Testing', 'Automation Testing', 'Selenium', 'Test Planning', 'Bug Tracking', 'API Testing', 'Performance Testing', 'QA Processes']
        }
    ]
    
    created_categories = 0
    created_skills = 0
    
    for category_data in categories_data:
        # Create or get category
        category, created = JobCategory.objects.get_or_create(
            name=category_data['name'],
            defaults={
                'description': category_data['description'],
                'is_active': True
            }
        )
        
        if created:
            created_categories += 1
            print(f"✅ Created category: {category.name}")
        else:
            print(f"📋 Category already exists: {category.name}")
        
        # Create skills for this category
        for skill_name in category_data['skills']:
            skill, skill_created = JobSkill.objects.get_or_create(
                name=skill_name,
                defaults={
                    'category': category,
                    'is_active': True
                }
            )
            
            if skill_created:
                created_skills += 1
                print(f"  ✅ Created skill: {skill.name}")
            else:
                # Update category if skill exists but has no category
                if not skill.category:
                    skill.category = category
                    skill.save()
                    print(f"  📋 Updated skill category: {skill.name}")
                else:
                    print(f"  📋 Skill already exists: {skill.name}")
    
    print(f"\n🎉 Seeding completed!")
    print(f"📊 Created {created_categories} new categories")
    print(f"🛠️ Created {created_skills} new skills")
    
    # Display summary
    total_categories = JobCategory.objects.filter(is_active=True).count()
    total_skills = JobSkill.objects.filter(is_active=True).count()
    
    print(f"\n📈 Total active categories: {total_categories}")
    print(f"📈 Total active skills: {total_skills}")
    
    return True

def list_categories_and_skills():
    """List all categories and their skills"""
    print("\n📋 Current Categories and Skills:")
    print("=" * 50)
    
    categories = JobCategory.objects.filter(is_active=True).prefetch_related('jobskill_set')
    
    for category in categories:
        print(f"\n🏷️  {category.name} (ID: {category.id})")
        print(f"   {category.description}")
        
        skills = category.jobskill_set.filter(is_active=True)
        if skills:
            print("   Skills:")
            for skill in skills:
                print(f"     • {skill.name} (ID: {skill.id})")
        else:
            print("   No skills yet")

def main():
    """Main function"""
    print("🚀 Job Categories & Skills Seeder")
    print("=" * 50)
    
    try:
        # Seed data
        create_categories_and_skills()
        
        # List current data
        list_categories_and_skills()
        
        print("\n✨ Success! You can now use these categories and skills in your job postings.")
        print("\n📝 API Endpoints to test:")
        print("  GET /api/jobs/categories/ - List all categories")
        print("  GET /api/jobs/skills/ - List all skills")
        print("  GET /api/jobs/skills/by-category/1/ - Get skills by category")
        print("  POST /api/jobs/categories/create/ - Create new category")
        print("  POST /api/jobs/skills/create/ - Create new skill")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
