"""
FLYTAU Route Decorators
Access control decorators for routes
"""
from functools import wraps
from flask import session, redirect, url_for, flash, abort


def login_required(f):
    """
    Decorator that requires user to be logged in.
    Redirects to login page if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def guest_only(f):
    """
    Decorator that only allows guests (not logged in).
    Redirects logged-in users away from login/register pages.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            if session.get('role') == 'manager':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('flights'))
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    """
    Decorator that requires user to be a logged-in manager.
    Returns 403 Forbidden if not a manager.
    """
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
    """
    Decorator that requires user to be a logged-in customer.
    Managers are explicitly blocked.
    """
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
    """
    Decorator that allows customers and guests (not managers).
    Guests can proceed without login for booking flow.
    Managers are explicitly blocked from purchasing.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') == 'manager':
            flash('Managers are not allowed to purchase tickets.', 'error')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Decorator factory that requires user to have one of the specified roles.
    
    Usage:
        @role_required('manager', 'admin')
        def admin_page():
            ...
    """
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
