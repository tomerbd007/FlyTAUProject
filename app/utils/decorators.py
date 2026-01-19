"""Decorators for protecting routes based on who's logged in."""
from functools import wraps
from flask import session, redirect, url_for, flash, abort


def login_required(f):
    """Makes sure someone is logged in before they can access the route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def guest_only(f):
    """Only for logged-out users (login/register pages shouldn't show if you're already in)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            if session.get('role') == 'manager':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('flights'))
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    """Manager-only routes - redirects everyone else."""
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
    """Customer-only routes - managers can't access these."""
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
    """Open to customers and guests, but managers are blocked from booking."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') == 'manager':
            flash('Managers are not allowed to purchase tickets.', 'error')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Restricts access to users with one of the specified roles."""
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
