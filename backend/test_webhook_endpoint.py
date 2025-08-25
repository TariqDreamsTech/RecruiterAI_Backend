#!/usr/bin/env python3
"""
Test script to verify webhook endpoints are working
"""

import requests
import json

def test_account_status_webhook():
    """Test the account status webhook endpoint"""
    
    url = "https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/account-status/"
    
    # Test payload (simulating Unipile webhook)
    test_payload = {
        "id": "test_event_123",
        "event_type": "account.status_updated",
        "account_id": "test_account_456",
        "timestamp": "2025-08-25T17:30:00Z",
        "data": {
            "account_id": "test_account_456",
            "status": "connected",
            "provider": "linkedin"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Unipile-Webhook/1.0"
    }
    
    try:
        print("🧪 Testing Account Status Webhook Endpoint")
        print("=" * 50)
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(test_payload, indent=2)}")
        print()
        
        response = requests.post(url, json=test_payload, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Webhook endpoint is working!")
            print("✅ Your ngrok tunnel is accessible")
            print("✅ Django server is responding")
            return True
        else:
            print(f"\n❌ Webhook failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error:")
        print("- Check if ngrok is running")
        print("- Check if Django server is running")
        print("- Verify the ngrok URL is correct")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_options_request():
    """Test OPTIONS request (CORS preflight)"""
    
    url = "https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/account-status/"
    
    try:
        print("\n🧪 Testing OPTIONS Request (CORS)")
        print("=" * 50)
        
        response = requests.options(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ OPTIONS request successful")
            return True
        else:
            print(f"❌ OPTIONS failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ OPTIONS test error: {e}")
        return False

def main():
    """Run webhook tests"""
    print("🚀 Testing Unipile Webhook Endpoints")
    print("=" * 60)
    
    # Test OPTIONS first
    options_ok = test_options_request()
    
    # Test POST webhook
    webhook_ok = test_account_status_webhook()
    
    print("\n" + "=" * 60)
    
    if options_ok and webhook_ok:
        print("🎉 All tests passed!")
        print("\n📝 You can now configure the webhook in Unipile dashboard:")
        print("1. URL: https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/account-status/")
        print("2. Select all account events")
        print("3. Save the webhook configuration")
        print("4. Test the webhook from Unipile dashboard")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure ngrok is running: ngrok http 8000")
        print("2. Ensure Django server is running: python manage.py runserver")
        print("3. Check ngrok URL is accessible in browser")

if __name__ == "__main__":
    main()
