"""Simple validation helpers - each returns (is_valid, error_message)."""
import re


def validate_email(email):
    if not email:
        return (False, "Email is required.")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return (False, "Please enter a valid email address.")
    return (True, None)


def validate_password(password, min_length=6):
    if not password:
        return (False, "Password is required.")
    if len(password) < min_length:
        return (False, f"Password must be at least {min_length} characters.")
    return (True, None)


def validate_required(value, field_name):
    if not value or (isinstance(value, str) and not value.strip()):
        return (False, f"{field_name} is required.")
    return (True, None)


def validate_positive_number(value, field_name):
    try:
        num = float(value)
        if num <= 0:
            return (False, f"{field_name} must be a positive number.")
        return (True, None)
    except (ValueError, TypeError):
        return (False, f"{field_name} must be a valid number.")


def validate_date(date_str, field_name="Date"):
    if not date_str:
        return (False, f"{field_name} is required.")
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return (False, f"{field_name} must be in YYYY-MM-DD format.")
    return (True, None)


def validate_time(time_str, field_name="Time"):
    if not time_str:
        return (False, f"{field_name} is required.")
    if not re.match(r'^\d{2}:\d{2}$', time_str):
        return (False, f"{field_name} must be in HH:MM format.")
    return (True, None)
