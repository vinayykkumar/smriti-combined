# Smriti Monorepo Setup Script (PowerShell)

Write-Host "🌳 Setting up Smriti Monorepo..." -ForegroundColor Blue

# Backend Setup
Write-Host "Setting up backend..." -ForegroundColor Cyan
Set-Location smriti-backend
if (-Not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Backend setup complete" -ForegroundColor Green
Set-Location ..

# Frontend Setup
Write-Host "Setting up frontend..." -ForegroundColor Cyan
Set-Location smriti-frontend
npm install
Write-Host "✓ Frontend setup complete" -ForegroundColor Green
Set-Location ..

Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Copy .env.example files and configure"
Write-Host "2. Start backend: cd smriti-backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload"
Write-Host "3. Start frontend: cd smriti-frontend && npm start"
