"""Route access control decorators."""
from functools import wraps
from flask import session, redirect, url_for, flash, abort


def login_required(f):
    """Require any logged-in user."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def guest_only(f):
    """Only allow non-logged-in users (for login/register pages)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            if session.get('role') == 'manager':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('flights'))
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    """Require manager role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('admin_login'))
        if session.get('role') != 'manager':
            flash('Access denied. Manager privileges required.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def customer_required(f):
    """Require customer role (block managers)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') == 'manager':
            flash('Managers cannot access customer features.', 'error')
            return redirect(url_for('admin_dashboard'))
        if 'user_id' not in session or session.get('role') != 'customer':
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def customer_or_guest(f):
    """Allow customers and guests, block managers."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') == 'manager':
            flash('Managers are not allowed to purchase tickets.', 'error')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Require one of the specified roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('Access denied. Insufficient privileges.', 'error')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
