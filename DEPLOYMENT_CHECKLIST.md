# 🚀 Render Deployment Checklist

Use this checklist to ensure smooth deployment to Render.

## 📋 Pre-Deployment Checklist

### Code Preparation
- [ ] Gunicorn added to requirements.txt
- [ ] Frontend API URL uses environment variable
- [ ] CORS configured for production domain
- [ ] All code committed to Git repository
- [ ] Code pushed to GitHub/GitLab

### Environment Variables Ready
- [ ] JWT_SECRET_KEY generated (strong random string)
- [ ] Frontend domain known (for CORS)
- [ ] .env.production updated with backend URL

### Files Created
- [ ] `requirements.txt` (with gunicorn)
- [ ] `render.yaml` (optional)
- [ ] `build.sh` (optional)
- [ ] `.env.production` (frontend)
- [ ] `RENDER_DEPLOYMENT.md` (documentation)

---

## 🔧 Backend Deployment Steps

### 1. Create Web Service on Render
- [ ] Go to https://dashboard.render.com/
- [ ] Click "New +" → "Web Service"
- [ ] Connect your repository

### 2. Configure Service
- [ ] **Name:** api-backend
- [ ] **Environment:** Python 3
- [ ] **Build Command:** `pip install -r requirements.txt`
- [ ] **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
- [ ] **Instance Type:** Free (or paid)

### 3. Set Environment Variables
- [ ] JWT_SECRET_KEY = `<generated-secret>`
- [ ] FLASK_ENV = production
- [ ] PYTHON_VERSION = 3.11.0

### 4. Deploy Backend
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (2-5 min)
- [ ] Check logs for errors
- [ ] Note backend URL: `https://_______.onrender.com`

### 5. Test Backend
- [ ] Visit: `https://your-backend.onrender.com/health`
- [ ] Should return: `{"status":"success","message":"API is running"}`
- [ ] Test login endpoint with curl/Postman

---

## 🎨 Frontend Deployment Steps

### 1. Update Configuration
- [ ] Edit `frontend/.env.production`
- [ ] Set VITE_API_URL to your backend URL
- [ ] Commit and push changes

### 2. Create Static Site on Render
- [ ] Go to https://dashboard.render.com/
- [ ] Click "New +" → "Static Site"
- [ ] Connect same repository

### 3. Configure Static Site
- [ ] **Name:** api-backend-frontend
- [ ] **Root Directory:** frontend
- [ ] **Build Command:** `npm install && npm run build`
- [ ] **Publish Directory:** dist

### 4. Deploy Frontend
- [ ] Click "Create Static Site"
- [ ] Wait for deployment (3-7 min)
- [ ] Check build logs
- [ ] Note frontend URL: `https://_______.onrender.com`

---

## 🔄 Post-Deployment Configuration

### Update Backend CORS
- [ ] Edit `app.py` CORS configuration
- [ ] Add frontend URL to origins list
- [ ] Commit changes
- [ ] Push to trigger auto-redeploy
- [ ] Wait for backend to redeploy

### Test Integration
- [ ] Open frontend URL in browser
- [ ] Try logging in (admin@example.com / Admin@123)
- [ ] Check browser console (F12) for errors
- [ ] Test all features:
  - [ ] Login works
  - [ ] Dashboard loads
  - [ ] User management (admin)
  - [ ] Profile editing
  - [ ] Logout works

---

## ✅ Verification Checklist

### Both Services Running
- [ ] Backend shows "Live" (green) on Render
- [ ] Frontend shows "Live" (green) on Render
- [ ] No errors in deployment logs

### Functionality Tests
- [ ] Health check endpoint responds
- [ ] Login with admin credentials works
- [ ] Login with user credentials works
- [ ] Dashboard displays correctly
- [ ] User list loads (admin)
- [ ] Can create new user (admin)
- [ ] Can edit user (admin)
- [ ] Can delete user (admin)
- [ ] Profile page loads
- [ ] Can edit own profile
- [ ] About page loads
- [ ] Logout works

### Performance & Security
- [ ] No CORS errors in console
- [ ] API calls complete successfully
- [ ] JWT tokens work correctly
- [ ] Password validation works
- [ ] Role-based access works
- [ ] HTTPS enabled (automatic on Render)

---

## 📝 Post-Deployment Notes

### Record Your URLs
```
Backend URL:  https://_________________.onrender.com
Frontend URL: https://_________________.onrender.com
Deployed On:  ____/____/____
```

### Important Settings
```
JWT_SECRET_KEY: [Stored in Render env vars]
CORS Origin:    [Your frontend URL]
Database:       SQLite (ephemeral on free tier)
```

---

## ⚠️ Known Issues & Solutions

### Issue: Cold Start Delay
**Problem:** First request after 15 min takes 30-60 sec
**Solution:** 
- [ ] Set up UptimeRobot to ping every 5 minutes
- [ ] Or upgrade to paid tier ($7/month)

### Issue: Database Resets
**Problem:** Database resets on every deploy (SQLite)
**Solution:**
- [ ] Use /reset endpoint after each deploy
- [ ] Or migrate to PostgreSQL
- [ ] Or upgrade to paid tier with persistent disk

### Issue: CORS Errors
**Problem:** Frontend can't reach backend
**Solution:**
- [ ] Verify backend CORS includes frontend URL
- [ ] Check browser console for exact error
- [ ] Redeploy backend after CORS change

---

## 🔄 Continuous Deployment

### Auto-Deploy Setup
- [ ] Auto-deploy enabled on both services
- [ ] Connected to Git repository
- [ ] Pushes to main branch trigger redeploy

### Testing Workflow
```bash
# Make changes locally
git add .
git commit -m "Your message"
git push

# Render automatically:
# 1. Detects push
# 2. Runs build command
# 3. Deploys new version
# 4. Takes 3-5 minutes
```

---

## 📊 Monitoring

### Daily Checks
- [ ] Both services showing "Live"
- [ ] No errors in logs
- [ ] Application loads correctly

### Weekly Checks
- [ ] Review Render dashboard
- [ ] Check bandwidth usage
- [ ] Review error logs
- [ ] Test all major features

---

## 🎯 Optional Enhancements

### After Successful Deployment
- [ ] Add custom domain
- [ ] Migrate to PostgreSQL database
- [ ] Set up monitoring (UptimeRobot)
- [ ] Configure error tracking
- [ ] Add analytics
- [ ] Set up backup strategy

---

## 📚 Documentation Updated

After deployment, update these files:
- [ ] README.md with production URLs
- [ ] DOCUMENTATION.md with deployment section
- [ ] Create deployment date log

---

## ✨ Success Criteria

Your deployment is successful when:
- ✅ Both services show "Live" status
- ✅ Can login from production URL
- ✅ All features work as expected
- ✅ No console errors
- ✅ No CORS issues
- ✅ Performance is acceptable

---

**Congratulations on your deployment! 🎉**

Save this checklist for future reference and redeployments.
