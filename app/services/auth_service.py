"""Login and registration logic for customers and managers."""
from app.repositories import user_repository
from app.utils.helpers import hash_password, check_password


def register_customer(email, password, first_name, last_name, phone=None, passport=None, date_of_birth=None):
    """Signs up a new customer. Throws an error if the email's already taken."""
    existing = user_repository.find_registered_customer_by_email(email.lower())
    if existing:
        raise ValueError('An account with this email already exists.')
    
    password_hash = hash_password(password)
    
    user_repository.create_registered_customer(
        email=email.lower(),
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        passport_num=passport,
        birth_date=date_of_birth
    )
    
    return email.lower()


def login_customer(email, password):
    """Verifies customer credentials - returns their info if valid, None if not."""
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
    """Verifies manager credentials - returns their info if valid, None if not."""
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
    """Finds a registered customer by their email."""
    return user_repository.find_registered_customer_by_email(email.lower())


def get_guest_customer_by_email(email):
    """Finds a guest customer by their email."""
    return user_repository.find_guest_customer_by_email(email.lower())


def get_or_create_guest_customer(email, first_name, last_name, phone=None):
    """Gets an existing guest or creates a new one. If they exist, adds any new phone number."""
    user_repository.create_guest_customer(
        email=email.lower(),
        first_name=first_name,
        last_name=last_name,
        phone=phone
    )
    return email.lower()


def get_manager_by_id(manager_id):
    """Looks up a manager by their ID."""
    return user_repository.find_manager_by_id(manager_id)
