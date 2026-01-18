"""Public flight search and seat selection routes."""
from datetime import date
from flask import render_template, request, redirect, url_for, flash, session
from app.services import flight_service
from app.utils.decorators import customer_or_guest


def register_flight_routes(app):
    """Register flight routes with the Flask app."""
    
    @app.route('/flights')
    def flights():
        """Flight search page with form."""
        # Get available airports for dropdowns
        airports = flight_service.get_all_airports()
        today = date.today().strftime('%Y-%m-%d')
        
        return render_template('flights/search.html', 
                               airports=airports,
                               today=today)
    
    @app.route('/flights/search')
    def flight_search():
        """Alias for flights page - redirects to search form."""
        return redirect(url_for('flights'))
    
    @app.route('/flights/results')
    def flight_search_results():
        """Search results page."""
        departure_date = request.args.get('date', '')
        origin = request.args.get('origin', '')
        destination = request.args.get('destination', '')
        passengers = request.args.get('passengers', '1')
        
        # Validate at least origin and destination
        if not origin or not destination:
            flash('Please select both origin and destination.', 'warning')
            return redirect(url_for('flights'))
        
        if origin == destination:
            flash('Origin and destination cannot be the same.', 'warning')
            return redirect(url_for('flights'))
        
        # Search for flights (includes direct and indirect)
        results = flight_service.search_available_flights(
            departure_date=departure_date if departure_date else None,
            origin=origin,
            destination=destination,
            include_indirect=True
        )
        
        # Get airports for the search form
        airports = flight_service.get_all_airports()
        today = date.today().strftime('%Y-%m-%d')
        
        return render_template('flights/results.html',
                               flights=results,
                               origin=origin,
                               destination=destination,
                               date=departure_date,
                               passengers=passengers,
                               airports=airports,
                               today=today)
    
    @app.route('/flights/<flight_id>')
    def flight_detail(flight_id):
        """Flight detail page."""
        # Check if user is a manager (view-only mode)
        is_manager = session.get('role') == 'manager'
        
        airplane_id = request.args.get('airplane_id')
        passengers = request.args.get('passengers', '1')
        
        flight = flight_service.get_flight_details(flight_id, airplane_id)
        
        if not flight:
            flash('Flight not found.', 'error')
            if is_manager:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('flights'))
        
        # Get seat availability counts
        seat_counts = flight_service.get_seat_availability(
            flight_id, 
            flight.get('Airplanes_AirplaneId') or airplane_id
        )
        
        return render_template('flights/detail.html',
                               flight=flight,
                               seat_counts=seat_counts,
                               passengers=passengers,
                               is_manager=is_manager)
    
    @app.route('/flights/<flight_id>/seats', methods=['GET', 'POST'])
    @customer_or_guest
    def seat_selection(flight_id):
        """Seat selection page."""
        airplane_id = request.args.get('airplane_id')
        
        # Check if user is a manager (managers cannot purchase tickets)
        if session.get('role') == 'manager':
            flash('Managers are not allowed to purchase tickets.', 'error')
            return redirect(url_for('flight_detail', flight_id=flight_id, airplane_id=airplane_id))
        
        flight = flight_service.get_flight_details(flight_id, airplane_id)
        if not flight:
            flash('Flight not found.', 'error')
            return redirect(url_for('flights'))
        
        actual_airplane_id = flight.get('Airplanes_AirplaneId') or airplane_id
        
        if flight.get('Status') != 'active':
            flash('This flight is not available for booking.', 'error')
            return redirect(url_for('flights'))
        
        if request.method == 'POST':
            selected_seats = request.form.getlist('seats')
            
            if not selected_seats:
                flash('Please select at least one seat.', 'warning')
                return redirect(url_for('seat_selection', flight_id=flight_id, airplane_id=actual_airplane_id))
            
            # Store selected seats in session for checkout
            session['checkout'] = {
                'flight_id': flight_id,
                'airplane_id': actual_airplane_id,
                'seats': selected_seats
            }
            
            return redirect(url_for('checkout'))
        
        # Build seat map for the flight
        seat_map = flight_service.build_seat_map(flight_id, actual_airplane_id)
        
        return render_template('flights/seat_selection.html',
                               flight=flight,
                               seat_map=seat_map)
