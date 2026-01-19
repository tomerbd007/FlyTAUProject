"""All the SQL queries for orders and tickets."""
from app.db import execute_query
import random
import string


def is_seat_taken_for_flight(flight_id, row_num, seat, exclude_order_code=None):
    """Checks if a seat is already booked. Can ignore a specific order (useful for updates)."""
    sql = """
        SELECT 1
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE o.Flights_FlightId = %s
          AND t.RowNum = %s
          AND t.Seat = %s
          AND o.Status != 'cancelled'
    """
    params = [flight_id, row_num, seat]
    
    if exclude_order_code:
        sql += " AND o.UniqueOrderCode != %s"
        params.append(exclude_order_code)
    
    result = execute_query(sql, tuple(params), fetch_one=True)
    return result is not None


def get_flight_id_for_order(order_code):
    """Gets the flight ID that an order is for."""
    sql = "SELECT Flights_FlightId FROM orders WHERE UniqueOrderCode = %s"
    result = execute_query(sql, (order_code,), fetch_one=True)
    return result['Flights_FlightId'] if result else None


# ============ BOOKING CODE GENERATION ============

def generate_booking_code():
    """Creates a unique booking code like FLY-ABC123."""
    while True:
        code = 'FLY-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not booking_code_exists(code):
            return code


def booking_code_exists(booking_code):
    """Checks if a booking code is already in use."""
    sql = "SELECT UniqueOrderCode FROM orders WHERE UniqueOrderCode = %s"
    return execute_query(sql, (booking_code,), fetch_one=True) is not None


