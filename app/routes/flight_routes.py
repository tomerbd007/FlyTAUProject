"""
FLYTAU Flight Routes
Handles public flight search, flight details, and seat selection
"""
from flask import render_template, request, redirect, url_for, flash, session
from app.services import flight_service
from app.utils.decorators import customer_or_guest


def register_flight_routes(app):
    """Register flight routes with the Flask app."""
    
    @app.route('/flights')
    def flights():
        """Flight search page with form."""
        # Get available origins and destinations for dropdowns
        routes = flight_service.get_all_routes()
        origins = sorted(set(r['origin'] for r in routes))
        destinations = sorted(set(r['destination'] for r in routes))
        
        return render_template('flights/search.html', 
                               origins=origins, 
                               destinations=destinations)
    
    @app.route('/flights/search')
    def flight_search():
        """Search results page."""
        departure_date = request.args.get('departure_date', '')
        origin = request.args.get('origin', '')
        destination = request.args.get('destination', '')
        
        # Validate at least one search parameter
        if not departure_date and not origin and not destination:
            flash('Please enter at least one search criterion.', 'warning')
            return redirect(url_for('flights'))
        
        # Search for flights
        results = flight_service.search_available_flights(
            departure_date=departure_date,
            origin=origin,
            destination=destination
        )
        
        # Get routes for the search form
        routes = flight_service.get_all_routes()
        origins = sorted(set(r['origin'] for r in routes))
        destinations = sorted(set(r['destination'] for r in routes))
        
        return render_template('flights/results.html',
                               flights=results,
                               search_params={
                                   'departure_date': departure_date,
                                   'origin': origin,
                                   'destination': destination
                               },
                               origins=origins,
                               destinations=destinations)
    
    @app.route('/flights/<int:flight_id>')
    def flight_detail(flight_id):
        """Flight detail page."""
        flight = flight_service.get_flight_details(flight_id)
        
        if not flight:
            flash('Flight not found.', 'error')
            return redirect(url_for('flights'))
        
        # Get seat availability counts
        seat_counts = flight_service.get_seat_availability_counts(flight_id)
        
        return render_template('flights/detail.html',
                               flight=flight,
                               seat_counts=seat_counts)
    
    @app.route('/flights/<int:flight_id>/seats', methods=['GET', 'POST'])
    @customer_or_guest
    def seat_selection(flight_id):
        """Seat selection page."""
        # Check if user is a manager (managers cannot purchase tickets)
        if session.get('role') == 'manager':
            flash('Managers are not allowed to purchase tickets.', 'error')
            return redirect(url_for('flight_detail', flight_id=flight_id))
        
        flight = flight_service.get_flight_details(flight_id)
        if not flight:
            flash('Flight not found.', 'error')
            return redirect(url_for('flights'))
        
        if flight['status'] != 'active':
            flash('This flight is not available for booking.', 'error')
            return redirect(url_for('flights'))
        
        if request.method == 'POST':
            selected_seats = request.form.getlist('seats')
            
            if not selected_seats:
                flash('Please select at least one seat.', 'warning')
                return redirect(url_for('seat_selection', flight_id=flight_id))
            
            # Store selected seats in session for checkout
            session['checkout'] = {
                'flight_id': flight_id,
                'seats': selected_seats
            }
            
            return redirect(url_for('checkout'))
        
        # Get all seats for the flight
        seats = flight_service.get_flight_seats(flight_id)
        
        # Organize seats by class and row for display
        seat_map = flight_service.organize_seat_map(seats, flight['aircraft_size'])
        
        return render_template('flights/seat_selection.html',
                               flight=flight,
                               seat_map=seat_map)
