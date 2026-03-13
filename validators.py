"""
Input validation functions for the API.
"""
from datetime import datetime
import re

from email_validator import EmailNotValidError, validate_email

class ValidationError(Exception):
    """Custom validation error exception"""
    def __init__(self, message, error_code="VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


PROJECT_STATUSES = ["active", "on_hold", "completed", "archived"]
TASK_STATUSES = ["todo", "in_progress", "in_review", "done", "blocked"]
TASK_PRIORITIES = ["low", "medium", "high", "critical"]
USER_ROLES = ["admin", "user"]


def _require_fields(data, required_fields):
    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            raise ValidationError(
                f"Missing required field: {field}",
                error_code="MISSING_FIELD"
            )


def _validate_string_field(value, field_name, min_length=1, max_length=255):
    normalized = str(value).strip()
    if len(normalized) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters long",
            error_code=f"INVALID_{field_name.upper().replace(' ', '_')}"
        )
    if len(normalized) > max_length:
        raise ValidationError(
            f"{field_name} must be less than {max_length} characters",
            error_code=f"INVALID_{field_name.upper().replace(' ', '_')}"
        )
    return normalized


def _validate_int_field(value, field_name, minimum=None, maximum=None):
    try:
        int_value = int(value)
    except (TypeError, ValueError):
        raise ValidationError(
            f"{field_name} must be a valid integer",
            error_code=f"INVALID_{field_name.upper().replace(' ', '_')}"
        )

    if minimum is not None and int_value < minimum:
        raise ValidationError(
            f"{field_name} must be greater than or equal to {minimum}",
            error_code=f"INVALID_{field_name.upper().replace(' ', '_')}"
        )
    if maximum is not None and int_value > maximum:
        raise ValidationError(
            f"{field_name} must be less than or equal to {maximum}",
            error_code=f"INVALID_{field_name.upper().replace(' ', '_')}"
        )
    return int_value


def _validate_float_field(value, field_name, minimum=None, maximum=None):
    try:
        float_value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(
            f"{field_name} must be a valid number",
            error_code=f"INVALID_{field_name.upper().replace(' ', '_')}"
        )

    if minimum is not None and float_value < minimum:
        raise ValidationError(
            f"{field_name} must be greater than or equal to {minimum}",
            error_code=f"INVALID_{field_name.upper().replace(' ', '_')}"
        )
    if maximum is not None and float_value > maximum:
        raise ValidationError(
            f"{field_name} must be less than or equal to {maximum}",
            error_code=f"INVALID_{field_name.upper().replace(' ', '_')}"
        )
    return float_value


def _validate_date_field(value, field_name):
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError(
            f"{field_name} must be in YYYY-MM-DD format",
            error_code=f"INVALID_{field_name.upper().replace(' ', '_')}"
        )


