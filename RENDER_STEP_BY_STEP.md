# Render Deployment - Step-by-Step Instructions

## 🚀 Quick Deployment Guide

### Prerequisites
- [x] Render account (free): https://render.com/
- [x] Git repository (GitHub, GitLab, or Bitbucket)
- [x] Your code pushed to repository

---

## 📦 OPTION 1: Two Separate Services (EASIEST)

### Step 1: Deploy Backend First

#### 1.1 Go to Render Dashboard
1. Visit https://dashboard.render.com/
2. Click **"New +"** button
3. Select **"Web Service"**

#### 1.2 Connect Repository
1. Click **"Connect repository"**
2. Authorize GitHub/GitLab access
3. Select your repository

#### 1.3 Configure Backend Service
Fill in these details:

**Basic Settings:**
```
Name: api-backend
Region: Oregon (US West) [or closest to you]
Branch: main
Root Directory: (leave empty)
Environment: Python 3
```

**Build & Deploy:**
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
```

**Instance Type:**
```
Free (or select paid tier)
```

#### 1.4 Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add these:
```
JWT_SECRET_KEY = your-super-secret-key-here-make-it-long-and-random
FLASK_ENV = production
PYTHON_VERSION = 3.11.0
```

💡 **Generate a strong JWT secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 1.5 Deploy Backend
1. Click **"Create Web Service"**
2. Wait for deployment (2-5 minutes)
3. Check logs for any errors
4. **Save your backend URL:** `https://api-backend-xxxx.onrender.com`

#### 1.6 Test Backend
```bash
# Health check
curl https://your-backend-url.onrender.com/health

# Should return: {"status":"success","message":"API is running"}
```

---

### Step 2: Update Frontend Configuration

#### 2.1 Update .env.production
Edit `frontend/.env.production`:
```env
VITE_API_URL=https://your-backend-url.onrender.com
```
Replace with your actual Render backend URL from Step 1.5

#### 2.2 Commit Changes
```bash
git add frontend/.env.production
git commit -m "Configure production API URL"
git push
```

---

### Step 3: Deploy Frontend

#### 3.1 Go to Render Dashboard
1. Visit https://dashboard.render.com/
2. Click **"New +"** button
3. Select **"Static Site"**

#### 3.2 Connect Repository
1. Select same repository as backend
2. Click **"Connect"**

#### 3.3 Configure Frontend Service
Fill in these details:

**Basic Settings:**
```
Name: api-backend-frontend
Region: Oregon (US West) [same as backend]
Branch: main
Root Directory: frontend
```

**Build Settings:**
```
Build Command: npm install && npm run build
Publish Directory: dist
```

**Auto-Deploy:**
```
[x] Yes (enabled)
```

#### 3.4 Deploy Frontend
1. Click **"Create Static Site"**
2. Wait for deployment (3-7 minutes)
3. Check build logs for errors
4. **Save your frontend URL:** `https://api-backend-frontend.onrender.com`

---

### Step 4: Update Backend CORS

#### 4.1 Update app.py CORS Configuration
Edit your `app.py` file and update CORS:

```python
# Replace the CORS line with:
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://api-backend-frontend.onrender.com",  # Your frontend URL
            "http://localhost:3000",  # Keep for local development
            "http://localhost:5173"   # Keep for local development
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
```

#### 4.2 Commit and Push
```bash
git add app.py
git commit -m "Update CORS for production"
git push
```

Render will automatically redeploy your backend.

---

### Step 5: Test Your Deployment! 🎉

#### 5.1 Open Your Frontend
Visit: `https://api-backend-frontend.onrender.com`

#### 5.2 Test Login
Use demo credentials:
- Admin: `admin@example.com` / `Admin@123`
- User: `john@example.com` / `User@123`

#### 5.3 Check Browser Console
- Press F12 to open DevTools
- Go to Console tab
- Look for any API errors

#### 5.4 Verify Features
- [x] Login works
- [x] Dashboard loads
- [x] User management works (admin)
- [x] Profile editing works
- [x] No CORS errors

---

## 🎯 OPTION 2: Single Service (Advanced)

If you want to serve everything from one service:

### Step 1: Use app_production.py
1. Rename or copy `app_production.py` to `app.py`
2. This version serves React build files from Flask

### Step 2: Update Build Command
```
Build Command: pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
```

### Step 3: Deploy as Single Web Service
Follow backend deployment steps, but with the updated build command.

**Your app will be at:** `https://your-app.onrender.com`
- Frontend: `https://your-app.onrender.com/`
- API: `https://your-app.onrender.com/health`

---

## ⚠️ Important Notes

### Free Tier Limitations
- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes 30-60 seconds (cold start)
- **Database resets on every deploy** (SQLite is ephemeral)

