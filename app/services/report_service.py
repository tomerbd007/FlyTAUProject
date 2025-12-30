"""
FLYTAU Report Service
Executes report queries and formats results
"""
from app import db
import os


# Path to SQL report files
SQL_REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sql', 'reports')


def _load_sql_file(filename):
    """Load SQL from file."""
    filepath = os.path.join(SQL_REPORTS_DIR, filename)
    with open(filepath, 'r') as f:
        return f.read()


def _execute_report_sql(sql):
    """Execute SQL and return results."""
    return db.execute_query(sql, fetch_all=True)


def get_average_occupancy():
    """
    Get average occupancy for completed flights.
    
    Returns:
        List of dicts with flight info and occupancy percentage
    """
    sql = """
        SELECT 
            f.flight_number,
            DATE(f.departure_datetime) AS flight_date,
            CONCAT(r.origin, ' → ', r.destination) AS route,
            COUNT(CASE WHEN fs.status = 'sold' THEN 1 END) AS sold_seats,
            COUNT(fs.id) AS total_seats,
            ROUND(
                COUNT(CASE WHEN fs.status = 'sold' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(fs.id), 0), 
                1
            ) AS occupancy_pct
        FROM flights f
        JOIN routes r ON f.route_id = r.id
        JOIN flight_seats fs ON f.id = fs.flight_id
        WHERE f.status = 'occurred'
        GROUP BY f.id, f.flight_number, f.departure_datetime, r.origin, r.destination
        ORDER BY f.departure_datetime DESC
    """
    return _execute_report_sql(sql)


def get_revenue_by_aircraft():
    """
    Get revenue breakdown by aircraft manufacturer, size, and seat class.
    
    Returns:
        List of dicts with revenue data
    """
    sql = """
        SELECT 
            a.manufacturer,
            a.size,
            fs.seat_class,
            SUM(ol.price) AS total_revenue
        FROM order_lines ol
        JOIN flight_seats fs ON ol.flight_seat_id = fs.id
        JOIN flights f ON fs.flight_id = f.id
        JOIN aircraft a ON f.aircraft_id = a.id
        JOIN orders o ON ol.order_id = o.id
        WHERE o.status IN ('active', 'completed')
        GROUP BY a.manufacturer, a.size, fs.seat_class
        ORDER BY a.manufacturer, a.size, fs.seat_class
    """
    return _execute_report_sql(sql)


def get_flight_hours_per_employee():
    """
    Get cumulative flight hours per crew member, split by short/long flights.
    
    Returns:
        List of dicts with employee flight hours
    """
    sql = """
        SELECT 
            e.employee_code,
            CONCAT(e.first_name, ' ', e.last_name) AS name,
            e.role,
            ROUND(SUM(
                CASE 
                    WHEN TIMESTAMPDIFF(MINUTE, f.departure_datetime, f.arrival_datetime) <= 360 
                    THEN TIMESTAMPDIFF(MINUTE, f.departure_datetime, f.arrival_datetime) / 60.0 
                    ELSE 0 
                END
            ), 1) AS short_flight_hours,
            ROUND(SUM(
                CASE 
                    WHEN TIMESTAMPDIFF(MINUTE, f.departure_datetime, f.arrival_datetime) > 360 
                    THEN TIMESTAMPDIFF(MINUTE, f.departure_datetime, f.arrival_datetime) / 60.0 
                    ELSE 0 
                END
            ), 1) AS long_flight_hours,
            ROUND(SUM(
                TIMESTAMPDIFF(MINUTE, f.departure_datetime, f.arrival_datetime) / 60.0
            ), 1) AS total_hours
        FROM employees e
        JOIN crew_assignments ca ON e.id = ca.employee_id
        JOIN flights f ON ca.flight_id = f.id
        WHERE f.status IN ('occurred', 'active')
          AND e.role IN ('pilot', 'attendant')
        GROUP BY e.id, e.employee_code, e.first_name, e.last_name, e.role
        ORDER BY total_hours DESC
    """
    return _execute_report_sql(sql)


def get_monthly_cancellation_rate():
    """
    Get monthly order cancellation rate.
    
    Returns:
        List of dicts with monthly cancellation statistics
    """
    sql = """
        SELECT 
            DATE_FORMAT(created_at, '%Y-%m') AS month,
            COUNT(*) AS total_orders,
            SUM(CASE WHEN status IN ('customer_canceled', 'system_canceled') THEN 1 ELSE 0 END) AS canceled_orders,
            ROUND(
                SUM(CASE WHEN status IN ('customer_canceled', 'system_canceled') THEN 1 ELSE 0 END) * 100.0 / 
                NULLIF(COUNT(*), 0),
                1
            ) AS cancellation_rate_pct
        FROM orders
        GROUP BY DATE_FORMAT(created_at, '%Y-%m')
        ORDER BY month DESC
    """
    return _execute_report_sql(sql)


def get_monthly_aircraft_activity():
    """
    Get monthly activity summary per aircraft.
    
    Returns:
        List of dicts with aircraft activity data
    """
    sql = """
        SELECT 
            DATE_FORMAT(f.departure_datetime, '%Y-%m') AS month,
            CONCAT(a.manufacturer, ' ', a.registration) AS aircraft,
            SUM(CASE WHEN f.status = 'occurred' THEN 1 ELSE 0 END) AS flights_completed,
            SUM(CASE WHEN f.status = 'canceled' THEN 1 ELSE 0 END) AS flights_canceled,
            ROUND(
                SUM(CASE WHEN f.status = 'occurred' THEN 1 ELSE 0 END) * 100.0 / 
                NULLIF(COUNT(*), 0),
                1
            ) AS utilization_pct,
            (
                SELECT CONCAT(r2.origin, ' → ', r2.destination)
                FROM flights f2
                JOIN routes r2 ON f2.route_id = r2.id
                WHERE f2.aircraft_id = a.id
                  AND DATE_FORMAT(f2.departure_datetime, '%Y-%m') = DATE_FORMAT(f.departure_datetime, '%Y-%m')
                GROUP BY r2.id, r2.origin, r2.destination
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) AS most_common_route
        FROM flights f
        JOIN aircraft a ON f.aircraft_id = a.id
        JOIN routes r ON f.route_id = r.id
        GROUP BY DATE_FORMAT(f.departure_datetime, '%Y-%m'), a.id, a.manufacturer, a.registration
        ORDER BY month DESC, aircraft
    """
    return _execute_report_sql(sql)
