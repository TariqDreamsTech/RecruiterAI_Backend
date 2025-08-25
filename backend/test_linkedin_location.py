#!/usr/bin/env python3
"""
Test script to get LinkedIn location IDs from Unipile API
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

django.setup()

from apps.jobs.unipile_service import UnipileService

def test_linkedin_locations():
    """Test getting LinkedIn location IDs"""
    print("🧪 Testing LinkedIn Location Search")
    print("=" * 50)
    
    try:
        # Initialize Unipile service
        unipile = UnipileService()
        
        # Get LinkedIn accounts first
        print("📡 Getting LinkedIn accounts...")
        linkedin_accounts = unipile.get_linkedin_accounts()
        
        if not linkedin_accounts:
            print("❌ No LinkedIn accounts found. Please connect a LinkedIn account first.")
            return False
        
        account = linkedin_accounts[0]
        account_id = account.get('id')
        account_name = account.get('name', 'Unknown')
        
        print(f"✅ Using LinkedIn account: {account_name} (ID: {account_id})")
        
        # Test getting all location parameters
        print("\n🌍 Getting all LinkedIn location parameters...")
        locations = unipile.get_linkedin_search_parameters(account_id, "LOCATION")
        
        if locations:
            print(f"✅ Found {len(locations)} location parameters:")
            for i, location in enumerate(locations[:10]):  # Show first 10
                print(f"  {i+1}. ID: {location.get('id', 'N/A')}")
                print(f"     Name: {location.get('name', 'N/A')}")
                print(f"     Type: {location.get('type', 'N/A')}")
                print()
            
            if len(locations) > 10:
                print(f"  ... and {len(locations) - 10} more locations")
        else:
            print("⚠️  No location parameters found")
        
        # Test searching for specific locations
        test_queries = ["San Francisco", "New York", "London", "Remote"]
        
        for query in test_queries:
            print(f"\n🔍 Searching for locations matching: '{query}'")
            search_results = unipile.search_linkedin_locations(account_id, query)
            
            if search_results:
                print(f"✅ Found {len(search_results)} matching locations:")
                for location in search_results[:5]:  # Show first 5
                    print(f"  - ID: {location.get('id', 'N/A')}")
                    print(f"    Name: {location.get('name', 'N/A')}")
                    print(f"    Type: {location.get('type', 'N/A')}")
            else:
                print(f"⚠️  No locations found for '{query}'")
        
        print("\n" + "=" * 50)
        print("🎯 Next Steps:")
        print("1. Use one of the location IDs above in your job posting")
        print("2. Test the job creation with a real location ID")
        print("3. If you need a specific location, use the search endpoint")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    print("🚀 LinkedIn Location ID Test")
    print("=" * 50)
    
    success = test_linkedin_locations()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("\n📝 Example usage in job posting:")
        print("  Use one of the location IDs from above instead of 'location_123'")
        print("  Example: 'location_id': 'actual_linkedin_location_id_here'")
    else:
        print("\n❌ Test failed. Check the errors above.")

if __name__ == "__main__":
    main()