def create_order(booking_code, flight_id, total_cost, status, 
                 guest_email=None, registered_email=None):
    """Inserts a new order into the database."""
    sql = """
        INSERT INTO orders (UniqueOrderCode, Flights_FlightId, TotalCost, Status, 
                           GuestCustomer_UniqueMail, RegisteredCustomer_UniqueMail)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    return execute_query(sql, (booking_code, flight_id, total_cost, status,
                               guest_email, registered_email), commit=True)


def get_order_by_booking_code(booking_code):
    """Fetches an order along with its flight info."""
    sql = """
        SELECT o.UniqueOrderCode, o.TotalCost, o.Status,
               o.GuestCustomer_UniqueMail, o.RegisteredCustomer_UniqueMail,
               o.Flights_FlightId,
               f.Airplanes_AirplaneId as Flights_Airplanes_AirplaneId,
               f.OriginPort, f.DestPort, f.DepartureDate, f.DepartureHour, f.Duration,
               f.EconomyPrice, f.BusinessPrice,
               a.Manufacturer,
               (SELECT CASE 
                    WHEN COUNT(DISTINCT t.Class) > 1 THEN 'mixed'
                    ELSE MAX(t.Class)
                END FROM Tickets t WHERE t.orders_UniqueOrderCode = o.UniqueOrderCode) as Class
        FROM orders o
        JOIN Flights f ON o.Flights_FlightId = f.FlightId
        JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
        WHERE o.UniqueOrderCode = %s
    """
    return execute_query(sql, (booking_code,), fetch_one=True)


def get_order_with_tickets(booking_code):
    """Gets the full order with all its tickets and flight details."""
    order = get_order_by_booking_code(booking_code)
    if not order:
        return None
    
    order = dict(order)
    
    # Get tickets for this order with dynamically calculated price
    sql = """
        SELECT t.TicketId, t.Class, t.RowNum, t.Seat,
               CASE WHEN t.Class = 'business' THEN f.BusinessPrice ELSE f.EconomyPrice END as Price,
               CONCAT(t.RowNum, t.Seat) as SeatCode
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        JOIN Flights f ON o.Flights_FlightId = f.FlightId
        WHERE t.orders_UniqueOrderCode = %s
        ORDER BY t.Class DESC, t.RowNum, t.Seat
    """
    tickets = execute_query(sql, (booking_code,))
    order['tickets'] = tickets if tickets else []
    
    return order


def get_orders_by_registered_customer(email, status_filter=None):
    """Gets all orders for someone with an account."""
    sql = """
        SELECT o.UniqueOrderCode, o.TotalCost, o.Status,
               o.Flights_FlightId,
               f.Airplanes_AirplaneId as Flights_Airplanes_AirplaneId,
               f.OriginPort, f.DestPort, f.DepartureDate, f.DepartureHour,
               COUNT(t.TicketId) as TicketCount,
               (SELECT CASE 
                    WHEN COUNT(DISTINCT t2.Class) > 1 THEN 'mixed'
                    ELSE MAX(t2.Class)
                END FROM Tickets t2 WHERE t2.orders_UniqueOrderCode = o.UniqueOrderCode) as Class
        FROM orders o
        JOIN Flights f ON o.Flights_FlightId = f.FlightId
        LEFT JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
        WHERE o.RegisteredCustomer_UniqueMail = %s
    """
    params = [email]
    
    if status_filter:
        # Map 'cancelled' to both customer_canceled and system_canceled
        if status_filter.lower() == 'cancelled':
            sql += " AND o.Status IN ('customer_canceled', 'system_canceled')"
        else:
            sql += " AND o.Status = %s"
            params.append(status_filter)
    
    sql += " GROUP BY o.UniqueOrderCode ORDER BY f.DepartureDate DESC"
    
    return execute_query(sql, tuple(params))


def get_orders_by_guest_email(email, status_filter=None):
    """Gets all orders for a guest customer by their email."""
    sql = """
        SELECT o.UniqueOrderCode, o.TotalCost, o.Status,
               o.Flights_FlightId,
               f.Airplanes_AirplaneId as Flights_Airplanes_AirplaneId,
               f.OriginPort, f.DestPort, f.DepartureDate, f.DepartureHour,
               COUNT(t.TicketId) as TicketCount,
               (SELECT CASE 
                    WHEN COUNT(DISTINCT t2.Class) > 1 THEN 'mixed'
                    ELSE MAX(t2.Class)
                END FROM Tickets t2 WHERE t2.orders_UniqueOrderCode = o.UniqueOrderCode) as Class
        FROM orders o
        JOIN Flights f ON o.Flights_FlightId = f.FlightId
        LEFT JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
        WHERE o.GuestCustomer_UniqueMail = %s
    """
    params = [email]
    
    if status_filter:
        if status_filter == 'cancelled':
            # Map 'cancelled' to both customer_canceled and system_canceled
            sql += " AND o.Status IN ('customer_canceled', 'system_canceled')"
        else:
            sql += " AND o.Status = %s"
            params.append(status_filter)
    
    sql += " GROUP BY o.UniqueOrderCode ORDER BY f.DepartureDate DESC"
    
    return execute_query(sql, tuple(params))


def get_order_by_code_and_email(booking_code, email):
    """Get order by booking code and email (for guest lookup)."""
    sql = """
        SELECT o.UniqueOrderCode, o.TotalCost, o.Status,
               o.GuestCustomer_UniqueMail, o.RegisteredCustomer_UniqueMail,
               o.Flights_FlightId,
               f.Airplanes_AirplaneId as Flights_Airplanes_AirplaneId,
               f.OriginPort, f.DestPort, f.DepartureDate, f.DepartureHour, f.Duration,
               (SELECT CASE 
                    WHEN COUNT(DISTINCT t.Class) > 1 THEN 'mixed'
                    ELSE MAX(t.Class)
                END FROM Tickets t WHERE t.orders_UniqueOrderCode = o.UniqueOrderCode) as Class
        FROM orders o
        JOIN Flights f ON o.Flights_FlightId = f.FlightId
        WHERE o.UniqueOrderCode = %s 
          AND (o.GuestCustomer_UniqueMail = %s OR o.RegisteredCustomer_UniqueMail = %s)
    """
    return execute_query(sql, (booking_code, email, email), fetch_one=True)


def update_order_status(booking_code, status, total_cost=None):
    """Update an order's status and optionally the total cost."""
    if total_cost is not None:
        sql = "UPDATE orders SET Status = %s, TotalCost = %s WHERE UniqueOrderCode = %s"
        return execute_query(sql, (status, total_cost, booking_code), commit=True)
    else:
        sql = "UPDATE orders SET Status = %s WHERE UniqueOrderCode = %s"
        return execute_query(sql, (status, booking_code), commit=True)


def count_orders():
    """Count total orders."""
    sql = "SELECT COUNT(*) AS count FROM orders"
    result = execute_query(sql, fetch_one=True)
    return result['count'] if result else 0


def count_orders_by_status(status):
    """Count orders by status."""
    sql = "SELECT COUNT(*) AS count FROM orders WHERE Status = %s"
    result = execute_query(sql, (status,), fetch_one=True)
    return result['count'] if result else 0


