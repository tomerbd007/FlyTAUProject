"""
FLYTAU User Repository
Database access for customers and employees
"""
from app.db import execute_query


# ============ CUSTOMER OPERATIONS ============

def find_customer_by_email(email):
    """Find a customer by email address."""
    sql = """
        SELECT id, email, password_hash, first_name, last_name, created_at
        FROM customers
        WHERE email = %s
    """
    return execute_query(sql, (email,), fetch_one=True)


def get_customer_by_id(customer_id):
    """Get a customer by ID."""
    sql = """
        SELECT id, email, password_hash, first_name, last_name, created_at
        FROM customers
        WHERE id = %s
    """
    return execute_query(sql, (customer_id,), fetch_one=True)


def create_customer(email, password_hash, first_name, last_name):
    """
    Create a new customer.
    
    Returns:
        New customer ID
    """
    sql = """
        INSERT INTO customers (email, password_hash, first_name, last_name, created_at)
        VALUES (%s, %s, %s, %s, NOW())
    """
    return execute_query(sql, (email, password_hash, first_name, last_name), commit=True)


# ============ EMPLOYEE OPERATIONS ============

def find_employee_by_code(employee_code):
    """Find an employee by employee code."""
    sql = """
        SELECT id, employee_code, password_hash, first_name, last_name, role, 
               long_flight_certified, created_at
        FROM employees
        WHERE employee_code = %s
    """
    return execute_query(sql, (employee_code,), fetch_one=True)


def get_employee_by_id(employee_id):
    """Get an employee by ID."""
    sql = """
        SELECT id, employee_code, password_hash, first_name, last_name, role,
               long_flight_certified, created_at
        FROM employees
        WHERE id = %s
    """
    return execute_query(sql, (employee_id,), fetch_one=True)


def get_employees_by_role(role):
    """Get all employees with a specific role."""
    sql = """
        SELECT id, employee_code, first_name, last_name, role, long_flight_certified
        FROM employees
        WHERE role = %s
        ORDER BY last_name, first_name
    """
    return execute_query(sql, (role,))
