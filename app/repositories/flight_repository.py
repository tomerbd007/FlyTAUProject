"""All the SQL queries for flights, airports, and routes."""
from app.db import execute_query
from app.repositories.aircraft_repository import get_airplane_by_id, generate_seat_map
import random
import string


def get_all_airports():
    """Grabs all airports, sorted by city."""
    sql = """
        SELECT Code as code, Name as name, City as city, Country as country
        FROM Airports
        ORDER BY City, Name
    """
    results = execute_query(sql)
    return results if results else []


def get_airport_by_code(code):
    """Looks up an airport by its code."""
    sql = "SELECT Code as code, Name as name, City as city, Country as country FROM Airports WHERE Code = %s"
    results = execute_query(sql, (code,))
    return results[0] if results else None


def get_route(origin, destination):
    """Finds the route between two airports."""
    sql = """
        SELECT RouteId as id, OriginPort as origin, DestPort as destination, 
               DurationMinutes as duration_minutes, DistanceKm as distance_km
        FROM Routes
        WHERE OriginPort = %s AND DestPort = %s
    """
    results = execute_query(sql, (origin, destination))
    return results[0] if results else None


def get_all_routes():
    """Gets every route we have in the system."""
    sql = """
        SELECT RouteId as id, OriginPort as origin, DestPort as destination, 
               DurationMinutes as duration_minutes, DistanceKm as distance_km
        FROM Routes
        ORDER BY OriginPort, DestPort
    """
    results = execute_query(sql)
    return results if results else []


# ============ FLIGHT OPERATIONS ============

def get_all_unique_cities():
    """Lists all the cities that show up in our flight origins/destinations."""
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


def search_flights(departure_date=None, origin=None, destination=None, status=None):
    """Searches for flights with whatever filters you pass in."""
    sql = """
        SELECT f.FlightId, f.Airplanes_AirplaneId, f.Status, 
               f.EconomyPrice, f.BusinessPrice, f.Duration,
               f.DepartureDate, f.DepartureHour, f.OriginPort, f.DestPort,
               a.Manufacturer, a.CouchRows, a.CouchCols,
               a.BusinessRows, a.BusinessCols
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
    """Fetches a specific flight with all its details."""
    if airplane_id:
        sql = """
            SELECT f.FlightId, f.Airplanes_AirplaneId, f.Status, 
                   f.EconomyPrice, f.BusinessPrice, f.Duration,
                   f.DepartureDate, f.DepartureHour, f.OriginPort, f.DestPort,
                   a.Manufacturer, a.CouchRows, a.CouchCols,
                   a.BusinessRows, a.BusinessCols, a.PurchaseDate
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
                   a.Manufacturer, a.CouchRows, a.CouchCols,
                   a.BusinessRows, a.BusinessCols, a.PurchaseDate
            FROM Flights f
            JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
            WHERE f.FlightId = %s
        """
        return execute_query(sql, (flight_id,), fetch_one=True)


def get_all_flights(status_filter=None):
    """Gets all flights, can filter by status if needed."""
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
    """Create a new flight."""
    sql = """
        INSERT INTO Flights (FlightId, Airplanes_AirplaneId, DepartureDate, DepartureHour,
                            OriginPort, DestPort, Duration, Status, EconomyPrice, BusinessPrice)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(sql, (flight_id, airplane_id, departure_date, departure_hour,
                               origin_port, dest_port, duration, status, 
                               economy_price, business_price), commit=True)


def update_flight_status(flight_id, new_status):
    """Update a flight's status."""
    sql = "UPDATE Flights SET Status = %s WHERE FlightId = %s"
    return execute_query(sql, (new_status, flight_id), commit=True)


def update_flight(flight_id, airplane_id, updates):
    """Update flight details."""
    allowed_fields = {
        'status': 'Status',
        'economy_price': 'EconomyPrice',
        'business_price': 'BusinessPrice',
        'departure_date': 'DepartureDate',
        'departure_hour': 'DepartureHour'
    }
    
    set_clauses = []
    params = []
    
    for key, value in updates.items():
        if key in allowed_fields:
            set_clauses.append(f"{allowed_fields[key]} = %s")
            params.append(value)
    
    if not set_clauses:
        return False
    
    params.extend([flight_id, airplane_id])
    sql = f"UPDATE Flights SET {', '.join(set_clauses)} WHERE FlightId = %s AND Airplanes_AirplaneId = %s"
    return execute_query(sql, tuple(params), commit=True)


def update_flight_comprehensive(flight_id, airplane_id, updates):
    """Comprehensive flight update supporting all editable fields."""
    allowed_fields = {
        'status': 'Status',
        'economy_price': 'EconomyPrice',
        'business_price': 'BusinessPrice',
        'departure_date': 'DepartureDate',
        'departure_hour': 'DepartureHour',
        'origin_port': 'OriginPort',
        'dest_port': 'DestPort',
        'duration': 'Duration'
    }
    
    set_clauses = []
    params = []
    
    for key, value in updates.items():
        if key in allowed_fields:
            set_clauses.append(f"{allowed_fields[key]} = %s")
            params.append(value)
    
    if not set_clauses:
        return False
    
    params.extend([flight_id, airplane_id])
    sql = f"UPDATE Flights SET {', '.join(set_clauses)} WHERE FlightId = %s AND Airplanes_AirplaneId = %s"
    return execute_query(sql, tuple(params), commit=True)


