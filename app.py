"""
Main Flask application for API Backend
Enterprise-grade RESTful API for teaching and practicing API testing
"""
from datetime import datetime, timezone
import os

from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token

from config import Config
from auth import jwt_required_custom, admin_required, get_current_user_info
from models_sqlite import AuditLogStore, CommentStore, Project, ProjectStore, Task, TaskStore, User, UserStore, init_db
from responses import success_response, error_response
from validators import (
    PROJECT_STATUSES,
    TASK_PRIORITIES,
    TASK_STATUSES,
    USER_ROLES,
    ValidationError,
    validate_bulk_task_update,
    validate_comment_data,
    validate_login_data,
    validate_pagination_params,
    validate_project_data,
    validate_task_data,
    validate_user_data,
    validate_user_id,
)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# SQLite Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
def build_cors_origins():
    default_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5000",
        "https://react-frontend-api-testing.vercel.app",
    ]
    configured = os.environ.get("CORS_ORIGINS", "")
    if configured:
        default_origins.extend([origin.strip() for origin in configured.split(",") if origin.strip()])

    origins = []
    for origin in default_origins:
        normalized = origin.rstrip("/")
        if normalized and normalized not in origins:
            origins.append(normalized)
    return origins


CORS(app, resources={
    r"/*": {
        "origins": build_cors_origins(),
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
jwt = JWTManager(app)

# Initialize database
init_db(app)

# Create user store instance
user_store = UserStore()


def log_action(entity_type, action, actor_id=None, entity_id=None, details=None):
    try:
        AuditLogStore.create_log(
            entity_type=entity_type,
            action=action,
            actor_id=actor_id,
            entity_id=entity_id,
            details=details,
        )
    except Exception as exc:
        app.logger.warning(f"Audit log skipped: {exc}")


def is_admin(current_user):
    return current_user.get("role") == "admin"


def can_manage_user(current_user, target_user_id):
    return is_admin(current_user) or current_user.get("user_id") == target_user_id


def can_manage_project(current_user, project):
    return is_admin(current_user) or current_user.get("user_id") == project.owner_id


def can_edit_task(current_user, task):
    return is_admin(current_user) or current_user.get("user_id") == task.created_by


def can_change_task_status(current_user, task):
    return can_edit_task(current_user, task) or current_user.get("user_id") == task.assigned_to


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return error_response(
        message="The requested resource was not found",
        error_code="NOT_FOUND",
        status_code=404
    )


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return error_response(
        message=f"Method {request.method} not allowed for this endpoint",
        error_code="METHOD_NOT_ALLOWED",
        status_code=405
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return error_response(
        message="Internal server error occurred",
        error_code="INTERNAL_SERVER_ERROR",
        status_code=500
    )


# ============================================================================
# JWT ERROR HANDLERS
# ============================================================================

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Handle expired JWT tokens"""
    return error_response(
        message="Token has expired. Please login again.",
        error_code="TOKEN_EXPIRED",
        status_code=401
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Handle invalid JWT tokens"""
    return error_response(
        message="Invalid token. Please provide a valid authentication token.",
        error_code="INVALID_TOKEN",
        status_code=401
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    """Handle missing JWT tokens"""
    return error_response(
        message="Authorization token is missing. Please include a valid token in the request.",
        error_code="MISSING_TOKEN",
        status_code=401
    )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response(
        data={
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "features": [
                "authentication",
                "user-management",
                "projects",
                "tasks",
                "comments",
                "analytics",
                "audit-logs"
            ]
        },
        message="API is running successfully"
    )


@app.route('/error', methods=['GET'])
def simulate_error():
    """Endpoint to simulate internal server error for testing"""
    raise Exception("Simulated internal server error for testing purposes")


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/register', methods=['POST'])
def register():
    """Register a standard user account."""
    try:
        data = request.get_json()

        if not data:
            return error_response(
                message="Request body is required",
                error_code="MISSING_BODY",
                status_code=400
            )

        validated_data = validate_user_data(data, is_update=False)
        validated_data['role'] = 'user'

        if user_store.email_exists(validated_data['email']):
            return error_response(
                message="Email already exists. Please use a different email.",
                error_code="DUPLICATE_EMAIL",
                status_code=409
            )

        new_user = user_store.create_user(validated_data)
        log_action('user', 'registered', entity_id=new_user['id'], details={'email': new_user['email']})

        return success_response(
            data=new_user,
            message="Registration successful",
            status_code=201
        )

    except ValidationError as e:
        return error_response(
            message=e.message,
            error_code=e.error_code,
            status_code=400
        )
    except Exception as e:
        app.logger.error(f"Register error: {str(e)}")
        return error_response(
            message="An error occurred during registration",
            error_code="REGISTER_ERROR",
            status_code=500
        )

@app.route('/login', methods=['POST'])
def login():
    """
    Login endpoint - Generates JWT token
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "your_password"
        }
    
    Response:
        {
            "status": "success",
            "data": {
                "token": "jwt_token_here",
                "user": {...}
            },
            "message": "Login successful"
        }
    """
    try:
        # Get and validate request data
        data = request.get_json()
        
        if not data:
            return error_response(
                message="Request body is required",
                error_code="MISSING_BODY",
                status_code=400
            )
        
        # Validate login data (email and password)
        validated_data = validate_login_data(data)
        email = validated_data["email"]
        password = validated_data["password"]
        
        # Find user object by email (need object to verify password)
        user_obj = user_store.get_user_object_by_email(email)
        
        if not user_obj:
            return error_response(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS",
                status_code=401
            )
        
        # Verify password
        if not user_obj.check_password(password):
            return error_response(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS",
                status_code=401
            )
        
        # Get user dict for response
        user = user_obj.to_dict()
        
        # Create JWT token with user information
        # Using user_id as the identity (simpler approach)
        identity = str(user["id"])
        
        additional_claims = {
            "role": user["role"],
            "email": user["email"]
        }
        
        access_token = create_access_token(
            identity=identity,
            additional_claims=additional_claims
        )
        
        # Return success response
        return success_response(
            data={
                "token": access_token,
                "user": user
            },
            message="Login successful"
        )
    
    except ValidationError as e:
        return error_response(
            message=e.message,
            error_code=e.error_code,
            status_code=400
        )
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return error_response(
            message="An error occurred during login",
            error_code="LOGIN_ERROR",
            status_code=500
        )


@app.route('/me', methods=['GET'])
@jwt_required_custom()
def get_me():
    """Return the currently authenticated user profile."""
    try:
        current_user = get_current_user_info()
        user = user_store.get_user_by_id(current_user['user_id'])

        if not user:
            return error_response(
                message="Authenticated user not found",
                error_code="USER_NOT_FOUND",
                status_code=404
            )

        return success_response(
            data=user,
            message="Profile retrieved successfully"
        )
    except Exception as e:
        app.logger.error(f"Get profile error: {str(e)}")
        return error_response(
            message="An error occurred while retrieving the profile",
            error_code="GET_PROFILE_ERROR",
            status_code=500
        )


@app.route('/me', methods=['PUT'])
@jwt_required_custom()
def update_me():
    """Update the current user's profile without allowing role changes."""
    try:
        current_user = get_current_user_info()
        data = request.get_json()

        if not data:
            return error_response(
                message="Request body is required",
                error_code="MISSING_BODY",
                status_code=400
            )

        validated_data = validate_user_data(data, is_update=True)
        validated_data.pop('role', None)

        if 'email' in validated_data and user_store.email_exists(validated_data['email'], exclude_user_id=current_user['user_id']):
            return error_response(
                message="Email already exists. Please use a different email.",
                error_code="DUPLICATE_EMAIL",
                status_code=409
            )

        updated_user = user_store.update_user(current_user['user_id'], validated_data)
        log_action('user', 'self_updated', actor_id=current_user['user_id'], entity_id=current_user['user_id'], details={'fields': list(validated_data.keys())})

        return success_response(
            data=updated_user,
            message="Profile updated successfully"
        )
    except ValidationError as e:
        return error_response(
            message=e.message,
            error_code=e.error_code,
            status_code=400
        )
    except Exception as e:
        app.logger.error(f"Update profile error: {str(e)}")
        return error_response(
            message="An error occurred while updating the profile",
            error_code="UPDATE_PROFILE_ERROR",
            status_code=500
        )


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/users', methods=['POST'])
@jwt_required_custom()
@admin_required()
def create_user():
    """
    Create a new user
    
    Request Body:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 25,
            "role": "user"  // optional, defaults to "user"
        }
    
    Response:
        {
            "status": "success",
            "data": {...user object...},
            "message": "User created successfully"
        }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return error_response(
                message="Request body is required",
                error_code="MISSING_BODY",
                status_code=400
            )
        
        # Validate user data
        validated_data = validate_user_data(data, is_update=False)
        
        # Check if email already exists
        if user_store.email_exists(validated_data["email"]):
            return error_response(
                message="Email already exists. Please use a different email.",
                error_code="DUPLICATE_EMAIL",
                status_code=409
            )
        
        current_user = get_current_user_info()

        # Create user
        new_user = user_store.create_user(validated_data)

        log_action('user', 'created', actor_id=current_user['user_id'], entity_id=new_user['id'], details={
            'email': new_user['email'],
            'role': new_user['role']
        })
        
        return success_response(
            data=new_user,
            message="User created successfully",
            status_code=201
        )
    
    except ValidationError as e:
        return error_response(
            message=e.message,
            error_code=e.error_code,
            status_code=400
        )
    except Exception as e:
        app.logger.error(f"Create user error: {str(e)}")
        return error_response(
            message="An error occurred while creating the user",
            error_code="CREATE_USER_ERROR",
            status_code=500
        )


@app.route('/users', methods=['GET'])
@jwt_required_custom()
@admin_required()
def get_all_users():
    """
    Get all users
    
    Query Parameters:
        role: Filter by role (optional)
    
    Response:
        {
            "status": "success",
            "data": [...array of users...],
            "message": "Users retrieved successfully"
        }
    """
    try:
        filters = validate_pagination_params(
            request.args,
            allowed_sort_fields=['name', 'email', 'created_at', 'updated_at', 'age'],
            default_sort_by='created_at'
        )

        role_filter = request.args.get('role')
        if role_filter:
            role_filter = role_filter.lower()
            if role_filter not in USER_ROLES:
                return error_response(
                    message="Invalid role filter. Must be 'admin' or 'user'",
                    error_code="INVALID_FILTER",
                    status_code=400
                )
            filters['role'] = role_filter

        users, pagination = user_store.list_users(filters)
        
        return success_response(
            data={
                "users": users,
                "count": len(users),
                "pagination": pagination
            },
            message=f"Retrieved {len(users)} user(s) successfully"
        )
    
    except Exception as e:
        app.logger.error(f"Get users error: {str(e)}")
        return error_response(
            message="An error occurred while retrieving users",
            error_code="GET_USERS_ERROR",
            status_code=500
        )


@app.route('/users/<user_id>', methods=['GET'])
@jwt_required_custom()
def get_user_by_id(user_id):
    """
    Get a specific user by ID
    
    Response:
        {
            "status": "success",
            "data": {...user object...},
            "message": "User retrieved successfully"
        }
    """
    try:
        # Validate user ID
        validated_id = validate_user_id(user_id)
        
        current_user = get_current_user_info()
        if not can_manage_user(current_user, validated_id):
            return error_response(
                message="You can only view your own user record unless you are an admin.",
                error_code="FORBIDDEN",
                status_code=403
            )

        # Get user
        user = user_store.get_user_by_id(validated_id)
        
        if not user:
            return error_response(
                message=f"User with ID {validated_id} not found",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
        
        return success_response(
            data=user,
            message="User retrieved successfully"
        )
    
    except ValidationError as e:
        return error_response(
            message=e.message,
            error_code=e.error_code,
            status_code=400
        )
    except Exception as e:
        app.logger.error(f"Get user error: {str(e)}")
        return error_response(
            message="An error occurred while retrieving the user",
            error_code="GET_USER_ERROR",
            status_code=500
        )


@app.route('/users/<user_id>', methods=['PUT'])
@jwt_required_custom()
@admin_required()
def update_user(user_id):
    """
    Update an existing user
    
    Request Body (all fields optional):
        {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "age": 30,
            "role": "admin"
        }
    
    Response:
        {
            "status": "success",
            "data": {...updated user object...},
            "message": "User updated successfully"
        }
    """
    try:
        # Validate user ID
        validated_id = validate_user_id(user_id)
        
        # Check if user exists
        existing_user = user_store.get_user_by_id(validated_id)
        if not existing_user:
            return error_response(
                message=f"User with ID {validated_id} not found",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
        
        # Get request data
        data = request.get_json()
        
        if not data:
            return error_response(
                message="Request body is required",
                error_code="MISSING_BODY",
                status_code=400
            )
        
        # Validate user data for update
        validated_data = validate_user_data(data, is_update=True)
        
        # Check if email is being updated and if it already exists
        if "email" in validated_data:
            if user_store.email_exists(validated_data["email"], exclude_user_id=validated_id):
                return error_response(
                    message="Email already exists. Please use a different email.",
                    error_code="DUPLICATE_EMAIL",
                    status_code=409
                )
        
        current_user = get_current_user_info()

        # Update user
        updated_user = user_store.update_user(validated_id, validated_data)

        log_action('user', 'updated', actor_id=current_user['user_id'], entity_id=validated_id, details={
            'fields': list(validated_data.keys())
        })
        
        return success_response(
            data=updated_user,
            message="User updated successfully"
        )
    
    except ValidationError as e:
        return error_response(
            message=e.message,
            error_code=e.error_code,
            status_code=400
        )
    except Exception as e:
        app.logger.error(f"Update user error: {str(e)}")
        return error_response(
            message="An error occurred while updating the user",
            error_code="UPDATE_USER_ERROR",
            status_code=500
        )


@app.route('/users/<user_id>', methods=['DELETE'])
@jwt_required_custom()
@admin_required()
def delete_user(user_id):
    """
    Delete a user (Admin only)
    
    Response:
        {
            "status": "success",
            "data": {...deleted user object...},
            "message": "User deleted successfully"
        }
    """
    try:
        # Validate user ID
        validated_id = validate_user_id(user_id)
        
        current_user = get_current_user_info()

        # Delete user
        deleted_user = user_store.delete_user(validated_id)
        
        if not deleted_user:
            return error_response(
                message=f"User with ID {validated_id} not found",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
        
        log_action('user', 'deleted', actor_id=current_user['user_id'], entity_id=validated_id, details={
            'email': deleted_user['email']
        })

        return success_response(
            data=deleted_user,
            message="User deleted successfully"
        )
    
    except ValidationError as e:
        return error_response(
            message=e.message,
            error_code=e.error_code,
            status_code=400
        )
    except Exception as e:
        app.logger.error(f"Delete user error: {str(e)}")
        return error_response(
            message="An error occurred while deleting the user",
            error_code="DELETE_USER_ERROR",
            status_code=500
        )


# ============================================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/projects', methods=['GET'])
@jwt_required_custom()
def get_projects():
    """Get projects with pagination, search, sorting, and status filters."""
    try:
        filters = validate_pagination_params(
            request.args,
            allowed_sort_fields=['title', 'status', 'created_at', 'updated_at'],
            default_sort_by='updated_at'
        )

        status = request.args.get('status')
        owner_id = request.args.get('owner_id')

        if status:
            status = status.strip().lower()
            if status not in PROJECT_STATUSES:
                return error_response(
                    message='Invalid project status filter',
                    error_code='INVALID_STATUS',
                    status_code=400
                )
            filters['status'] = status

        if owner_id:
            filters['owner_id'] = validate_user_id(owner_id)

        projects, pagination = ProjectStore.list_projects(filters)
        return success_response(
            data={
                'projects': projects,
                'count': len(projects),
                'pagination': pagination
            },
            message='Projects retrieved successfully'
        )
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Get projects error: {str(e)}")
        return error_response('An error occurred while retrieving projects', 'GET_PROJECTS_ERROR', 500)


@app.route('/projects', methods=['POST'])
@jwt_required_custom()
def create_project():
    """Create a project owned by the authenticated user."""
    try:
        current_user = get_current_user_info()
        data = request.get_json()

        if not data:
            return error_response('Request body is required', 'MISSING_BODY', 400)

        validated_data = validate_project_data(data, is_update=False)
        validated_data['owner_id'] = current_user['user_id']

        project = ProjectStore.create_project(validated_data)
        log_action('project', 'created', actor_id=current_user['user_id'], entity_id=project['id'], details={'title': project['title']})

        return success_response(data=project, message='Project created successfully', status_code=201)
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Create project error: {str(e)}")
        return error_response('An error occurred while creating the project', 'CREATE_PROJECT_ERROR', 500)


@app.route('/projects/<project_id>', methods=['GET'])
@jwt_required_custom()
def get_project_by_id(project_id):
    try:
        validated_id = validate_user_id(project_id)
        project = ProjectStore.get_project_by_id(validated_id)

        if not project:
            return error_response('Project not found', 'PROJECT_NOT_FOUND', 404)

        return success_response(data=project, message='Project retrieved successfully')
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Get project error: {str(e)}")
        return error_response('An error occurred while retrieving the project', 'GET_PROJECT_ERROR', 500)


@app.route('/projects/<project_id>', methods=['PUT'])
@jwt_required_custom()
def update_project(project_id):
    try:
        validated_id = validate_user_id(project_id)
        current_user = get_current_user_info()
        project = ProjectStore.get_project_object(validated_id)

        if not project:
            return error_response('Project not found', 'PROJECT_NOT_FOUND', 404)

        if not can_manage_project(current_user, project):
            return error_response('Only the owner or an admin can update this project.', 'FORBIDDEN', 403)

        data = request.get_json()
        if not data:
            return error_response('Request body is required', 'MISSING_BODY', 400)

        validated_data = validate_project_data(data, is_update=True)
        if not is_admin(current_user):
            validated_data.pop('owner_id', None)

        updated_project = ProjectStore.update_project(project, validated_data)
        log_action('project', 'updated', actor_id=current_user['user_id'], entity_id=validated_id, details={'fields': list(validated_data.keys())})

        return success_response(data=updated_project, message='Project updated successfully')
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Update project error: {str(e)}")
        return error_response('An error occurred while updating the project', 'UPDATE_PROJECT_ERROR', 500)


@app.route('/projects/<project_id>', methods=['DELETE'])
@jwt_required_custom()
def delete_project(project_id):
    try:
        validated_id = validate_user_id(project_id)
        current_user = get_current_user_info()
        project = ProjectStore.get_project_object(validated_id)

        if not project:
            return error_response('Project not found', 'PROJECT_NOT_FOUND', 404)

        if not can_manage_project(current_user, project):
            return error_response('Only the owner or an admin can delete this project.', 'FORBIDDEN', 403)

        deleted_project = ProjectStore.delete_project(project)
        log_action('project', 'deleted', actor_id=current_user['user_id'], entity_id=validated_id, details={'title': deleted_project['title']})
        return success_response(data=deleted_project, message='Project deleted successfully')
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Delete project error: {str(e)}")
        return error_response('An error occurred while deleting the project', 'DELETE_PROJECT_ERROR', 500)


@app.route('/projects/<project_id>/archive', methods=['PATCH'])
@jwt_required_custom()
def archive_project(project_id):
    try:
        validated_id = validate_user_id(project_id)
        current_user = get_current_user_info()
        project = ProjectStore.get_project_object(validated_id)

        if not project:
            return error_response('Project not found', 'PROJECT_NOT_FOUND', 404)

        if not can_manage_project(current_user, project):
            return error_response('Only the owner or an admin can archive this project.', 'FORBIDDEN', 403)

        updated_project = ProjectStore.update_project(project, {'status': 'archived'})
        log_action('project', 'archived', actor_id=current_user['user_id'], entity_id=validated_id, details={'title': updated_project['title']})
        return success_response(data=updated_project, message='Project archived successfully')
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Archive project error: {str(e)}")
        return error_response('An error occurred while archiving the project', 'ARCHIVE_PROJECT_ERROR', 500)


# ============================================================================
# TASK MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/tasks', methods=['GET'])
@jwt_required_custom()
def get_tasks():
    """Get tasks with pagination, search, sorting, and multiple filters."""
    try:
        filters = validate_pagination_params(
            request.args,
            allowed_sort_fields=['title', 'status', 'priority', 'created_at', 'updated_at', 'due_date'],
            default_sort_by='updated_at'
        )

        for field in ['project_id', 'assigned_to', 'created_by']:
            value = request.args.get(field)
            if value:
                filters[field] = validate_user_id(value)

        status = request.args.get('status')
        priority = request.args.get('priority')
        overdue = request.args.get('overdue')

        if status:
            status = status.strip().lower()
            if status not in TASK_STATUSES:
                return error_response('Invalid task status filter', 'INVALID_STATUS', 400)
            filters['status'] = status

        if priority:
            priority = priority.strip().lower()
            if priority not in TASK_PRIORITIES:
                return error_response('Invalid task priority filter', 'INVALID_PRIORITY', 400)
            filters['priority'] = priority

        if overdue:
            filters['overdue'] = overdue.strip().lower() in ['1', 'true', 'yes']

        tasks, pagination = TaskStore.list_tasks(filters)
        return success_response(
            data={
                'tasks': tasks,
                'count': len(tasks),
                'pagination': pagination
            },
            message='Tasks retrieved successfully'
        )
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Get tasks error: {str(e)}")
        return error_response('An error occurred while retrieving tasks', 'GET_TASKS_ERROR', 500)


@app.route('/tasks', methods=['POST'])
@jwt_required_custom()
def create_task():
    try:
        current_user = get_current_user_info()
        data = request.get_json()

        if not data:
            return error_response('Request body is required', 'MISSING_BODY', 400)

        validated_data = validate_task_data(data, is_update=False)
        if not ProjectStore.get_project_object(validated_data['project_id']):
            return error_response('Associated project not found', 'PROJECT_NOT_FOUND', 404)

        validated_data['created_by'] = current_user['user_id']
        task = TaskStore.create_task(validated_data)
        log_action('task', 'created', actor_id=current_user['user_id'], entity_id=task['id'], details={'title': task['title'], 'project_id': task['project_id']})

        return success_response(data=task, message='Task created successfully', status_code=201)
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Create task error: {str(e)}")
        return error_response('An error occurred while creating the task', 'CREATE_TASK_ERROR', 500)


@app.route('/tasks/<task_id>', methods=['GET'])
@jwt_required_custom()
def get_task_by_id(task_id):
    try:
        validated_id = validate_user_id(task_id)
        task = TaskStore.get_task_by_id(validated_id)
        if not task:
            return error_response('Task not found', 'TASK_NOT_FOUND', 404)
        return success_response(data=task, message='Task retrieved successfully')
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Get task error: {str(e)}")
        return error_response('An error occurred while retrieving the task', 'GET_TASK_ERROR', 500)


@app.route('/tasks/<task_id>', methods=['PUT'])
@jwt_required_custom()
def update_task(task_id):
    try:
        validated_id = validate_user_id(task_id)
        current_user = get_current_user_info()
        task = TaskStore.get_task_object(validated_id)

        if not task:
            return error_response('Task not found', 'TASK_NOT_FOUND', 404)

        if not can_edit_task(current_user, task):
            return error_response('Only the creator or an admin can update full task details.', 'FORBIDDEN', 403)

        data = request.get_json()
        if not data:
            return error_response('Request body is required', 'MISSING_BODY', 400)

        validated_data = validate_task_data(data, is_update=True)
        if 'project_id' in validated_data and not ProjectStore.get_project_object(validated_data['project_id']):
            return error_response('Associated project not found', 'PROJECT_NOT_FOUND', 404)

        updated_task = TaskStore.update_task(task, validated_data)
        log_action('task', 'updated', actor_id=current_user['user_id'], entity_id=validated_id, details={'fields': list(validated_data.keys())})
        return success_response(data=updated_task, message='Task updated successfully')
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Update task error: {str(e)}")
        return error_response('An error occurred while updating the task', 'UPDATE_TASK_ERROR', 500)


@app.route('/tasks/<task_id>/status', methods=['PATCH'])
@jwt_required_custom()
def update_task_status(task_id):
    try:
        validated_id = validate_user_id(task_id)
        current_user = get_current_user_info()
        task = TaskStore.get_task_object(validated_id)

        if not task:
            return error_response('Task not found', 'TASK_NOT_FOUND', 404)

        if not can_change_task_status(current_user, task):
            return error_response('Only the assignee, creator, or an admin can change task status.', 'FORBIDDEN', 403)

        data = request.get_json()
        if not data:
            return error_response('Request body is required', 'MISSING_BODY', 400)

        validated_data = validate_task_data(data, is_update=True, allow_partial_status_only=True)
        allowed_fields = {'status', 'priority'}
        if not validated_data or any(field not in allowed_fields for field in validated_data):
            return error_response('Only status and priority can be updated from this endpoint.', 'INVALID_STATUS_UPDATE', 400)

        updated_task = TaskStore.update_task(task, validated_data)
        log_action('task', 'status_updated', actor_id=current_user['user_id'], entity_id=validated_id, details=validated_data)
        return success_response(data=updated_task, message='Task status updated successfully')
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Update task status error: {str(e)}")
        return error_response('An error occurred while updating task status', 'UPDATE_TASK_STATUS_ERROR', 500)


@app.route('/tasks/bulk-update', methods=['PATCH'])
@jwt_required_custom()
@admin_required()
def bulk_update_tasks():
    try:
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 'MISSING_BODY', 400)

        validated = validate_bulk_task_update(data)
        updated_tasks = []
        for task_id in validated['task_ids']:
            task = TaskStore.get_task_object(task_id)
            if task:
                updated_tasks.append(TaskStore.update_task(task, validated['updates']))

        current_user = get_current_user_info()
        log_action('task', 'bulk_updated', actor_id=current_user['user_id'], details={
            'task_ids': validated['task_ids'],
            'updates': validated['updates']
        })

        return success_response(
            data={'tasks': updated_tasks, 'count': len(updated_tasks)},
            message='Tasks updated successfully'
        )
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Bulk update tasks error: {str(e)}")
        return error_response('An error occurred while bulk updating tasks', 'BULK_UPDATE_TASKS_ERROR', 500)


@app.route('/tasks/<task_id>', methods=['DELETE'])
@jwt_required_custom()
def delete_task(task_id):
    try:
        validated_id = validate_user_id(task_id)
        current_user = get_current_user_info()
        task = TaskStore.get_task_object(validated_id)

        if not task:
            return error_response('Task not found', 'TASK_NOT_FOUND', 404)

        if not can_edit_task(current_user, task):
            return error_response('Only the creator or an admin can delete a task.', 'FORBIDDEN', 403)

        deleted_task = TaskStore.delete_task(task)
        log_action('task', 'deleted', actor_id=current_user['user_id'], entity_id=validated_id, details={'title': deleted_task['title']})
        return success_response(data=deleted_task, message='Task deleted successfully')
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Delete task error: {str(e)}")
        return error_response('An error occurred while deleting the task', 'DELETE_TASK_ERROR', 500)


# ============================================================================
# COMMENT, ANALYTICS, AND AUDIT ENDPOINTS
# ============================================================================

@app.route('/tasks/<task_id>/comments', methods=['GET'])
@jwt_required_custom()
def get_task_comments(task_id):
    try:
        validated_id = validate_user_id(task_id)
        task = TaskStore.get_task_object(validated_id)

        if not task:
            return error_response('Task not found', 'TASK_NOT_FOUND', 404)

        comments = CommentStore.list_comments(validated_id)
        return success_response(
            data={'comments': comments, 'count': len(comments)},
            message='Comments retrieved successfully'
        )
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Get comments error: {str(e)}")
        return error_response('An error occurred while retrieving comments', 'GET_COMMENTS_ERROR', 500)


@app.route('/tasks/<task_id>/comments', methods=['POST'])
@jwt_required_custom()
def create_task_comment(task_id):
    try:
        validated_task_id = validate_user_id(task_id)
        current_user = get_current_user_info()
        task = TaskStore.get_task_object(validated_task_id)

        if not task:
            return error_response('Task not found', 'TASK_NOT_FOUND', 404)

        data = request.get_json()
        if not data:
            return error_response('Request body is required', 'MISSING_BODY', 400)

        validated_comment = validate_comment_data(data)
        comment = CommentStore.create_comment({
            'task_id': validated_task_id,
            'author_id': current_user['user_id'],
            'content': validated_comment['content']
        })
        log_action('comment', 'created', actor_id=current_user['user_id'], entity_id=comment['id'], details={'task_id': validated_task_id})

        return success_response(data=comment, message='Comment created successfully', status_code=201)
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Create comment error: {str(e)}")
        return error_response('An error occurred while creating the comment', 'CREATE_COMMENT_ERROR', 500)


@app.route('/comments/<comment_id>', methods=['DELETE'])
@jwt_required_custom()
def delete_comment(comment_id):
    try:
        validated_id = validate_user_id(comment_id)
        current_user = get_current_user_info()
        comment = CommentStore.get_comment_object(validated_id)

        if not comment:
            return error_response('Comment not found', 'COMMENT_NOT_FOUND', 404)

        if not (is_admin(current_user) or comment.author_id == current_user['user_id']):
            return error_response('Only the author or an admin can delete this comment.', 'FORBIDDEN', 403)

        deleted_comment = CommentStore.delete_comment(comment)
        log_action('comment', 'deleted', actor_id=current_user['user_id'], entity_id=validated_id, details={'task_id': deleted_comment['task_id']})

        return success_response(data=deleted_comment, message='Comment deleted successfully')
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Delete comment error: {str(e)}")
        return error_response('An error occurred while deleting the comment', 'DELETE_COMMENT_ERROR', 500)


@app.route('/analytics/summary', methods=['GET'])
@jwt_required_custom()
def get_analytics_summary():
    try:
        current_user = get_current_user_info()

        if is_admin(current_user):
            users = User.query.all()
            projects = Project.query.order_by(Project.updated_at.desc()).limit(5).all()
            tasks = Task.query.order_by(Task.updated_at.desc()).limit(6).all()
            logs, _ = AuditLogStore.list_logs({'page': 1, 'per_page': 10})

            summary = {
                'users': {
                    'total': len(users),
                    'admins': len([user for user in users if user.role == 'admin']),
                    'regular': len([user for user in users if user.role == 'user'])
                },
                'projects': {
                    'total': Project.query.count(),
                    'active': Project.query.filter_by(status='active').count(),
                    'archived': Project.query.filter_by(status='archived').count(),
                    'recent': [project.to_dict() for project in projects]
                },
                'tasks': {
                    'total': Task.query.count(),
                    'todo': Task.query.filter_by(status='todo').count(),
                    'in_progress': Task.query.filter_by(status='in_progress').count(),
                    'done': Task.query.filter_by(status='done').count(),
                    'blocked': Task.query.filter_by(status='blocked').count(),
                    'critical': Task.query.filter_by(priority='critical').count(),
                    'recent': [task.to_dict() for task in tasks]
                },
                'audit_logs': logs[:5]
            }
        else:
            my_user = user_store.get_user_by_id(current_user['user_id'])
            owned_projects = Project.query.filter_by(owner_id=current_user['user_id']).order_by(Project.updated_at.desc()).all()
            assigned_tasks = Task.query.filter_by(assigned_to=current_user['user_id']).order_by(Task.updated_at.desc()).all()
            created_tasks = Task.query.filter_by(created_by=current_user['user_id']).order_by(Task.updated_at.desc()).all()

            summary = {
                'profile': my_user,
                'projects': {
                    'owned': len(owned_projects),
                    'recent': [project.to_dict() for project in owned_projects[:5]]
                },
                'tasks': {
                    'assigned': len(assigned_tasks),
                    'created': len(created_tasks),
                    'todo': len([task for task in assigned_tasks if task.status == 'todo']),
                    'in_progress': len([task for task in assigned_tasks if task.status == 'in_progress']),
                    'done': len([task for task in assigned_tasks if task.status == 'done']),
                    'recent': [task.to_dict() for task in assigned_tasks[:6]]
                }
            }

        return success_response(data=summary, message='Analytics retrieved successfully')
    except Exception as e:
        app.logger.error(f"Analytics error: {str(e)}")
        return error_response('An error occurred while retrieving analytics', 'ANALYTICS_ERROR', 500)


@app.route('/audit-logs', methods=['GET'])
@jwt_required_custom()
@admin_required()
def get_audit_logs():
    try:
        filters = validate_pagination_params(request.args, allowed_sort_fields=['created_at'], default_sort_by='created_at')
        filters['entity_type'] = request.args.get('entity_type', '').strip() or None
        filters['action'] = request.args.get('action', '').strip() or None

        actor_id = request.args.get('actor_id')
        if actor_id:
            filters['actor_id'] = validate_user_id(actor_id)

        logs, pagination = AuditLogStore.list_logs(filters)
        return success_response(
            data={'logs': logs, 'count': len(logs), 'pagination': pagination},
            message='Audit logs retrieved successfully'
        )
    except ValidationError as e:
        return error_response(e.message, e.error_code, 400)
    except Exception as e:
        app.logger.error(f"Audit log error: {str(e)}")
        return error_response('An error occurred while retrieving audit logs', 'AUDIT_LOGS_ERROR', 500)


# ============================================================================
# RESET ENDPOINT (FOR TESTING)
# ============================================================================

@app.route('/reset', methods=['POST'])
def reset_data():
    """
    Reset the data store to initial state (for testing purposes)
    
    Response:
        {
            "status": "success",
            "message": "Data store reset successfully"
        }
    """
    try:
        user_store.reset()
        return success_response(
            message="Data store reset to initial state successfully"
        )
    except Exception as e:
        app.logger.error(f"Reset error: {str(e)}")
        return error_response(
            message="An error occurred while resetting the data store",
            error_code="RESET_ERROR",
            status_code=500
        )


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("API Backend Server Starting...")
    print("="*60)
    print(f"Environment: Development")
    print(f"Server: http://127.0.0.1:5000")
    print(f"Health Check: http://127.0.0.1:5000/health")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
