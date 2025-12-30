"""
FLYTAU Crew Repository
Database access for crew members and assignments
"""
from app.db import execute_query


def get_available_employees(role, departure_datetime, arrival_datetime):
    """
    Get employees of a role not assigned to overlapping flights.
    
    Args:
        role: 'pilot' or 'attendant'
        departure_datetime: Flight departure time
        arrival_datetime: Flight arrival time
    
    Returns:
        List of available employee dicts
    """
    sql = """
        SELECT e.id, e.employee_code, e.first_name, e.last_name, e.role, e.long_flight_certified
        FROM employees e
        WHERE e.role = %s
          AND e.id NOT IN (
              SELECT ca.employee_id
              FROM crew_assignments ca
              JOIN flights f ON ca.flight_id = f.id
              WHERE f.status IN ('active', 'full')
                AND NOT (f.arrival_datetime <= %s OR f.departure_datetime >= %s)
          )
        ORDER BY e.last_name, e.first_name
    """
    return execute_query(sql, (role, departure_datetime, arrival_datetime))


def get_crew_for_flight(flight_id):
    """Get all crew members assigned to a flight."""
    sql = """
        SELECT e.id, e.employee_code, e.first_name, e.last_name, e.role, e.long_flight_certified
        FROM employees e
        JOIN crew_assignments ca ON e.id = ca.employee_id
        WHERE ca.flight_id = %s
        ORDER BY e.role, e.last_name
    """
    return execute_query(sql, (flight_id,))


def create_crew_assignment(flight_id, employee_id):
    """Create a crew assignment."""
    sql = """
        INSERT INTO crew_assignments (flight_id, employee_id)
        VALUES (%s, %s)
    """
    return execute_query(sql, (flight_id, employee_id), commit=True)


def delete_crew_assignments(flight_id):
    """Delete all crew assignments for a flight."""
    sql = "DELETE FROM crew_assignments WHERE flight_id = %s"
    return execute_query(sql, (flight_id,), commit=True)


def count_crew():
    """Count total crew members (pilots + attendants)."""
    sql = "SELECT COUNT(*) AS count FROM employees WHERE role IN ('pilot', 'attendant')"
    result = execute_query(sql, fetch_one=True)
    return result['count'] if result else 0


def get_pilots():
    """Get all pilots."""
    sql = """
        SELECT id, employee_code, first_name, last_name, long_flight_certified
        FROM employees
        WHERE role = 'pilot'
        ORDER BY last_name, first_name
    """
    return execute_query(sql)


def get_attendants():
    """Get all attendants."""
    sql = """
        SELECT id, employee_code, first_name, last_name, long_flight_certified
        FROM employees
        WHERE role = 'attendant'
        ORDER BY last_name, first_name
    """
    return execute_query(sql)
