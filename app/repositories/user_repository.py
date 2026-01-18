"""Database access for customers and employees."""
import json
from app.db import execute_query


def find_registered_customer_by_email(email):
    """Find registered customer by email."""
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
    """Create new registered customer. Returns email (PK)."""
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
    """Create or update guest customer. Appends new phone if provided."""
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


def find_manager_by_id(manager_id):
    """Find manager by ID."""
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


def find_pilot_by_id(pilot_id):
    """Find pilot by ID."""
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
    """Get all pilots. Can filter to only certified for long flights."""
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
    """Get pilots not assigned to flights on same date."""
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


def find_flight_attendant_by_id(attendant_id):
    """Find flight attendant by ID."""
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
    """Get all flight attendants. Can filter to only long-flight certified."""
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
    """Get attendants not assigned to flights on same date."""
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
