"""
FLYTAU Helper Functions
Utility functions for password hashing, booking code generation, etc.
"""
import bcrypt
import random
import string


def hash_password(password):
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password(password, password_hash):
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to check
        password_hash: Stored hash to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def generate_booking_code(length=8):
    """
    Generate a random booking code.
    
    Args:
        length: Length of the code (default 8)
    
    Returns:
        Uppercase alphanumeric booking code
    """
    # Use uppercase letters and digits, excluding confusing characters (0, O, I, 1)
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(random.choices(chars, k=length))


def format_currency(amount):
    """
    Format a number as currency.
    
    Args:
        amount: Numeric amount
    
    Returns:
        Formatted string (e.g., "$1,234.56")
    """
    return f"${amount:,.2f}"


def format_datetime(dt, format_str="%Y-%m-%d %H:%M"):
    """
    Format a datetime object as a string.
    
    Args:
        dt: datetime object
        format_str: strftime format string
    
    Returns:
        Formatted datetime string
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def format_date(dt, format_str="%Y-%m-%d"):
    """
    Format a datetime object as a date string.
    
    Args:
        dt: datetime object
        format_str: strftime format string
    
    Returns:
        Formatted date string
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def format_time(dt, format_str="%H:%M"):
    """
    Format a datetime object as a time string.
    
    Args:
        dt: datetime object
        format_str: strftime format string
    
    Returns:
        Formatted time string
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def format_duration(minutes):
    """
    Format duration in minutes as a human-readable string.
    
    Args:
        minutes: Duration in minutes
    
    Returns:
        Formatted string (e.g., "5h 30m")
    """
    if minutes is None:
        return ""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours}h {mins}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{mins}m"