def update_flight_with_new_ids(original_flight_id, original_airplane_id, 
                               new_flight_id, new_airplane_id, updates):
    """Update a flight with potentially changed IDs. Updates FK references first."""
    ids_changing = (original_flight_id != new_flight_id or 
                    original_airplane_id != new_airplane_id)
    
    # If IDs aren't changing, just update in place
    if not ids_changing:
        return update_flight_comprehensive(original_flight_id, original_airplane_id, updates)
    
    # Check if the new flight ID already exists
    check_sql = """
        SELECT FlightId FROM Flights 
        WHERE FlightId = %s
    """
    existing = execute_query(check_sql, (new_flight_id,), fetch_one=True)
    if existing:
        raise ValueError(f"Flight {new_flight_id} already exists")
    
    # Get the original flight data
    sql = """
        SELECT FlightId, Airplanes_AirplaneId, DepartureDate, DepartureHour,
               OriginPort, DestPort, Duration, Status, EconomyPrice, BusinessPrice
        FROM Flights
        WHERE FlightId = %s
    """
    original = execute_query(sql, (original_flight_id,), fetch_one=True)
    
    if not original:
        return False
    
    # Step 1: Update all foreign key references FIRST (before changing the flight)
    # This must be done before we can change the flight's primary key
    
    # Update orders (Tickets are linked via orders, so no direct Tickets update needed)
    update_orders_sql = """
        UPDATE orders 
        SET Flights_FlightId = %s
        WHERE Flights_FlightId = %s
    """
    execute_query(update_orders_sql, (
        new_flight_id,
        original_flight_id
    ), commit=True)
    
    # Update pilot assignments
    update_pilots_sql = """
        UPDATE Pilot_has_Flights 
        SET Flights_FlightId = %s
        WHERE Flights_FlightId = %s
    """
    execute_query(update_pilots_sql, (
        new_flight_id,
        original_flight_id
    ), commit=True)
    
    # Update flight attendant assignments
    update_attendants_sql = """
        UPDATE FlightAttendant_has_Flights 
        SET Flights_FlightId = %s
        WHERE Flights_FlightId = %s
    """
    execute_query(update_attendants_sql, (
        new_flight_id,
        original_flight_id
    ), commit=True)
    
    # Update manager edits log
    update_manager_edits_sql = """
        UPDATE Managers_edits_Flights 
        SET Flights_FlightId = %s
        WHERE Flights_FlightId = %s
    """
    execute_query(update_manager_edits_sql, (
        new_flight_id,
        original_flight_id
    ), commit=True)
    
    # Step 2: Now update the flight record itself (including the primary key)
    # Prepare new values
    new_departure_date = updates.get('departure_date', original['DepartureDate'])
    new_departure_hour = updates.get('departure_hour', original['DepartureHour'])
    new_origin = updates.get('origin_port', original['OriginPort'])
    new_dest = updates.get('dest_port', original['DestPort'])
    new_duration = updates.get('duration', original['Duration'])
    new_status = updates.get('status', original['Status'])
    new_economy = updates.get('economy_price', original['EconomyPrice'])
    new_business = updates.get('business_price', original['BusinessPrice'])
    
    update_flight_sql = """
        UPDATE Flights 
        SET FlightId = %s, Airplanes_AirplaneId = %s,
            DepartureDate = %s, DepartureHour = %s,
            OriginPort = %s, DestPort = %s,
            Duration = %s, Status = %s,
            EconomyPrice = %s, BusinessPrice = %s
        WHERE FlightId = %s
    """
    execute_query(update_flight_sql, (
        new_flight_id, new_airplane_id,
        new_departure_date, new_departure_hour,
        new_origin, new_dest,
        new_duration, new_status,
        new_economy, new_business,
        original_flight_id
    ), commit=True)
    
    return True


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
    """Generate a unique 6-character alphanumeric flight number."""
    while True:
        # Generate 6 uppercase alphanumeric characters
        number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        sql = "SELECT FlightId FROM Flights WHERE FlightId = %s"
        if not execute_query(sql, (number,), fetch_one=True):
            return number


def get_flight_seats(flight_id, airplane_id):
    """Get all seats for a flight with availability status."""
    # Get the airplane to generate seat map
    airplane = get_airplane_by_id(airplane_id)
    if not airplane:
        return []
    
    # Generate all possible seats
    all_seats = generate_seat_map(airplane_id)
    
    # Get taken seats from Tickets table (via orders)
    sql = """
        SELECT t.RowNum, t.Seat, t.Class
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE o.Flights_FlightId = %s 
          AND o.Status != 'cancelled'
    """
    taken_tickets = execute_query(sql, (flight_id,))
    
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
    
    # Get taken seat counts from Tickets (via orders)
    sql = """
        SELECT t.Class, COUNT(*) as taken_count
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE o.Flights_FlightId = %s 
          AND o.Status != 'cancelled'
        GROUP BY t.Class
    """
    taken_results = execute_query(sql, (flight_id,))
    
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
    """Get seat availability (alias for get_seat_counts)."""
    return get_seat_counts(flight_id, airplane_id)


def get_taken_seats(flight_id, airplane_id=None):
    """Get list of taken seats for a flight."""
    sql = """
        SELECT t.RowNum, t.Seat, t.Class
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE o.Flights_FlightId = %s 
          AND o.Status != 'cancelled'
    """
    results = execute_query(sql, (flight_id,))
    return results if results else []


def get_available_seat_codes(flight_id, airplane_id, seat_class=None):
    """Get list of available seat codes for a flight."""
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
        WHERE o.Flights_FlightId = %s 
          AND t.RowNum = %s
          AND t.Seat = %s
          AND o.Status != 'cancelled'
    """
    result = execute_query(sql, (flight_id, row_num, seat_letter), fetch_one=True)
    return result is None  # Available if no ticket found
