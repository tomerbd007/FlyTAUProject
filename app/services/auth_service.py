"""
FLYTAU Authentication Service
Handles customer registration, login validation, and manager authentication
"""
from app.repositories import user_repository
from app.utils.helpers import hash_password, check_password


def register_customer(email, password, first_name, last_name):
    """
    Register a new customer.
    
    Args:
        email: Customer email address
        password: Plain text password
        first_name: Customer first name
        last_name: Customer last name
    
    Returns:
        Customer ID if successful
    
    Raises:
        ValueError: If email already exists or validation fails
    """
    # Check if email already exists
    existing = user_repository.find_customer_by_email(email)
    if existing:
        raise ValueError('An account with this email already exists.')
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create customer
    customer_id = user_repository.create_customer(
        email=email.lower(),
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name
    )
    
    return customer_id


def login_customer(email, password):
    """
    Authenticate a customer.
    
    Args:
        email: Customer email
        password: Plain text password
    
    Returns:
        Customer dict if valid, None otherwise
    """
    customer = user_repository.find_customer_by_email(email.lower())
    
    if not customer:
        return None
    
    if not check_password(password, customer['password_hash']):
        return None
    
    return customer


def login_manager(employee_code, password):
    """
    Authenticate a manager.
    
    Args:
        employee_code: Manager's employee code (e.g., M001)
        password: Plain text password
    
    Returns:
        Employee dict if valid manager, None otherwise
    """
    employee = user_repository.find_employee_by_code(employee_code.upper())
    
    if not employee:
        return None
    
    # Verify this is a manager
    if employee['role'] != 'manager':
        return None
    
    if not check_password(password, employee['password_hash']):
        return None
    
    return employee


def get_customer_by_id(customer_id):
    """Get customer by ID."""
    return user_repository.get_customer_by_id(customer_id)


def get_employee_by_id(employee_id):
    """Get employee by ID."""
    return user_repository.get_employee_by_id(employee_id)
