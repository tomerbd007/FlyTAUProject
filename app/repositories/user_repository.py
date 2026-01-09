"""
FLYTAU User Repository
Database access for customers (Guest/Registered) and employees (Managers/Pilots/FlightAttendants)

Schema:
- GuestCustomer: UniqueMail (PK), PhoneNum (JSON), FirstName, SecondName
- RegisteredCustomer: UniqueMail (PK), PhoneNum (JSON), FirstName, SecondName, Password, RegistrationDate, PassportNum, BirthDate
- Managers: ManagerId (PK), PhoneNum (JSON), FirstName, SecondName, JoinDate, Street, City, HouseNum, Password
- Pilot: Id (PK), PhoneNum (JSON), FirstName, SecondName, JoinDate, Street, City, HouseNum, LongFlightsTraining
- FlightAttendant: Id (PK), PhoneNum (JSON), FirstName, SecondName, JoinDate, Street, City, HouseNum, LongFlightsTraining
"""
import json
from app.db import execute_query


# ============ REGISTERED CUSTOMER OPERATIONS ============

def find_registered_customer_by_email(email):
    """Find a registered customer by email address."""
    sql = """
        SELECT UniqueMail, Password, FirstName, SecondName, 
               PhoneNum, RegistrationDate, PassportNum, BirthDate
        FROM RegisteredCustomer
        WHERE UniqueMail = %s
    """
    result = execute_query(sql, (email,), fetch_one=True)
    if result:
        # Parse JSON phone number if present
        result = dict(result)
        if result.get('PhoneNum'):
            try:
                result['PhoneNum'] = json.loads(result['PhoneNum']) if isinstance(result['PhoneNum'], str) else result['PhoneNum']
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def create_registered_customer(email, password_hash, first_name, last_name, phone=None, passport_num=None, birth_date=None):
    """
    Create a new registered customer.
    
    Args:
        email: Customer's email (becomes primary key)
        password_hash: Bcrypt hashed password
        first_name: First name
        last_name: Last name (SecondName in schema)
        phone: Phone number (will be stored as JSON)
        passport_num: Optional passport number
        birth_date: Optional birth date
    
    Returns:
        Email of created customer (the PK)
    """
    phone_json = json.dumps(phone) if phone else None
    sql = """
        INSERT INTO RegisteredCustomer 
        (UniqueMail, Password, FirstName, SecondName, PhoneNum, RegistrationDate, PassportNum, BirthDate)
        VALUES (%s, %s, %s, %s, %s, CURDATE(), %s, %s)
    """
    execute_query(sql, (email, password_hash, first_name, last_name, phone_json, passport_num, birth_date), commit=True)
    return email


def email_exists_registered(email):
    """Check if email already exists in RegisteredCustomer table."""
    sql = "SELECT 1 FROM RegisteredCustomer WHERE UniqueMail = %s"
    result = execute_query(sql, (email,), fetch_one=True)
    return result is not None


# ============ GUEST CUSTOMER OPERATIONS ============

