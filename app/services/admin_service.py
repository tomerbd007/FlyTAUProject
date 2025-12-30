"""
FLYTAU Admin Service
Handles flight creation, cancellation, crew management, and admin operations
"""
from datetime import datetime, timedelta
from decimal import Decimal
from app.repositories import (
    flight_repository, 
    aircraft_repository, 
    crew_repository,
    order_repository
)
from app import db


# Hours before departure when flight cancellation is no longer allowed
FLIGHT_CANCELLATION_CUTOFF_HOURS = 72

# Flight duration threshold for long flights (in minutes)
LONG_FLIGHT_THRESHOLD_MINUTES = 360  # 6 hours


def get_dashboard_stats():
    """
    Get summary statistics for admin dashboard.
    
    Returns:
        Dict with various statistics
    """
    return {
        'total_flights': flight_repository.count_flights(),
        'active_flights': flight_repository.count_flights_by_status('active'),
        'total_orders': order_repository.count_orders(),
        'active_orders': order_repository.count_orders_by_status('active'),
        'total_aircraft': aircraft_repository.count_aircraft(),
        'total_crew': crew_repository.count_crew()
    }


def get_all_flights(status_filter=None):
    """
    Get all flights, optionally filtered by status.
    
    Args:
        status_filter: Optional status to filter by
    
    Returns:
        List of flight dicts
    """
    return flight_repository.get_all_flights(status_filter)


def get_route(origin, destination):
    """Get route by origin and destination."""
    return flight_repository.get_route_by_cities(origin, destination)


def compute_flight_times(departure_date, departure_time, duration_minutes):
    """
    Compute departure and arrival datetimes.
    
    Args:
        departure_date: Date string (YYYY-MM-DD)
        departure_time: Time string (HH:MM)
        duration_minutes: Flight duration in minutes
    
    Returns:
        Tuple of (departure_datetime, arrival_datetime)
    """
    departure_str = f"{departure_date} {departure_time}"
    departure_datetime = datetime.strptime(departure_str, "%Y-%m-%d %H:%M")
    arrival_datetime = departure_datetime + timedelta(minutes=duration_minutes)
    
    return (departure_datetime, arrival_datetime)


def get_aircraft_by_id(aircraft_id):
    """Get aircraft by ID."""
    return aircraft_repository.get_aircraft_by_id(aircraft_id)


def get_available_aircraft(departure_datetime, arrival_datetime, is_long_flight):
    """
    Get aircraft available for a flight.
    
    Args:
        departure_datetime: Flight departure time (ISO string or datetime)
        arrival_datetime: Flight arrival time (ISO string or datetime)
        is_long_flight: Whether this is a long flight (> 6 hours)
    
    Returns:
        List of available aircraft dicts
    """
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    # Get all aircraft not assigned to overlapping flights
    aircraft = aircraft_repository.get_available_aircraft(
        departure_datetime, 
        arrival_datetime
    )
    
    # Filter: small aircraft can only do short flights
    if is_long_flight:
        aircraft = [a for a in aircraft if a['size'] == 'large']
    
    return aircraft


def get_available_pilots(departure_datetime, arrival_datetime, is_long_flight):
    """
    Get pilots available for a flight.
    
    Args:
        departure_datetime: Flight departure time
        arrival_datetime: Flight arrival time
        is_long_flight: Whether this is a long flight
    
    Returns:
        List of available pilot dicts
    """
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    pilots = crew_repository.get_available_employees(
        role='pilot',
        departure_datetime=departure_datetime,
        arrival_datetime=arrival_datetime
    )
    
    # Filter by certification for long flights
    if is_long_flight:
        pilots = [p for p in pilots if p['long_flight_certified']]
    
    return pilots


def get_available_attendants(departure_datetime, arrival_datetime, is_long_flight):
    """
    Get attendants available for a flight.
    
    Args:
        departure_datetime: Flight departure time
        arrival_datetime: Flight arrival time
        is_long_flight: Whether this is a long flight
    
    Returns:
        List of available attendant dicts
    """
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    attendants = crew_repository.get_available_employees(
        role='attendant',
        departure_datetime=departure_datetime,
        arrival_datetime=arrival_datetime
    )
    
    # Filter by certification for long flights
    if is_long_flight:
        attendants = [a for a in attendants if a['long_flight_certified']]
    
    return attendants


def create_flight(route_id, aircraft_id, departure_datetime, arrival_datetime,
                  economy_price, business_price, pilot_ids, attendant_ids):
    """
    Create a new flight with crew assignments and seats.
    
    Args:
        route_id: Route ID
        aircraft_id: Aircraft ID
        departure_datetime: Departure datetime (ISO string or datetime)
        arrival_datetime: Arrival datetime (ISO string or datetime)
        economy_price: Economy class ticket price
        business_price: Business class ticket price (or None for small aircraft)
        pilot_ids: List of pilot employee IDs
        attendant_ids: List of attendant employee IDs
    
    Returns:
        New flight ID
    """
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    try:
        # Generate flight number
        flight_number = flight_repository.generate_flight_number()
        
        # Create flight record
        flight_id = flight_repository.create_flight(
            flight_number=flight_number,
            aircraft_id=aircraft_id,
            route_id=route_id,
            departure_datetime=departure_datetime,
            arrival_datetime=arrival_datetime,
            status='active',
            economy_price=economy_price,
            business_price=business_price
        )
        
        # Create crew assignments
        all_crew_ids = pilot_ids + attendant_ids
        for employee_id in all_crew_ids:
            crew_repository.create_crew_assignment(flight_id, int(employee_id))
        
        # Create flight seats from aircraft seat map
        seat_map = aircraft_repository.get_seat_map(aircraft_id)
        for seat in seat_map:
            price = economy_price if seat['seat_class'] == 'economy' else business_price
            flight_repository.create_flight_seat(
                flight_id=flight_id,
                seat_code=seat['seat_code'],
                seat_class=seat['seat_class'],
                row_num=seat['row_num'],
                col_letter=seat['col_letter'],
                price=price
            )
        
        db.commit()
        return flight_id
        
    except Exception as e:
        db.rollback()
        raise


def can_cancel_flight(flight):
    """
    Check if a flight can be canceled (72h rule).
    
    Args:
        flight: Flight dict
    
    Returns:
        Tuple of (can_cancel: bool, message: str)
    """
    if flight['status'] == 'canceled':
        return (False, "Flight is already canceled.")
    
    if flight['status'] == 'occurred':
        return (False, "Cannot cancel a flight that has already occurred.")
    
    departure = flight['departure_datetime']
    if isinstance(departure, str):
        departure = datetime.fromisoformat(departure)
    
    cutoff = datetime.utcnow() + timedelta(hours=FLIGHT_CANCELLATION_CUTOFF_HOURS)
    
    if departure <= cutoff:
        return (False, f"Cannot cancel flight within {FLIGHT_CANCELLATION_CUTOFF_HOURS} hours of departure.")
    
    return (True, "")


def get_affected_orders_count(flight_id):
    """Get count of active orders that would be affected by flight cancellation."""
    return order_repository.count_active_orders_for_flight(flight_id)


def cancel_flight(flight_id):
    """
    Cancel a flight and credit all active orders.
    
    Args:
        flight_id: Flight ID
    """
    try:
        # Update flight status
        flight_repository.update_flight_status(flight_id, 'canceled')
        
        # Get all active orders for this flight
        orders = order_repository.get_active_orders_for_flight(flight_id)
        
        # Credit each order (set paid_total to 0, status to system_canceled)
        for order in orders:
            order_repository.update_order_status(
                order['id'],
                status='system_canceled',
                paid_total=0
            )
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise
