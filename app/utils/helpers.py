"""Handy utility functions - password hashing, formatting, random codes."""
import bcrypt
import random
import string


def hash_password(password):
    """Securely hashes a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password(password, password_hash):
    """Checks if a password matches its hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def generate_booking_code(length=8):
    """Generates a random booking code (avoids confusing characters like 0/O, 1/I)."""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # no confusing chars (0,O,I,1)
    return ''.join(random.choices(chars, k=length))


def format_currency(amount):
    return f"${amount:,.2f}"


def format_datetime(dt, format_str="%Y-%m-%d %H:%M"):
    return dt.strftime(format_str) if dt else ""


def format_date(dt, format_str="%Y-%m-%d"):
    return dt.strftime(format_str) if dt else ""


def format_time(dt, format_str="%H:%M"):
    return dt.strftime(format_str) if dt else ""


def format_duration(minutes):
    """Turns minutes into a nice readable format like '5h 30m'."""
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
