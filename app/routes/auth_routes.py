"""
FLYTAU Authentication Routes
Handles customer registration, login, manager login, and logout
"""
from flask import render_template, request, redirect, url_for, flash, session
from app.services import auth_service
from app.utils.decorators import guest_only


def register_auth_routes(app):
    """Register authentication routes with the Flask app."""
    
    @app.route('/register', methods=['GET', 'POST'])
    @guest_only
    def register():
        """Customer registration page."""
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            
            # Validation
            errors = []
            if not email:
                errors.append('Email is required.')
            if not password or len(password) < 6:
                errors.append('Password must be at least 6 characters.')
            if password != confirm_password:
                errors.append('Passwords do not match.')
            if not first_name:
                errors.append('First name is required.')
            if not last_name:
                errors.append('Last name is required.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('auth/register.html')
            
            # Attempt registration
            try:
                auth_service.register_customer(email, password, first_name, last_name)
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except ValueError as e:
                flash(str(e), 'error')
                return render_template('auth/register.html')
        
        return render_template('auth/register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    @guest_only
    def login():
        """Customer login page."""
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            if not email or not password:
                flash('Email and password are required.', 'error')
                return render_template('auth/login.html')
            
            user = auth_service.login_customer(email, password)
            if user:
                session['user_id'] = user['id']
                session['user_type'] = 'customer'
                session['role'] = 'customer'
                session['email'] = user['email']
                session['name'] = f"{user['first_name']} {user['last_name']}"
                flash(f"Welcome back, {user['first_name']}!", 'success')
                return redirect(url_for('my_account'))
            else:
                flash('Invalid email or password.', 'error')
                return render_template('auth/login.html')
        
        return render_template('auth/login.html')
    
    @app.route('/admin/login', methods=['GET', 'POST'])
    @guest_only
    def admin_login():
        """Manager login page."""
        if request.method == 'POST':
            employee_code = request.form.get('employee_code', '').strip()
            password = request.form.get('password', '')
            
            if not employee_code or not password:
                flash('Employee code and password are required.', 'error')
                return render_template('auth/manager_login.html')
            
            user = auth_service.login_manager(employee_code, password)
            if user:
                session['user_id'] = user['id']
                session['user_type'] = 'manager'
                session['role'] = 'manager'
                session['employee_code'] = user['employee_code']
                session['name'] = f"{user['first_name']} {user['last_name']}"
                flash(f"Welcome, {user['first_name']}!", 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid employee code or password.', 'error')
                return render_template('auth/manager_login.html')
        
        return render_template('auth/manager_login.html')
    
    @app.route('/account')
    def my_account():
        """Customer account page with profile and recent orders."""
        if session.get('role') != 'customer':
            flash('Please log in to access your account.', 'warning')
            return redirect(url_for('login'))
        
        from app.services import order_service
        
        # Get recent orders for this customer
        customer_id = session.get('user_id')
        recent_orders = order_service.get_customer_orders(customer_id, '')[:5]  # Last 5 orders
        
        return render_template('auth/my_account.html', 
                               recent_orders=recent_orders,
                               user_name=session.get('name'),
                               user_email=session.get('email'))
    
    @app.route('/logout')
    def logout():
        """Log out the current user."""
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
