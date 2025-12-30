"""
FLYTAU Order Repository
Database access for orders and order lines
"""
from app.db import execute_query


# ============ ORDER OPERATIONS ============

def create_order(booking_code, customer_id, guest_email, paid_total, status):
    """Create a new order."""
    sql = """
        INSERT INTO orders (booking_code, customer_id, guest_email, paid_total, status, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """
    return execute_query(sql, (booking_code, customer_id, guest_email, paid_total, status), commit=True)


def get_order_by_id(order_id):
    """Get an order by ID."""
    sql = """
        SELECT id, booking_code, customer_id, guest_email, paid_total, status, created_at
        FROM orders
        WHERE id = %s
    """
    return execute_query(sql, (order_id,), fetch_one=True)


def get_order_by_booking_code(booking_code):
    """Get an order by booking code."""
    sql = """
        SELECT id, booking_code, customer_id, guest_email, paid_total, status, created_at
        FROM orders
        WHERE booking_code = %s
    """
    return execute_query(sql, (booking_code,), fetch_one=True)


def get_order_with_lines(order_id):
    """Get an order with all its order lines and flight details."""
    # First get the order
    order = get_order_by_id(order_id)
    if not order:
        return None
    
    # Get order lines with flight info
    sql = """
        SELECT ol.id, ol.order_id, ol.flight_seat_id, ol.passenger_name, ol.price,
               fs.seat_code, fs.seat_class,
               f.id AS flight_id, f.flight_number, f.departure_datetime, f.arrival_datetime,
               r.origin, r.destination
        FROM order_lines ol
        JOIN flight_seats fs ON ol.flight_seat_id = fs.id
        JOIN flights f ON fs.flight_id = f.id
        JOIN routes r ON f.route_id = r.id
        WHERE ol.order_id = %s
        ORDER BY f.departure_datetime, fs.seat_code
    """
    lines = execute_query(sql, (order_id,))
    
    order['lines'] = lines
    return order


def get_orders_by_customer(customer_id, status_filter=None):
    """Get all orders for a customer."""
    sql = """
        SELECT o.id, o.booking_code, o.paid_total, o.status, o.created_at,
               COUNT(ol.id) AS ticket_count
        FROM orders o
        LEFT JOIN order_lines ol ON o.id = ol.order_id
        WHERE o.customer_id = %s
    """
    params = [customer_id]
    
    if status_filter:
        sql += " AND o.status = %s"
        params.append(status_filter)
    
    sql += " GROUP BY o.id ORDER BY o.created_at DESC"
    
    return execute_query(sql, tuple(params))


def update_order_status(order_id, status, paid_total=None):
    """Update an order's status and optionally the paid total."""
    if paid_total is not None:
        sql = "UPDATE orders SET status = %s, paid_total = %s WHERE id = %s"
        return execute_query(sql, (status, paid_total, order_id), commit=True)
    else:
        sql = "UPDATE orders SET status = %s WHERE id = %s"
        return execute_query(sql, (status, order_id), commit=True)


def booking_code_exists(booking_code):
    """Check if a booking code already exists."""
    sql = "SELECT id FROM orders WHERE booking_code = %s"
    return execute_query(sql, (booking_code,), fetch_one=True) is not None


def count_orders():
    """Count total orders."""
    sql = "SELECT COUNT(*) AS count FROM orders"
    result = execute_query(sql, fetch_one=True)
    return result['count'] if result else 0


def count_orders_by_status(status):
    """Count orders by status."""
    sql = "SELECT COUNT(*) AS count FROM orders WHERE status = %s"
    result = execute_query(sql, (status,), fetch_one=True)
    return result['count'] if result else 0


def get_active_orders_for_flight(flight_id):
    """Get all active orders that include a seat on the given flight."""
    sql = """
        SELECT DISTINCT o.id, o.booking_code, o.customer_id, o.guest_email, o.paid_total
        FROM orders o
        JOIN order_lines ol ON o.id = ol.order_id
        JOIN flight_seats fs ON ol.flight_seat_id = fs.id
        WHERE fs.flight_id = %s AND o.status = 'active'
    """
    return execute_query(sql, (flight_id,))


def count_active_orders_for_flight(flight_id):
    """Count active orders for a flight."""
    sql = """
        SELECT COUNT(DISTINCT o.id) AS count
        FROM orders o
        JOIN order_lines ol ON o.id = ol.order_id
        JOIN flight_seats fs ON ol.flight_seat_id = fs.id
        WHERE fs.flight_id = %s AND o.status = 'active'
    """
    result = execute_query(sql, (flight_id,), fetch_one=True)
    return result['count'] if result else 0


# ============ ORDER LINE OPERATIONS ============

def create_order_line(order_id, flight_seat_id, passenger_name, price):
    """Create a new order line."""
    sql = """
        INSERT INTO order_lines (order_id, flight_seat_id, passenger_name, price)
        VALUES (%s, %s, %s, %s)
    """
    return execute_query(sql, (order_id, flight_seat_id, passenger_name, price), commit=True)


def get_order_lines(order_id):
    """Get all lines for an order."""
    sql = """
        SELECT id, order_id, flight_seat_id, passenger_name, price
        FROM order_lines
        WHERE order_id = %s
    """
    return execute_query(sql, (order_id,))
