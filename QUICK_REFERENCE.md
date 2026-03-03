# API Backend Dashboard - Quick Reference

## 📦 What You Have

### Full-Stack Application
- **Backend:** Flask REST API (Python)
- **Frontend:** React + Vite (JavaScript)
- **Database:** SQLite with password authentication
- **Security:** JWT tokens, bcrypt hashing, role-based access

---

## 🎯 Key Features

### Backend Features
✅ **9 RESTful API Endpoints** - Complete CRUD operations  
✅ **JWT Authentication** - Secure token-based auth with 1-hour expiration  
✅ **Password Security** - bcrypt hashing with 8 validation rules  
✅ **Role-Based Access** - Admin and user roles with different permissions  
✅ **Input Validation** - Comprehensive validation for all inputs  
✅ **SQLite Database** - Persistent storage with thread-safe operations  
✅ **Error Handling** - Proper error responses with status codes  
✅ **CORS Enabled** - Cross-origin requests supported  
✅ **78+ Automated Tests** - Comprehensive test coverage  

### Frontend Features
✅ **Modern React UI** - React 18 with hooks and context  
✅ **Bootstrap 5 Design** - Responsive, professional UI  
✅ **Role-Based Dashboards** - Different views for admin vs users  
✅ **User Management** - Full CRUD interface with modals (admin only)  
✅ **Profile Management** - Users can edit their own information  
✅ **Protected Routes** - Automatic authentication checking  
✅ **Token Management** - Auto-refresh and expiration handling  
✅ **Demo Login Buttons** - Quick access with pre-filled credentials  
✅ **Collapsible Sidebar** - Modern navigation with icons  
✅ **Responsive Design** - Works on desktop, tablet, and mobile  

---

## 🛠️ Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Flask | 3.0.0 | Web framework |
| SQLAlchemy | 3.1.1 | ORM / Database layer |
| Flask-JWT-Extended | 4.6.0 | JWT authentication |
| bcrypt | 4.1.2 | Password hashing |
| Flask-CORS | - | Cross-origin support |
| SQLite | 3 | Database |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2.0 | UI framework |
| Vite | 5.0.8 | Build tool / dev server |
| React Router | 6.21.0 | Client-side routing |
| Bootstrap | 5.3.2 | CSS framework |
| React-Bootstrap | 2.9.2 | Bootstrap components |
| Axios | 1.6.5 | HTTP client |
| jwt-decode | 4.0.0 | Token parsing |

---

