"""
FLYTAU Order Repository
Database access for orders and tickets

Schema:
- orders: UniqueOrderCode (PK), TotalCost, Class, Status, 
          GuestCustomer_UniqueMail (nullable), RegisteredCustomer_UniqueMail (nullable),
          Flights_FlightId, Flights_Airplanes_AirplaneId
- Tickets: TicketId (PK), Class, RowNum, Seat, Price, orders_UniqueOrderCode,
           Flights_FlightId, Flights_Airplanes_AirplaneId

Note: Either GuestCustomer_UniqueMail OR RegisteredCustomer_UniqueMail should be set, not both.
"""
from app.db import execute_query
import random
import string


def generate_booking_code():
    """Generate a unique booking code in format FLY-XXXXXX."""
    while True:
        code = 'FLY-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not booking_code_exists(code):
            return code


def booking_code_exists(booking_code):
    """Check if a booking code already exists."""
    sql = "SELECT UniqueOrderCode FROM orders WHERE UniqueOrderCode = %s"
    return execute_query(sql, (booking_code,), fetch_one=True) is not None


# ============ ORDER OPERATIONS ============

def create_order(booking_code, flight_id, airplane_id, total_cost, status, 
                 guest_email=None, registered_email=None, seat_class=None):
    """
    Create a new order.
    
    Args:
        booking_code: UniqueOrderCode
        flight_id: Flights_FlightId
        airplane_id: Flights_Airplanes_AirplaneId
        total_cost: TotalCost
        status: Order status (e.g., 'confirmed', 'cancelled')
        guest_email: GuestCustomer_UniqueMail (if guest booking)
        registered_email: RegisteredCustomer_UniqueMail (if registered user booking)
        seat_class: Class (e.g., 'economy', 'business', 'mixed')
    """
    sql = """
        INSERT INTO orders (UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId,
                           TotalCost, Status, GuestCustomer_UniqueMail, 
                           RegisteredCustomer_UniqueMail, Class)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(sql, (booking_code, flight_id, airplane_id, total_cost, status,
                               guest_email, registered_email, seat_class), commit=True)


def get_order_by_booking_code(booking_code):
    """Get an order by booking code (UniqueOrderCode)."""
    sql = """
        SELECT o.UniqueOrderCode, o.TotalCost, o.Class, o.Status,
               o.GuestCustomer_UniqueMail, o.RegisteredCustomer_UniqueMail,
               o.Flights_FlightId, o.Flights_Airplanes_AirplaneId,
               f.OriginPort, f.DestPort, f.DepartureDate, f.DepartureHour, f.Duration,
               a.Manufacturer
        FROM orders o
        JOIN Flights f ON o.Flights_FlightId = f.FlightId 
            AND o.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
        JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
        WHERE o.UniqueOrderCode = %s
    """
    return execute_query(sql, (booking_code,), fetch_one=True)


def get_order_with_tickets(booking_code):
    """Get an order with all its tickets and flight details."""
    order = get_order_by_booking_code(booking_code)
    if not order:
        return None
    
    order = dict(order)
    
    # Get tickets for this order
    sql = """
        SELECT t.TicketId, t.Class, t.RowNum, t.Seat, t.Price,
               CONCAT(t.RowNum, t.Seat) as SeatCode
        FROM Tickets t
        WHERE t.orders_UniqueOrderCode = %s
        ORDER BY t.Class DESC, t.RowNum, t.Seat
    """
    tickets = execute_query(sql, (booking_code,))
    order['tickets'] = tickets if tickets else []
    
    return order


def get_orders_by_registered_customer(email, status_filter=None):
    """Get all orders for a registered customer."""
    sql = """
        SELECT o.UniqueOrderCode, o.TotalCost, o.Class, o.Status,
               o.Flights_FlightId, o.Flights_Airplanes_AirplaneId,
               f.OriginPort, f.DestPort, f.DepartureDate, f.DepartureHour,
               COUNT(t.TicketId) as TicketCount
        FROM orders o
        JOIN Flights f ON o.Flights_FlightId = f.FlightId 
            AND o.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
        LEFT JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
        WHERE o.RegisteredCustomer_UniqueMail = %s
    """
    params = [email]
    
    if status_filter:
        sql += " AND o.Status = %s"
        params.append(status_filter)
    
    sql += " GROUP BY o.UniqueOrderCode ORDER BY f.DepartureDate DESC"
    
    return execute_query(sql, tuple(params))


def get_orders_by_guest_email(email, status_filter=None):
    """Get all orders for a guest customer by email."""
    sql = """
        SELECT o.UniqueOrderCode, o.TotalCost, o.Class, o.Status,
               o.Flights_FlightId, o.Flights_Airplanes_AirplaneId,
               f.OriginPort, f.DestPort, f.DepartureDate, f.DepartureHour,
               COUNT(t.TicketId) as TicketCount
        FROM orders o
        JOIN Flights f ON o.Flights_FlightId = f.FlightId 
            AND o.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
        LEFT JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
        WHERE o.GuestCustomer_UniqueMail = %s
    """
    params = [email]
    
    if status_filter:
        sql += " AND o.Status = %s"
        params.append(status_filter)
    
    sql += " GROUP BY o.UniqueOrderCode ORDER BY f.DepartureDate DESC"
    
    return execute_query(sql, tuple(params))


def get_order_by_code_and_email(booking_code, email):
    """Get order by booking code and email (for guest lookup)."""
    sql = """
        SELECT o.UniqueOrderCode, o.TotalCost, o.Class, o.Status,
               o.GuestCustomer_UniqueMail, o.RegisteredCustomer_UniqueMail,
               o.Flights_FlightId, o.Flights_Airplanes_AirplaneId,
               f.OriginPort, f.DestPort, f.DepartureDate, f.DepartureHour, f.Duration
        FROM orders o
        JOIN Flights f ON o.Flights_FlightId = f.FlightId 
            AND o.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
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


