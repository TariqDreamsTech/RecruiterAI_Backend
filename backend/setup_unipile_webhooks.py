#!/usr/bin/env python3
"""
Script to setup Unipile webhooks with your ngrok URL
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('UNIPILE_API_KEY', 'P0P4J3SX.MX5Dvt2lWBiny9TDqdfRp88uKBEcRFk6TWuMi+5bXiY=')
os.environ.setdefault('UNIPILE_BASE_URL', 'https://api10.unipile.com:14090/api/v1')
os.environ.setdefault('UNIPILE_WEBHOOK_URL', 'https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks')

django.setup()

from apps.jobs.unipile_service import UnipileService

def main():
    """Setup all Unipile webhooks"""
    print("🔗 Setting up Unipile Webhooks with ngrok URL")
    print("=" * 60)
    
    ngrok_url = "https://0b72c5ff662f.ngrok-free.app"
    
    print(f"📡 Base URL: {ngrok_url}")
    print("\n📋 Webhook URLs to configure in Unipile:")
    print("-" * 60)
    
    webhooks = [
        ("Account Status", "account-status", "Account Status Update"),
        ("Messaging", "messaging", "Messaging Multiple events"),
        ("Mailing", "mailing", "Mailing Multiple events"),
        ("Mail Tracking", "mail-tracking", "Mail Tracking Multiple events"),
        ("Users Relations", "users-relations", "Users Relations events"),
    ]
    
    for name, path, description in webhooks:
        url = f"{ngrok_url}/api/jobs/webhooks/{path}/"
        print(f"• {name:15} → {url}")
    
    print("\n" + "=" * 60)
    
    try:
        print("🧪 Testing Unipile connection...")
        service = UnipileService()
        
        # Test connection
        accounts = service.get_accounts()
        print(f"✅ Connected! Found {len(accounts)} Unipile accounts")
        
        # Setup webhooks programmatically
        print("\n🔧 Setting up webhooks programmatically...")
        results = service.setup_webhooks()
        
        print("\n📊 Webhook Setup Results:")
        for webhook_type, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  • {webhook_type:20} → {status}")
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"\n🎉 Setup completed: {success_count}/{total_count} webhooks configured")
        
        if success_count < total_count:
            print("\n⚠️  Some webhooks failed to setup. You may need to configure them manually in Unipile dashboard.")
            print("📱 Manual Setup Instructions:")
            print("1. Go to Unipile dashboard → Webhooks")
            print("2. Create new webhook for each service")
            print("3. Use the URLs listed above")
            print("4. Select appropriate events for each webhook type")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n📱 Manual Setup Required:")
        print("1. Go to Unipile dashboard → Webhooks")
        print("2. Create new webhook for each service using URLs above")
        print("3. Select appropriate events for each webhook type")
    
    print("\n" + "=" * 60)
    print("✅ Webhook setup completed!")
    print("\n📝 Next steps:")
    print("1. Ensure ngrok is running and accessible")
    print("2. Test webhook endpoints are responding")
    print("3. Monitor webhook events in Django logs")

if __name__ == "__main__":
    main()
