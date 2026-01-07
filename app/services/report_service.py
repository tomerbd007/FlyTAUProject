"""
FLYTAU Report Service
Executes report queries and formats results

Schema:
- Flights: FlightId + Airplanes_AirplaneId (composite PK), OriginPort, DestPort,
           DepartureDate, DepartureHour, Duration, Status
- Tickets: Track sold seats
- orders: UniqueOrderCode, TotalCost, Status
- Pilot/FlightAttendant: LongFlightsTraining
- Pilot_has_Flights, FlightAttendant_has_Flights: Crew assignments
"""
from app.db import execute_query
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
    return execute_query(sql)


def get_average_occupancy():
    """
    Get average occupancy for completed flights.
    
    Returns:
        List of dicts with flight info and occupancy percentage
    """
    sql = """
        SELECT 
            f.FlightId,
            f.DepartureDate,
            CONCAT(f.OriginPort, ' → ', f.DestPort) AS route,
            a.Manufacturer,
            COUNT(t.TicketId) AS sold_seats,
            (
                IFNULL(
                    (SELECT CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(`Business (Rows, Cols)`, ',', 1), '(', -1) AS UNSIGNED) *
                            CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(`Business (Rows, Cols)`, ')', 1), ',', -1) AS UNSIGNED)
                     FROM Airplanes WHERE AirplaneId = f.Airplanes_AirplaneId), 0
                ) +
                IFNULL(
                    (SELECT CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(`Couch (Rows, Cols)`, ',', 1), '(', -1) AS UNSIGNED) *
                            CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(`Couch (Rows, Cols)`, ')', 1), ',', -1) AS UNSIGNED)
                     FROM Airplanes WHERE AirplaneId = f.Airplanes_AirplaneId), 0
                )
            ) AS total_seats,
            ROUND(
                COUNT(t.TicketId) * 100.0 / 
                NULLIF(
                    (
                        IFNULL(
                            (SELECT CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(`Business (Rows, Cols)`, ',', 1), '(', -1) AS UNSIGNED) *
                                    CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(`Business (Rows, Cols)`, ')', 1), ',', -1) AS UNSIGNED)
                             FROM Airplanes WHERE AirplaneId = f.Airplanes_AirplaneId), 0
                        ) +
                        IFNULL(
                            (SELECT CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(`Couch (Rows, Cols)`, ',', 1), '(', -1) AS UNSIGNED) *
                                    CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(`Couch (Rows, Cols)`, ')', 1), ',', -1) AS UNSIGNED)
                             FROM Airplanes WHERE AirplaneId = f.Airplanes_AirplaneId), 0
                        )
                    ), 1
                ), 
                1
            ) AS occupancy_pct
        FROM Flights f
        JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
        LEFT JOIN Tickets t ON f.FlightId = t.Flights_FlightId 
            AND f.Airplanes_AirplaneId = t.Flights_Airplanes_AirplaneId
        LEFT JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        WHERE f.Status = 'occurred' AND (o.Status IS NULL OR o.Status != 'cancelled')
        GROUP BY f.FlightId, f.Airplanes_AirplaneId, f.DepartureDate, f.OriginPort, f.DestPort, a.Manufacturer
        ORDER BY f.DepartureDate DESC
    """
    return _execute_report_sql(sql)


def get_revenue_by_aircraft():
    """
    Get revenue breakdown by aircraft manufacturer and seat class.
    
    Returns:
        List of dicts with revenue data
    """
    sql = """
        SELECT 
            a.Manufacturer,
            t.Class,
            SUM(t.Price) AS total_revenue,
            COUNT(t.TicketId) AS tickets_sold
        FROM Tickets t
        JOIN orders o ON t.orders_UniqueOrderCode = o.UniqueOrderCode
        JOIN Flights f ON t.Flights_FlightId = f.FlightId 
            AND t.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
        JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
        WHERE o.Status = 'confirmed'
        GROUP BY a.Manufacturer, t.Class
        ORDER BY a.Manufacturer, t.Class
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
            crew_member,
            role,
            ROUND(SUM(
                CASE 
                    WHEN Duration <= 360 
                    THEN Duration / 60.0 
                    ELSE 0 
                END
            ), 1) AS short_flight_hours,
            ROUND(SUM(
                CASE 
                    WHEN Duration > 360 
                    THEN Duration / 60.0 
                    ELSE 0 
                END
            ), 1) AS long_flight_hours,
            ROUND(SUM(Duration / 60.0), 1) AS total_hours
        FROM (
            SELECT 
                CONCAT(p.FirstName, ' ', p.LastName) AS crew_member,
                'Pilot' AS role,
                f.Duration
            FROM Pilot p
            JOIN Pilot_has_Flights phf ON p.PilotId = phf.Pilot_PilotId
            JOIN Flights f ON phf.Flights_FlightId = f.FlightId 
                AND phf.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
            WHERE f.Status IN ('occurred', 'active')
            
            UNION ALL
            
            SELECT 
                CONCAT(fa.FirstName, ' ', fa.LastName) AS crew_member,
                'Flight Attendant' AS role,
                f.Duration
            FROM FlightAttendant fa
            JOIN FlightAttendant_has_Flights fahf ON fa.FlightAttendantId = fahf.FlightAttendant_FlightAttendantId
            JOIN Flights f ON fahf.Flights_FlightId = f.FlightId 
                AND fahf.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
            WHERE f.Status IN ('occurred', 'active')
        ) AS crew_flights
        GROUP BY crew_member, role
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
            DATE_FORMAT(f.DepartureDate, '%Y-%m') AS month,
            COUNT(o.UniqueOrderCode) AS total_orders,
            SUM(CASE WHEN o.Status IN ('customer_canceled', 'system_canceled') THEN 1 ELSE 0 END) AS canceled_orders,
            ROUND(
                SUM(CASE WHEN o.Status IN ('customer_canceled', 'system_canceled') THEN 1 ELSE 0 END) * 100.0 / 
                NULLIF(COUNT(o.UniqueOrderCode), 0),
                1
            ) AS cancellation_rate_pct
        FROM orders o
        JOIN Flights f ON o.Flights_FlightId = f.FlightId 
            AND o.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
        GROUP BY DATE_FORMAT(f.DepartureDate, '%Y-%m')
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
            DATE_FORMAT(f.DepartureDate, '%Y-%m') AS month,
            a.Manufacturer AS aircraft,
            SUM(CASE WHEN f.Status = 'done' THEN 1 ELSE 0 END) AS flights_completed,
            SUM(CASE WHEN f.Status = 'cancelled' THEN 1 ELSE 0 END) AS flights_canceled,
            COUNT(*) AS total_flights,
            ROUND(
                SUM(CASE WHEN f.Status = 'done' THEN 1 ELSE 0 END) * 100.0 / 
                NULLIF(COUNT(*), 0),
                1
            ) AS utilization_pct,
            (
                SELECT CONCAT(f2.OriginPort, ' → ', f2.DestPort)
                FROM Flights f2
                WHERE f2.Airplanes_AirplaneId = a.AirplaneId
                  AND DATE_FORMAT(f2.DepartureDate, '%Y-%m') = DATE_FORMAT(f.DepartureDate, '%Y-%m')
                GROUP BY f2.OriginPort, f2.DestPort
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) AS most_common_route
        FROM Flights f
        JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
        GROUP BY DATE_FORMAT(f.DepartureDate, '%Y-%m'), a.AirplaneId, a.Manufacturer
        ORDER BY month DESC, aircraft
    """
    return _execute_report_sql(sql)
