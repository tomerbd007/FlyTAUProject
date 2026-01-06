"""
FLYTAU Flight Repository
Database access for Flights

Schema:
- Flights: FlightId (PK), Airplanes_AirplaneId (PK), Status, EconomyPrice, BusinessPrice,
           Duration, DepartureDate, DepartureHour, OriginPort, DestPort

Note: 
- No separate routes table - origin/destination stored directly in Flights
- Composite primary key: (FlightId, Airplanes_AirplaneId)
- Seat availability tracked via Tickets table (taken seats)
"""
from app.db import execute_query
from app.repositories.aircraft_repository import get_airplane_by_id, generate_seat_map
import random
import string


# ============ FLIGHT OPERATIONS ============

def get_all_unique_cities():
    """Get all unique cities used as origin or destination."""
    sql = """
        SELECT DISTINCT city FROM (
            SELECT OriginPort AS city FROM Flights
            UNION
            SELECT DestPort AS city FROM Flights
        ) AS cities
        ORDER BY city
    """
    results = execute_query(sql)
    return [row['city'] for row in results] if results else []


def get_all_routes():
    """
    Get all unique origin-destination pairs from flights.
    
    Returns:
        List of dicts with 'origin' and 'destination' keys
    """
    sql = """
        SELECT DISTINCT OriginPort as origin, DestPort as destination
        FROM Flights
        ORDER BY OriginPort, DestPort
    """
    results = execute_query(sql)
    return results if results else []


def search_flights(departure_date=None, origin=None, destination=None, status=None):
    """
    Search flights with filters.
    
    Args:
        departure_date: Filter by DepartureDate (DATE or 'YYYY-MM-DD')
        origin: Filter by OriginPort
        destination: Filter by DestPort
        status: Filter by Status
    """
    sql = """
        SELECT f.FlightId, f.Airplanes_AirplaneId, f.Status, 
               f.EconomyPrice, f.BusinessPrice, f.Duration,
               f.DepartureDate, f.DepartureHour, f.OriginPort, f.DestPort,
               a.Manufacturer, a.`Couch (Rows, Cols)` as EconomyConfig,
               a.`Business (Rows, Cols)` as BusinessConfig
        FROM Flights f
        JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
        WHERE 1=1
    """
    params = []
    
    if departure_date:
        sql += " AND f.DepartureDate = %s"
        params.append(departure_date)
    
    if origin:
        sql += " AND f.OriginPort = %s"
        params.append(origin)
    
    if destination:
        sql += " AND f.DestPort = %s"
        params.append(destination)
    
    if status:
        sql += " AND f.Status = %s"
        params.append(status)
    
    sql += " ORDER BY f.DepartureDate, f.DepartureHour"
    
    return execute_query(sql, tuple(params) if params else None)


def get_flight_by_id(flight_id, airplane_id=None):
    """
    Get flight with all details.
    
    Args:
        flight_id: FlightId
        airplane_id: Airplanes_AirplaneId (optional if FlightId is unique)
    """
    if airplane_id:
        sql = """
            SELECT f.FlightId, f.Airplanes_AirplaneId, f.Status, 
                   f.EconomyPrice, f.BusinessPrice, f.Duration,
                   f.DepartureDate, f.DepartureHour, f.OriginPort, f.DestPort,
                   a.Manufacturer, a.`Couch (Rows, Cols)` as EconomyConfig,
                   a.`Business (Rows, Cols)` as BusinessConfig, a.PurchaseDate
            FROM Flights f
            JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
            WHERE f.FlightId = %s AND f.Airplanes_AirplaneId = %s
        """
        return execute_query(sql, (flight_id, airplane_id), fetch_one=True)
    else:
        # If airplane_id not provided, get the first match
        sql = """
            SELECT f.FlightId, f.Airplanes_AirplaneId, f.Status, 
                   f.EconomyPrice, f.BusinessPrice, f.Duration,
                   f.DepartureDate, f.DepartureHour, f.OriginPort, f.DestPort,
                   a.Manufacturer, a.`Couch (Rows, Cols)` as EconomyConfig,
                   a.`Business (Rows, Cols)` as BusinessConfig, a.PurchaseDate
            FROM Flights f
            JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
            WHERE f.FlightId = %s
        """
        return execute_query(sql, (flight_id,), fetch_one=True)


