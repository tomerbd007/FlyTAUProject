"""Admin report routes."""
from datetime import datetime
from flask import render_template, request
from app.services import report_service
from app.utils.decorators import manager_required


def register_report_routes(app):
    """Register report routes with the Flask app."""
    
    @app.route('/admin/reports')
    @manager_required
    def reports_index():
        """Reports landing page with list of available reports."""
        reports = [
            {
                'id': 'occupancy',
                'name': 'Average Flight Occupancy',
                'description': 'Average seat occupancy percentage for completed flights.'
            },
            {
                'id': 'revenue',
                'name': 'Revenue by Aircraft',
                'description': 'Total revenue breakdown by aircraft manufacturer, size, and seat class.'
            },
            {
                'id': 'flight-hours',
                'name': 'Flight Hours per Employee',
                'description': 'Cumulative flight hours for each crew member, split by short and long flights.'
            },
            {
                'id': 'cancellation-rate',
                'name': 'Monthly Cancellation Rate',
                'description': 'Monthly order cancellation rate (customer and system cancellations).'
            },
            {
                'id': 'aircraft-activity',
                'name': 'Monthly Aircraft Activity',
                'description': 'Monthly flight activity summary per aircraft including utilization and routes.'
            }
        ]
        
        return render_template('reports/index.html', reports=reports)
    
    @app.route('/admin/reports/occupancy')
    @manager_required
    def report_occupancy():
        """Average occupancy report for flights."""
        result = report_service.get_average_occupancy()
        data = result.get('data', [])
        summary = result.get('summary', {})
        chart = result.get('chart')
        
        # Define columns for the table
        columns = [
            {'key': 'FlightId', 'label': 'Flight Number'},
            {'key': 'DepartureDate', 'label': 'Date', 'type': 'date'},
            {'key': 'route', 'label': 'Route'},
            {'key': 'Manufacturer', 'label': 'Aircraft'},
            {'key': 'sold_seats', 'label': 'Sold Seats', 'type': 'number'},
            {'key': 'total_seats', 'label': 'Total Seats', 'type': 'number'},
            {'key': 'occupancy_pct', 'label': 'Occupancy %', 'type': 'percent'},
        ]
        
        # Build summary items for display
        summary_items = []
        if summary.get('average_occupancy') is not None:
            summary_items.append({
                'label': 'Overall Average Occupancy',
                'value': f"{summary['average_occupancy']:.1f}%"
            })
        
        return render_template('reports/report_result.html',
                               report_title='Average Flight Occupancy',
                               report_description='Seat occupancy percentage across all flights',
                               columns=columns,
                               data=data,
                               summary=summary_items if summary_items else None,
                               chart=chart,
                               now=datetime.now())
    
    @app.route('/admin/reports/revenue')
    @manager_required
    def report_revenue():
        """Revenue breakdown by aircraft manufacturer, size, and class."""
        result = report_service.get_revenue_by_aircraft()
        data = result.get('data', [])
        summary = result.get('summary', {})
        chart = result.get('chart')
        
        # Define columns for the table
        columns = [
            {'key': 'AirplaneSize', 'label': 'Size'},
            {'key': 'Manufacturer', 'label': 'Manufacturer'},
            {'key': 'CabinClass', 'label': 'Cabin Class'},
            {'key': 'TotalRevenue', 'label': 'Total Revenue', 'type': 'currency'},
        ]
        
        # Build summary items
        summary_items = []
        if summary.get('total_revenue') is not None:
            summary_items.append({
                'label': 'Total Revenue',
                'value': f"${summary['total_revenue']:,.2f}"
            })
        
        return render_template('reports/report_result.html',
                               report_title='Revenue by Aircraft',
                               report_description='Revenue breakdown by aircraft manufacturer, size, and cabin class',
                               columns=columns,
                               data=data,
                               summary=summary_items if summary_items else None,
                               chart=chart,
                               now=datetime.now())
    
    @app.route('/admin/reports/flight-hours')
    @manager_required
    def report_flight_hours():
        """Flight hours per employee split by short/long flights."""
        result = report_service.get_flight_hours_per_employee()
        data = result.get('data', [])
        summary = result.get('summary', {})
        chart = result.get('chart')
        
        # Define columns for the table
        columns = [
            {'key': 'EmployeeID', 'label': 'Employee ID'},
            {'key': 'FullName', 'label': 'Name'},
            {'key': 'Role', 'label': 'Role'},
            {'key': 'CumulativeShortHours', 'label': 'Short Flight Hours', 'type': 'number'},
            {'key': 'CumulativeLongHours', 'label': 'Long Flight Hours', 'type': 'number'},
        ]
        
        # Build summary items
        summary_items = []
        if summary.get('total_short_hours') is not None:
            summary_items.append({
                'label': 'Total Short Flight Hours',
                'value': f"{summary['total_short_hours']:.1f}h"
            })
        if summary.get('total_long_hours') is not None:
            summary_items.append({
                'label': 'Total Long Flight Hours',
                'value': f"{summary['total_long_hours']:.1f}h"
            })
        
        return render_template('reports/report_result.html',
                               report_title='Flight Hours per Employee',
                               report_description='Cumulative flight hours split by short (≤6h) and long (>6h) flights',
                               columns=columns,
                               data=data,
                               summary=summary_items if summary_items else None,
                               chart=chart,
                               now=datetime.now())
    
    @app.route('/admin/reports/cancellation-rate')
    @manager_required
    def report_cancellation_rate():
        """Monthly order cancellation rate."""
        result = report_service.get_monthly_cancellation_rate()
        data = result.get('data', [])
        summary = result.get('summary', {})
        chart = result.get('chart')
        
        # Define columns for the table
        columns = [
            {'key': 'OrderMonth', 'label': 'Month', 'type': 'month'},
            {'key': 'CancellationRatePercent', 'label': 'Cancellation Rate', 'type': 'percent'},
        ]
        
        # Build summary items
        summary_items = []
        if summary.get('average_rate') is not None:
            summary_items.append({
                'label': 'Average Cancellation Rate',
                'value': f"{summary['average_rate']:.1f}%"
            })
        
        return render_template('reports/report_result.html',
                               report_title='Monthly Cancellation Rate',
                               report_description='Order cancellation rate by month',
                               columns=columns,
                               data=data,
                               summary=summary_items if summary_items else None,
                               chart=chart,
                               now=datetime.now())
    
    @app.route('/admin/reports/aircraft-activity')
    @manager_required
    def report_aircraft_activity():
        """Monthly activity summary per aircraft."""
        result = report_service.get_monthly_aircraft_activity()
        data = result.get('data', [])
        summary = result.get('summary', {})
        chart = result.get('chart')
        
        # Define columns for the table
        columns = [
            {'key': 'AirplaneId', 'label': 'Aircraft ID'},
            {'key': 'FlightMonth', 'label': 'Month', 'type': 'month'},
            {'key': 'FlightsPerformed', 'label': 'Flights Performed', 'type': 'number'},
            {'key': 'FlightsCancelled', 'label': 'Flights Cancelled', 'type': 'number'},
            {'key': 'UtilizationRatePercent', 'label': 'Utilization %', 'type': 'percent'},
            {'key': 'DominantRoute', 'label': 'Most Common Route'},
        ]
        
        # Build summary items
        summary_items = []
        if summary.get('total_performed') is not None:
            summary_items.append({
                'label': 'Total Flights Performed',
                'value': str(summary['total_performed'])
            })
        if summary.get('total_cancelled') is not None:
            summary_items.append({
                'label': 'Total Flights Cancelled',
                'value': str(summary['total_cancelled'])
            })
        
        return render_template('reports/report_result.html',
                               report_title='Monthly Aircraft Activity',
                               report_description='Flight activity and utilization per aircraft',
                               columns=columns,
                               data=data,
                               summary=summary_items if summary_items else None,
                               chart=chart,
                               now=datetime.now())