### Database Considerations
For production, consider:
1. **Keep SQLite** - Simple but resets on deploy
2. **Upgrade to PostgreSQL** - $7/month, persistent storage
3. **Use Render Persistent Disk** - Available on paid tiers

### Keeping Services Awake
To prevent cold starts:
1. Use a service like [UptimeRobot](https://uptimerobot.com/) (free)
2. Ping your health endpoint every 5 minutes
3. Or upgrade to paid tier ($7/month)

---

## 🔧 Troubleshooting

### Issue: Build Failed
**Check:**
- Build logs on Render dashboard
- Python/Node versions
- requirements.txt syntax

**Solution:**
```bash
# Test build locally
pip install -r requirements.txt
cd frontend && npm install && npm run build
```

### Issue: CORS Error
**Symptoms:** Red errors in browser console about CORS

**Solution:**
1. Update CORS in app.py with your frontend URL
2. Redeploy backend
3. Clear browser cache

### Issue: 502 Bad Gateway
**Check:**
- Start command is correct
- Port binding: `--bind 0.0.0.0:$PORT`
- App starts without errors locally

### Issue: Cannot Connect to Backend
**Check:**
1. Backend URL in frontend/.env.production
2. Backend service is running (green status)
3. Health endpoint works: `/health`

**Solution:**
```bash
# Test backend directly
curl https://your-backend.onrender.com/health
```

### Issue: Database Empty After Deploy
**Cause:** SQLite is ephemeral on Render free tier

**Solutions:**
1. Use `/reset` endpoint to restore default users
2. Migrate to PostgreSQL (persistent)
3. Upgrade to paid tier with persistent disk

---

## 📊 Monitoring Your Deployment

### Check Service Status
1. Go to Render Dashboard
2. Both services should show **"Live"** (green)
3. Check logs for errors

### View Logs
```
Render Dashboard → Your Service → Logs tab
```

Logs show:
- Build output
- Runtime logs
- Error messages
- API requests

### Enable Notifications
1. Dashboard → Service → Settings
2. Enable deploy notifications
3. Get alerts for failed deployments

---

## 🔄 Redeployment

### Auto Deploy (Recommended)
- Enabled by default
- Push to GitHub triggers automatic redeploy
- Takes 3-5 minutes

### Manual Deploy
1. Dashboard → Your Service
2. Click **"Manual Deploy"**
3. Select branch
4. Click **"Deploy"**

### Rollback
1. Dashboard → Your Service → Events
2. Find previous successful deploy
3. Click **"Rollback"**

---

## 💰 Cost Breakdown

### Free Tier (Both Services)
```
Backend:       $0/month (with limitations)
Frontend:      $0/month
Total:         $0/month
```

**Limitations:**
- Spins down after inactivity
- 750 hours/month total
- Shared resources

### Starter Tier (Recommended)
```
Backend:       $7/month (always on)
Frontend:      $0/month (static sites are free)
Total:         $7/month
```

**Benefits:**
- No spin down
- Better performance
- Persistent storage option
- More bandwidth

---

## ✅ Post-Deployment Checklist

- [ ] Backend deployed and showing "Live"
- [ ] Frontend deployed and showing "Live"
- [ ] Health endpoint responds: `/health`
- [ ] Can login with demo credentials
- [ ] Dashboard loads correctly
- [ ] User management works (admin)
- [ ] Profile page works
- [ ] No CORS errors in console
- [ ] No 502/504 errors
- [ ] Both URLs saved/documented

---

## 🎓 Next Steps

After successful deployment:

1. **Custom Domain (Optional)**
   - Add your own domain in Render settings
   - Update CORS with new domain

2. **Database Upgrade (Recommended)**
   - Switch from SQLite to PostgreSQL
   - Persistent data storage

3. **Monitoring**
   - Set up UptimeRobot for health checks
   - Enable error tracking

4. **Security**
   - Change JWT_SECRET_KEY regularly
   - Use strong passwords
   - Enable HTTPS (automatic on Render)

---

## 📚 Helpful Resources

- [Render Documentation](https://render.com/docs)
- [Deploy Flask Apps](https://render.com/docs/deploy-flask)
- [Deploy Static Sites](https://render.com/docs/static-sites)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Custom Domains](https://render.com/docs/custom-domains)

---

## 🆘 Need Help?

If you encounter issues:

1. **Check Logs:** Most issues shown in deployment logs
2. **Test Locally:** Verify app works on your machine
3. **Search Render Docs:** Look for specific error messages
4. **Render Community:** https://community.render.com/

---

**Ready to deploy? Start with Step 1 above! 🚀**

Good luck with your deployment! Your backend is already set up for it since you deployed before. Now you just need to add the frontend! 🎉
