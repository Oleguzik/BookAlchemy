#!/bin/bash

# Test RapidAPI Connection Script
# This script verifies your RapidAPI credentials are working

echo "========================================="
echo "RapidAPI Connection Test"
echo "========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Create a .env file with your RapidAPI credentials"
    exit 1
fi

# Load environment variables
source .env

# Check if RAPIDAPI_KEY is set
if [ -z "$RAPIDAPI_KEY" ]; then
    echo "❌ ERROR: RAPIDAPI_KEY not set in .env file"
    exit 1
fi

echo ""
echo "Testing connection with API key: ${RAPIDAPI_KEY:0:8}..."
echo ""

# Test the API endpoint
response=$(curl -s -w "\n%{http_code}" -X POST \
  "$RAPIDAPI_URL" \
  -H "x-rapidapi-key: $RAPIDAPI_KEY" \
  -H "x-rapidapi-host: $RAPIDAPI_HOST" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Say hello"
      }
    ],
    "web_access": false
  }')

# Extract HTTP status code (last line)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

echo "HTTP Status Code: $http_code"
echo ""

if [ "$http_code" = "200" ]; then
    echo "✅ SUCCESS! API connection is working."
    echo ""
    echo "Response preview:"
    echo "$body" | head -c 200
    echo "..."
elif [ "$http_code" = "401" ]; then
    echo "❌ FAILED: 401 Unauthorized"
    echo ""
    echo "Possible causes:"
    echo "1. Invalid API key"
    echo "2. Not subscribed to the API"
    echo "3. Subscription expired"
    echo ""
    echo "Fix:"
    echo "1. Go to: https://rapidapi.com/2Stallions/api/open-ai21"
    echo "2. Click 'Subscribe to Test'"
    echo "3. Select 'Basic' (Free) plan"
    echo "4. Copy your API key from 'Code Snippets' section"
    echo "5. Update RAPIDAPI_KEY in .env file"
elif [ "$http_code" = "429" ]; then
    echo "❌ FAILED: 429 Too Many Requests"
    echo ""
    echo "You've exceeded your monthly limit (50 requests for free tier)"
    echo "Wait until next month or upgrade your plan"
else
    echo "❌ FAILED: Unexpected status code"
    echo ""
    echo "Response body:"
    echo "$body"
fi

echo ""
echo "========================================="
