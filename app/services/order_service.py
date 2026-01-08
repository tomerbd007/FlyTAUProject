"""
FLYTAU Order Service
Handles order creation, cancellation, and refund calculations

Schema (normalized):
- orders: UniqueOrderCode (PK), TotalCost, Status,
          GuestCustomer_UniqueMail (nullable), RegisteredCustomer_UniqueMail (nullable),
          Flights_FlightId
- Tickets: TicketId, Class, RowNum, Seat, orders_UniqueOrderCode

Note:
- Ticket price is calculated dynamically from Flight's EconomyPrice/BusinessPrice
- Order's class is derived from its tickets
- Airplane ID is derived from Flights table via Flights_FlightId
"""
from datetime import datetime, timedelta
from decimal import Decimal
from app.repositories import order_repository, flight_repository
from app.services import auth_service


# Cancellation fee percentage
CANCELLATION_FEE_PERCENT = Decimal('0.05')

# Hours before departure when cancellation is no longer allowed
CANCELLATION_CUTOFF_HOURS = 36


def create_order(flight_id, airplane_id, selected_seats, economy_price, business_price,
                 registered_email=None, guest_email=None, guest_first_name=None, guest_last_name=None):
    """
    Create a new order with selected seats.
    
    Args:
        flight_id: Flight ID
        airplane_id: Airplane ID (used for seat validation, derived from flight)
        selected_seats: List of dicts with row, seat, class info
        economy_price: Price per economy seat
        business_price: Price per business seat
        registered_email: Registered customer email (if logged in)
        guest_email: Guest email (if not logged in)
        guest_first_name: Guest first name (required if guest)
        guest_last_name: Guest last name (required if guest)
    
    Returns:
        Booking code for the new order
    
    Raises:
        ValueError: If seats are no longer available
    """
    # Verify all seats are still available
    taken_seats = flight_repository.get_taken_seats(flight_id, airplane_id)
    taken_set = {(t['RowNum'], t['Seat']) for t in taken_seats}
    
    for seat in selected_seats:
        if (seat['row'], seat['seat']) in taken_set:
            raise ValueError(f"Seat {seat['row']}{seat['seat']} is no longer available.")
    
    # Calculate total (price will be derived dynamically from flight)
    total = Decimal('0')
    for seat in selected_seats:
        seat_class = seat.get('class', 'economy')
        price = business_price if seat_class == 'business' else economy_price
        total += Decimal(str(price))
    
    # Generate unique booking code
    booking_code = order_repository.generate_booking_code()
    
    # Handle guest customer
    actual_guest_email = None
    actual_registered_email = None
    
    if registered_email:
        actual_registered_email = registered_email.lower()
    elif guest_email:
        # Get or create guest customer
        auth_service.get_or_create_guest_customer(
            guest_email.lower(),
            guest_first_name or 'Guest',
            guest_last_name or 'User'
        )
        actual_guest_email = guest_email.lower()
    
    # Create order (no Class or Airplane_Id columns - derived from tickets and flight)
    order_repository.create_order(
        booking_code=booking_code,
        flight_id=flight_id,
        total_cost=total,
        status='confirmed',
        guest_email=actual_guest_email,
        registered_email=actual_registered_email
    )
    
    # Create tickets for each seat (no Price or Flight columns - derived dynamically)
    # The repository will validate seat availability before each insert
    try:
        for seat in selected_seats:
            seat_class = seat.get('class', 'economy')
            
            order_repository.create_ticket(
                order_code=booking_code,
                row_num=seat['row'],
                seat=seat['seat'],
                seat_class=seat_class
            )
    except order_repository.SeatAlreadyTakenError as e:
        # If a seat was taken between validation and insert, cancel the order
        order_repository.update_order_status(booking_code, 'cancelled')
        order_repository.delete_tickets_for_order(booking_code)
        raise ValueError(str(e))
    
    # Check if flight is now full
    from app.services import flight_service
    flight_service.check_flight_full(flight_id, airplane_id)
    
    return booking_code


def get_order_by_booking_code(booking_code):
    """Get order by its booking code."""
    return order_repository.get_order_by_booking_code(booking_code.upper())


def get_order_with_tickets(booking_code):
    """Get order with all tickets and flight details."""
    return order_repository.get_order_with_tickets(booking_code.upper())


def get_customer_orders(email, is_registered=True, status_filter=None):
    """
    Get all orders for a customer.
    
    Args:
        email: Customer email
        is_registered: True if registered customer, False if guest
        status_filter: Optional status to filter by
    
    Returns:
        List of order dicts
    """
    if is_registered:
        return order_repository.get_orders_by_registered_customer(email.lower(), status_filter)
    else:
        return order_repository.get_orders_by_guest_email(email.lower(), status_filter)


def get_order_for_guest(booking_code, email):
    """
    Get order for guest lookup (requires both booking code and email match).
    
    Args:
        booking_code: Order booking code
        email: Guest email address
    
    Returns:
        Order dict if found and email matches, None otherwise
    """
    order = order_repository.get_order_by_code_and_email(booking_code.upper(), email.lower())
    
    if not order:
        return None
    
    return order_repository.get_order_with_tickets(booking_code.upper())


