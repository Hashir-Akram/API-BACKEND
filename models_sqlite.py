"""
SQLite database models and operations using SQLAlchemy
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    """User model for SQLite database"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set the password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against the hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user object to dictionary (excluding password)"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class UserStore:
    """User store operations using SQLAlchemy"""
    
    @staticmethod
    def create_user(user_data):
        """Create a new user"""
        try:
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                age=user_data['age'],
                role=user_data.get('role', 'user')
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            db.session.commit()
            return user.to_dict()
        except IntegrityError:
            db.session.rollback()
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        user = User.query.get(user_id)
        return user.to_dict() if user else None
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email (returns dict)"""
        user = User.query.filter_by(email=email).first()
        return user.to_dict() if user else None
    
    @staticmethod
    def get_user_object_by_email(email):
        """Get user object by email (for password verification)"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        users = User.query.all()
        return [user.to_dict() for user in users]
    
    @staticmethod
    def update_user(user_id, user_data):
        """Update an existing user"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        try:
            # Update only provided fields
            if 'name' in user_data:
                user.name = user_data['name']
            if 'email' in user_data:
                user.email = user_data['email']
            if 'age' in user_data:
                user.age = user_data['age']
            if 'role' in user_data:
                user.role = user_data['role']
            if 'password' in user_data:
                user.set_password(user_data['password'])
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return user.to_dict()
        except IntegrityError:
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_user(user_id):
        """Delete a user"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        user_dict = user.to_dict()
        db.session.delete(user)
        db.session.commit()
        return user_dict
    
    @staticmethod
    def email_exists(email, exclude_user_id=None):
        """Check if email already exists"""
        query = User.query.filter_by(email=email)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None
    
    @staticmethod
    def reset():
        """Reset the database to initial state"""
        try:
            # Delete all users
            User.query.delete()
            db.session.commit()
            
            # Reset auto-increment (SQLite specific)
            # Only attempt if sqlite_sequence table exists
            try:
                db.session.execute(db.text("DELETE FROM sqlite_sequence WHERE name='users'"))
                db.session.commit()
            except Exception:
                # Table may not exist, which is fine
                db.session.rollback()
            
            # Re-seed initial data
            UserStore._init_sample_data()
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def _init_sample_data():
        """Initialize with sample users for testing"""
        sample_users = [
            {
                "name": "Admin User",
                "email": "admin@example.com",
                "password": "Admin@123",
                "age": 30,
                "role": "admin"
            },
            {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "User@123",
                "age": 25,
                "role": "user"
            }
        ]
        
        for user_data in sample_users:
            UserStore.create_user(user_data)


def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Seed initial data if database is empty
        if User.query.count() == 0:
            UserStore._init_sample_data()
