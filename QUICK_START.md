# Getting Started with API Backend Dashboard

Quick guide to get the entire application running.

## Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd "C:\Users\Akram Alimaad\Desktop\API Backend"
   ```

2. **Install Python dependencies (if not done):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the backend server:**
   ```bash
   python app.py
   ```

   The backend will start on: http://127.0.0.1:5000

## Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd "C:\Users\Akram Alimaad\Desktop\API Backend\frontend"
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will start on: http://localhost:5173

## Access the Application

1. Open your browser to: http://localhost:5173
2. Log in with demo credentials:

### Admin Account
- Email: `admin@example.com`
- Password: `Admin@123`

### User Account
- Email: `john@example.com`
- Password: `User@123`

## Features Available

### For Admin Users:
- ✅ Dashboard with system statistics
- ✅ User management (view, create, edit, delete users)
- ✅ Role assignment
- ✅ Profile management
- ✅ About page

### For Regular Users:
- ✅ Personal dashboard
- ✅ Profile management
- ✅ About page

## Troubleshooting

### Backend Issues:
- Port 5000 already in use: Change port in `app.py` and `vite.config.js`
- Database error: Delete `users.db` and restart

### Frontend Issues:
- Port 5173 in use: Vite will automatically use next available port
- API connection error: Ensure backend is running on port 5000
- Login fails: Check console for error messages

## Quick Commands Reference

```bash
# Backend
cd "C:\Users\Akram Alimaad\Desktop\API Backend"
python app.py

# Frontend (new terminal)
cd "C:\Users\Akram Alimaad\Desktop\API Backend\frontend"
npm run dev
```

## Project Structure

```
API Backend/
├── app.py                    # Flask backend
├── models_sqlite.py          # Database models
├── validators.py             # Input validation
├── requirements.txt          # Python dependencies
├── users.db                  # SQLite database
├── QUICK_START.md           # This file
└── frontend/
    ├── src/
    │   ├── components/      # React components
    │   ├── pages/           # Page components
    │   ├── context/         # React context
    │   └── services/        # API services
    ├── package.json
    ├── vite.config.js
    └── README.md            # Detailed frontend docs
```

## Next Steps

After getting both servers running:
1. Explore the admin dashboard
2. Try creating a new user
3. Test the profile editing feature
4. Check out the About page for more information

Enjoy exploring the application! 🚀
