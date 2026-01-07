"""
FLYTAU Admin Service
Handles flight creation, cancellation, crew management, and admin operations

Schema:
- Flights: FlightId + Airplanes_AirplaneId (composite PK), OriginPort, DestPort,
           DepartureDate, DepartureHour, Duration, Status
- Routes: RouteId (PK), OriginPort, DestPort, DurationMinutes, DistanceKm
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


def get_route(origin, destination):
    """
    Get route information for given origin-destination pair.
    
    Args:
        origin: Origin airport code
        destination: Destination airport code
    
    Returns:
        Dict with id, origin, destination, duration_minutes, distance_km
        or None if route not found
    """
    return flight_repository.get_route(origin, destination)


def update_expired_flight_statuses():
    """
    Check all 'active' and 'full' flights and update their status to 'done'
    if the flight has already landed (current time > departure time + duration).
    
    Cancelled flights are NOT modified - they remain 'cancelled'.
    """
    # Get all flights that could potentially need status update
    raw_flights = flight_repository.get_all_flights()
    
    now = datetime.now()
    
    for f in raw_flights:
        status = f.get('Status', '').lower()
        
        # Skip cancelled and already done flights
        if status in ('cancelled', 'done'):
            continue
        
        # Only process active or full flights
        if status not in ('active', 'full'):
            continue
        
        # Parse departure date and time
        departure_date = f.get('DepartureDate')
        departure_hour = f.get('DepartureHour', '00:00')
        duration_minutes = f.get('Duration', 0)
        
        if not departure_date or not duration_minutes:
            continue
        
        # Handle departure_hour which might be a timedelta or string
        if hasattr(departure_hour, 'total_seconds'):
            total_seconds = int(departure_hour.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            departure_hour = f"{hours:02d}:{minutes:02d}"
        elif not isinstance(departure_hour, str):
            departure_hour = str(departure_hour)
        
        # Normalize departure_hour to HH:MM format (handle HH:MM:SS)
        if departure_hour and len(departure_hour) > 5 and ':' in departure_hour:
            departure_hour = departure_hour[:5]
        
        try:
            departure_datetime = datetime.combine(
                departure_date,
                datetime.strptime(departure_hour, "%H:%M").time()
            )
            
            # Calculate landing time (departure + duration)
            landing_time = departure_datetime + timedelta(minutes=duration_minutes)
            
            # If current time has passed landing time, update status to 'done'
            if now > landing_time:
                flight_id = f.get('FlightId')
                airplane_id = f.get('Airplanes_AirplaneId')
                flight_repository.update_flight_status(flight_id, airplane_id, 'done')
                
        except (ValueError, TypeError):
            # Skip flights with invalid date/time data
            continue


def get_dashboard_stats():
    """
    Get summary statistics for admin dashboard.
    
    Returns:
        Dict with various statistics including all flights
    """
    # Get all flights with transformed data
    flights = get_all_flights()
    
    return {
        'total_flights': flight_repository.count_flights(),
        'active_flights': flight_repository.count_flights_by_status('active'),
        'full_flights': flight_repository.count_flights_by_status('full'),
        'total_orders': order_repository.count_orders(),
        'confirmed_orders': order_repository.count_orders_by_status('confirmed'),
        'total_aircraft': aircraft_repository.count_airplanes(),
        'total_revenue': order_repository.get_total_revenue(),
        'flights': flights  # Include all flights for the dashboard table
    }


def get_all_flights(status_filter=None):
    """
    Get all flights, optionally filtered by status.
    Transforms raw database results into template-friendly format.
    
    Also checks and updates flight statuses - flights that have landed
    (current time > departure + duration) are marked as 'done'.
    
    Args:
        status_filter: Optional status to filter by
    
    Returns:
        List of flight dicts with template-friendly field names
    """
    # First, update any expired flight statuses
    update_expired_flight_statuses()
    
    raw_flights = flight_repository.get_all_flights(status_filter)
    
    flights = []
    for f in raw_flights:
        # Parse departure date and time into a datetime object
        departure_date = f.get('DepartureDate')
        departure_hour = f.get('DepartureHour', '00:00')
        
        # Handle departure_hour which might be a timedelta or string
        if hasattr(departure_hour, 'total_seconds'):
            # It's a timedelta, convert to HH:MM
            total_seconds = int(departure_hour.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            departure_hour = f"{hours:02d}:{minutes:02d}"
        elif not isinstance(departure_hour, str):
            departure_hour = str(departure_hour)
        
        # Normalize departure_hour to HH:MM format (handle HH:MM:SS)
        if departure_hour and len(departure_hour) > 5 and ':' in departure_hour:
            # If format is HH:MM:SS, trim to HH:MM
            departure_hour = departure_hour[:5]
        
        # Combine date and time
        if departure_date:
            try:
                departure_datetime = datetime.combine(
                    departure_date,
                    datetime.strptime(departure_hour, "%H:%M").time()
                )
            except (ValueError, TypeError):
                departure_datetime = datetime.now()
        else:
            departure_datetime = datetime.now()
        
        # Get airplane info for total seats
        airplane_id = f.get('Airplanes_AirplaneId')
        airplane = aircraft_repository.get_airplane_by_id(airplane_id)
        total_seats = airplane.get('total_seats', 0) if airplane else 0
        
        # Get booked seat count
        seat_counts = flight_repository.get_seat_counts(f.get('FlightId'), airplane_id)
        booked_seats = (seat_counts.get('business', {}).get('taken', 0) + 
                       seat_counts.get('economy', {}).get('taken', 0))
        
        # Determine if flight can be cancelled (more than 72 hours before departure)
        can_cancel = (departure_datetime - datetime.now()).total_seconds() > (FLIGHT_CANCELLATION_CUTOFF_HOURS * 3600)
        
        flights.append({
            'id': f.get('FlightId'),
            'flight_number': f.get('FlightId'),  # FlightId is the flight number
            'airplane_id': airplane_id,
            'origin': f.get('OriginPort'),
            'destination': f.get('DestPort'),
            'departure_time': departure_datetime,
            'duration': f.get('Duration'),
            'status': f.get('Status', 'active'),
            'economy_price': f.get('EconomyPrice'),
            'business_price': f.get('BusinessPrice'),
            'aircraft_type': f.get('Manufacturer', 'Unknown'),
            'total_seats': total_seats,
            'booked_seats': booked_seats,
            'can_cancel': can_cancel
        })
    
    return flights


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
        List of available airplane dicts with template-friendly field names
    
    Business Rule:
        - Long flights (> 6 hours): Only big airplanes (those with Business class)
        - Short flights (≤ 6 hours): All airplanes (big and small)
        - An airplane is considered 'big' if it has Business config (not null)
        - An airplane is unavailable if it has any flight that overlaps with the
          requested time period (from departure to landing)
    """
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    # Repository now checks for time overlap, not just date
    airplanes = aircraft_repository.get_available_airplanes(departure_datetime, arrival_datetime)
    
    # For long flights, only big airplanes are allowed
    # A big airplane has Business class seats (business_seats > 0)
    if for_long_flight:
        airplanes = [a for a in airplanes if a.get('business_seats', 0) > 0]
    
    # Transform to template-friendly format
    # All aircraft returned by repository are already available
    result = []
    for airplane in airplanes:
        airplane_id = airplane['AirplaneId']
        result.append({
            'id': airplane_id,
            'type': airplane['Manufacturer'],
            'registration': f"TAU-{airplane_id}",
            'total_seats': airplane['total_seats'],
            'economy_seats': airplane['economy_seats'],
            'business_seats': airplane['business_seats'],
            'size': airplane['size'],
            'is_available': True  # All returned aircraft are available
        })
    
    return result


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
    
    # Repository expects just the departure date
    departure_date = departure_datetime.date()
    
    pilots = crew_repository.get_available_pilots(
        departure_date,
        require_long_flight_cert=for_long_flight
    )
    
    return pilots if pilots else []


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
    
    # Repository expects just the departure date
    departure_date = departure_datetime.date()
    
    attendants = crew_repository.get_available_flight_attendants(
        departure_date,
        require_long_flight_cert=for_long_flight
    )
    
    return attendants if attendants else []


