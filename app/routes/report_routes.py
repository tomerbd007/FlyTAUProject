"""
FLYTAU Report Routes
Handles admin reports - occupancy, revenue, flight hours, cancellation rate, aircraft activity
"""
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
        """Average occupancy report for completed flights."""
        results = report_service.get_average_occupancy()
        
        # Calculate overall average
        if results:
            overall_avg = sum(r['occupancy_pct'] for r in results) / len(results)
        else:
            overall_avg = 0
        
        return render_template('reports/report_result.html',
                               report_name='Average Flight Occupancy',
                               columns=['Flight Number', 'Date', 'Route', 'Sold Seats', 'Total Seats', 'Occupancy %'],
                               rows=results,
                               summary={'Overall Average Occupancy': f'{overall_avg:.1f}%'})
    
    @app.route('/admin/reports/revenue')
    @manager_required
    def report_revenue():
        """Revenue breakdown by aircraft manufacturer, size, and class."""
        results = report_service.get_revenue_by_aircraft()
        
        # Calculate total
        total_revenue = sum(r['total_revenue'] for r in results) if results else 0
        
        return render_template('reports/report_result.html',
                               report_name='Revenue by Aircraft',
                               columns=['Manufacturer', 'Size', 'Seat Class', 'Total Revenue'],
                               rows=results,
                               summary={'Total Revenue': f'${total_revenue:,.2f}'})
    
    @app.route('/admin/reports/flight-hours')
    @manager_required
    def report_flight_hours():
        """Flight hours per employee split by short/long flights."""
        results = report_service.get_flight_hours_per_employee()
        
        return render_template('reports/report_result.html',
                               report_name='Flight Hours per Employee',
                               columns=['Employee Code', 'Name', 'Role', 'Short Flight Hours', 'Long Flight Hours', 'Total Hours'],
                               rows=results,
                               summary=None)
    
    @app.route('/admin/reports/cancellation-rate')
    @manager_required
    def report_cancellation_rate():
        """Monthly order cancellation rate."""
        results = report_service.get_monthly_cancellation_rate()
        
        return render_template('reports/report_result.html',
                               report_name='Monthly Cancellation Rate',
                               columns=['Month', 'Total Orders', 'Canceled Orders', 'Cancellation Rate %'],
                               rows=results,
                               summary=None)
    
    @app.route('/admin/reports/aircraft-activity')
    @manager_required
    def report_aircraft_activity():
        """Monthly activity summary per aircraft."""
        results = report_service.get_monthly_aircraft_activity()
        
        return render_template('reports/report_result.html',
                               report_name='Monthly Aircraft Activity',
                               columns=['Month', 'Aircraft', 'Flights Completed', 'Flights Canceled', 'Utilization %', 'Most Common Route'],
                               rows=results,
                               summary=None)