def get_active_orders_for_flight(flight_id, airplane_id):
    """Get all active (non-cancelled) orders for a specific flight."""
    sql = """
        SELECT o.UniqueOrderCode, o.TotalCost, o.Class, o.Status,
               o.GuestCustomer_UniqueMail, o.RegisteredCustomer_UniqueMail,
               COUNT(t.TicketId) as TicketCount
        FROM orders o
        LEFT JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
        WHERE o.Flights_FlightId = %s 
          AND o.Flights_Airplanes_AirplaneId = %s
          AND o.Status != 'cancelled'
        GROUP BY o.UniqueOrderCode
    """
    return execute_query(sql, (flight_id, airplane_id))


def count_active_orders_for_flight(flight_id, airplane_id):
    """Count active orders for a flight."""
    sql = """
        SELECT COUNT(*) AS count
        FROM orders
        WHERE Flights_FlightId = %s 
          AND Flights_Airplanes_AirplaneId = %s
          AND Status != 'cancelled'
    """
    result = execute_query(sql, (flight_id, airplane_id), fetch_one=True)
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


# ============ TICKET OPERATIONS ============

def create_ticket(order_code, flight_id, airplane_id, row_num, seat, seat_class, price):
    """
    Create a new ticket.
    
    Args:
        order_code: orders_UniqueOrderCode
        flight_id: Flights_FlightId
        airplane_id: Flights_Airplanes_AirplaneId
        row_num: Row number
        seat: Seat letter (e.g., 'A', 'B', 'C')
        seat_class: 'business' or 'economy'
        price: Ticket price
    """
    sql = """
        INSERT INTO Tickets (orders_UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId,
                            RowNum, Seat, Class, Price)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(sql, (order_code, flight_id, airplane_id, row_num, seat, seat_class, price), commit=True)


def get_tickets_for_order(booking_code):
    """Get all tickets for an order."""
    sql = """
        SELECT TicketId, Class, RowNum, Seat, Price,
               Flights_FlightId, Flights_Airplanes_AirplaneId,
               CONCAT(RowNum, Seat) as SeatCode
        FROM Tickets
        WHERE orders_UniqueOrderCode = %s
        ORDER BY Class DESC, RowNum, Seat
    """
    return execute_query(sql, (booking_code,))


def get_ticket_by_id(ticket_id):
    """Get a ticket by its ID."""
    sql = """
        SELECT TicketId, Class, RowNum, Seat, Price,
               orders_UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId
        FROM Tickets
        WHERE TicketId = %s
    """
    return execute_query(sql, (ticket_id,), fetch_one=True)


def delete_tickets_for_order(booking_code):
    """Delete all tickets for an order (used when cancelling)."""
    sql = "DELETE FROM Tickets WHERE orders_UniqueOrderCode = %s"
    return execute_query(sql, (booking_code,), commit=True)


def count_tickets_for_flight(flight_id, airplane_id):
    """Count total tickets sold for a flight."""
    sql = """
        SELECT COUNT(*) AS count
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE t.Flights_FlightId = %s 
          AND t.Flights_Airplanes_AirplaneId = %s
          AND o.Status != 'cancelled'
    """
    result = execute_query(sql, (flight_id, airplane_id), fetch_one=True)
    return result['count'] if result else 0
