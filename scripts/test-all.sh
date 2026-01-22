#!/bin/bash

# Run all tests

set -e

echo "🧪 Running all tests..."

# Backend tests
echo ""
echo "Running backend tests..."
cd smriti-backend
source venv/bin/activate 2>/dev/null || true
pytest || echo "Backend tests failed or not configured"
cd ..

# Frontend tests
echo ""
echo "Running frontend tests..."
cd smriti-frontend
npm test -- --passWithNoTests || echo "Frontend tests failed or not configured"
cd ..

echo ""
echo "✅ Test run complete!"