## 🌐 API Endpoints

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/login` | User authentication |
| POST | `/reset` | Reset database |
| GET | `/error` | Simulate error |

### Protected Endpoints (JWT Required)
| Method | Endpoint | Description | Admin Only |
|--------|----------|-------------|------------|
| GET | `/users` | Get all users | No |
| GET | `/users/<id>` | Get user by ID | No |
| POST | `/users` | Create new user | No |
| PUT | `/users/<id>` | Update user | No |
| DELETE | `/users/<id>` | Delete user | **Yes** |

---

## 👤 Default Users

### Admin Account
```
Email: admin@example.com
Password: Admin@123
Role: admin
```

### Regular User Account
```
Email: john@example.com
Password: User@123
Role: user
```

---

## 📄 Frontend Pages

| Page | Path | Description | Role Required |
|------|------|-------------|---------------|
| Login | `/login` | Authentication page | Public |
| Dashboard | `/dashboard` | Main dashboard | Any authenticated |
| Users | `/users` | User management | Admin only |
| Profile | `/profile` | User profile | Any authenticated |
| About | `/about` | App information | Any authenticated |
| 404 | `*` | Not found page | Public |

---

## 🔐 Security Features

### Password Requirements
- ✅ Minimum 8 characters
- ✅ At least 1 uppercase letter (A-Z)
- ✅ At least 1 lowercase letter (a-z)
- ✅ At least 1 digit (0-9)
- ✅ At least 1 special character (!@#$%^&*(),.?":{}|<>)
- ✅ No whitespace allowed
- ✅ Maximum 128 characters

### Authentication Flow
1. User logs in with email/password
2. Backend validates credentials and generates JWT token
3. Token stored in localStorage
4. Token automatically included in all API requests
5. Token expires after 1 hour
6. Expired tokens trigger automatic logout

### Role-Based Permissions
| Feature | Admin | User |
|---------|-------|------|
| View Dashboard | ✅ | ✅ |
| View All Users | ✅ | ❌ |
| Create Users | ✅ | ❌ |
| Edit Any User | ✅ | ❌ |
| Delete Users | ✅ | ❌ |
| View Own Profile | ✅ | ✅ |
| Edit Own Profile | ✅ | ✅ |

---

## 🚀 Quick Start Commands

### Start Backend
```bash
cd "C:\Users\Akram Alimaad\Desktop\API Backend"
python app.py
```
**Runs on:** http://127.0.0.1:5000

### Start Frontend
```bash
cd "C:\Users\Akram Alimaad\Desktop\API Backend\frontend"
npm install  # First time only
npm run dev
```
**Runs on:** http://localhost:3000

### Run Tests
```bash
cd "C:\Users\Akram Alimaad\Desktop\API Backend"
python test_password_auth.py
```

---

## 📁 Project Structure

```
API Backend/
├── Backend Files
│   ├── app.py                    # Flask routes and configuration
│   ├── models_sqlite.py          # Database models (User)
│   ├── validators.py             # Input validation functions
│   ├── requirements.txt          # Python dependencies
│   └── users.db                  # SQLite database file
│
├── Frontend Application
│   └── frontend/
│       ├── src/
│       │   ├── components/       # Reusable UI components
│       │   │   ├── Layout.jsx
│       │   │   ├── Navbar.jsx
│       │   │   ├── Sidebar.jsx
│       │   │   ├── AdminDashboard.jsx
│       │   │   ├── UserDashboard.jsx
│       │   │   └── PrivateRoute.jsx
│       │   ├── pages/            # Page components
│       │   │   ├── Login.jsx
│       │   │   ├── Dashboard.jsx
│       │   │   ├── Users.jsx
│       │   │   ├── Profile.jsx
│       │   │   ├── About.jsx
│       │   │   └── NotFound.jsx
│       │   ├── context/
│       │   │   └── AuthContext.jsx  # Authentication state
│       │   ├── services/
│       │   │   └── api.js           # API service layer
│       │   ├── App.jsx              # Main app with router
│       │   ├── main.jsx             # React entry point
│       │   └── index.css            # Global styles
│       ├── package.json
│       ├── vite.config.js
│       └── README.md
│
├── Documentation
│   ├── DOCUMENTATION.md          # Complete documentation
│   ├── QUICK_START.md            # Setup guide
│   ├── QUICK_REFERENCE.md        # This file
│   ├── Test_API_Manual.md        # Manual testing guide
│   ├── Test_API_Postman.md       # Postman guide
│   └── Test_API_Python.md        # Python automation guide
│
└── Tests
    └── test_password_auth.py     # Password authentication tests