def can_cancel_order(order):
    """
    Check if an order can be canceled (36h rule).
    
    Args:
        order: Order dict with flight info
    
    Returns:
        True if cancellation is allowed
    """
    if order.get('Status') not in ('confirmed', 'active'):
        return False
    
    # Get departure date and time
    departure_date = order.get('DepartureDate')
    departure_hour = order.get('DepartureHour')
    
    if not departure_date:
        return False
    
    # Combine date and time
    if isinstance(departure_date, str):
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
    
    if departure_hour:
        if isinstance(departure_hour, str):
            hour_parts = departure_hour.split(':')
            departure_datetime = datetime.combine(
                departure_date,
                datetime.strptime(f"{hour_parts[0]}:{hour_parts[1]}", '%H:%M').time()
            )
        elif hasattr(departure_hour, 'seconds'):
            # timedelta from MySQL TIME
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
    
    # Check 36h rule
    cutoff = datetime.now() + timedelta(hours=CANCELLATION_CUTOFF_HOURS)
    return departure_datetime > cutoff


def calculate_cancellation_fee(paid_total):
    """
    Calculate cancellation fee and refund amount.
    
    Args:
        paid_total: Original paid amount
    
    Returns:
        Tuple of (fee, refund)
    """
    total = Decimal(str(paid_total))
    fee = total * CANCELLATION_FEE_PERCENT
    refund = total - fee
    return (fee, refund)


def cancel_order(booking_code, email):
    """
    Cancel an order (customer cancellation).
    
    Args:
        booking_code: Order booking code
        email: Email of user requesting cancellation (for ownership verification)
    
    Returns:
        Tuple of (fee, refund)
    
    Raises:
        ValueError: If order cannot be canceled
    """
    order = get_order_with_tickets(booking_code)
    
    if not order:
        raise ValueError("Order not found.")
    
    # Verify ownership
    owner_email = order.get('RegisteredCustomer_UniqueMail') or order.get('GuestCustomer_UniqueMail')
    if owner_email and owner_email.lower() != email.lower():
        raise ValueError("You don't have permission to cancel this order.")
    
    # Verify cancellation is allowed
    if not can_cancel_order(order):
        raise ValueError("This order cannot be canceled. Cancellations must be made at least 36 hours before departure.")
    
    # Calculate refund
    fee, refund = calculate_cancellation_fee(order['TotalCost'])
    
    # Update order status
    order_repository.update_order_status(
        booking_code, 
        status='customer_canceled',
        total_cost=refund
    )
    
    # Delete tickets (seats become available again)
    order_repository.delete_tickets_for_order(booking_code)
    
    return (fee, refund)


def update_order_seats(booking_code, new_seats, flight):
    """
    Update seats for an existing order.
    
    Args:
        booking_code: Order booking code
        new_seats: List of new seat codes (e.g., ['1A', '1B'])
        flight: Flight dict with pricing info
    
    Raises:
        ValueError: If seats are not available
    """
    from decimal import Decimal
    
    order = get_order_with_tickets(booking_code)
    if not order:
        raise ValueError("Order not found.")
    
    flight_id = order.get('Flights_FlightId')
    airplane_id = order.get('Flights_Airplanes_AirplaneId')
    
    # Get current seats for this order
    current_seat_codes = set(f"{t.get('RowNum')}{t.get('Seat')}" for t in order.get('tickets', []))
    
    # Get all taken seats for the flight (excluding this order's seats)
    taken_seats = flight_repository.get_taken_seats(flight_id, airplane_id)
    taken_set = set()
    for t in taken_seats:
        seat_code = f"{t['RowNum']}{t['Seat']}"
        if seat_code not in current_seat_codes:
            taken_set.add(seat_code)
    
    # Verify new seats are available
    for seat_code in new_seats:
        if seat_code in taken_set:
            raise ValueError(f"Seat {seat_code} is no longer available.")
    
    # Parse seat codes and calculate new total
    economy_price = Decimal(str(flight.get('EconomyPrice') or 0))
    business_price = Decimal(str(flight.get('BusinessPrice') or 0))
    
    # Get business row count from flight config
    business_config = flight.get('BusinessConfig', '')
    business_rows = 0
    if business_config:
        parts = business_config.split()
        if len(parts) >= 1:
            try:
                business_rows = int(parts[0])
            except ValueError:
                pass
    
    new_total = Decimal('0')
    seat_details = []
    for seat_code in new_seats:
        # Parse row number and seat letter
        row_num = int(''.join(c for c in seat_code if c.isdigit()))
        seat_letter = ''.join(c for c in seat_code if c.isalpha())
        
        # Determine class based on row
        if row_num <= business_rows:
            seat_class = 'business'
            price = business_price
        else:
            seat_class = 'economy'
            price = economy_price
        
        new_total += price
        seat_details.append({
            'row': row_num,
            'seat': seat_letter,
            'class': seat_class
        })
    
    # Delete old tickets
    order_repository.delete_tickets_for_order(booking_code)
    
    # Create new tickets (price derived dynamically from flight)
    # Seat validation will exclude the current order since old tickets are deleted
    try:
        for seat in seat_details:
            order_repository.create_ticket(
                order_code=booking_code,
                row_num=seat['row'],
                seat=seat['seat'],
                seat_class=seat['class']
            )
    except order_repository.SeatAlreadyTakenError as e:
        raise ValueError(str(e))
    
    # Update order total
    order_repository.update_order_status(booking_code, status='confirmed', total_cost=new_total)