def create_flight(airplane_id, origin, destination, departure_date, departure_hour,
                  duration, economy_price, business_price, pilot_ids, attendant_ids,
                  manager_id=None, flight_id=None):
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
        flight_id: Optional pre-generated flight ID
    
    Returns:
        New flight ID
    """
    # Generate flight ID if not provided
    if not flight_id:
        flight_id = flight_repository.generate_flight_number()
    
    # Create flight record
    flight_repository.create_flight(
        flight_id=flight_id,
        airplane_id=airplane_id,
        departure_date=departure_date,
        departure_hour=departure_hour,
        origin_port=origin,
        dest_port=destination,
        duration=duration,
        status='active',
        economy_price=economy_price,
        business_price=business_price
    )
    
    # Create pilot assignments
    for pilot_id in pilot_ids:
        crew_repository.assign_pilot_to_flight(
            pilot_id=pilot_id,
            flight_id=flight_id,
            airplane_id=airplane_id
        )
    
    # Create attendant assignments
    for attendant_id in attendant_ids:
        crew_repository.assign_attendant_to_flight(
            attendant_id=attendant_id,
            flight_id=flight_id,
            airplane_id=airplane_id
        )
    
    # Log manager action (if manager_id provided)
    if manager_id:
        log_manager_edit(manager_id, flight_id, airplane_id, 'created')
    
    return flight_id


def log_manager_edit(manager_id, flight_id, airplane_id, action):
    """Log a manager edit action on a flight. Uses INSERT IGNORE to handle duplicate entries."""
    from app.db import execute_query
    sql = """
        INSERT IGNORE INTO Managers_edits_Flights 
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


