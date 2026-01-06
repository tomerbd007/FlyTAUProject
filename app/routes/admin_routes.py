"""
FLYTAU Admin Routes
Handles admin dashboard, flight management, and flight cancellation
"""
from flask import render_template, request, redirect, url_for, flash, session
from app.services import admin_service, flight_service
from app.utils.decorators import manager_required


def register_admin_routes(app):
    """Register admin routes with the Flask app."""
    
    @app.route('/admin')
    @manager_required
    def admin_dashboard():
        """Admin dashboard page."""
        # Get summary statistics
        stats = admin_service.get_dashboard_stats()
        return render_template('admin/dashboard.html', stats=stats)
    
    @app.route('/admin/flights')
    @manager_required
    def admin_flights():
        """Admin flight list with status filter."""
        status_filter = request.args.get('status', '')
        flights = admin_service.get_all_flights(status_filter)
        
        return render_template('admin/flight_list.html',
                               flights=flights,
                               current_filter=status_filter)
    
    @app.route('/admin/flights/add', methods=['GET', 'POST'])
    @manager_required
    def add_flight_step1():
        """Add flight - Step 1: Date, time, origin, destination."""
        if request.method == 'POST':
            departure_date = request.form.get('departure_date', '')
            departure_time = request.form.get('departure_time', '')
            origin = request.form.get('origin', '')
            destination = request.form.get('destination', '')
            
            # Validation
            errors = []
            if not departure_date:
                errors.append('Departure date is required.')
            if not departure_time:
                errors.append('Departure time is required.')
            if not origin:
                errors.append('Origin is required.')
            if not destination:
                errors.append('Destination is required.')
            if origin and destination and origin == destination:
                errors.append('Origin and destination must be different.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                airports = flight_service.get_all_airports()
                return render_template('admin/add_flight_step1.html', airports=airports)
            
            # Get route and compute duration
            route = admin_service.get_route(origin, destination)
            if not route:
                flash('No route found for this origin-destination pair.', 'error')
                airports = flight_service.get_all_airports()
                return render_template('admin/add_flight_step1.html', airports=airports)
            
            # Calculate arrival datetime
            departure_datetime, arrival_datetime = admin_service.compute_flight_times(
                departure_date, departure_time, route['duration_minutes']
            )
            
            # Store in session for next step
            session['add_flight'] = {
                'route_id': route['id'],
                'origin': origin,
                'destination': destination,
                'duration_minutes': route['duration_minutes'],
                'departure_datetime': departure_datetime.isoformat(),
                'arrival_datetime': arrival_datetime.isoformat()
            }
            
            return redirect(url_for('add_flight_step2'))
        
        airports = flight_service.get_all_airports()
        return render_template('admin/add_flight_step1.html', airports=airports)
    
    @app.route('/admin/flights/add/crew', methods=['GET', 'POST'])
    @manager_required
    def add_flight_step2():
        """Add flight - Step 2: Select aircraft and assign crew."""
        flight_data = session.get('add_flight')
        if not flight_data:
            flash('Please start from step 1.', 'warning')
            return redirect(url_for('add_flight_step1'))
        
        duration = flight_data['duration_minutes']
        is_long_flight = duration > 360  # > 6 hours
        
        if request.method == 'POST':
            aircraft_id = request.form.get('aircraft_id')
            pilot_ids = request.form.getlist('pilots')
            attendant_ids = request.form.getlist('attendants')
            
            if not aircraft_id:
                flash('Please select an aircraft.', 'error')
                return redirect(url_for('add_flight_step2'))
            
            # Get aircraft to determine crew requirements
            aircraft = admin_service.get_aircraft_by_id(aircraft_id)
            if not aircraft:
                flash('Invalid aircraft selection.', 'error')
                return redirect(url_for('add_flight_step2'))
            
            # Validate crew requirements
            is_large = aircraft['size'] == 'large'
            required_pilots = 3 if is_large else 2
            required_attendants = 6 if is_large else 3
            
            if len(pilot_ids) != required_pilots:
                flash(f'Please select exactly {required_pilots} pilots.', 'error')
                return redirect(url_for('add_flight_step2'))
            
            if len(attendant_ids) != required_attendants:
                flash(f'Please select exactly {required_attendants} attendants.', 'error')
                return redirect(url_for('add_flight_step2'))
            
            # Store selections in session
            flight_data['aircraft_id'] = aircraft_id
            flight_data['aircraft_size'] = aircraft['size']
            flight_data['pilot_ids'] = pilot_ids
            flight_data['attendant_ids'] = attendant_ids
            session['add_flight'] = flight_data
            
            return redirect(url_for('add_flight_step3'))
        
        # Get available aircraft (big planes only for long flights, all for short)
        aircraft_list = admin_service.get_available_airplanes(
            flight_data['departure_datetime'],
            flight_data['arrival_datetime'],
            is_long_flight
        )
        
        # Get available crew
        available_pilots = admin_service.get_available_pilots(
            flight_data['departure_datetime'],
            flight_data['arrival_datetime'],
            is_long_flight
        )
        available_attendants = admin_service.get_available_attendants(
            flight_data['departure_datetime'],
            flight_data['arrival_datetime'],
            is_long_flight
        )
        
        return render_template('admin/add_flight_step2.html',
                               flight_data=flight_data,
                               aircraft_list=aircraft_list,
                               available_pilots=available_pilots,
                               available_attendants=available_attendants,
                               is_long_flight=is_long_flight)
    
    @app.route('/admin/flights/add/pricing', methods=['GET', 'POST'])
    @manager_required
    def add_flight_step3():
        """Add flight - Step 3: Set ticket prices."""
        flight_data = session.get('add_flight')
        if not flight_data or 'aircraft_id' not in flight_data:
            flash('Please complete the previous steps first.', 'warning')
            return redirect(url_for('add_flight_step1'))
        
        is_large = flight_data['aircraft_size'] == 'large'
        
        if request.method == 'POST':
            economy_price = request.form.get('economy_price', '')
            business_price = request.form.get('business_price', '') if is_large else None
            
            # Validation
            try:
                economy_price = float(economy_price)
                if economy_price <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                flash('Please enter a valid economy price.', 'error')
                return render_template('admin/add_flight_step3.html',
                                       flight_data=flight_data,
                                       is_large=is_large)
            
            if is_large:
                try:
                    business_price = float(business_price)
                    if business_price <= 0:
                        raise ValueError()
                except (ValueError, TypeError):
                    flash('Please enter a valid business price.', 'error')
                    return render_template('admin/add_flight_step3.html',
                                           flight_data=flight_data,
                                           is_large=is_large)
            
            # Create the flight
            try:
                flight_id = admin_service.create_flight(
                    route_id=flight_data['route_id'],
                    aircraft_id=flight_data['aircraft_id'],
                    departure_datetime=flight_data['departure_datetime'],
                    arrival_datetime=flight_data['arrival_datetime'],
                    economy_price=economy_price,
                    business_price=business_price,
                    pilot_ids=flight_data['pilot_ids'],
                    attendant_ids=flight_data['attendant_ids']
                )
                
                # Clear session data
                session.pop('add_flight', None)
                
                flash('Flight created successfully!', 'success')
                return redirect(url_for('admin_flights'))
            except Exception as e:
                flash(f'Error creating flight: {str(e)}', 'error')
                return render_template('admin/add_flight_step3.html',
                                       flight_data=flight_data,
                                       is_large=is_large)
        
        return render_template('admin/add_flight_step3.html',
                               flight_data=flight_data,
                               is_large=is_large)
    
    @app.route('/admin/flights/<int:flight_id>/cancel', methods=['GET', 'POST'])
    @manager_required
    def cancel_flight(flight_id):
        """Cancel a flight (72h rule applies)."""
        flight = flight_service.get_flight_details(flight_id)
        
        if not flight:
            flash('Flight not found.', 'error')
            return redirect(url_for('admin_flights'))
        
        # Check if cancellation is allowed
        can_cancel, message = admin_service.can_cancel_flight(flight)
        
        if not can_cancel:
            flash(message, 'error')
            return redirect(url_for('admin_flights'))
        
        # Get affected orders count
        affected_orders = admin_service.get_affected_orders_count(flight_id)
        
        if request.method == 'POST':
            try:
                admin_service.cancel_flight(flight_id)
                flash('Flight canceled. All active orders have been credited.', 'success')
                return redirect(url_for('admin_flights'))
            except Exception as e:
                flash(f'Error canceling flight: {str(e)}', 'error')
                return redirect(url_for('admin_flights'))
        
        return render_template('admin/cancel_flight.html',
                               flight=flight,
                               affected_orders=affected_orders)
