"""
FLYTAU Authentication Service
Handles customer registration, login validation, and manager authentication

Schema:
- RegisteredCustomer: UniqueMail (PK), Password, Passport, FirstName, LastName, DateOfBirth
- GuestCustomer: UniqueMail (PK), FirstName, LastName
- Managers: ManagerId (PK), Password, FirstName, LastName, PhoneNum (JSON)
"""
from app.repositories import user_repository
from app.utils.helpers import hash_password, check_password


def register_customer(email, password, first_name, last_name, passport=None, date_of_birth=None):
    """
    Register a new customer (RegisteredCustomer).
    
    Args:
        email: Customer email address (will be UniqueMail PK)
        password: Plain text password
        first_name: Customer first name
        last_name: Customer last name
        passport: Passport number (optional)
        date_of_birth: Date of birth (optional, YYYY-MM-DD)
    
    Returns:
        Email (UniqueMail) if successful
    
    Raises:
        ValueError: If email already exists or validation fails
    """
    # Check if email already exists as registered customer
    existing = user_repository.find_registered_customer_by_email(email.lower())
    if existing:
        raise ValueError('An account with this email already exists.')
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create registered customer
    user_repository.create_registered_customer(
        email=email.lower(),
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        passport=passport,
        date_of_birth=date_of_birth
    )
    
    return email.lower()


def login_customer(email, password):
    """
    Authenticate a registered customer.
    
    Args:
        email: Customer email
        password: Plain text password
    
    Returns:
        Customer dict if valid, None otherwise
    """
    customer = user_repository.find_registered_customer_by_email(email.lower())
    
    if not customer:
        return None
    
    if not check_password(password, customer['Password']):
        return None
    
    # Map database columns to expected keys
    return {
        'id': customer['UniqueMail'],
        'email': customer['UniqueMail'],
        'first_name': customer['FirstName'],
        'last_name': customer['SecondName'],
        'passport': customer.get('PassportNum'),
        'birth_date': customer.get('BirthDate'),
        'phone': customer.get('PhoneNum')
    }


def login_manager(manager_id, password):
    """
    Authenticate a manager.
    
    Args:
        manager_id: Manager ID (e.g., M001)
        password: Plain text password
    
    Returns:
        Manager dict if valid, None otherwise
    """
    manager = user_repository.find_manager_by_id(manager_id.upper())
    
    if not manager:
        return None
    
    if not check_password(password, manager['Password']):
        return None
    
    # Map database columns to expected keys
    return {
        'id': manager['ManagerId'],
        'employee_code': manager['ManagerId'],
        'first_name': manager['FirstName'],
        'last_name': manager['SecondName'],
        'phone': manager.get('PhoneNum')
    }


def get_registered_customer_by_email(email):
    """Get registered customer by email (UniqueMail)."""
    return user_repository.find_registered_customer_by_email(email.lower())


def get_guest_customer_by_email(email):
    """Get guest customer by email (UniqueMail)."""
    return user_repository.find_guest_customer_by_email(email.lower())


def get_or_create_guest_customer(email, first_name, last_name):
    """
    Get existing guest customer or create a new one.
    
    Args:
        email: Guest email address
        first_name: First name
        last_name: Last name
    
    Returns:
        Guest customer email (UniqueMail)
    """
    existing = user_repository.find_guest_customer_by_email(email.lower())
    if existing:
        return existing['UniqueMail']
    
    user_repository.create_guest_customer(
        email=email.lower(),
        first_name=first_name,
        last_name=last_name
    )
    return email.lower()


def get_manager_by_id(manager_id):
    """Get manager by ID."""
    return user_repository.find_manager_by_id(manager_id)
