"""
FLYTAU Aircraft Repository
Database access for aircraft and seat maps
"""
from app.db import execute_query


def get_aircraft_by_id(aircraft_id):
    """Get aircraft by ID."""
    sql = """
        SELECT id, registration, manufacturer, size, 
               economy_rows, economy_cols, business_rows, business_cols, purchased_date
        FROM aircraft
        WHERE id = %s
    """
    return execute_query(sql, (aircraft_id,), fetch_one=True)


def get_all_aircraft():
    """Get all aircraft."""
    sql = """
        SELECT id, registration, manufacturer, size, 
               economy_rows, economy_cols, business_rows, business_cols, purchased_date
        FROM aircraft
        ORDER BY manufacturer, registration
    """
    return execute_query(sql)


def get_available_aircraft(departure_datetime, arrival_datetime):
    """
    Get aircraft not assigned to flights overlapping with the given time window.
    """
    sql = """
        SELECT a.id, a.registration, a.manufacturer, a.size,
               a.economy_rows, a.economy_cols, a.business_rows, a.business_cols
        FROM aircraft a
        WHERE a.id NOT IN (
            SELECT f.aircraft_id
            FROM flights f
            WHERE f.status IN ('active', 'full')
              AND NOT (f.arrival_datetime <= %s OR f.departure_datetime >= %s)
        )
        ORDER BY a.manufacturer, a.registration
    """
    return execute_query(sql, (departure_datetime, arrival_datetime))


def count_aircraft():
    """Count total aircraft."""
    sql = "SELECT COUNT(*) AS count FROM aircraft"
    result = execute_query(sql, fetch_one=True)
    return result['count'] if result else 0


def get_seat_map(aircraft_id):
    """Get the seat map for an aircraft."""
    sql = """
        SELECT id, aircraft_id, seat_code, seat_class, row_num, col_letter
        FROM seat_map
        WHERE aircraft_id = %s
        ORDER BY seat_class DESC, row_num, col_letter
    """
    return execute_query(sql, (aircraft_id,))
