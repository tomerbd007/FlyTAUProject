"""
FLYTAU Form Validators
Server-side form validation helpers
"""
import re


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email: Email string to validate
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    if not email:
        return (False, "Email is required.")
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return (False, "Please enter a valid email address.")
    
    return (True, None)


def validate_password(password, min_length=6):
    """
    Validate password strength.
    
    Args:
        password: Password string to validate
        min_length: Minimum required length (default 6)
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    if not password:
        return (False, "Password is required.")
    
    if len(password) < min_length:
        return (False, f"Password must be at least {min_length} characters.")
    
    return (True, None)


def validate_required(value, field_name):
    """
    Validate that a field is not empty.
    
    Args:
        value: Value to check
        field_name: Name of the field for error message
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    if not value or (isinstance(value, str) and not value.strip()):
        return (False, f"{field_name} is required.")
    
    return (True, None)


def validate_positive_number(value, field_name):
    """
    Validate that a value is a positive number.
    
    Args:
        value: Value to check
        field_name: Name of the field for error message
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    try:
        num = float(value)
        if num <= 0:
            return (False, f"{field_name} must be a positive number.")
        return (True, None)
    except (ValueError, TypeError):
        return (False, f"{field_name} must be a valid number.")


def validate_date(date_str, field_name="Date"):
    """
    Validate date string format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        field_name: Name of the field for error message
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    if not date_str:
        return (False, f"{field_name} is required.")
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return (False, f"{field_name} must be in YYYY-MM-DD format.")
    
    return (True, None)


def validate_time(time_str, field_name="Time"):
    """
    Validate time string format (HH:MM).
    
    Args:
        time_str: Time string to validate
        field_name: Name of the field for error message
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    if not time_str:
        return (False, f"{field_name} is required.")
    
    pattern = r'^\d{2}:\d{2}$'
    if not re.match(pattern, time_str):
        return (False, f"{field_name} must be in HH:MM format.")
    
    return (True, None)
