"""Customer and manager authentication."""
from app.repositories import user_repository
from app.utils.helpers import hash_password, check_password


def register_customer(email, password, first_name, last_name, passport=None, date_of_birth=None):
    """Register new customer. Raises ValueError if email exists."""
    existing = user_repository.find_registered_customer_by_email(email.lower())
    if existing:
        raise ValueError('An account with this email already exists.')
    
    password_hash = hash_password(password)
    
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
    """Authenticate customer, returns user dict or None."""
    customer = user_repository.find_registered_customer_by_email(email.lower())
    
    if not customer:
        return None
    
    if not check_password(password, customer['Password']):
        return None
    
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
    """Authenticate manager, returns user dict or None."""
    manager = user_repository.find_manager_by_id(manager_id.upper())
    
    if not manager:
        return None
    
    if not check_password(password, manager['Password']):
        return None
    
    return {
        'id': manager['ManagerId'],
        'employee_code': manager['ManagerId'],
        'first_name': manager['FirstName'],
        'last_name': manager['SecondName'],
        'phone': manager.get('PhoneNum')
    }


def get_registered_customer_by_email(email):
    """Get registered customer by email."""
    return user_repository.find_registered_customer_by_email(email.lower())


def get_guest_customer_by_email(email):
    """Get guest customer by email."""
    return user_repository.find_guest_customer_by_email(email.lower())


def get_or_create_guest_customer(email, first_name, last_name, phone=None):
    """Get or create guest customer. Appends phone if guest exists."""
    user_repository.create_guest_customer(
        email=email.lower(),
        first_name=first_name,
        last_name=last_name,
        phone=phone
    )
    return email.lower()


def get_manager_by_id(manager_id):
    """Get manager by ID."""
    return user_repository.find_manager_by_id(manager_id)
