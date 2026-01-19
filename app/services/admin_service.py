"""All the manager-side stuff - creating flights, assigning crew, dashboard stats."""
from datetime import datetime, timedelta
from decimal import Decimal
from app.repositories import (
    flight_repository, 
    aircraft_repository, 
    crew_repository,
    order_repository
)


FLIGHT_CANCELLATION_CUTOFF_HOURS = 72
LONG_FLIGHT_THRESHOLD_MINUTES = 360  # 6 hours


def get_route(origin, destination):
    """Gets the route details between two airports."""
    return flight_repository.get_route(origin, destination)


def update_expired_flight_statuses():
    """Goes through flights and marks ones that have landed as 'done'. Skips cancelled ones."""
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
                flight_repository.update_flight_status(flight_id, 'done')
                
        except (ValueError, TypeError):
            # Skip flights with invalid date/time data
            continue


def get_dashboard_stats():
    """Pulls together all the numbers for the admin dashboard."""
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
    """Gets all flights in a nice format for the templates. Also updates any expired statuses."""
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
    """Works out departure and arrival datetimes from the inputs."""
    departure_str = f"{departure_date} {departure_time}"
    departure_datetime = datetime.strptime(departure_str, "%Y-%m-%d %H:%M")
    arrival_datetime = departure_datetime + timedelta(minutes=duration_minutes)
    
    return (departure_datetime, arrival_datetime)


def is_long_flight(duration_minutes):
    """A flight over 6 hours counts as 'long' (needs certified crew and big planes)."""
    return duration_minutes > LONG_FLIGHT_THRESHOLD_MINUTES


def get_airplane_by_id(airplane_id):
    """Looks up an airplane by its ID."""
    return aircraft_repository.get_airplane_by_id(airplane_id)


def get_available_airplanes(departure_datetime, arrival_datetime, origin_airport=None, for_long_flight=False):
    """Finds planes that are free during the time slot and at the right airport. Long flights need big planes."""
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    # Repository now checks for time overlap AND location
    airplanes = aircraft_repository.get_available_airplanes(departure_datetime, arrival_datetime, origin_airport)
    
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
            'is_available': True,  # All returned aircraft are available
            'current_location': airplane.get('current_location', origin_airport)
        })
    
    return result


def get_available_pilots(departure_datetime, arrival_datetime, origin_airport=None, for_long_flight=False):
    """Finds pilots who are free and at the departure airport."""
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    # Repository now uses datetime for time overlap check and location filter
    pilots = crew_repository.get_available_pilots(
        departure_datetime,
        arrival_datetime,
        origin_airport,
        require_long_flight_cert=for_long_flight
    )
    
    return pilots if pilots else []


def get_available_attendants(departure_datetime, arrival_datetime, origin_airport=None, for_long_flight=False):
    """Finds flight attendants who are free and at the departure airport."""
    if isinstance(departure_datetime, str):
        departure_datetime = datetime.fromisoformat(departure_datetime)
    if isinstance(arrival_datetime, str):
        arrival_datetime = datetime.fromisoformat(arrival_datetime)
    
    # Repository now uses datetime for time overlap check and location filter
    attendants = crew_repository.get_available_flight_attendants(
        departure_datetime,
        arrival_datetime,
        origin_airport,
        require_long_flight_cert=for_long_flight
    )
    
    return attendants if attendants else []


def create_flight(airplane_id, origin, destination, departure_date, departure_hour,
                  duration, economy_price, business_price, pilot_ids, attendant_ids,
                  manager_id=None, flight_id=None):
    """Creates a new flight with all its crew assignments. Returns the flight ID."""
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
    """Records that a manager made changes to a flight (for audit trail)."""
    from app.db import execute_query
    sql = """
        INSERT IGNORE INTO Managers_edits_Flights 
        (Managers_ManagerId, Flights_FlightId)
        VALUES (%s, %s)
    """
    execute_query(sql, (manager_id, flight_id), commit=True)


