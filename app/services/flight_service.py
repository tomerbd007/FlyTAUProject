"""
FLYTAU Flight Service
Handles flight search, seat availability, and flight details
"""
from app.repositories import flight_repository, aircraft_repository


def get_all_routes():
    """Get all available routes for search dropdowns."""
    return flight_repository.get_all_routes()


def search_available_flights(departure_date=None, origin=None, destination=None):
    """
    Search for available flights based on criteria.
    Only returns flights with status 'active'.
    
    Args:
        departure_date: Date string (YYYY-MM-DD)
        origin: Origin city/airport
        destination: Destination city/airport
    
    Returns:
        List of matching flight dicts
    """
    return flight_repository.search_flights(
        departure_date=departure_date,
        origin=origin,
        destination=destination,
        status='active'
    )


def get_flight_details(flight_id):
    """
    Get detailed information about a flight.
    
    Args:
        flight_id: Flight ID
    
    Returns:
        Flight dict with route and aircraft info, or None
    """
    return flight_repository.get_flight_by_id(flight_id)


def get_seat_availability_counts(flight_id):
    """
    Get count of available seats per class for a flight.
    
    Args:
        flight_id: Flight ID
    
    Returns:
        Dict with seat counts: {'economy': {'available': X, 'total': Y}, 'business': {...}}
    """
    return flight_repository.get_seat_counts(flight_id)


def get_flight_seats(flight_id):
    """
    Get all seats for a flight with their status.
    
    Args:
        flight_id: Flight ID
    
    Returns:
        List of seat dicts
    """
    return flight_repository.get_flight_seats(flight_id)


def get_seats_by_codes(flight_id, seat_codes):
    """
    Get specific seats by their codes.
    
    Args:
        flight_id: Flight ID
        seat_codes: List of seat codes (e.g., ['1A', '1B'])
    
    Returns:
        List of seat dicts with price information
    """
    return flight_repository.get_seats_by_codes(flight_id, seat_codes)


def organize_seat_map(seats, aircraft_size):
    """
    Organize seats into a structured map for display.
    
    Args:
        seats: List of seat dicts
        aircraft_size: 'small' or 'large'
    
    Returns:
        Dict with organized seat data by class and row
    """
    seat_map = {
        'economy': {},
        'business': {} if aircraft_size == 'large' else None
    }
    
    for seat in seats:
        seat_class = seat['seat_class']
        row_num = seat['row_num']
        
        if seat_class not in seat_map or seat_map[seat_class] is None:
            continue
        
        if row_num not in seat_map[seat_class]:
            seat_map[seat_class][row_num] = []
        
        seat_map[seat_class][row_num].append({
            'code': seat['seat_code'],
            'col': seat['col_letter'],
            'status': seat['status'],
            'price': seat.get('price', 0)
        })
    
    # Sort rows and columns
    for seat_class in seat_map:
        if seat_map[seat_class]:
            for row in seat_map[seat_class]:
                seat_map[seat_class][row].sort(key=lambda x: x['col'])
    
    return seat_map


def update_flight_status(flight_id, new_status):
    """
    Update a flight's status.
    
    Args:
        flight_id: Flight ID
        new_status: New status value
    """
    flight_repository.update_flight_status(flight_id, new_status)


def check_flight_full(flight_id):
    """
    Check if a flight is fully booked and update status if so.
    
    Args:
        flight_id: Flight ID
    """
    counts = get_seat_availability_counts(flight_id)
    
    total_available = 0
    for seat_class in counts.values():
        if seat_class:
            total_available += seat_class.get('available', 0)
    
    if total_available == 0:
        update_flight_status(flight_id, 'full')