def get_available_airplanes_for_edit(departure_date, duration_minutes, current_airplane_id=None):
    """
    Get airplanes available for a flight edit, including current airplane.
    
    Args:
        departure_date: Date of departure
        duration_minutes: Flight duration in minutes
        current_airplane_id: ID of currently assigned airplane (always included)
    
    Returns:
        List of available airplane dicts with template-friendly field names
    """
    is_long = is_long_flight(duration_minutes)
    
    # Get all available airplanes for this date
    airplanes = aircraft_repository.get_available_airplanes(departure_date)
    
    # For long flights, only big airplanes are allowed
    if is_long:
        airplanes = [a for a in airplanes if a.get('business_seats', 0) > 0]
    
    # Make sure current airplane is included
    airplane_ids = {a['AirplaneId'] for a in airplanes}
    if current_airplane_id and current_airplane_id not in airplane_ids:
        current_plane = aircraft_repository.get_airplane_by_id(current_airplane_id)
        if current_plane:
            # Only include if it's allowed for this flight type
            if not is_long or current_plane.get('business_seats', 0) > 0:
                airplanes.append(current_plane)
    
    # Transform to template-friendly format
    result = []
    for airplane in airplanes:
        airplane_id = airplane['AirplaneId']
        result.append({
            'id': airplane_id,
            'type': airplane['Manufacturer'],
            'registration': f"TAU-{airplane_id}",
            'total_seats': airplane.get('total_seats', 0),
            'economy_seats': airplane.get('economy_seats', 0),
            'business_seats': airplane.get('business_seats', 0),
            'size': airplane.get('size', 'small')
        })
    
    return result


def get_available_pilots_for_edit(departure_date, for_long_flight, flight_id, airplane_id):
    """
    Get pilots available for a flight edit, including currently assigned pilots.
    
    Args:
        departure_date: Date of departure
        for_long_flight: Whether this is a long flight
        flight_id: Current flight ID (to include its assigned crew)
        airplane_id: Current airplane ID
    
    Returns:
        List of available pilot dicts
    """
    # Get available pilots for this date, excluding the current flight from conflict check
    # This way, currently assigned pilots will appear as "available"
    available = crew_repository.get_available_pilots(
        departure_date,
        require_long_flight_cert=for_long_flight,
        exclude_flight_id=flight_id,
        exclude_airplane_id=airplane_id
    ) or []
    
    return available


def get_available_attendants_for_edit(departure_date, for_long_flight, flight_id, airplane_id):
    """
    Get attendants available for a flight edit, including currently assigned attendants.
    
    Args:
        departure_date: Date of departure
        for_long_flight: Whether this is a long flight
        flight_id: Current flight ID (to include its assigned crew)
        airplane_id: Current airplane ID
    
    Returns:
        List of available attendant dicts
    """
    # Get available attendants for this date, excluding the current flight from conflict check
    # This way, currently assigned attendants will appear as "available"
    available = crew_repository.get_available_flight_attendants(
        departure_date,
        require_long_flight_cert=for_long_flight,
        exclude_flight_id=flight_id,
        exclude_airplane_id=airplane_id
    ) or []
    
    return available


def update_flight_comprehensive(original_flight_id, original_airplane_id, 
                                new_flight_id, new_airplane_id,
                                new_origin, new_destination,
                                new_departure_date, new_departure_time,
                                new_duration, new_status,
                                new_economy_price, new_business_price,
                                new_pilot_ids, new_attendant_ids,
                                manager_id=None):
    """
    Comprehensive flight update that handles all fields including flight number, aircraft, and crew changes.
    
    This is a complex operation that may involve:
    - Changing flight identification (flight number)
    - Changing aircraft assignment
    - Updating route and schedule
    - Reassigning crew members
    """
    # Check if flight number changed - this requires special handling
    flight_id_changed = original_flight_id != new_flight_id
    airplane_changed = original_airplane_id != new_airplane_id
    
    # Start with basic updates
    updates = {
        'status': new_status,
        'economy_price': new_economy_price,
        'business_price': new_business_price,
        'departure_date': new_departure_date,
        'departure_hour': new_departure_time,
        'origin_port': new_origin,
        'dest_port': new_destination,
        'duration': new_duration
    }
    
    if flight_id_changed or airplane_changed:
        # Complex case: need to recreate flight with new identifiers
        flight_repository.update_flight_with_new_ids(
            original_flight_id, original_airplane_id,
            new_flight_id, new_airplane_id,
            updates
        )
        
        # Crew needs to be reassigned to new flight/airplane combo
        crew_repository.delete_all_crew_from_flight(original_flight_id, original_airplane_id)
    else:
        # Simple case: just update the existing flight
        flight_repository.update_flight_comprehensive(original_flight_id, original_airplane_id, updates)
        
        # Clear existing crew
        crew_repository.delete_all_crew_from_flight(original_flight_id, original_airplane_id)
    
    # Assign new crew
    target_flight_id = new_flight_id if flight_id_changed else original_flight_id
    target_airplane_id = new_airplane_id if airplane_changed else original_airplane_id
    
    for pilot_id in new_pilot_ids:
        crew_repository.assign_pilot_to_flight(pilot_id, target_flight_id, target_airplane_id)
    
    for attendant_id in new_attendant_ids:
        crew_repository.assign_attendant_to_flight(attendant_id, target_flight_id, target_airplane_id)
    
    # Log the edit
    if manager_id:
        log_manager_edit(manager_id, target_flight_id, target_airplane_id, 'comprehensive_edit')
