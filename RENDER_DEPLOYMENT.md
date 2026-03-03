# Deployment Guide for Render

## 🚀 Deployment Options

You have **two options** for deploying to Render:

### Option 1: Two Separate Services (Recommended)
- **Backend:** Web Service (Flask API)
- **Frontend:** Static Site (React app)
- Easier to manage and scale independently

### Option 2: Single Service (Flask Serves Frontend)
- **Combined:** Web Service (Flask serves both API and React build)
- Single deployment, lower cost

---

## 📦 Option 1: Two Separate Services (RECOMMENDED)

### Step 1: Deploy Backend API

#### 1.1 Create `render.yaml` (Optional but recommended)
Already created in your project root.

#### 1.2 Update Backend for Production

Make sure your `app.py` has production settings:
```python
# Update CORS to allow your frontend domain
CORS(app, resources={
    r"/*": {
        "origins": ["https://your-frontend.onrender.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

#### 1.3 Deploy Backend to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your repository (or upload files)
4. Configure:
   - **Name:** `api-backend` (or your choice)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free` (or paid)

5. Add Environment Variables:
   ```
   JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
   FLASK_ENV=production
   ```

6. Click **"Create Web Service"**

7. **Note your backend URL:** `https://api-backend-xxxx.onrender.com`

### Step 2: Deploy Frontend

#### 2.1 Update Frontend API URL

Before building, update the API URL in `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://your-backend.onrender.com'  // Your Render backend URL
  : '/api';
```

#### 2.2 Deploy Frontend to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Static Site"**
3. Connect your repository (point to `frontend` folder)
4. Configure:
   - **Name:** `api-backend-frontend` (or your choice)
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`

5. Click **"Create Static Site"**

6. **Your frontend URL:** `https://api-backend-frontend.onrender.com`

#### 2.3 Update Backend CORS

Go back to your backend service and update the CORS origins to include your frontend URL:

```python
CORS(app, resources={
    r"/*": {
        "origins": ["https://api-backend-frontend.onrender.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

Redeploy the backend service.

---

## 📦 Option 2: Single Service (Flask Serves Frontend)

This option serves the React build from Flask, so you only need one Render service.

### Step 1: Prepare Backend to Serve Frontend

I'll create the updated `app.py` with static file serving.

### Step 2: Build Frontend Locally

```bash
cd frontend
npm run build
# This creates frontend/dist/ folder
```

### Step 3: Deploy to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your repository
4. Configure:
   - **Name:** `api-backend-fullstack`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`

5. Add Environment Variables:
   ```
   JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
   FLASK_ENV=production
   ```

6. Click **"Create Web Service"**

**Your app will be available at:** `https://api-backend-fullstack.onrender.com`

---

## 🔧 Required Files

### 1. Gunicorn (Production Server)

Add to `requirements.txt`:
```
gunicorn==21.2.0
```

### 2. Build Script (Optional)

Create `build.sh` in project root:
```bash
#!/bin/bash
pip install -r requirements.txt
cd frontend
npm install
npm run build
cd ..
```

### 3. Render.yaml (Infrastructure as Code)

Already created for you - see `render.yaml` in project root.

---

## 🔐 Environment Variables to Set on Render

### Required:
- `JWT_SECRET_KEY` - Strong secret key for JWT tokens
- `FLASK_ENV` - Set to `production`

### Optional:
- `DATABASE_URL` - If using external database (currently using SQLite)
- `CORS_ORIGINS` - Comma-separated allowed origins

---

## ⚠️ Important Notes

### SQLite Limitations on Render
- **Free tier:** Ephemeral storage (database resets on redeploy)
- **Paid tier:** Persistent storage available
- **Recommendation:** Use PostgreSQL for production

### To Migrate to PostgreSQL:
1. Create PostgreSQL database on Render
2. Update `models_sqlite.py` to support PostgreSQL
3. Use `DATABASE_URL` environment variable

---

## 📝 Deployment Checklist

### Before Deploying:

- [ ] Update `JWT_SECRET_KEY` to strong random value
- [ ] Update CORS origins to your frontend domain
- [ ] Add `gunicorn` to requirements.txt
- [ ] Test locally with production build
- [ ] Update frontend API URL for production
- [ ] Commit all changes to repository

### After Deploying Backend:

- [ ] Note your backend URL
- [ ] Test health endpoint: `https://your-backend.onrender.com/health`
- [ ] Verify environment variables are set

### After Deploying Frontend:

- [ ] Update backend CORS with frontend URL
- [ ] Test login functionality
- [ ] Verify API calls work
- [ ] Check browser console for errors

---

## 🧪 Test Your Deployment

### 1. Test Backend API
```bash
# Health check
curl https://your-backend.onrender.com/health

# Login test
curl -X POST https://your-backend.onrender.com/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin@123"}'
```

### 2. Test Frontend
- Open `https://your-frontend.onrender.com`
- Try logging in with demo credentials
- Check browser console for errors
- Test user management features

---

## 🔄 Continuous Deployment

Render supports auto-deploy from Git:

1. Connect your GitHub/GitLab repository
2. Enable auto-deploy on push
3. Every push to main branch triggers rebuild

---

## 💰 Cost Considerations

### Free Tier (Both Options):
- 750 hours/month of runtime
- Services spin down after 15 min of inactivity
- Cold starts take 30-60 seconds

### Paid Tier (Starting at $7/month):
- Always-on services
- No cold starts
- Persistent storage
- Better performance

---

## 🐛 Common Issues

### Issue: CORS Error
**Solution:** Update backend CORS to include frontend URL

### Issue: Database Resets
**Solution:** Use PostgreSQL or paid tier for persistent storage

### Issue: Build Fails
**Solution:** Check build logs, verify Node/Python versions

### Issue: 502 Bad Gateway
**Solution:** Check start command, verify app.py works locally

### Issue: Frontend Can't Reach Backend
**Solution:** Update API_BASE_URL in frontend code

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Deploy Flask Apps](https://render.com/docs/deploy-flask)
- [Deploy Static Sites](https://render.com/docs/static-sites)
- [Deploy from GitHub](https://render.com/docs/github)

---

## 🎯 Recommended Approach

I recommend **Option 1 (Two Separate Services)** because:
- ✅ Easier to debug issues
- ✅ Independent scaling
- ✅ Faster frontend deploys (no backend rebuild)
- ✅ Can use CDN for frontend
- ✅ Standard modern architecture

---

**Next Steps:** Let me create the necessary configuration files for you!
