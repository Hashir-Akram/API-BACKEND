"""
Input validation functions for the API
"""
import re
from email_validator import validate_email, EmailNotValidError

class ValidationError(Exception):
    """Custom validation error exception"""
    def __init__(self, message, error_code="VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def validate_user_data(data, is_update=False):
    """
    Validate user data for create/update operations
    
    Args:
        data: Dictionary containing user data
        is_update: Boolean indicating if this is an update operation
    
    Returns:
        Dictionary of validated data
    
    Raises:
        ValidationError: If validation fails
    """
    validated = {}
    
    # For create, all fields are required. For update, fields are optional
    if not is_update:
        required_fields = ["name", "email", "age", "password"]
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == "":
                raise ValidationError(
                    f"Missing required field: {field}",
                    error_code="MISSING_FIELD"
                )
    
    # Validate name
    if "name" in data:
        name = str(data["name"]).strip()
        if len(name) < 3:
            raise ValidationError(
                "Name must be at least 3 characters long",
                error_code="INVALID_NAME"
            )
        if len(name) > 100:
            raise ValidationError(
                "Name must be less than 100 characters",
                error_code="INVALID_NAME"
            )
        validated["name"] = name
    
    # Validate email
    if "email" in data:
        email = str(data["email"]).strip()
        try:
            # Validate email format
            email_info = validate_email(email, check_deliverability=False)
            validated["email"] = email_info.normalized
        except EmailNotValidError as e:
            raise ValidationError(
                "Invalid email format",
                error_code="INVALID_EMAIL"
            )
    
    # Validate age
    if "age" in data:
        try:
            age = int(data["age"])
            if age < 18:
                raise ValidationError(
                    "Age must be 18 or older",
                    error_code="INVALID_AGE"
                )
            if age > 150:
                raise ValidationError(
                    "Age must be less than 150",
                    error_code="INVALID_AGE"
                )
            validated["age"] = age
        except (ValueError, TypeError):
            raise ValidationError(
                "Age must be a valid integer",
                error_code="INVALID_AGE"
            )
    
    # Validate role
    if "role" in data:
        role = str(data["role"]).strip().lower()
        if role not in ["admin", "user"]:
            raise ValidationError(
                "Role must be either 'admin' or 'user'",
                error_code="INVALID_ROLE"
            )
        validated["role"] = role
    
    # Validate password
    if "password" in data:
        password = str(data["password"])
        
        if len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long",
                error_code="INVALID_PASSWORD"
            )
        
        if len(password) > 128:
            raise ValidationError(
                "Password must be less than 128 characters",
                error_code="INVALID_PASSWORD"
            )
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "Password must contain at least one uppercase letter",
                error_code="INVALID_PASSWORD"
            )
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                "Password must contain at least one lowercase letter",
                error_code="INVALID_PASSWORD"
            )
        
        # Check for digit
        if not re.search(r'\d', password):
            raise ValidationError(
                "Password must contain at least one digit",
                error_code="INVALID_PASSWORD"
            )
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)",
                error_code="INVALID_PASSWORD"
            )
        
        validated["password"] = password
    
    return validated


def validate_login_data(data):
    """
    Validate login data
    
    Args:
        data: Dictionary containing login credentials
    
    Returns:
        Dictionary of validated data
    
    Raises:
        ValidationError: If validation fails
    """
    if "email" not in data or not data["email"]:
        raise ValidationError(
            "Missing required field: email",
            error_code="MISSING_FIELD"
        )
    
    if "password" not in data or not data["password"]:
        raise ValidationError(
            "Missing required field: password",
            error_code="MISSING_FIELD"
        )
    
    email = str(data["email"]).strip()
    password = str(data["password"])
    
    try:
        email_info = validate_email(email, check_deliverability=False)
        validated_email = email_info.normalized
    except EmailNotValidError:
        raise ValidationError(
            "Invalid email format",
            error_code="INVALID_EMAIL"
        )
    
    return {"email": validated_email, "password": password}


def validate_user_id(user_id_str):
    """
    Validate user ID
    
    Args:
        user_id_str: String representation of user ID
    
    Returns:
        Integer user ID
    
    Raises:
        ValidationError: If validation fails
    """
    try:
        user_id = int(user_id_str)
        if user_id < 1:
            raise ValidationError(
                "User ID must be a positive integer",
                error_code="INVALID_USER_ID"
            )
        return user_id
    except (ValueError, TypeError):
        raise ValidationError(
            "User ID must be a valid integer",
            error_code="INVALID_USER_ID"
        )
