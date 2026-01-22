#!/bin/bash

# Smriti Monorepo Setup Script

set -e

echo "🌳 Setting up Smriti Monorepo..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backend Setup
echo -e "${BLUE}Setting up backend...${NC}"
cd smriti-backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Backend setup complete${NC}"
cd ..

# Frontend Setup
echo -e "${BLUE}Setting up frontend...${NC}"
cd smriti-frontend
npm install
echo -e "${GREEN}✓ Frontend setup complete${NC}"
cd ..

echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Copy .env.example files and configure"
echo "2. Start backend: cd smriti-backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Start frontend: cd smriti-frontend && npm start"
