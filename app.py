"""
Main Flask application for API Backend
Enterprise-grade RESTful API for teaching and practicing API testing
"""
from flask import Flask, request
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS
from datetime import datetime
import os

from config import Config
from models_sqlite import UserStore, init_db, User
from validators import validate_user_data, validate_login_data, validate_user_id, ValidationError
from responses import success_response, error_response
from auth import jwt_required_custom, admin_required, get_current_user_info

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# SQLite Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
# CORS Configuration - allows frontend to communicate with backend
# For production, update origins list with your deployed frontend URL
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",      # Vite dev server
            "http://localhost:5173",      # Alternative Vite port
            "http://127.0.0.1:5000",      # Local development
            "https://react-frontend-api-testing.onrender.com"
            # Add your production frontend URL here:
            # "https://your-frontend.onrender.com"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
jwt = JWTManager(app)

# Initialize database
init_db(app)

# Create user store instance
user_store = UserStore()


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
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
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
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"]
                }
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


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/users', methods=['POST'])
@jwt_required_custom()
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
        
        # Create user
        new_user = user_store.create_user(validated_data)
        
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
        # Get all users
        users = user_store.get_all_users()
        
        # Apply role filter if provided
        role_filter = request.args.get('role')
        if role_filter:
            role_filter = role_filter.lower()
            if role_filter not in ['admin', 'user']:
                return error_response(
                    message="Invalid role filter. Must be 'admin' or 'user'",
                    error_code="INVALID_FILTER",
                    status_code=400
                )
            users = [u for u in users if u['role'] == role_filter]
        
        return success_response(
            data={
                "users": users,
                "count": len(users)
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
        
        # Update user
        updated_user = user_store.update_user(validated_id, validated_data)
        
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
        
        # Delete user
        deleted_user = user_store.delete_user(validated_id)
        
        if not deleted_user:
            return error_response(
                message=f"User with ID {validated_id} not found",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
        
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
