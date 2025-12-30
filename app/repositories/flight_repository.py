"""
FLYTAU Flight Repository
Database access for flights, routes, and flight seats
"""
from app.db import execute_query
import random
import string


# ============ ROUTE OPERATIONS ============

def get_all_routes():
    """Get all routes."""
    sql = """
        SELECT id, origin, destination, duration_minutes
        FROM routes
        ORDER BY origin, destination
    """
    return execute_query(sql)


def get_route_by_cities(origin, destination):
    """Get route by origin and destination."""
    sql = """
        SELECT id, origin, destination, duration_minutes
        FROM routes
        WHERE origin = %s AND destination = %s
    """
    return execute_query(sql, (origin, destination), fetch_one=True)


def get_route_by_id(route_id):
    """Get route by ID."""
    sql = """
        SELECT id, origin, destination, duration_minutes
        FROM routes
        WHERE id = %s
    """
    return execute_query(sql, (route_id,), fetch_one=True)


# ============ FLIGHT OPERATIONS ============

def search_flights(departure_date=None, origin=None, destination=None, status=None):
    """Search flights with filters."""
    sql = """
        SELECT f.id, f.flight_number, f.departure_datetime, f.arrival_datetime,
               f.status, f.economy_price, f.business_price,
               r.origin, r.destination, r.duration_minutes,
               a.registration AS aircraft_registration, a.manufacturer, a.size AS aircraft_size
        FROM flights f
        JOIN routes r ON f.route_id = r.id
        JOIN aircraft a ON f.aircraft_id = a.id
        WHERE 1=1
    """
    params = []
    
    if departure_date:
        sql += " AND DATE(f.departure_datetime) = %s"
        params.append(departure_date)
    
    if origin:
        sql += " AND r.origin = %s"
        params.append(origin)
    
    if destination:
        sql += " AND r.destination = %s"
        params.append(destination)
    
    if status:
        sql += " AND f.status = %s"
        params.append(status)
    
    sql += " ORDER BY f.departure_datetime"
    
    return execute_query(sql, tuple(params) if params else None)


def get_flight_by_id(flight_id):
    """Get flight with all details."""
    sql = """
        SELECT f.id, f.flight_number, f.departure_datetime, f.arrival_datetime,
               f.status, f.economy_price, f.business_price,
               f.aircraft_id, f.route_id,
               r.origin, r.destination, r.duration_minutes,
               a.registration AS aircraft_registration, a.manufacturer, 
               a.size AS aircraft_size
        FROM flights f
        JOIN routes r ON f.route_id = r.id
        JOIN aircraft a ON f.aircraft_id = a.id
        WHERE f.id = %s
    """
    return execute_query(sql, (flight_id,), fetch_one=True)


def get_all_flights(status_filter=None):
    """Get all flights, optionally filtered by status."""
    sql = """
        SELECT f.id, f.flight_number, f.departure_datetime, f.arrival_datetime,
               f.status, f.economy_price, f.business_price,
               r.origin, r.destination,
               a.registration AS aircraft_registration, a.manufacturer, a.size AS aircraft_size
        FROM flights f
        JOIN routes r ON f.route_id = r.id
        JOIN aircraft a ON f.aircraft_id = a.id
    """
    params = []
    
    if status_filter:
        sql += " WHERE f.status = %s"
        params.append(status_filter)
    
    sql += " ORDER BY f.departure_datetime DESC"
    
    return execute_query(sql, tuple(params) if params else None)


def create_flight(flight_number, aircraft_id, route_id, departure_datetime, 
                  arrival_datetime, status, economy_price, business_price):
    """Create a new flight."""
    sql = """
        INSERT INTO flights (flight_number, aircraft_id, route_id, departure_datetime,
                            arrival_datetime, status, economy_price, business_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(sql, (flight_number, aircraft_id, route_id, departure_datetime,
                               arrival_datetime, status, economy_price, business_price), commit=True)


def update_flight_status(flight_id, new_status):
    """Update a flight's status."""
    sql = "UPDATE flights SET status = %s WHERE id = %s"
    return execute_query(sql, (new_status, flight_id), commit=True)


