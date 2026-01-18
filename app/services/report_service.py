"""
FLYTAU Report Service
Executes report queries from SQL files and generates visualizations.

Schema:
- Flights: FlightId, Airplanes_AirplaneId, OriginPort, DestPort,
           DepartureDate, DepartureHour, Duration, Status
- Tickets: Track sold seats
- orders: UniqueOrderCode, TotalCost, Status
- Pilot/FlightAttendant: LongFlightsTraining
- Pilot_has_Flights, FlightAttendant_has_Flights: Crew assignments
"""
from app.db import execute_query
from app.utils import charts
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
    Get average occupancy across all flights.
    Uses the avg_occupancy.sql report file.
    
    Returns:
        dict with 'data' (list of flight occupancy data), 'summary', and 'chart'
    """
    # Get per-flight occupancy data for the table
    detail_sql = """
        SELECT 
            f.FlightId,
            f.DepartureDate,
            CONCAT(f.OriginPort, ' → ', f.DestPort) AS route,
            a.Manufacturer,
            COUNT(t.TicketId) AS sold_seats,
            (
                IFNULL(a.BusinessRows * a.BusinessCols, 0) +
                IFNULL(a.CouchRows * a.CouchCols, 0)
            ) AS total_seats,
            ROUND(
                COUNT(t.TicketId) * 100.0 / 
                NULLIF(
                    IFNULL(a.BusinessRows * a.BusinessCols, 0) +
                    IFNULL(a.CouchRows * a.CouchCols, 0),
                    0
                ), 
                1
            ) AS occupancy_pct
        FROM Flights f
        JOIN Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
        LEFT JOIN orders o ON f.FlightId = o.Flights_FlightId AND o.Status = 'confirmed'
        LEFT JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
        GROUP BY f.FlightId, f.Airplanes_AirplaneId, f.DepartureDate, f.OriginPort, f.DestPort, a.Manufacturer,
                 a.BusinessRows, a.BusinessCols, a.CouchRows, a.CouchCols
        ORDER BY f.DepartureDate DESC
    """
    detail_data = _execute_report_sql(detail_sql) or []
    
    # Get overall average from the SQL file's query
    avg_sql = _load_sql_file('avg_occupancy.sql')
    avg_result = _execute_report_sql(avg_sql)
    
    avg_occupancy = 0
    if avg_result and len(avg_result) > 0:
        avg_occupancy = float(avg_result[0].get('AverageOccupancyRate') or 0)
    
    # Generate donut chart for average occupancy
    chart_img = None
    if avg_occupancy > 0:
        chart_img = charts.create_donut_chart(
            value=avg_occupancy,
            max_value=100,
            title='Average Flight Occupancy',
            label='of seats filled'
        )
    
    return {
        'data': detail_data,
        'summary': {'average_occupancy': avg_occupancy},
        'chart': chart_img
    }


def get_revenue_by_aircraft():
    """
    Get revenue breakdown by aircraft size, manufacturer, and cabin class.
    Uses the revenue_by_aircraft.sql report file.
    
    Returns:
        dict with 'data', 'summary', and 'chart'
    """
    sql = _load_sql_file('revenue_by_aircraft.sql')
    results = _execute_report_sql(sql) or []
    
    # Calculate total revenue
    total_revenue = sum(float(r.get('TotalRevenue') or 0) for r in results)
    
    # Prepare data for grouped bar chart
    # Group by Manufacturer, with Business and Economy as series
    manufacturers = []
    chart_data = {'Business': [], 'Economy': []}
    
    # Process results to group by manufacturer
    mfg_data = {}
    for row in results:
        mfg = row.get('Manufacturer') or 'Unknown'
        cabin = row.get('CabinClass') or 'economy'
        revenue = float(row.get('TotalRevenue') or 0)
        
        if mfg not in mfg_data:
            mfg_data[mfg] = {'business': 0, 'economy': 0}
        
        if cabin.lower() == 'business':
            mfg_data[mfg]['business'] += revenue
        else:
            mfg_data[mfg]['economy'] += revenue
    
    # Convert to chart format
    for mfg in sorted(mfg_data.keys()):
        manufacturers.append(mfg)
        chart_data['Business'].append(mfg_data[mfg]['business'])
        chart_data['Economy'].append(mfg_data[mfg]['economy'])
    
    # Generate grouped bar chart
    chart_img = None
    if manufacturers:
        chart_img = charts.create_grouped_bar_chart(
            categories=manufacturers,
            groups=['Business', 'Economy'],
            data=chart_data,
            title='Revenue by Manufacturer and Cabin Class',
            xlabel='Manufacturer',
            ylabel='Revenue ($)',
            value_format='${:,.0f}'
        )
    
    return {
        'data': results,
        'summary': {'total_revenue': total_revenue},
        'chart': chart_img
    }


def get_flight_hours_per_employee():
    """
    Get cumulative flight hours per employee, split by short/long flights.
    Uses the flight_hours_per_employee.sql report file.
    
    Returns:
        dict with 'data', 'summary', and 'chart'
    """
    sql = _load_sql_file('flight_hours_per_employee.sql')
    results = _execute_report_sql(sql) or []
    
    # Prepare data for stacked horizontal bar chart
    labels = []
    short_hours = []
    long_hours = []
    
    for row in results:
        name = row.get('FullName') or row.get('crew_member') or 'Unknown'
        role = row.get('Role') or row.get('role') or ''
        labels.append(f"{name} ({role})")
        short_hours.append(float(row.get('CumulativeShortHours') or row.get('short_flight_hours') or 0))
        long_hours.append(float(row.get('CumulativeLongHours') or row.get('long_flight_hours') or 0))
    
    # Calculate totals
    total_short = sum(short_hours)
    total_long = sum(long_hours)
    
    # Generate stacked bar chart
    chart_img = None
    if labels:
        chart_img = charts.create_stacked_bar_chart(
            labels=labels[:15],  # Limit to top 15 employees
            data={
                'Short Flights (≤6h)': short_hours[:15],
                'Long Flights (>6h)': long_hours[:15]
            },
            title='Flight Hours per Employee',
            xlabel='Hours',
            ylabel='Employee',
            horizontal=True
        )
    
    return {
        'data': results,
        'summary': {'total_short_hours': total_short, 'total_long_hours': total_long},
        'chart': chart_img
    }


def get_monthly_cancellation_rate():
    """
    Get monthly order cancellation rate.
    Uses the monthly_cancellation_rate.sql report file.
    
    Returns:
        dict with 'data', 'summary', and 'chart'
    """
    sql = _load_sql_file('monthly_cancellation_rate.sql')
    results = _execute_report_sql(sql) or []
    
    # Prepare data for line chart
    months = []
    rates = []
    
    # Convert month numbers to readable format
    month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for row in results:
        month_num = int(row.get('OrderMonth') or 0)
        if 1 <= month_num <= 12:
            months.append(month_names[month_num])
        else:
            months.append(f"Month {month_num}")
        rates.append(float(row.get('CancellationRatePercent') or 0))
    
    # Calculate average cancellation rate
    avg_rate = sum(rates) / len(rates) if rates else 0
    
    # Generate line chart (reverse to show chronological order)
    chart_img = None
    if months:
        # Reverse lists for chronological order (oldest first)
        chart_img = charts.create_line_chart(
            labels=list(reversed(months)),
            values=list(reversed(rates)),
            title='Monthly Cancellation Rate Trend',
            xlabel='Month',
            ylabel='Cancellation Rate (%)',
            fill=True,
            marker=True
        )
    
    return {
        'data': results,
        'summary': {'average_rate': avg_rate},
        'chart': chart_img
    }


def get_monthly_aircraft_activity():
    """
    Get monthly activity summary per aircraft.
    Uses the monthly_aircraft_activity.sql report file.
    
    Returns:
        dict with 'data', 'summary', and 'chart'
    """
    sql = _load_sql_file('monthly_aircraft_activity.sql')
    results = _execute_report_sql(sql) or []
    
    # Prepare data for multi-bar chart
    # Group by aircraft, showing performed vs cancelled
    aircraft_data = {}
    for row in results:
        aircraft = row.get('AirplaneId') or 'Unknown'
        performed = int(row.get('FlightsPerformed') or 0)
        cancelled = int(row.get('FlightsCancelled') or 0)
        
        if aircraft not in aircraft_data:
            aircraft_data[aircraft] = {'performed': 0, 'cancelled': 0}
        aircraft_data[aircraft]['performed'] += performed
        aircraft_data[aircraft]['cancelled'] += cancelled
    
    # Convert to chart format
    aircraft_labels = sorted(aircraft_data.keys())
    performed_values = [aircraft_data[a]['performed'] for a in aircraft_labels]
    cancelled_values = [aircraft_data[a]['cancelled'] for a in aircraft_labels]
    
    # Calculate totals
    total_performed = sum(performed_values)
    total_cancelled = sum(cancelled_values)
    
    # Generate multi-bar chart
    chart_img = None
    if aircraft_labels:
        chart_img = charts.create_multi_bar_chart(
            categories=aircraft_labels,
            series1_label='Flights Performed',
            series1_values=performed_values,
            series2_label='Flights Cancelled',
            series2_values=cancelled_values,
            title='Aircraft Activity Summary',
            xlabel='Aircraft',
            ylabel='Number of Flights'
        )
    
    return {
        'data': results,
        'summary': {'total_performed': total_performed, 'total_cancelled': total_cancelled},
        'chart': chart_img
    }
