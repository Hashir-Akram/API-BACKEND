"""
Production-ready Flask application with static file serving
Serves both API and React frontend build files
"""
from flask import Flask, request, send_from_directory
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
app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
app.config.from_object(Config)

# SQLite Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS Configuration - Update with your frontend domain
# For development
CORS(app)
# For production, uncomment and update with your domain:
# CORS(app, resources={r"/*": {"origins": ["https://your-frontend.onrender.com"]}})

# Initialize extensions
jwt = JWTManager(app)

# Initialize database
init_db(app)

# Create user store instance
user_store = UserStore()


# ============================================================================
# STATIC FILE SERVING (For single-service deployment)
# ============================================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """
    Serve React app for routes that don't match API endpoints
    This allows React Router to handle client-side routing
    """
    # Serve API routes normally
    if path.startswith('api/'):
        return error_response(message="API endpoint not found", status_code=404)
    
    # Check if file exists in static folder
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    
    # Otherwise serve index.html for React Router
    return send_from_directory(app.static_folder, 'index.html')


# Note: All your existing API routes go here
# Make sure they are prefixed with /api or handle the routing accordingly
# Example: @app.route('/api/health')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