def count_flights():
    """Count total flights."""
    sql = "SELECT COUNT(*) AS count FROM flights"
    result = execute_query(sql, fetch_one=True)
    return result['count'] if result else 0


def count_flights_by_status(status):
    """Count flights by status."""
    sql = "SELECT COUNT(*) AS count FROM flights WHERE status = %s"
    result = execute_query(sql, (status,), fetch_one=True)
    return result['count'] if result else 0


def generate_flight_number():
    """Generate a unique flight number."""
    # Format: FT followed by 3 digits
    while True:
        number = 'FT' + ''.join(random.choices(string.digits, k=3))
        sql = "SELECT id FROM flights WHERE flight_number = %s"
        if not execute_query(sql, (number,), fetch_one=True):
            return number


# ============ FLIGHT SEAT OPERATIONS ============

def get_flight_seats(flight_id):
    """Get all seats for a flight."""
    sql = """
        SELECT id, flight_id, seat_code, seat_class, row_num, col_letter, status, order_line_id
        FROM flight_seats
        WHERE flight_id = %s
        ORDER BY seat_class DESC, row_num, col_letter
    """
    return execute_query(sql, (flight_id,))


def get_seat_counts(flight_id):
    """Get available and total seat counts per class."""
    sql = """
        SELECT 
            seat_class,
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) AS available
        FROM flight_seats
        WHERE flight_id = %s
        GROUP BY seat_class
    """
    results = execute_query(sql, (flight_id,))
    
    counts = {}
    for row in results:
        counts[row['seat_class']] = {
            'total': row['total'],
            'available': row['available']
        }
    
    return counts


def get_seats_by_codes(flight_id, seat_codes):
    """Get specific seats by their codes."""
    if not seat_codes:
        return []
    
    placeholders = ', '.join(['%s'] * len(seat_codes))
    sql = f"""
        SELECT fs.id, fs.flight_id, fs.seat_code, fs.seat_class, fs.row_num, 
               fs.col_letter, fs.status,
               CASE WHEN fs.seat_class = 'economy' THEN f.economy_price 
                    ELSE f.business_price END AS price
        FROM flight_seats fs
        JOIN flights f ON fs.flight_id = f.id
        WHERE fs.flight_id = %s AND fs.seat_code IN ({placeholders})
    """
    return execute_query(sql, (flight_id,) + tuple(seat_codes))


def get_seat_by_id(seat_id):
    """Get a seat by ID."""
    sql = """
        SELECT id, flight_id, seat_code, seat_class, row_num, col_letter, status, order_line_id
        FROM flight_seats
        WHERE id = %s
    """
    return execute_query(sql, (seat_id,), fetch_one=True)


def create_flight_seat(flight_id, seat_code, seat_class, row_num, col_letter, price):
    """Create a flight seat."""
    sql = """
        INSERT INTO flight_seats (flight_id, seat_code, seat_class, row_num, col_letter, status)
        VALUES (%s, %s, %s, %s, %s, 'available')
    """
    return execute_query(sql, (flight_id, seat_code, seat_class, row_num, col_letter), commit=True)


def update_seat_status(seat_id, status, order_line_id=None):
    """Update a seat's status and order line reference."""
    sql = """
        UPDATE flight_seats 
        SET status = %s, order_line_id = %s 
        WHERE id = %s
    """
    return execute_query(sql, (status, order_line_id, seat_id), commit=True)


def release_seat(seat_id):
    """Release a seat (set to available, clear order line)."""
    sql = """
        UPDATE flight_seats 
        SET status = 'available', order_line_id = NULL 
        WHERE id = %s
    """
    return execute_query(sql, (seat_id,), commit=True)