def _validate_choice(value, field_name, allowed_values):
    normalized = str(value).strip().lower()
    if normalized not in allowed_values:
        raise ValidationError(
            f"{field_name} must be one of: {', '.join(allowed_values)}",
            error_code=f"INVALID_{field_name.upper().replace(' ', '_')}"
        )
    return normalized


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

    if not is_update:
        _require_fields(data, ["name", "email", "age", "password"])
    
    # Validate name
    if "name" in data:
        validated["name"] = _validate_string_field(data["name"], "name", min_length=3, max_length=100)
    
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
            validated["age"] = _validate_int_field(data["age"], "age", minimum=18, maximum=150)
        except ValidationError:
            raise
    
    # Validate role
    if "role" in data:
        validated["role"] = _validate_choice(data["role"], "role", USER_ROLES)
    
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
        
        if re.search(r'\s', password):
            raise ValidationError(
                "Password must not contain spaces",
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
    _require_fields(data, ["email", "password"])
    
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
    return _validate_int_field(user_id_str, "user id", minimum=1)


def validate_pagination_params(args, allowed_sort_fields=None, default_sort_by="created_at"):
    page = _validate_int_field(args.get("page", 1), "page", minimum=1)
    per_page = _validate_int_field(args.get("per_page", 10), "per page", minimum=1, maximum=100)
    sort_order = _validate_choice(args.get("sort_order", "desc"), "sort order", ["asc", "desc"])
    sort_by = str(args.get("sort_by", default_sort_by)).strip()

    if allowed_sort_fields and sort_by not in allowed_sort_fields:
        raise ValidationError(
            f"sort_by must be one of: {', '.join(allowed_sort_fields)}",
            error_code="INVALID_SORT_BY"
        )

    return {
        "page": page,
        "per_page": per_page,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "q": str(args.get("q", "")).strip() or None,
    }


def validate_project_data(data, is_update=False):
    validated = {}

    if not is_update:
        _require_fields(data, ["title", "description"])

    if "title" in data:
        validated["title"] = _validate_string_field(data["title"], "title", min_length=3, max_length=150)

    if "description" in data:
        validated["description"] = _validate_string_field(data["description"], "description", min_length=10, max_length=2000)

    if "status" in data:
        validated["status"] = _validate_choice(data["status"], "project status", PROJECT_STATUSES)

    if "owner_id" in data and data["owner_id"] not in [None, ""]:
        validated["owner_id"] = _validate_int_field(data["owner_id"], "owner id", minimum=1)

    return validated


def validate_task_data(data, is_update=False, allow_partial_status_only=False):
    validated = {}

    if not is_update and not allow_partial_status_only:
        _require_fields(data, ["title", "description", "project_id"])

    if "title" in data:
        validated["title"] = _validate_string_field(data["title"], "title", min_length=3, max_length=150)

    if "description" in data:
        validated["description"] = _validate_string_field(data["description"], "description", min_length=5, max_length=3000)

    if "status" in data:
        validated["status"] = _validate_choice(data["status"], "task status", TASK_STATUSES)

    if "priority" in data:
        validated["priority"] = _validate_choice(data["priority"], "task priority", TASK_PRIORITIES)

    if "project_id" in data and data["project_id"] not in [None, ""]:
        validated["project_id"] = _validate_int_field(data["project_id"], "project id", minimum=1)

    if "created_by" in data and data["created_by"] not in [None, ""]:
        validated["created_by"] = _validate_int_field(data["created_by"], "created by", minimum=1)

    if "assigned_to" in data:
        if data["assigned_to"] in [None, ""]:
            validated["assigned_to"] = None
        else:
            validated["assigned_to"] = _validate_int_field(data["assigned_to"], "assigned to", minimum=1)

    if "estimated_hours" in data and data["estimated_hours"] not in [None, ""]:
        validated["estimated_hours"] = _validate_float_field(data["estimated_hours"], "estimated hours", minimum=0, maximum=1000)

    if "due_date" in data and data["due_date"] not in [None, ""]:
        validated["due_date"] = _validate_date_field(data["due_date"], "due date")

    if "tags" in data:
        tags = data["tags"]
        if isinstance(tags, list):
            validated["tags"] = [str(tag).strip() for tag in tags if str(tag).strip()]
        elif isinstance(tags, str):
            validated["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]
        else:
            raise ValidationError(
                "tags must be a comma-separated string or array of strings",
                error_code="INVALID_TAGS"
            )

    return validated


def validate_comment_data(data):
    _require_fields(data, ["content"])
    return {
        "content": _validate_string_field(data["content"], "content", min_length=2, max_length=2000)
    }


def validate_bulk_task_update(data):
    _require_fields(data, ["task_ids"])

    task_ids = data.get("task_ids")
    if not isinstance(task_ids, list) or not task_ids:
        raise ValidationError(
            "task_ids must be a non-empty array",
            error_code="INVALID_TASK_IDS"
        )

    validated_ids = []
    for task_id in task_ids:
        validated_ids.append(_validate_int_field(task_id, "task id", minimum=1))

    updates = validate_task_data(data, is_update=True)
    updates.pop("project_id", None)
    updates.pop("created_by", None)

    if not updates:
        raise ValidationError(
            "At least one updatable task field is required",
            error_code="MISSING_UPDATE_FIELDS"
        )

    return {
        "task_ids": validated_ids,
        "updates": updates,
    }
