# Deployment Guide

## Backend Deployment

### Render.com

1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Configure environment variables
5. Deploy

### Environment Variables

Required variables:
- `MONGODB_URI`
- `SECRET_KEY`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Frontend Deployment

### Expo

1. Install EAS CLI: `npm install -g eas-cli`
2. Configure `eas.json`
3. Build: `eas build --platform android`
4. Submit: `eas submit --platform android`

### Environment Variables

Create `.env` file with:
- `API_BASE_URL`
- Firebase configuration

## CI/CD

GitHub Actions automatically:
- Run tests on push
- Check code quality
- Build and deploy on tags