def find_guest_customer_by_email(email):
    """Find a guest customer by email address."""
    sql = """
        SELECT UniqueMail, FirstName, SecondName, PhoneNum
        FROM GuestCustomer
        WHERE UniqueMail = %s
    """
    result = execute_query(sql, (email,), fetch_one=True)
    if result:
        result = dict(result)
        if result.get('PhoneNum'):
            try:
                result['PhoneNum'] = json.loads(result['PhoneNum']) if isinstance(result['PhoneNum'], str) else result['PhoneNum']
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def create_guest_customer(email, first_name, last_name, phone=None):
    """
    Create a new guest customer or update existing one.
    If the guest already exists and a new phone is provided, append it to the phone list.
    
    Args:
        email: Guest's email (becomes primary key)
        first_name: First name
        last_name: Last name (SecondName in schema)
        phone: Phone number (will be appended to JSON array)
    
    Returns:
        Email of created/updated guest (the PK)
    """
    # Check if guest already exists
    existing = find_guest_customer_by_email(email)
    
    if existing:
        # Guest exists - append new phone if provided and not already in list
        existing_phones = existing.get('PhoneNum') or []
        if not isinstance(existing_phones, list):
            existing_phones = [existing_phones] if existing_phones else []
        
        if phone and phone not in existing_phones:
            existing_phones.append(phone)
        
        phone_json = json.dumps(existing_phones) if existing_phones else None
        sql = """
            UPDATE GuestCustomer 
            SET FirstName = %s, SecondName = %s, PhoneNum = %s
            WHERE UniqueMail = %s
        """
        execute_query(sql, (first_name, last_name, phone_json, email), commit=True)
    else:
        # New guest - create with phone as array
        phone_json = json.dumps([phone]) if phone else None
        sql = """
            INSERT INTO GuestCustomer (UniqueMail, FirstName, SecondName, PhoneNum)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(sql, (email, first_name, last_name, phone_json), commit=True)
    
    return email


def email_exists_guest(email):
    """Check if email already exists in GuestCustomer table."""
    sql = "SELECT 1 FROM GuestCustomer WHERE UniqueMail = %s"
    result = execute_query(sql, (email,), fetch_one=True)
    return result is not None


# ============ MANAGER OPERATIONS ============

def find_manager_by_id(manager_id):
    """Find a manager by their ManagerId."""
    sql = """
        SELECT ManagerId, Password, FirstName, SecondName, 
               PhoneNum, JoinDate, Street, City, HouseNum
        FROM Managers
        WHERE ManagerId = %s
    """
    result = execute_query(sql, (manager_id,), fetch_one=True)
    if result:
        result = dict(result)
        if result.get('PhoneNum'):
            try:
                result['PhoneNum'] = json.loads(result['PhoneNum']) if isinstance(result['PhoneNum'], str) else result['PhoneNum']
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def get_all_managers():
    """Get all managers."""
    sql = """
        SELECT ManagerId, FirstName, SecondName, JoinDate, PhoneNum, City
        FROM Managers
        ORDER BY SecondName, FirstName
    """
    return execute_query(sql)


# ============ PILOT OPERATIONS ============

def find_pilot_by_id(pilot_id):
    """Find a pilot by their Id."""
    sql = """
        SELECT Id, FirstName, SecondName, PhoneNum, JoinDate, 
               Street, City, HouseNum, LongFlightsTraining
        FROM Pilot
        WHERE Id = %s
    """
    result = execute_query(sql, (pilot_id,), fetch_one=True)
    if result:
        result = dict(result)
        if result.get('PhoneNum'):
            try:
                result['PhoneNum'] = json.loads(result['PhoneNum']) if isinstance(result['PhoneNum'], str) else result['PhoneNum']
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def get_all_pilots(long_flight_certified_only=False):
    """
    Get all pilots.
    
    Args:
        long_flight_certified_only: If True, only return pilots with LongFlightsTraining=1
    """
    if long_flight_certified_only:
        sql = """
            SELECT Id, FirstName, SecondName, JoinDate, LongFlightsTraining, PhoneNum
            FROM Pilot
            WHERE LongFlightsTraining = 1
            ORDER BY SecondName, FirstName
        """
        return execute_query(sql)
    else:
        sql = """
            SELECT Id, FirstName, SecondName, JoinDate, LongFlightsTraining, PhoneNum
            FROM Pilot
            ORDER BY SecondName, FirstName
        """
        return execute_query(sql)


def get_available_pilots(flight_id, airplane_id, require_long_flight_cert=False):
    """
    Get pilots not already assigned to a flight on the same date.
    
    Args:
        flight_id: FlightId to check
        airplane_id: Airplanes_AirplaneId to check
        require_long_flight_cert: If True, only return certified pilots
    """
    cert_condition = "AND p.LongFlightsTraining = 1" if require_long_flight_cert else ""
    sql = f"""
        SELECT p.Id, p.FirstName, p.SecondName, p.LongFlightsTraining
        FROM Pilot p
        WHERE p.Id NOT IN (
            SELECT pf.Pilot_Id 
            FROM Pilot_has_Flights pf
            JOIN Flights f ON pf.Flights_FlightId = f.FlightId 
                AND pf.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
            WHERE f.DepartureDate = (
                SELECT DepartureDate FROM Flights 
                WHERE FlightId = %s AND Airplanes_AirplaneId = %s
            )
        )
        {cert_condition}
        ORDER BY p.SecondName, p.FirstName
    """
    return execute_query(sql, (flight_id, airplane_id))


# ============ FLIGHT ATTENDANT OPERATIONS ============

def find_flight_attendant_by_id(attendant_id):
    """Find a flight attendant by their Id."""
    sql = """
        SELECT Id, FirstName, SecondName, PhoneNum, JoinDate, 
               Street, City, HouseNum, LongFlightsTraining
        FROM FlightAttendant
        WHERE Id = %s
    """
    result = execute_query(sql, (attendant_id,), fetch_one=True)
    if result:
        result = dict(result)
        if result.get('PhoneNum'):
            try:
                result['PhoneNum'] = json.loads(result['PhoneNum']) if isinstance(result['PhoneNum'], str) else result['PhoneNum']
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def get_all_flight_attendants(long_flight_certified_only=False):
    """
    Get all flight attendants.
    
    Args:
        long_flight_certified_only: If True, only return attendants with LongFlightsTraining=1
    """
    if long_flight_certified_only:
        sql = """
            SELECT Id, FirstName, SecondName, JoinDate, LongFlightsTraining, PhoneNum
            FROM FlightAttendant
            WHERE LongFlightsTraining = 1
            ORDER BY SecondName, FirstName
        """
        return execute_query(sql)
    else:
        sql = """
            SELECT Id, FirstName, SecondName, JoinDate, LongFlightsTraining, PhoneNum
            FROM FlightAttendant
            ORDER BY SecondName, FirstName
        """
        return execute_query(sql)


def get_available_flight_attendants(flight_id, airplane_id, require_long_flight_cert=False):
    """
    Get flight attendants not already assigned to a flight on the same date.
    
    Args:
        flight_id: FlightId to check
        airplane_id: Airplanes_AirplaneId to check
        require_long_flight_cert: If True, only return certified attendants
    """
    cert_condition = "AND fa.LongFlightsTraining = 1" if require_long_flight_cert else ""
    sql = f"""
        SELECT fa.Id, fa.FirstName, fa.SecondName, fa.LongFlightsTraining
        FROM FlightAttendant fa
        WHERE fa.Id NOT IN (
            SELECT faf.FlightAttendant_Id 
            FROM FlightAttendant_has_Flights faf
            JOIN Flights f ON faf.Flights_FlightId = f.FlightId 
                AND faf.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
            WHERE f.DepartureDate = (
                SELECT DepartureDate FROM Flights 
                WHERE FlightId = %s AND Airplanes_AirplaneId = %s
            )
        )
        {cert_condition}
        ORDER BY fa.SecondName, fa.FirstName
    """
    return execute_query(sql, (flight_id, airplane_id))
