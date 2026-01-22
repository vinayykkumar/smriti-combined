# Troubleshooting Guide

## Common Issues

### Backend

#### Database Connection Failed

**Problem**: Cannot connect to MongoDB

**Solution**:
- Check `MONGODB_URI` in `.env`
- Verify network access in MongoDB Atlas
- Check IP whitelist

#### Port Already in Use

**Problem**: Port 8000 already in use

**Solution**:
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
uvicorn app.main:app --port 8001
```

### Frontend

#### Metro Bundler Issues

**Problem**: Metro bundler not starting

**Solution**:
```bash
cd smriti-frontend
rm -rf node_modules
npm install
npm start -- --reset-cache
```

#### Build Errors

**Problem**: Build fails with errors

**Solution**:
- Clear Expo cache: `expo start -c`
- Clear node_modules and reinstall
- Check for version conflicts

## Getting Help

1. Check existing issues on GitHub
2. Review documentation
3. Create new issue with details