def can_cancel_flight(flight):
    """Checks if a flight can be cancelled (72-hour rule). Returns (can_cancel, reason)."""
    if flight.get('Status') == 'cancelled':
        return (False, "Flight is already cancelled.")
    
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


def get_affected_orders_count(flight_id):
    """Counts how many active orders would be impacted if we cancel this flight."""
    return order_repository.count_active_orders_for_flight(flight_id)


def get_flight_cancellation_info(flight_id, airplane_id):
    """Gathers all the details needed for the flight cancellation page - affected orders, refund totals, etc."""
    from app.services import flight_service
    
    flight = flight_repository.get_flight_by_id(flight_id, airplane_id)
    if not flight:
        return None
    
    flight = dict(flight)
    
    # Parse departure datetime
    departure_date = flight.get('DepartureDate')
    departure_hour = flight.get('DepartureHour')
    
    departure_datetime = None
    if departure_date:
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
            elif isinstance(departure_hour, str):
                try:
                    time_str = departure_hour[:5] if len(departure_hour) > 5 else departure_hour
                    departure_datetime = datetime.combine(
                        departure_date,
                        datetime.strptime(time_str, '%H:%M').time()
                    )
                except ValueError:
                    departure_datetime = datetime.combine(departure_date, datetime.min.time())
            else:
                departure_datetime = datetime.combine(departure_date, datetime.min.time())
        else:
            departure_datetime = datetime.combine(departure_date, datetime.min.time())
    
    # Calculate arrival time
    duration_minutes = flight.get('Duration', 0) or 0
    arrival_datetime = None
    if departure_datetime and duration_minutes:
        arrival_datetime = departure_datetime + timedelta(minutes=int(duration_minutes))
    
    # Get active orders and calculate impact
    active_orders = order_repository.get_active_orders_for_flight(flight_id)
    affected_orders_count = len(active_orders) if active_orders else 0
    
    # Count tickets and total refund
    affected_tickets = 0
    total_refund = 0.0
    if active_orders:
        for order in active_orders:
            affected_tickets += order.get('TicketCount', 0)
            total_refund += float(order.get('TotalCost', 0) or 0)
    
    return {
        'id': flight_id,
        'flight_number': flight_id,
        'airplane_id': airplane_id,
        'origin': flight.get('OriginPort'),
        'destination': flight.get('DestPort'),
        'departure_time': departure_datetime,
        'arrival_time': arrival_datetime,
        'duration_minutes': duration_minutes,
        'status': flight.get('Status', 'active'),
        'economy_price': flight.get('EconomyPrice'),
        'business_price': flight.get('BusinessPrice'),
        'affected_orders': affected_orders_count,
        'affected_tickets': affected_tickets,
        'total_refund': total_refund
    }


def cancel_flight(flight_id, manager_id=None):
    """Cancels a flight and refunds all the affected orders."""
    # Update flight status
    flight_repository.update_flight_status(flight_id, 'cancelled')
    
    # Get all active orders for this flight
    orders = order_repository.get_active_orders_for_flight(flight_id)
    
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
        log_manager_edit(manager_id, flight_id, airplane_id, 'cancelled')


def get_flight_crew(flight_id, airplane_id):
    """Gets the pilots and attendants assigned to a flight."""
    pilots = crew_repository.get_pilots_for_flight(flight_id, airplane_id)
    attendants = crew_repository.get_attendants_for_flight(flight_id, airplane_id)
    return {
        'pilots': pilots or [],
        'attendants': attendants or []
    }


def get_available_airplanes_for_edit(departure_date, duration_minutes, current_airplane_id=None):
    """Gets available planes for editing a flight, always including the one currently assigned."""
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
    """Gets available pilots for editing - the currently assigned ones will show up too."""
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
    """Gets available attendants for editing - the currently assigned ones will show up too."""
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
    The big edit function - can change pretty much anything about a flight
    including the flight number, aircraft, route, schedule, and crew.
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
