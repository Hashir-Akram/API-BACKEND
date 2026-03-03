# API Backend Dashboard - Complete Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Backend Documentation](#backend-documentation)
- [Frontend Documentation](#frontend-documentation)
- [Authentication & Security](#authentication--security)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Setup & Installation](#setup--installation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What is This Application?

The **API Backend Dashboard** is a full-stack web application designed for teaching and practicing API testing and automation. It provides a comprehensive RESTful API backend with a modern React frontend, featuring enterprise-grade security practices including JWT authentication, password hashing, role-based access control, and comprehensive input validation.

### Key Highlights

- ✅ **Complete CRUD Operations** - Create, read, update, and delete users
- ✅ **JWT Authentication** - Secure token-based authentication system
- ✅ **Password Security** - Bcrypt hashing with strong validation rules
- ✅ **Role-Based Access** - Admin and user roles with different permissions
- ✅ **Modern UI** - React 18 with Bootstrap 5 and responsive design
- ✅ **RESTful API** - Well-structured API endpoints following REST principles
- ✅ **Persistent Storage** - SQLite database with thread-safe operations
- ✅ **Comprehensive Testing** - 78+ automated tests
- ✅ **Production Ready** - Error handling, validation, and security best practices

### Use Cases

1. **API Testing Training** - Practice manual and automated API testing
2. **Automation Practice** - Build test automation frameworks
3. **Web Development Learning** - Study full-stack development patterns
4. **Security Testing** - Understand authentication and authorization
5. **Database Operations** - Learn CRUD operations with a real database

---

## System Architecture

### Technology Stack

#### Backend
- **Framework:** Flask 3.0.0 (Python web framework)
- **Database:** SQLite 3 (Lightweight SQL database)
- **ORM:** SQLAlchemy 3.1.1 (Database abstraction layer)
- **Authentication:** Flask-JWT-Extended 4.6.0 (JWT token management)
- **Password Security:** bcrypt 4.1.2 (Password hashing)
- **Validation:** Custom validators with email and password checks
- **CORS:** Flask-CORS (Cross-origin resource sharing)

#### Frontend
- **Framework:** React 18.2.0 (UI library)
- **Build Tool:** Vite 5.0.8 (Fast dev server and bundler)
- **Routing:** React Router DOM 6.21.0 (Client-side routing)
- **UI Library:** Bootstrap 5.3.2 + React-Bootstrap 2.9.2
- **HTTP Client:** Axios 1.6.5 (API communication)
- **State Management:** React Context API (Authentication state)
- **Token Handling:** jwt-decode 4.0.0 (JWT parsing)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                        │
│                     http://localhost:3000                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         │ (with JWT tokens)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    VITE DEV SERVER (Proxy)                   │
│                     http://localhost:3000                    │
│                         /api/* → Port 5000                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Proxied Requests
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK BACKEND API                       │
│                   http://127.0.0.1:5000                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │  │  Validators  │  │     Auth     │     │
│  │  (app.py)    │→ │ (validators) │→ │  (JWT-Ext)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        SQLAlchemy ORM (models_sqlite.py)            │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
└─────────────────┼────────────────────────────────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   users.db       │
         │  (SQLite DB)     │
         └─────────────────┘
```

### Request Flow

1. **User Action** → User interacts with React frontend
2. **API Call** → Axios sends HTTP request with JWT token
3. **Proxy** → Vite proxies request to Flask backend
4. **Authentication** → Flask validates JWT token
5. **Validation** → Input data validated against rules
6. **Database** → SQLAlchemy executes database operations
7. **Response** → JSON response sent back to frontend
8. **UI Update** → React updates the interface

---

## Backend Documentation

### File Structure

```
API Backend/
├── app.py                      # Main Flask application with routes
├── models_sqlite.py            # SQLAlchemy database models
├── validators.py               # Input validation functions
├── requirements.txt            # Python dependencies
├── users.db                    # SQLite database file
├── test_password_auth.py       # Password authentication tests
├── Test_API_Manual.md          # Manual testing guide
├── Test_API_Postman.md         # Postman testing guide
├── Test_API_Python.md          # Python automation guide
└── QUICK_START.md             # Quick setup guide
```

### Core Components

#### 1. **app.py** - Main Application

**Purpose:** Defines all API routes, handles HTTP requests/responses, manages CORS, and JWT configuration.

**Key Features:**
- 9 RESTful endpoints
- JWT token generation and validation
- Error handling with try-catch blocks
- CORS enabled for cross-origin requests
- JSON response formatting

**Configuration:**
```python
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
```

#### 2. **models_sqlite.py** - Database Models

**Purpose:** Defines the User model and database operations using SQLAlchemy ORM.

**User Model Fields:**
- `id` (Integer, Primary Key, Auto-increment)
- `name` (String, Required, Min 3 characters)
- `email` (String, Unique, Required)
- `age` (Integer, Required, Min 18)
- `password_hash` (String, Required, Hashed with bcrypt)
- `role` (String, Default: 'user', Options: 'user'/'admin')
- `created_at` (DateTime, Auto-generated)
- `updated_at` (DateTime, Auto-updated)

**Key Methods:**
- `set_password(password)` - Hash and store password using bcrypt
- `check_password(password)` - Verify password against stored hash
- `to_dict()` - Convert model to dictionary (excludes password_hash)
- `init_db()` - Initialize database tables
- `reset_database()` - Clear and reinitialize database with default users

**Thread Safety:**
- Uses `RLock()` for thread-safe database operations
- Prevents race conditions in concurrent requests

#### 3. **validators.py** - Input Validation

**Purpose:** Validate all user inputs before database operations.

**Validation Rules:**

**Name Validation:**
- Minimum 3 characters
- Maximum 50 characters
- Required field

**Email Validation:**
- Valid email format (regex pattern)
- Required field
- Unique in database

**Age Validation:**
- Minimum 18 years old
- Maximum 150 years old
- Must be integer
- Required field

**Password Validation (8 Rules):**
1. Minimum 8 characters
2. At least one uppercase letter (A-Z)
3. At least one lowercase letter (a-z)
4. At least one digit (0-9)
5. At least one special character (!@#$%^&*(),.?":{}|<>)
6. No whitespace allowed
7. Maximum 128 characters
8. Required field

**Role Validation:**
- Must be either 'user' or 'admin'
- Defaults to 'user' if not provided

### API Endpoints

#### 1. Health Check
```
GET /health
```
**Purpose:** Check if API is running  
**Authentication:** Not required  
**Response:**
```json
{
  "status": "success",
  "message": "API is running",
  "timestamp": "2024-03-03T10:30:00.123456"
}
```

#### 2. User Login
```
POST /login
```
**Purpose:** Authenticate user and receive JWT token  
**Authentication:** Not required  
**Request Body:**
```json
{
  "email": "admin@example.com",
  "password": "Admin@123"
}
```
**Success Response (200):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "name": "Admin User",
      "email": "admin@example.com",
      "age": 30,
      "role": "admin",
      "created_at": "2024-03-03T10:00:00",
      "updated_at": "2024-03-03T10:00:00"
    }
  }
}
```
**Error Response (401):**
```json
{
  "status": "error",
  "message": "Invalid credentials"
}
```

#### 3. Get All Users
```
GET /users
```
**Purpose:** Retrieve list of all users  
**Authentication:** Required (JWT token)  
**Headers:**
```
Authorization: Bearer <token>
```
**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "users": [
      {
        "id": 1,
        "name": "Admin User",
        "email": "admin@example.com",
        "age": 30,
        "role": "admin",
        "created_at": "2024-03-03T10:00:00",
        "updated_at": "2024-03-03T10:00:00"
      },
      {
        "id": 2,
        "name": "John Doe",
        "email": "john@example.com",
        "age": 25,
        "role": "user",
        "created_at": "2024-03-03T10:00:00",
        "updated_at": "2024-03-03T10:00:00"
      }
    ],
    "total": 2
  }
}
```

#### 4. Get User by ID
```
GET /users/<id>
```
**Purpose:** Retrieve specific user details  
**Authentication:** Required (JWT token)  
**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Admin User",
    "email": "admin@example.com",
    "age": 30,
    "role": "admin",
    "created_at": "2024-03-03T10:00:00",
    "updated_at": "2024-03-03T10:00:00"
  }
}
```
**Error Response (404):**
```json
{
  "status": "error",
  "message": "User not found"
}
```

#### 5. Create User
```
POST /users
```
**Purpose:** Create a new user  
**Authentication:** Required (JWT token)  
**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "age": 28,
  "password": "SecurePass@123",
  "role": "user"
}
```
**Success Response (201):**
```json
{
  "status": "success",
  "message": "User created successfully",
  "data": {
    "id": 3,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "age": 28,
    "role": "user",
    "created_at": "2024-03-03T10:30:00",
    "updated_at": "2024-03-03T10:30:00"
  }
}
```
**Validation Error (400):**
```json
{
  "status": "error",
  "message": "Password must be at least 8 characters"
}
```

#### 6. Update User
```
PUT /users/<id>
```
**Purpose:** Update existing user details  
**Authentication:** Required (JWT token)  
**Request Body (all fields optional):**
```json
{
  "name": "Jane Smith Updated",
  "email": "jane.new@example.com",
  "age": 29,
  "password": "NewPassword@456",
  "role": "admin"
}
```
**Success Response (200):**
```json
{
  "status": "success",
  "message": "User updated successfully",
  "data": {
    "id": 3,
    "name": "Jane Smith Updated",
    "email": "jane.new@example.com",
    "age": 29,
    "role": "admin",
    "created_at": "2024-03-03T10:30:00",
    "updated_at": "2024-03-03T11:00:00"
  }
}
```

#### 7. Delete User
```
DELETE /users/<id>
```
**Purpose:** Delete a user (Admin only)  
**Authentication:** Required (JWT token + Admin role)  
**Success Response (200):**
```json
{
  "status": "success",
  "message": "User deleted successfully"
}
```
**Authorization Error (403):**
```json
{
  "status": "error",
  "message": "Admin access required"
}
```

#### 8. Reset Database
```
POST /reset
```
**Purpose:** Clear database and restore default users  
**Authentication:** Not required  
**Success Response (200):**
```json
{
  "status": "success",
  "message": "Database reset successfully"
}
```

#### 9. Simulate Error
```
GET /error
```
**Purpose:** Test error handling  
**Authentication:** Not required  
**Response (500):**
```json
{
  "status": "error",
  "message": "Simulated server error"
}
```

### Default Users

The database comes with two pre-configured users:

**Admin User:**
- Name: Admin User
- Email: admin@example.com
- Password: Admin@123
- Role: admin
- Age: 30

**Regular User:**
- Name: John Doe
- Email: john@example.com
- Password: User@123
- Role: user
- Age: 25

---

## Frontend Documentation

### File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.jsx              # Main layout wrapper
│   │   ├── Navbar.jsx              # Top navigation bar
│   │   ├── Sidebar.jsx             # Side navigation menu
│   │   ├── Sidebar.css             # Sidebar styles
│   │   ├── PrivateRoute.jsx        # Protected route component
│   │   ├── AdminDashboard.jsx      # Admin dashboard view
│   │   └── UserDashboard.jsx       # User dashboard view
│   ├── pages/
│   │   ├── Login.jsx               # Login page
│   │   ├── Login.css               # Login page styles
│   │   ├── Dashboard.jsx           # Main dashboard
│   │   ├── Users.jsx               # User management page
│   │   ├── Profile.jsx             # User profile page
│   │   ├── About.jsx               # About page
│   │   └── NotFound.jsx            # 404 page
│   ├── context/
│   │   └── AuthContext.jsx         # Authentication context
│   ├── services/
│   │   └── api.js                  # Axios API service
│   ├── App.jsx                     # Main app with router
│   ├── main.jsx                    # React entry point
│   └── index.css                   # Global styles
├── package.json                    # Dependencies
├── vite.config.js                  # Vite configuration
├── .eslintrc.cjs                   # ESLint config
├── .gitignore                      # Git ignore rules
├── index.html                      # HTML template
└── README.md                       # Frontend documentation
```

### Core Components

#### 1. **App.jsx** - Application Router

**Purpose:** Defines all routes and navigation structure.

**Routes:**
- `/login` - Public login page
- `/` - Redirects to dashboard
- `/dashboard` - Main dashboard (protected)
- `/users` - User management (protected)
- `/profile` - User profile (protected)
- `/about` - About page (protected)
- `*` - 404 Not Found page

**Route Protection:**
All routes inside `<Layout>` are wrapped with `<PrivateRoute>` requiring authentication.

#### 2. **AuthContext.jsx** - Authentication Management

**Purpose:** Global authentication state management using React Context API.

**State Variables:**
- `user` - Current logged-in user object
- `token` - JWT authentication token
- `loading` - Loading state during initialization

**Functions:**
```javascript
login(email, password)      // Authenticate user
logout()                    // Clear session
updateUser(updatedUser)     // Update user info
isAdmin()                  // Check if user is admin
isAuthenticated            // Boolean auth status
```

**Features:**
- Stores token and user in localStorage
- Automatic token validation on mount
- Token expiration checking
- Automatic logout on expired token

#### 3. **api.js** - HTTP Client

**Purpose:** Centralized API communication using Axios.

**Features:**
- Base URL configuration
- Automatic JWT token injection in headers
- Request/response interceptors
- Error handling
- Token refresh logic

**API Methods:**
```javascript
login(email, password)           // POST /login
getUsers()                       // GET /users
getUserById(id)                  // GET /users/:id
createUser(userData)             // POST /users
updateUser(id, userData)         // PUT /users/:id
deleteUser(id)                   // DELETE /users/:id
getDashboardStats()              // GET /users (for stats)
```

#### 4. **Layout.jsx** - Main Layout

**Purpose:** Provides consistent layout structure for all protected pages.

**Features:**
- Sidebar navigation (collapsible)
- Top navbar with user info
- Content area with `<Outlet>` for child routes
- Responsive design

#### 5. **Navbar.jsx** - Top Navigation

**Purpose:** Display user information and quick actions.

**Features:**
- Logo/brand name
- Sidebar toggle button
- User dropdown menu with:
  - User name and role badge
  - Profile link
  - Logout button

#### 6. **Sidebar.jsx** - Side Navigation

**Purpose:** Main navigation menu with role-based filtering.

**Features:**
- Collapsible sidebar
- Icons for each menu item
- Active route highlighting
- Role-based menu filtering (admin sees more options)

**Menu Items:**
- Dashboard (both roles)
- Users (admin only)
- Profile (both roles)
- About (both roles)

### Pages

#### 1. **Login.jsx** - Authentication Page

**Features:**
- Email and password input fields
- Form validation
- Demo credential buttons for quick login
- Error message display
- Beautiful gradient background
- Responsive design

**Demo Buttons:**
- "Login as Admin" - Auto-fills admin credentials
- "Login as User" - Auto-fills user credentials

#### 2. **Dashboard.jsx** - Main Dashboard

**Purpose:** Role-based dashboard that renders different views.

**Features:**
- Fetches user statistics from API
- Renders `<AdminDashboard>` for admins
- Renders `<UserDashboard>` for regular users
- Loading state spinner
- Error handling

#### 3. **AdminDashboard.jsx** - Admin View

**Features:**

**Statistics Cards:**
- Total Users count
- Admin Users count
- Regular Users count
- System Status

**Quick Actions:**
- Add New User button
- Refresh Data button
- View Reports button

**Recent Users Table:**
- Lists all users with details
- View/Edit/Delete actions
- Role badges
- Pagination ready

#### 4. **UserDashboard.jsx** - User View

**Features:**

**Profile Cards:**
- User information display
- Role badge
- Account creation date

**Statistics:**
- Account age
- Last login info
- Activity summary

**Quick Actions:**
- Edit Profile button
- Change Password button

#### 5. **Users.jsx** - User Management (Admin Only)

**Features:**

**User Table:**
- Displays all users
- Columns: ID, Name, Email, Age, Role, Created At
- Action buttons: Edit, Delete
- Responsive table design

**Add User Modal:**
- Form with all user fields
- Password strength indicator
- Role selection dropdown
- Validation feedback

**Edit User Modal:**
- Pre-filled form with existing data
- Optional password field
- Update button

**Delete Confirmation:**
- Confirmation dialog before deletion
- Prevents accidental deletions

**Permissions:**
- Admin role verification
- Redirects non-admins with warning

#### 6. **Profile.jsx** - User Profile

**Features:**

**View Mode:**
- Display user information
- Edit Profile button
- Info cards with labels

**Edit Mode:**
- Editable form fields
- Optional password change section
- Confirm password field
- Save/Cancel buttons

**Security Card:**
- Password encryption info
- Session expiration notice

**Account Info Card:**
- Member since date
- Last updated timestamp

#### 7. **About.jsx** - Application Info

**Features:**

**Introduction Section:**
- Application overview
- Purpose and use cases
- Key highlights

**Features Grid:**
- 6 feature cards with icons
- JWT Authentication
- SQLite Database
- Input Validation
- User Management
- Password Hashing
- Role-Based Access

**Technology Stack:**
- Backend technologies
- Frontend technologies
- Database info
- Security features

**API Endpoints:**
- Complete endpoint list
- HTTP methods with badges
- Authentication requirements
- Categorized by function

**Version Info:**
- Application version
- Credits and attribution

#### 8. **NotFound.jsx** - 404 Page

**Features:**
- Large "404" display
- Friendly error message
- "Back to Dashboard" button
- Center-aligned design

### Styling

**Global Styles (index.css):**
- CSS variables for colors
- Smooth transitions
- Fade-in animations
- Responsive utilities
- Custom scrollbar

**Component Styles:**
- Bootstrap 5 utility classes
- Custom CSS for Sidebar
- Login page gradient background
- Card shadows and hover effects

**Color Scheme:**
- Primary: #667eea (purple-blue)
- Success: #28a745 (green)
- Danger: #dc3545 (red)
- Warning: #ffc107 (yellow)
- Info: #17a2b8 (cyan)

---

## Authentication & Security

### JWT Authentication Flow

1. **Login Request:**
   - User submits email and password
   - Backend validates credentials
   - Password checked using bcrypt

2. **Token Generation:**
   - Flask-JWT-Extended creates JWT token
   - Token contains user identity (id)
   - Expiration set to 1 hour

3. **Token Storage:**
   - Frontend stores token in localStorage
   - User object stored separately

4. **Authenticated Requests:**
   - Axios interceptor adds token to headers
   - Format: `Authorization: Bearer <token>`

5. **Token Validation:**
   - `@jwt_required()` decorator validates token
   - Expired tokens rejected with 401
   - Invalid tokens rejected with 422

6. **Logout:**
   - Token removed from localStorage
   - User redirected to login page

### Password Security

**Hashing Algorithm:**
- bcrypt with automatic salt generation
- Work factor: 12 (default)
- One-way hashing (cannot be decrypted)

**Storage:**
- Passwords never stored in plain text
- Only password hash stored in database
- Hash is 60 characters long

**Verification:**
- `check_password()` method compares hashes
- Timing-attack resistant
- Returns boolean (True/False)

### Validation Rules

**Password Requirements:**
```python
- Length: 8-128 characters
- Uppercase: A-Z (at least 1)
- Lowercase: a-z (at least 1)
- Digits: 0-9 (at least 1)
- Special: !@#$%^&*(),.?":{}|<> (at least 1)
- No whitespace allowed
```

**Email Validation:**
```python
- Valid email format
- Unique in database
- Case-insensitive comparison
```

**Age Validation:**
```python
- Minimum: 18 years
- Maximum: 150 years
- Integer only
```

### Role-Based Access Control (RBAC)

**Roles:**
- `admin` - Full system access
- `user` - Limited access

**Permissions:**

| Feature | Admin | User |
|---------|-------|------|
| View Dashboard | ✅ | ✅ |
| View All Users | ✅ | ❌ |
| Create User | ✅ | ❌ |
| Edit Any User | ✅ | ❌ |
| Delete User | ✅ | ❌ |
| View Own Profile | ✅ | ✅ |
| Edit Own Profile | ✅ | ✅ |
| Change Own Password | ✅ | ✅ |

**Implementation:**
- Backend: Role checking in endpoints
- Frontend: Conditional rendering based on role
- Sidebar: Menu items filtered by role

### CORS Configuration

```python
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## Database Schema

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

**Indexes:**
- Primary key on `id`
- Unique index on `email`

**Constraints:**
- `name` cannot be null, min 3 chars
- `email` cannot be null, must be unique
- `age` cannot be null, must be >= 18
- `password_hash` cannot be null
- `role` defaults to 'user'

**Triggers:**
- Auto-update `updated_at` on row modification

### Sample Data

```sql
-- Admin User
INSERT INTO users VALUES (
    1,
    'Admin User',
    'admin@example.com',
    30,
    '$2b$12$...',  -- Hash of 'Admin@123'
    'admin',
    '2024-03-03 10:00:00',
    '2024-03-03 10:00:00'
);

-- Regular User
INSERT INTO users VALUES (
    2,
    'John Doe',
    'john@example.com',
    25,
    '$2b$12$...',  -- Hash of 'User@123'
    'user',
    '2024-03-03 10:00:00',
    '2024-03-03 10:00:00'
);
```

---

## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- Git (optional)

### Backend Setup

1. **Navigate to project directory:**
   ```bash
   cd "C:\Users\Akram Alimaad\Desktop\API Backend"
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend:**
   ```bash
   python app.py
   ```

5. **Verify backend is running:**
   - Open: http://127.0.0.1:5000/health
   - Should see: `{"status": "success", "message": "API is running"}`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Access application:**
   - Open: http://localhost:3000
   - Login with demo credentials

### Production Build

```bash
# Frontend
cd frontend
npm run build

# Production files created in: frontend/dist/
# Deploy dist/ folder to web server
```

---

## Testing

### Manual Testing

See [Test_API_Manual.md](Test_API_Manual.md) for detailed manual testing instructions.

**Tools:**
- Web Browser
- Postman or curl
- Database browser (optional)

### Automated Testing

**Test Files:**
- `test_password_auth.py` - Password authentication tests

**Run Tests:**
```bash
python test_password_auth.py
```

**Test Coverage:**
- Login with valid credentials ✅
- Login with invalid password ✅
- Password hashing verification ✅
- Password validation rules ✅
- Token generation ✅
- Protected endpoint access ✅
- Role-based permissions ✅

### Postman Testing

See [Test_API_Postman.md](Test_API_Postman.md) for Postman collection setup.

**Collection Features:**
- Pre-configured requests
- Environment variables
- Token auto-refresh
- Test assertions

---

## Troubleshooting

### Common Issues

#### Backend Issues

**Port Already in Use:**
```
Error: Address already in use
```
**Solution:** Change port in app.py:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Database Locked:**
```
Error: database is locked
```
**Solution:**
```bash
# Delete database and restart
rm users.db
python app.py
```

**Import Error:**
```
Error: No module named 'flask'
```
**Solution:**
```bash
pip install -r requirements.txt
```

#### Frontend Issues

**Dependencies Not Installed:**
```
Error: Cannot find module
```
**Solution:**
```bash
npm install
```

**API Connection Failed:**
```
Error: Network Error
```
**Solution:**
- Verify backend is running on port 5000
- Check Vite proxy configuration
- Inspect browser console for errors

**Token Expired:**
```
Error: 401 Unauthorized
```
**Solution:**
- Logout and login again
- Clear localStorage
- Token expires after 1 hour

**Build Errors:**
```
Error: Build failed
```
**Solution:**
```bash
# Clear cache
rm -rf node_modules
rm package-lock.json
npm install
npm run dev
```

### Debug Tips

**Backend Debugging:**
```python
# Enable debug mode in app.py
app.run(debug=True)

# Add print statements
print(f"User: {user}")

# Check logs in terminal
```

**Frontend Debugging:**
```javascript
// Browser console
console.log('User:', user);

// React DevTools
// Install Chrome extension

// Network tab
// Check API requests/responses
```

---

## Best Practices

### Security Recommendations

1. **Change JWT Secret:** Update `JWT_SECRET_KEY` in production
2. **Use HTTPS:** Enable SSL/TLS in production
3. **Rate Limiting:** Add request rate limiting
4. **Input Sanitization:** Already implemented with validators
5. **Password Policy:** Already enforced with validators
6. **Token Expiration:** Already set to 1 hour
7. **CORS:** Configure allowed origins for production

### Code Quality

1. **Error Handling:** All endpoints have try-catch blocks
2. **Consistent Responses:** Standardized JSON format
3. **Validation:** Comprehensive input validation
4. **Comments:** Code is well-documented
5. **Modularity:** Separated concerns (routes, models, validators)

### Performance

1. **Database Indexing:** Email field is indexed
2. **Token Storage:** localStorage for persistence
3. **Lazy Loading:** Components loaded on demand
4. **Build Optimization:** Vite handles optimization

---

## API Response Format

### Success Response

```json
{
  "status": "success",
  "message": "Operation successful",
  "data": {
    // Response data here
  }
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE"  // Optional
}
```

### HTTP Status Codes

- `200` - OK (Success)
- `201` - Created (New resource)
- `400` - Bad Request (Validation error)
- `401` - Unauthorized (No token or invalid)
- `403` - Forbidden (Insufficient permissions)
- `404` - Not Found (Resource doesn't exist)
- `500` - Internal Server Error (Server error)

---

## License & Credits

**License:** Educational use only

**Purpose:** Teaching API testing and automation

**Author:** Created for educational purposes

**Technologies Used:**
- Flask (BSD License)
- React (MIT License)
- Bootstrap (MIT License)
- SQLAlchemy (MIT License)
- And many other open-source libraries

---

## Support & Resources

### Documentation Files
- `DOCUMENTATION.md` - This file (complete documentation)
- `QUICK_START.md` - Quick setup guide
- `README.md` - Frontend specific docs
- `Test_API_Manual.md` - Manual testing guide
- `Test_API_Postman.md` - Postman guide
- `Test_API_Python.md` - Python automation guide

### Useful Commands

**Backend:**
```bash
# Start server
python app.py

# Reset database
# POST request to /reset endpoint

# Run tests
python test_password_auth.py
```

**Frontend:**
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Changelog

### Version 1.0.0 (Current)

**Features:**
- ✅ Complete CRUD operations
- ✅ JWT authentication
- ✅ Password hashing with bcrypt
- ✅ Role-based access control
- ✅ React frontend with Bootstrap
- ✅ Responsive design
- ✅ Comprehensive validation
- ✅ Error handling
- ✅ Full documentation

**Known Issues:**
- None at this time

**Future Enhancements:**
- Email verification
- Password reset functionality
- Profile picture upload
- Activity logs
- Advanced search/filtering
- Bulk operations
- Export data feature
- Two-factor authentication

---

## Contact & Feedback

For questions, issues, or suggestions, please refer to:
- Application's About page
- This documentation
- Testing guides

---

**End of Documentation**

Last Updated: March 3, 2026
Version: 1.0.0
