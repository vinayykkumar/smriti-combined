#!/bin/bash

# Environment Variable Checker

echo "🔍 Checking environment variables..."

check_var() {
    if [ -z "${!1}" ]; then
        echo "❌ $1 is not set"
        return 1
    else
        echo "✓ $1 is set"
        return 0
    fi
}

# Backend variables
echo ""
echo "Backend (.env in smriti-backend/):"
cd smriti-backend
if [ -f ".env" ]; then
    source .env
    check_var "MONGODB_URI"
    check_var "SECRET_KEY"
    check_var "CLOUDINARY_CLOUD_NAME"
else
    echo "❌ .env file not found"
fi
cd ..

# Frontend variables
echo ""
echo "Frontend (.env in smriti-frontend/):"
cd smriti-frontend
if [ -f ".env" ]; then
    source .env
    check_var "API_BASE_URL"
else
    echo "❌ .env file not found"
fi
cd ..

echo ""
echo "Done!"