def get_active_orders_for_flight(flight_id):
    """Get all active (non-cancelled) orders for a specific flight."""
    sql = """
        SELECT o.UniqueOrderCode, o.TotalCost, o.Status,
               o.GuestCustomer_UniqueMail, o.RegisteredCustomer_UniqueMail,
               COUNT(t.TicketId) as TicketCount,
               (SELECT CASE 
                    WHEN COUNT(DISTINCT t2.Class) > 1 THEN 'mixed'
                    ELSE MAX(t2.Class)
                END FROM Tickets t2 WHERE t2.orders_UniqueOrderCode = o.UniqueOrderCode) as Class
        FROM orders o
        LEFT JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
        WHERE o.Flights_FlightId = %s 
          AND o.Status != 'cancelled'
        GROUP BY o.UniqueOrderCode
    """
    return execute_query(sql, (flight_id,))


def count_active_orders_for_flight(flight_id):
    """Count active orders for a flight."""
    sql = """
        SELECT COUNT(*) AS count
        FROM orders
        WHERE Flights_FlightId = %s 
          AND Status != 'cancelled'
    """
    result = execute_query(sql, (flight_id,), fetch_one=True)
    return result['count'] if result else 0


def get_total_revenue():
    """Get total revenue from all confirmed orders."""
    sql = """
        SELECT COALESCE(SUM(TotalCost), 0) as total_revenue
        FROM orders
        WHERE Status = 'confirmed'
    """
    result = execute_query(sql, fetch_one=True)
    return float(result['total_revenue']) if result else 0


class SeatAlreadyTakenError(Exception):
    """Raised when attempting to book a seat that is already taken."""
    pass


def create_ticket(order_code, row_num, seat, seat_class, validate_seat=True):
    """Create ticket with optional seat validation. Raises SeatAlreadyTakenError if taken."""
    if validate_seat:
        # Get flight ID from order
        flight_id = get_flight_id_for_order(order_code)
        if flight_id and is_seat_taken_for_flight(flight_id, row_num, seat):
            raise SeatAlreadyTakenError(f"Seat {row_num}{seat} is already taken for this flight.")
    
    sql = """
        INSERT INTO Tickets (orders_UniqueOrderCode, RowNum, Seat, Class)
        VALUES (%s, %s, %s, %s)
    """
    return execute_query(sql, (order_code, row_num, seat, seat_class), commit=True)


def get_tickets_for_order(booking_code):
    """Get all tickets for an order with dynamically calculated price."""
    sql = """
        SELECT t.TicketId, t.Class, t.RowNum, t.Seat,
               CASE WHEN t.Class = 'business' THEN f.BusinessPrice ELSE f.EconomyPrice END as Price,
               o.Flights_FlightId,
               f.Airplanes_AirplaneId as Flights_Airplanes_AirplaneId,
               CONCAT(t.RowNum, t.Seat) as SeatCode
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        JOIN Flights f ON o.Flights_FlightId = f.FlightId
        WHERE t.orders_UniqueOrderCode = %s
        ORDER BY t.Class DESC, t.RowNum, t.Seat
    """
    return execute_query(sql, (booking_code,))


def get_ticket_by_id(ticket_id):
    """Get a ticket by its ID with flight info from order."""
    sql = """
        SELECT t.TicketId, t.Class, t.RowNum, t.Seat,
               CASE WHEN t.Class = 'business' THEN f.BusinessPrice ELSE f.EconomyPrice END as Price,
               t.orders_UniqueOrderCode,
               o.Flights_FlightId,
               f.Airplanes_AirplaneId as Flights_Airplanes_AirplaneId
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        JOIN Flights f ON o.Flights_FlightId = f.FlightId
        WHERE t.TicketId = %s
    """
    return execute_query(sql, (ticket_id,), fetch_one=True)


def delete_tickets_for_order(booking_code):
    """Delete all tickets for an order (used when cancelling)."""
    sql = "DELETE FROM Tickets WHERE orders_UniqueOrderCode = %s"
    return execute_query(sql, (booking_code,), commit=True)


def count_tickets_for_flight(flight_id):
    """Count total tickets sold for a flight (non-cancelled orders only)."""
    sql = """
        SELECT COUNT(*) AS count
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE o.Flights_FlightId = %s 
          AND o.Status != 'cancelled'
    """
    result = execute_query(sql, (flight_id,), fetch_one=True)
    return result['count'] if result else 0
