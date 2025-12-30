"""
FLYTAU Order Service
Handles order creation, cancellation, and refund calculations
"""
from datetime import datetime, timedelta
from decimal import Decimal
from app.repositories import order_repository, flight_repository
from app.utils.helpers import generate_booking_code
from app import db


# Cancellation fee percentage
CANCELLATION_FEE_PERCENT = Decimal('0.05')

# Hours before departure when cancellation is no longer allowed
CANCELLATION_CUTOFF_HOURS = 36


def create_order(flight_id, seats_info, passengers, customer_id=None, guest_email=None):
    """
    Create a new order with selected seats.
    
    Args:
        flight_id: Flight ID
        seats_info: List of seat dicts with prices
        passengers: Dict mapping seat_code to passenger name
        customer_id: Customer ID if logged in, None for guest
        guest_email: Guest email if not logged in
    
    Returns:
        Booking code for the new order
    
    Raises:
        ValueError: If seats are no longer available
    """
    # Verify all seats are still available
    for seat in seats_info:
        current_seat = flight_repository.get_seat_by_id(seat['id'])
        if current_seat['status'] != 'available':
            raise ValueError(f"Seat {seat['seat_code']} is no longer available.")
    
    # Calculate total
    total = sum(Decimal(str(seat['price'])) for seat in seats_info)
    
    # Generate unique booking code
    booking_code = generate_booking_code()
    while order_repository.booking_code_exists(booking_code):
        booking_code = generate_booking_code()
    
    try:
        # Create order
        order_id = order_repository.create_order(
            booking_code=booking_code,
            customer_id=customer_id,
            guest_email=guest_email.lower() if guest_email else None,
            paid_total=total,
            status='active'
        )
        
        # Create order lines and update seat status
        for seat in seats_info:
            order_line_id = order_repository.create_order_line(
                order_id=order_id,
                flight_seat_id=seat['id'],
                passenger_name=passengers[seat['seat_code']],
                price=seat['price']
            )
            
            # Mark seat as sold
            flight_repository.update_seat_status(seat['id'], 'sold', order_line_id)
        
        db.commit()
        
        # Check if flight is now full
        from app.services import flight_service
        flight_service.check_flight_full(flight_id)
        
        return booking_code
        
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to create order: {str(e)}")


def get_order_by_booking_code(booking_code):
    """Get order by its booking code."""
    return order_repository.get_order_by_booking_code(booking_code.upper())


def get_order_with_lines(order_id):
    """Get order with all order lines and flight details."""
    return order_repository.get_order_with_lines(order_id)


def get_customer_orders(customer_id, status_filter=None):
    """
    Get all orders for a customer.
    
    Args:
        customer_id: Customer ID
        status_filter: Optional status to filter by
    
    Returns:
        List of order dicts
    """
    return order_repository.get_orders_by_customer(customer_id, status_filter)


def get_order_for_guest(booking_code, email):
    """
    Get order for guest lookup (requires both booking code and email match).
    
    Args:
        booking_code: Order booking code
        email: Guest email address
    
    Returns:
        Order dict if found and email matches, None otherwise
    """
    order = order_repository.get_order_by_booking_code(booking_code.upper())
    
    if not order:
        return None
    
    # For guest orders, verify email matches
    if order['guest_email'] and order['guest_email'].lower() == email.lower():
        return order_repository.get_order_with_lines(order['id'])
    
    return None


def can_cancel_order(order):
    """
    Check if an order can be canceled (36h rule).
    
    Args:
        order: Order dict with lines
    
    Returns:
        True if cancellation is allowed
    """
    if order['status'] != 'active':
        return False
    
    # Get the earliest departure time from all flights in the order
    earliest_departure = None
    for line in order.get('lines', []):
        if line.get('departure_datetime'):
            dep_time = line['departure_datetime']
            if isinstance(dep_time, str):
                dep_time = datetime.fromisoformat(dep_time)
            if earliest_departure is None or dep_time < earliest_departure:
                earliest_departure = dep_time
    
    if earliest_departure is None:
        return False
    
    # Check 36h rule
    cutoff = datetime.utcnow() + timedelta(hours=CANCELLATION_CUTOFF_HOURS)
    return earliest_departure > cutoff


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


def cancel_order(order_id, user_id):
    """
    Cancel an order (customer cancellation).
    
    Args:
        order_id: Order ID
        user_id: User ID requesting cancellation (for ownership verification)
    
    Raises:
        ValueError: If order cannot be canceled
    """
    order = get_order_with_lines(order_id)
    
    if not order:
        raise ValueError("Order not found.")
    
    # Verify ownership
    if order['customer_id'] != user_id:
        raise ValueError("You don't have permission to cancel this order.")
    
    # Verify cancellation is allowed
    if not can_cancel_order(order):
        raise ValueError("This order cannot be canceled. Cancellations must be made at least 36 hours before departure.")
    
    # Calculate refund
    fee, refund = calculate_cancellation_fee(order['paid_total'])
    
    try:
        # Update order status and paid_total
        order_repository.update_order_status(
            order_id, 
            status='customer_canceled',
            paid_total=refund
        )
        
        # Release seats
        for line in order['lines']:
            flight_repository.release_seat(line['flight_seat_id'])
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to cancel order: {str(e)}")
