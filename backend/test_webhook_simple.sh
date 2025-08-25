#!/bin/bash

echo "🧪 Testing Webhook Endpoint with curl"
echo "===================================="

WEBHOOK_URL="https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/account-status/"

echo "📡 Testing OPTIONS request..."
curl -X OPTIONS "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n" \
  -v

echo ""
echo "📡 Testing POST request..."
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_event_123",
    "event_type": "account.status_updated",
    "account_id": "test_account_456",
    "timestamp": "2025-08-25T17:30:00Z",
    "data": {
      "account_id": "test_account_456",
      "status": "connected",
      "provider": "linkedin"
    }
  }' \
  -w "\nStatus: %{http_code}\n" \
  -v

echo ""
echo "✅ Test completed!"
