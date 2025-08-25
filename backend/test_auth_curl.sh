#!/bin/bash

# Test script for job posting API with Supabase JWT authentication

# Your JWT token from Supabase
JWT_TOKEN="eyJhbGciOiJIUzI1NiIsImtpZCI6IloxeTRYMnRISTdqTmZSTmUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3VtbWJoc2NqdGJyeW5uaWNwdHBtLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJkNjgyNzEyZC1jNDQwLTRmY2YtYTM3Mi05MDE4MGY4ODYwMDkiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MTQ1MjY2LCJpYXQiOjE3NTYxNDE2NjYsImVtYWlsIjoiYWhzYW50YXJpcTA3MjRAZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbCI6ImFoc2FudGFyaXEwNzI0QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmdWxsX25hbWUiOiJzdHJpbmciLCJwaG9uZV9udW1iZXIiOiIwMzIyODc5MTU5OSIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwic3ViIjoiZDY4MjcxMmQtYzQ0MC00ZmNmLWEzNzItOTAxODBmODg2MDA5IiwidXNlcl90eXBlIjoicmVjcnVpdGVyIiwidXNlcm5hbWUiOiJzdHJpbmcxMjMifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc1NjE0MTY2Nn1dLCJzZXNzaW9uX2lkIjoiMGIwZjdkMjItMjg4Yy00Yjk5LTg0NzAtNmNlMGEwZmU5N2U2IiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.GsZiiw3YafLo6EsD1tqyu-t0GR1BstcVrrFn4qzCC30"

BASE_URL="http://127.0.0.1:8000"

echo "🧪 Testing Job Posting API Authentication"
echo "=========================================="

echo
echo "📡 1. Testing Unipile Accounts (with Bearer token)..."
curl -X GET "${BASE_URL}/api/jobs/unipile/accounts/" \
  -H "accept: application/json" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -w "\nStatus: %{http_code}\n" | jq .

echo
echo "📡 2. Testing Unipile Accounts (direct JWT)..."  
curl -X GET "${BASE_URL}/api/jobs/unipile/accounts/" \
  -H "accept: application/json" \
  -H "Authorization: ${JWT_TOKEN}" \
  -w "\nStatus: %{http_code}\n" | jq .

echo
echo "📡 3. Testing LinkedIn Accounts..."
curl -X GET "${BASE_URL}/api/jobs/unipile/linkedin-accounts/" \
  -H "accept: application/json" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -w "\nStatus: %{http_code}\n" | jq .

echo
echo "📡 4. Testing Job Categories (public endpoint)..."
curl -X GET "${BASE_URL}/api/jobs/categories/" \
  -H "accept: application/json" \
  -w "\nStatus: %{http_code}\n" | jq .

echo
echo "📡 5. Testing Job Skills (public endpoint)..."
curl -X GET "${BASE_URL}/api/jobs/skills/" \
  -H "accept: application/json" \
  -w "\nStatus: %{http_code}\n" | jq .

echo
echo "📡 6. Testing Job List..."
curl -X GET "${BASE_URL}/api/jobs/jobs/" \
  -H "accept: application/json" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -w "\nStatus: %{http_code}\n" | jq .

echo
echo "✅ Test completed!"
