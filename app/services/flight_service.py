"""
FLYTAU Flight Service
Handles flight search, seat availability, and flight details

Schema:
- Flights: FlightId + Airplanes_AirplaneId (composite PK), OriginPort, DestPort, 
           DepartureDate, DepartureHour, Duration, Status
- Airplanes: AirplaneId (PK), Manufacturer, `Couch (Rows, Cols)`, `Business (Rows, Cols)`
- Tickets: Used to track sold seats (RowNum, Seat per flight)
"""
from app.repositories import flight_repository, aircraft_repository


def search_available_flights(departure_date=None, origin=None, destination=None):
    """
    Search for available flights based on criteria.
    Only returns flights with status 'active'.
    
    Args:
        departure_date: Date string (YYYY-MM-DD)
        origin: Origin airport code
        destination: Destination airport code
    
    Returns:
        List of matching flight dicts with seat availability
    """
    flights = flight_repository.search_flights(
        departure_date=departure_date,
        origin=origin,
        destination=destination,
        status='active'
    )
    
    # Add seat availability to each flight
    for flight in flights:
        availability = flight_repository.get_seat_availability(
            flight['FlightId'], 
            flight['Airplanes_AirplaneId']
        )
        flight['seat_availability'] = availability
    
    return flights


def get_flight_details(flight_id, airplane_id):
    """
    Get detailed information about a flight.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID
    
    Returns:
        Flight dict with aircraft info and seat availability, or None
    """
    flight = flight_repository.get_flight_by_id(flight_id, airplane_id)
    if flight:
        flight = dict(flight)
        flight['seat_availability'] = flight_repository.get_seat_availability(flight_id, airplane_id)
    return flight


def get_seat_availability(flight_id, airplane_id):
    """
    Get seat availability for a flight.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID
    
    Returns:
        Dict with seat availability: {'economy': {'available': X, 'total': Y}, 'business': {...}}
    """
    return flight_repository.get_seat_availability(flight_id, airplane_id)


def get_taken_seats(flight_id, airplane_id):
    """
    Get list of taken seats for a flight.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID
    
    Returns:
        List of dicts with RowNum, Seat, Class
    """
    return flight_repository.get_taken_seats(flight_id, airplane_id)


def get_available_seats_for_class(flight_id, airplane_id, seat_class):
    """
    Get list of available seats for a specific class.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID
        seat_class: 'business' or 'economy'
    
    Returns:
        List of available seat dicts (row, col combinations)
    """
    # Get airplane seat configuration
    airplane = aircraft_repository.get_airplane_by_id(airplane_id)
    if not airplane:
        return []
    
    # Get taken seats for this flight
    taken_seats = flight_repository.get_taken_seats(flight_id, airplane_id)
    taken_set = {(t['RowNum'], t['Seat']) for t in taken_seats}
    
    available = []
    
    if seat_class == 'business' and airplane.get('business_rows'):
        rows = airplane['business_rows']
        cols = airplane['business_cols']
        for row in range(1, rows + 1):
            for col_idx in range(cols):
                col_letter = chr(65 + col_idx)  # A, B, C, ...
                if (row, col_letter) not in taken_set:
                    available.append({
                        'row': row,
                        'seat': col_letter,
                        'seat_code': f"{row}{col_letter}",
                        'class': 'business'
                    })
    
    elif seat_class == 'economy':
        # Economy rows start after business rows
        start_row = (airplane.get('business_rows') or 0) + 1
        rows = airplane.get('economy_rows', 0)
        cols = airplane.get('economy_cols', 0)
        
        for row in range(start_row, start_row + rows):
            for col_idx in range(cols):
                col_letter = chr(65 + col_idx)
                if (row, col_letter) not in taken_set:
                    available.append({
                        'row': row,
                        'seat': col_letter,
                        'seat_code': f"{row}{col_letter}",
                        'class': 'economy'
                    })
    
    return available


def build_seat_map(flight_id, airplane_id):
    """
    Build a seat map for display showing all seats and their status.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID
    
    Returns:
        Dict with seat map organized by class and row
    """
    airplane = aircraft_repository.get_airplane_by_id(airplane_id)
    if not airplane:
        return None
    
    taken_seats = flight_repository.get_taken_seats(flight_id, airplane_id)
    taken_set = {(t['RowNum'], t['Seat']) for t in taken_seats}
    
    seat_map = {
        'business': None,
        'economy': {'rows': {}}
    }
    
    # Build business class section
    if airplane.get('business_rows'):
        seat_map['business'] = {'rows': {}}
        for row in range(1, airplane['business_rows'] + 1):
            seat_map['business']['rows'][row] = []
            for col_idx in range(airplane['business_cols']):
                col_letter = chr(65 + col_idx)
                status = 'taken' if (row, col_letter) in taken_set else 'available'
                seat_map['business']['rows'][row].append({
                    'code': f"{row}{col_letter}",
                    'col': col_letter,
                    'status': status
                })
    
    # Build economy class section
    start_row = (airplane.get('business_rows') or 0) + 1
    for row in range(start_row, start_row + airplane.get('economy_rows', 0)):
        seat_map['economy']['rows'][row] = []
        for col_idx in range(airplane.get('economy_cols', 0)):
            col_letter = chr(65 + col_idx)
            status = 'taken' if (row, col_letter) in taken_set else 'available'
            seat_map['economy']['rows'][row].append({
                'code': f"{row}{col_letter}",
                'col': col_letter,
                'status': status
            })
    
    return seat_map


def update_flight_status(flight_id, airplane_id, new_status):
    """
    Update a flight's status.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID
        new_status: New status value
    """
    flight_repository.update_flight_status(flight_id, airplane_id, new_status)


def check_flight_full(flight_id, airplane_id):
    """
    Check if a flight is fully booked and update status if so.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID
    """
    availability = get_seat_availability(flight_id, airplane_id)
    
    total_available = 0
    for seat_class in availability.values():
        if seat_class:
            total_available += seat_class.get('available', 0)
    
    if total_available == 0:
        update_flight_status(flight_id, airplane_id, 'full')
        if seat_class:
            total_available += seat_class.get('available', 0)
    
    if total_available == 0:
        update_flight_status(flight_id, 'full')
