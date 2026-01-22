#!/bin/bash

# Clean script for Smriti Monorepo

echo "🧹 Cleaning Smriti Monorepo..."

# Backend cleanup
echo "Cleaning backend..."
cd smriti-backend
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf .coverage
rm -rf htmlcov
rm -rf *.egg-info
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
echo "✓ Backend cleaned"
cd ..

# Frontend cleanup
echo "Cleaning frontend..."
cd smriti-frontend
rm -rf node_modules
rm -rf .expo
rm -rf dist
rm -rf build
rm -rf coverage
echo "✓ Frontend cleaned"
cd ..

echo "🎉 Cleanup complete!"
