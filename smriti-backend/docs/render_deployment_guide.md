# Deploy Smriti Backend to Render.com - Complete Guide

## Prerequisites
- ✅ GitHub account
- ✅ Code pushed to GitHub repository
- ✅ MongoDB Atlas account (we'll set this up)

---

## Part 1: Setup MongoDB Atlas (Free Database)

### Step 1: Create MongoDB Atlas Account
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Click **"Try Free"**
3. Sign up with Google/GitHub or email
4. Complete verification

### Step 2: Create Free Cluster
1. Choose **M0 (Free)** tier
2. Select **AWS** as provider
3. Choose region closest to you (e.g., `us-east-1`)
4. Cluster Name: `smriti-cluster` (or any name)
5. Click **"Create Deployment"**
6. **Save the username and password** shown (you'll need this!)

### Step 3: Configure Network Access
1. In Atlas dashboard, go to **"Network Access"** (left sidebar)
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (for Render)
4. Confirm (IP: `0.0.0.0/0`)

### Step 4: Get Connection String
1. Go to **"Database"** → Click **"Connect"**
2. Choose **"Drivers"**
3. Select **Python** and version **3.12 or later**
4. Copy the connection string:
   ```
   mongodb+srv://<username>:<password>@smriti-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. **Replace `<username>` and `<password>`** with your actual credentials
6. **Save this string** - you'll need it for Render!

---

## Part 2: Push Code to GitHub

### Step 1: Commit Your Changes
```bash
cd c:\Users\Vinay\OneDrive\Desktop\smriti-backend

# Check status
git status

# Add all files
git add .

# Commit
git commit -m "feat: production-ready backend with validation and docs"

# Push to GitHub
git push origin feature/v1
```

### Step 2: Verify on GitHub
1. Go to your GitHub repository
2. Confirm all files are there (especially `app/`, `requirements.txt`)

---

## Part 3: Deploy to Render.com

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Click **"Get Started"**
3. Sign up with **GitHub** (easiest)
4. Authorize Render to access your repositories

### Step 2: Create New Web Service
1. Click **"New +"** (top right)
2. Select **"Web Service"**
3. Click **"Connect a repository"**
4. Find and select **`smriti-backend`**
5. Click **"Connect"**

### Step 3: Configure Service Settings

**Basic Settings:**
- **Name:** `smriti-api` (or your choice)
- **Region:** Choose closest to you
- **Branch:** `feature/v1`
- **Root Directory:** Leave blank
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:**
  ```
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Select **"Free"** (0.1 CPU, 512MB RAM)

### Step 4: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these one by one:

| Key | Value | Notes |
|-----|-------|-------|
| `MONGODB_URI` | `mongodb+srv://...` | From MongoDB Atlas Step 4 |
| `SECRET_KEY` | Your secret key | From your `.env` file |
| `ENVIRONMENT` | `production` | Important! |
| `CLOUDINARY_CLOUD_NAME` | Your cloud name | From Cloudinary dashboard |
| `CLOUDINARY_API_KEY` | Your API key | From Cloudinary |
| `CLOUDINARY_API_SECRET` | Your API secret | From Cloudinary |

**Important:** Make sure `MONGODB_URI` has your actual username and password!

### Step 5: Deploy!
1. Click **"Create Web Service"**
2. Render will start building (takes 2-3 minutes)
3. Watch the logs for any errors

---

## Part 4: Verify Deployment

### Step 1: Check Build Logs
- Watch for `Build successful` message
- Look for `Starting server...` in deploy logs

### Step 2: Get Your URL
Your API will be at:
```
https://smriti-api.onrender.com
```
(Replace `smriti-api` with your chosen name)

### Step 3: Test Health Endpoints

**Test 1: Basic Health**
```bash
curl https://smriti-api.onrender.com/health
```
Expected:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Smriti API"
}
```

**Test 2: Database Health**
```bash
curl https://smriti-api.onrender.com/health/db
```
Expected:
```json
{
  "status": "healthy",
  "database": "connected",
  "type": "MongoDB"
}
```

### Step 4: Test API Endpoints

**Create a user:**
```bash
curl -X POST https://smriti-api.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

---

## Part 5: Update Production Settings

### Step 1: Update CORS Origins
1. In Render dashboard, go to **Environment**
2. Add new variable:
   - **Key:** `ALLOWED_ORIGINS`
   - **Value:** Your frontend URL (when you have it)
   
   For now, the code defaults to allowing all origins in development.

### Step 2: Enable Auto-Deploy
Render automatically deploys on every push to your branch!

To disable:
1. Go to **Settings**
2. Find **"Auto-Deploy"**
3. Toggle off (if needed)

---

## Troubleshooting

### Build Fails
**Check:**
- `requirements.txt` is in root directory
- All dependencies are listed
- Python version compatibility

**View logs:**
- Click on your service
- Go to **"Logs"** tab

### Database Connection Fails
**Check:**
- MongoDB Atlas IP whitelist includes `0.0.0.0/0`
- `MONGODB_URI` has correct username/password
- No special characters in password (or URL-encode them)

### Service Won't Start
**Check:**
- Start command is correct: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `$PORT` is used (Render provides this)
- All environment variables are set

---

## Free Tier Limits

**Render Free Tier:**
- ✅ 750 hours/month (enough for 24/7)
- ✅ Spins down after 15 min of inactivity
- ✅ First request after sleep takes ~30 seconds
- ✅ 512MB RAM, 0.1 CPU

**MongoDB Atlas Free Tier:**
- ✅ 512MB storage
- ✅ Shared CPU
- ✅ Perfect for development/small apps

---

## Post-Deployment

### Update Your Frontend
Once deployed, update your mobile app to use:
```
https://smriti-api.onrender.com
```

### Monitor Your API
- Check Render dashboard for metrics
- Use `/health` and `/health/db` for monitoring
- View logs in Render dashboard

### Future Updates
Just push to GitHub:
```bash
git add .
git commit -m "your changes"
git push origin feature/v1
```
Render auto-deploys! 🚀

---

## Summary Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Connection string obtained
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service configured
- [ ] Environment variables added
- [ ] Service deployed successfully
- [ ] Health endpoints tested
- [ ] API endpoints verified

**Your API is now live!** 🎉