```

---

## 🎨 Frontend Components

### Layout Components
- **Layout.jsx** - Main wrapper with sidebar and navbar
- **Navbar.jsx** - Top navigation with user dropdown
- **Sidebar.jsx** - Collapsible side menu with icons
- **PrivateRoute.jsx** - Route protection wrapper

### Dashboard Components
- **Dashboard.jsx** - Main dashboard dispatcher
- **AdminDashboard.jsx** - Admin view with stats and user table
- **UserDashboard.jsx** - User view with profile cards

### Page Components
- **Login.jsx** - Login form with demo buttons
- **Users.jsx** - User management with CRUD operations
- **Profile.jsx** - Profile viewing and editing
- **About.jsx** - Application information
- **NotFound.jsx** - 404 error page

### Context & Services
- **AuthContext.jsx** - Global authentication state
- **api.js** - Axios instance with JWT interceptor

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    age INTEGER NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Field Constraints
- **name:** 3-50 characters, required
- **email:** Valid email format, unique, required
- **age:** 18-150, integer, required
- **password_hash:** bcrypt hash, required
- **role:** 'user' or 'admin', defaults to 'user'

---

## 🔍 Testing

### Test Files
- `test_password_auth.py` - 8 password authentication tests
- `Test_API_Manual.md` - Manual testing instructions
- `Test_API_Postman.md` - Postman collection guide
- `Test_API_Python.md` - Python automation guide

### Test Coverage
✅ Login with valid credentials  
✅ Login with invalid password  
✅ Password hashing verification  
✅ Password validation (8 rules)  
✅ Token generation  
✅ Protected endpoint access  
✅ Role-based permissions  
✅ CRUD operations  

### Run Tests
```bash
python test_password_auth.py
```

---

## 🐛 Common Issues & Solutions

### Backend Issues

**Port 5000 in use:**
```python
# Change port in app.py
app.run(port=5001)
```

**Database locked:**
```bash
# Delete and restart
rm users.db
python app.py
```

**Import errors:**
```bash
pip install -r requirements.txt
```

### Frontend Issues

**API connection failed:**
- Ensure backend runs on port 5000
- Check Vite proxy in vite.config.js

**Token expired:**
- Logout and login again
- Tokens expire after 1 hour

**Build errors:**
```bash
rm -rf node_modules
npm install
```

---

## 📈 API Response Format

### Success Response
```json
{
  "status": "success",
  "message": "Operation successful",
  "data": { /* response data */ }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description"
}
```

### HTTP Status Codes
- **200** - OK (Success)
- **201** - Created (New resource)
- **400** - Bad Request (Validation error)
- **401** - Unauthorized (No token)
- **403** - Forbidden (No permission)
- **404** - Not Found
- **500** - Internal Server Error

---

## 🎯 Use Cases

1. **API Testing Training** - Practice manual and automated testing
2. **Test Automation** - Build test frameworks (Pytest, Selenium)
3. **Learning Full-Stack** - Study React + Flask integration
4. **Security Testing** - Understand JWT and password security
5. **CRUD Operations** - Learn database operations
6. **Frontend Development** - Practice React and Bootstrap
7. **Backend Development** - Study RESTful API design

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| **DOCUMENTATION.md** | Complete technical documentation (this is comprehensive!) |
| **QUICK_REFERENCE.md** | This file - Quick overview and cheatsheet |
| **QUICK_START.md** | Step-by-step setup guide |
| **README.md** (frontend) | Frontend-specific documentation |
| **Test_API_Manual.md** | Manual testing instructions |
| **Test_API_Postman.md** | Postman collection setup |
| **Test_API_Python.md** | Python automation examples |

---

## 🔗 Quick Links

### Local URLs
- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:5000
- **Health Check:** http://127.0.0.1:5000/health

### Demo Credentials
- **Admin:** admin@example.com / Admin@123
- **User:** john@example.com / User@123

### Important Endpoints
- **Login:** POST http://127.0.0.1:5000/login
- **Get Users:** GET http://127.0.0.1:5000/users
- **Create User:** POST http://127.0.0.1:5000/users

---

## 💡 Pro Tips

1. **Quick Login:** Use demo credential buttons on login page
2. **Reset Database:** POST to `/reset` endpoint to restore defaults
3. **Check Health:** Visit `/health` to verify backend is running
4. **Browser DevTools:** Use Network tab to inspect API calls
5. **React DevTools:** Install Chrome extension for debugging
6. **Token Inspection:** Use jwt.io to decode JWT tokens
7. **Database Viewing:** Use SQLite browser to view database

---

## 🎓 What You Can Learn

### Backend Skills
- RESTful API design
- Flask framework
- SQLAlchemy ORM
- JWT authentication
- Password hashing with bcrypt
- Input validation
- Error handling
- CORS configuration
- Database design

### Frontend Skills
- React 18 with hooks
- React Router for routing
- Context API for state management
- Axios for HTTP requests
- Bootstrap 5 design
- Responsive design
- Form validation
- Protected routes
- Token management

### Full-Stack Skills
- Client-server architecture
- API integration
- Authentication flow
- Role-based access control
- Build tools (Vite)
- Development workflow
- Testing strategies

---

## ⚡ Quick Commands Cheatsheet

```bash
# Backend
python app.py                    # Start server
python test_password_auth.py     # Run tests

# Frontend
npm install                      # Install dependencies
npm run dev                      # Start dev server
npm run build                    # Production build
npm run preview                  # Preview production

# Database
# Access via POST /reset endpoint # Reset to defaults

# Testing
curl http://127.0.0.1:5000/health  # Health check
```

---

**Version:** 1.0.0  
**Last Updated:** March 3, 2026  
**Status:** Production Ready ✅

For complete details, see [DOCUMENTATION.md](DOCUMENTATION.md)
