#!/usr/bin/env python3
"""
Test script to verify Unipile API connection
"""

import requests
import json

# Unipile API Configuration
API_KEY = "P0P4J3SX.MX5Dvt2lWBiny9TDqdfRp88uKBEcRFk6TWuMi+5bXiY="
BASE_URL = "https://api10.unipile.com:14090/api/v1"

def test_unipile_connection():
    """Test connection to Unipile API"""
    
    url = f"{BASE_URL}/accounts"
    headers = {
        'X-API-KEY': API_KEY,
        'accept': 'application/json'
    }
    
    try:
        print("Testing Unipile API connection...")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            accounts = response.json()
            print(f"\n✅ Success! Response received:")
            print(f"Raw response: {accounts}")
            
            # Handle case where accounts might be a list or dict
            if isinstance(accounts, list):
                print(f"Found {len(accounts)} accounts:")
                for account in accounts:
                    if isinstance(account, dict):
                        print(f"  - ID: {account.get('id', 'N/A')}")
                        print(f"    Provider: {account.get('provider', 'N/A')}")
                        print(f"    Username: {account.get('username', 'N/A')}")
                        print(f"    Status: {account.get('status', 'N/A')}")
                        print()
                    else:
                        print(f"  - Account: {account}")
            elif isinstance(accounts, dict):
                print(f"Response is a dict: {accounts}")
            else:
                print(f"Unexpected response type: {type(accounts)}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_unipile_connection()
