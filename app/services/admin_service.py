"""
FLYTAU Admin Service
Handles flight creation, cancellation, crew management, and admin operations

Schema:
- Flights: FlightId + Airplanes_AirplaneId (composite PK), OriginPort, DestPort,
           DepartureDate, DepartureHour, Duration, Status
- Pilot_has_Flights, FlightAttendant_has_Flights: Junction tables for crew assignments
- Managers_edits_Flights: Audit trail for manager edits
"""
from datetime import datetime, timedelta
from decimal import Decimal
from app.repositories import (
    flight_repository, 
    aircraft_repository, 
    crew_repository,
    order_repository
)


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
        'confirmed_orders': order_repository.count_orders_by_status('confirmed'),
        'total_aircraft': aircraft_repository.count_airplanes(),
        'total_revenue': order_repository.get_total_revenue()
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


def compute_flight_times(departure_date, departure_time, duration_minutes):
    """
    Compute departure datetime and arrival datetime.
    
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


def is_long_flight(duration_minutes):
    """Check if a flight is considered a long flight."""
    return duration_minutes > LONG_FLIGHT_THRESHOLD_MINUTES


def get_airplane_by_id(airplane_id):
    """Get airplane by ID."""
    return aircraft_repository.get_airplane_by_id(airplane_id)


def get_available_airplanes(departure_datetime, arrival_datetime, for_long_flight=False):
    """
    Get airplanes available for a flight.
    
    Args:
        departure_datetime: Flight departure time
        arrival_datetime: Flight arrival time
        for_long_flight: Whether this is a long flight (> 6 hours)
    
    Returns:
        List of available airplane dicts
    """
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    airplanes = aircraft_repository.get_available_airplanes(
        departure_datetime, 
        arrival_datetime
    )
    
    # Note: If small planes can't do long flights, filter them here
    # (depends on business rules - current schema doesn't indicate this)
    
    return airplanes


def get_available_pilots(departure_datetime, arrival_datetime, for_long_flight=False):
    """
    Get pilots available for a flight.
    
    Args:
        departure_datetime: Flight departure time
        arrival_datetime: Flight arrival time
        for_long_flight: Whether this is a long flight
    
    Returns:
        List of available pilot dicts
    """
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    pilots = crew_repository.get_available_pilots(
        departure_datetime=departure_datetime,
        arrival_datetime=arrival_datetime
    )
    
    # Filter by long flight certification if needed
    if for_long_flight:
        pilots = [p for p in pilots if p.get('LongFlightsTraining')]
    
    return pilots


def get_available_attendants(departure_datetime, arrival_datetime, for_long_flight=False):
    """
    Get attendants available for a flight.
    
    Args:
        departure_datetime: Flight departure time
        arrival_datetime: Flight arrival time
        for_long_flight: Whether this is a long flight
    
    Returns:
        List of available attendant dicts
    """
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    attendants = crew_repository.get_available_attendants(
        departure_datetime=departure_datetime,
        arrival_datetime=arrival_datetime
    )
    
    # Filter by long flight certification if needed
    if for_long_flight:
        attendants = [a for a in attendants if a.get('LongFlightsTraining')]
    
    return attendants


def create_flight(airplane_id, origin, destination, departure_date, departure_hour,
                  duration, economy_price, business_price, pilot_ids, attendant_ids,
                  manager_id=None):
    """
    Create a new flight with crew assignments.
    
    Args:
        airplane_id: Airplane ID
        origin: Origin airport code
        destination: Destination airport code
        departure_date: Departure date (YYYY-MM-DD)
        departure_hour: Departure hour (HH:MM)
        duration: Duration in minutes
        economy_price: Economy class ticket price
        business_price: Business class ticket price (can be None if no business class)
        pilot_ids: List of pilot IDs
        attendant_ids: List of attendant IDs
        manager_id: Manager ID creating this flight (for audit)
    
    Returns:
        New flight ID
    """
    # Generate flight ID
    flight_id = flight_repository.generate_flight_id()
    
    # Create flight record
    flight_repository.create_flight(
        flight_id=flight_id,
        airplane_id=airplane_id,
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        departure_hour=departure_hour,
        duration=duration,
        status='active',
        economy_price=economy_price,
        business_price=business_price
    )
    
    # Create pilot assignments
    for pilot_id in pilot_ids:
        crew_repository.create_pilot_assignment(
            flight_id=flight_id,
            airplane_id=airplane_id,
            pilot_id=pilot_id
        )
    
    # Create attendant assignments
    for attendant_id in attendant_ids:
        crew_repository.create_attendant_assignment(
            flight_id=flight_id,
            airplane_id=airplane_id,
            attendant_id=attendant_id
        )
    
    # Log manager action (if manager_id provided)
    if manager_id:
        log_manager_edit(manager_id, flight_id, airplane_id, 'created')
    
    return flight_id


def log_manager_edit(manager_id, flight_id, airplane_id, action):
    """Log a manager edit action on a flight."""
    from app.db import execute_query
    sql = """
        INSERT INTO Managers_edits_Flights 
        (Managers_ManagerId, Flights_FlightId, Flights_Airplanes_AirplaneId)
        VALUES (%s, %s, %s)
    """
    execute_query(sql, (manager_id, flight_id, airplane_id), commit=True)


def can_cancel_flight(flight):
    """
    Check if a flight can be canceled (72h rule).
    
    Args:
        flight: Flight dict
    
    Returns:
        Tuple of (can_cancel: bool, message: str)
    """
    if flight.get('Status') == 'canceled':
        return (False, "Flight is already canceled.")
    
    if flight.get('Status') == 'occurred':
        return (False, "Cannot cancel a flight that has already occurred.")
    
    departure_date = flight.get('DepartureDate')
    departure_hour = flight.get('DepartureHour')
    
    if not departure_date:
        return (False, "Invalid flight data.")
    
    # Combine date and time
    if isinstance(departure_date, str):
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
    
    if departure_hour:
        if hasattr(departure_hour, 'total_seconds'):
            total_seconds = int(departure_hour.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            departure_datetime = datetime.combine(
                departure_date,
                datetime.strptime(f"{hours}:{minutes}", '%H:%M').time()
            )
        else:
            departure_datetime = datetime.combine(departure_date, datetime.min.time())
    else:
        departure_datetime = datetime.combine(departure_date, datetime.min.time())
    
    cutoff = datetime.now() + timedelta(hours=FLIGHT_CANCELLATION_CUTOFF_HOURS)
    
    if departure_datetime <= cutoff:
        return (False, f"Cannot cancel flight within {FLIGHT_CANCELLATION_CUTOFF_HOURS} hours of departure.")
    
    return (True, "")


def get_affected_orders_count(flight_id, airplane_id):
    """Get count of active orders that would be affected by flight cancellation."""
    return order_repository.count_active_orders_for_flight(flight_id, airplane_id)


def cancel_flight(flight_id, airplane_id, manager_id=None):
    """
    Cancel a flight and credit all active orders.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID
        manager_id: Manager performing cancellation (for audit)
    """
    # Update flight status
    flight_repository.update_flight_status(flight_id, airplane_id, 'canceled')
    
    # Get all active orders for this flight
    orders = order_repository.get_active_orders_for_flight(flight_id, airplane_id)
    
    # Credit each order (set TotalCost to 0, status to system_canceled)
    for order in orders:
        order_repository.update_order_status(
            order['UniqueOrderCode'],
            status='system_canceled',
            total_cost=0
        )
        # Delete tickets for the order
        order_repository.delete_tickets_for_order(order['UniqueOrderCode'])
    
    # Log manager action
    if manager_id:
        log_manager_edit(manager_id, flight_id, airplane_id, 'canceled')


def get_flight_crew(flight_id, airplane_id):
    """Get crew assigned to a flight."""
    pilots = crew_repository.get_pilots_for_flight(flight_id, airplane_id)
    attendants = crew_repository.get_attendants_for_flight(flight_id, airplane_id)
    return {
        'pilots': pilots or [],
        'attendants': attendants or []
    }