def get_all_flights(status_filter=None):
    """Get all flights, optionally filtered by status."""
    sql = """
        SELECT f.FlightId, f.Airplanes_AirplaneId, f.Status, 
               f.EconomyPrice, f.BusinessPrice, f.Duration,
               f.DepartureDate, f.DepartureHour, f.OriginPort, f.DestPort,
               a.Manufacturer
        FROM Flights f
        JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
    """
    params = []
    
    if status_filter:
        sql += " WHERE f.Status = %s"
        params.append(status_filter)
    
    sql += " ORDER BY f.DepartureDate DESC, f.DepartureHour DESC"
    
    return execute_query(sql, tuple(params) if params else None)


def create_flight(flight_id, airplane_id, departure_date, departure_hour,
                  origin_port, dest_port, duration, status, economy_price, business_price):
    """
    Create a new flight.
    
    Args:
        flight_id: Unique FlightId (e.g., "TAU101")
        airplane_id: AirplaneId of the assigned airplane
        departure_date: DepartureDate (DATE or 'YYYY-MM-DD')
        departure_hour: DepartureHour (e.g., "08:00" or "14:30")
        origin_port: Origin airport/city
        dest_port: Destination airport/city
        duration: Duration in minutes
        status: Flight status (e.g., 'scheduled', 'active', 'cancelled')
        economy_price: Economy ticket price
        business_price: Business ticket price
    """
    sql = """
        INSERT INTO Flights (FlightId, Airplanes_AirplaneId, DepartureDate, DepartureHour,
                            OriginPort, DestPort, Duration, Status, EconomyPrice, BusinessPrice)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(sql, (flight_id, airplane_id, departure_date, departure_hour,
                               origin_port, dest_port, duration, status, 
                               economy_price, business_price), commit=True)


def update_flight_status(flight_id, airplane_id, new_status):
    """Update a flight's status."""
    sql = "UPDATE Flights SET Status = %s WHERE FlightId = %s AND Airplanes_AirplaneId = %s"
    return execute_query(sql, (new_status, flight_id, airplane_id), commit=True)


def count_flights():
    """Count total flights."""
    sql = "SELECT COUNT(*) AS count FROM Flights"
    result = execute_query(sql, fetch_one=True)
    return result['count'] if result else 0


def count_flights_by_status(status):
    """Count flights by status."""
    sql = "SELECT COUNT(*) AS count FROM Flights WHERE Status = %s"
    result = execute_query(sql, (status,), fetch_one=True)
    return result['count'] if result else 0


def generate_flight_number():
    """Generate a unique flight number in format TAU###."""
    while True:
        number = 'TAU' + ''.join(random.choices(string.digits, k=3))
        sql = "SELECT FlightId FROM Flights WHERE FlightId = %s"
        if not execute_query(sql, (number,), fetch_one=True):
            return number


# ============ SEAT OPERATIONS (via Tickets table) ============

def get_flight_seats(flight_id, airplane_id):
    """
    Get all seats for a flight with availability status.
    
    Generates seat map from airplane config and marks taken seats from Tickets table.
    """
    # Get the airplane to generate seat map
    airplane = get_airplane_by_id(airplane_id)
    if not airplane:
        return []
    
    # Generate all possible seats
    all_seats = generate_seat_map(airplane_id)
    
    # Get taken seats from Tickets table
    sql = """
        SELECT t.RowNum, t.Seat, t.Class
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE t.Flights_FlightId = %s 
          AND t.Flights_Airplanes_AirplaneId = %s
          AND o.Status != 'cancelled'
    """
    taken_tickets = execute_query(sql, (flight_id, airplane_id))
    
    # Create a set of taken seat codes
    taken_seats = set()
    if taken_tickets:
        for ticket in taken_tickets:
            seat_code = f"{ticket['RowNum']}{ticket['Seat']}"
            taken_seats.add(seat_code)
    
    # Get flight for pricing
    flight = get_flight_by_id(flight_id, airplane_id)
    economy_price = float(flight['EconomyPrice']) if flight and flight.get('EconomyPrice') else 0
    business_price = float(flight['BusinessPrice']) if flight and flight.get('BusinessPrice') else 0
    
    # Add status and price to each seat
    for seat in all_seats:
        seat['status'] = 'taken' if seat['seat_code'] in taken_seats else 'available'
        seat['price'] = business_price if seat['seat_class'] == 'business' else economy_price
        seat['flight_id'] = flight_id
        seat['airplane_id'] = airplane_id
    
    return all_seats


def get_seat_counts(flight_id, airplane_id):
    """Get available and total seat counts per class."""
    airplane = get_airplane_by_id(airplane_id)
    if not airplane:
        return {}
    
    # Get taken seat counts from Tickets
    sql = """
        SELECT t.Class, COUNT(*) as taken_count
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE t.Flights_FlightId = %s 
          AND t.Flights_Airplanes_AirplaneId = %s
          AND o.Status != 'cancelled'
        GROUP BY t.Class
    """
    taken_results = execute_query(sql, (flight_id, airplane_id))
    
    taken_by_class = {}
    if taken_results:
        for row in taken_results:
            taken_by_class[row['Class'].lower()] = row['taken_count']
    
    return {
        'business': {
            'total': airplane['business_seats'],
            'available': airplane['business_seats'] - taken_by_class.get('business', 0),
            'taken': taken_by_class.get('business', 0)
        },
        'economy': {
            'total': airplane['economy_seats'],
            'available': airplane['economy_seats'] - taken_by_class.get('economy', 0),
            'taken': taken_by_class.get('economy', 0)
        }
    }


def get_seat_availability(flight_id, airplane_id):
    """
    Get seat availability for a flight.
    Alias for get_seat_counts for backward compatibility.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID
    
    Returns:
        Dict with seat availability by class
    """
    return get_seat_counts(flight_id, airplane_id)


def get_taken_seats(flight_id, airplane_id):
    """
    Get list of taken seats for a flight.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID
    
    Returns:
        List of dicts with RowNum, Seat, Class
    """
    sql = """
        SELECT t.RowNum, t.Seat, t.Class
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE t.Flights_FlightId = %s 
          AND t.Flights_Airplanes_AirplaneId = %s
          AND o.Status != 'cancelled'
    """
    results = execute_query(sql, (flight_id, airplane_id))
    return results if results else []


def get_available_seat_codes(flight_id, airplane_id, seat_class=None):
    """
    Get list of available seat codes for a flight.
    
    Args:
        flight_id: FlightId
        airplane_id: Airplanes_AirplaneId
        seat_class: Optional filter by 'business' or 'economy'
    """
    seats = get_flight_seats(flight_id, airplane_id)
    available = [s for s in seats if s['status'] == 'available']
    
    if seat_class:
        available = [s for s in available if s['seat_class'] == seat_class.lower()]
    
    return available


def is_seat_available(flight_id, airplane_id, row_num, seat_letter):
    """Check if a specific seat is available."""
    sql = """
        SELECT 1
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE t.Flights_FlightId = %s 
          AND t.Flights_Airplanes_AirplaneId = %s
          AND t.RowNum = %s
          AND t.Seat = %s
          AND o.Status != 'cancelled'
    """
    result = execute_query(sql, (flight_id, airplane_id, row_num, seat_letter), fetch_one=True)
    return result is None  # Available if no ticket found
