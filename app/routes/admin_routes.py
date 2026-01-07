"""
FLYTAU Admin Routes
Handles admin dashboard, flight management, and flight cancellation
"""
import json
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, session
from app.services import admin_service, flight_service
from app.repositories import flight_repository, crew_repository
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
        from datetime import datetime, timedelta

        status_filter = request.args.get('status', '')
        flights_raw = admin_service.get_all_flights(status_filter) or []

        flights = []
        for f in flights_raw:
            # Parse departure date/time into a single datetime object
            dep_date = f.get('DepartureDate')
            dep_hour = f.get('DepartureHour')

            if isinstance(dep_date, str):
                try:
                    dep_date_obj = datetime.strptime(dep_date, '%Y-%m-%d').date()
                except ValueError:
                    dep_date_obj = None
            else:
                dep_date_obj = dep_date

            if dep_hour:
                if isinstance(dep_hour, str):
                    try:
                        parts = dep_hour.split(':')
                        dep_time_obj = datetime.strptime(f"{parts[0]}:{parts[1]}", '%H:%M').time()
                    except ValueError:
                        dep_time_obj = datetime.min.time()
                elif hasattr(dep_hour, 'seconds'):
                    total_seconds = int(dep_hour.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    dep_time_obj = datetime.strptime(f"{hours}:{minutes}", '%H:%M').time()
                else:
                    dep_time_obj = datetime.min.time()
            else:
                dep_time_obj = datetime.min.time()

            departure_dt = datetime.combine(dep_date_obj, dep_time_obj) if dep_date_obj else datetime.now()

            # Seat availability for booked/total calculation
            seat_avail = flight_service.get_seat_availability(f.get('FlightId'), f.get('Airplanes_AirplaneId')) or {}
            business_avail = seat_avail.get('business', {}) or {}
            economy_avail = seat_avail.get('economy', {}) or {}

            business_total = business_avail.get('total', 0) or 0
            economy_total = economy_avail.get('total', 0) or 0
            business_available = business_avail.get('available', 0) or 0
            economy_available = economy_avail.get('available', 0) or 0

            total_seats = business_total + economy_total
            total_available = business_available + economy_available
            booked_seats = max(total_seats - total_available, 0)

            can_cancel = (departure_dt - datetime.now()) > timedelta(hours=36)

            flights.append({
                'id': f.get('FlightId'),
                'flight_number': f.get('FlightId'),
                'origin': f.get('OriginPort'),
                'destination': f.get('DestPort'),
                'departure_time': departure_dt,
                'aircraft_type': f.get('Manufacturer'),
                'status': (f.get('Status') or '').lower(),
                'booked_seats': booked_seats,
                'total_seats': total_seats,
                'can_cancel': can_cancel
            })

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
            flight_number = request.form.get('flight_number', '').upper().strip()
            
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
            
            # Validate flight number: exactly 6 alphanumeric characters
            if not flight_number:
                errors.append('Flight number is required.')
            elif len(flight_number) != 6:
                errors.append('Flight number must be exactly 6 characters.')
            elif not flight_number.isalnum():
                errors.append('Flight number must contain only letters and numbers.')
            else:
                # Check if flight number already exists
                existing = flight_repository.get_flight_by_id(flight_number)
                if existing:
                    errors.append(f'Flight number {flight_number} already exists.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                airports = flight_service.get_all_airports()
                min_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                return render_template('admin/add_flight_step1.html', 
                                       airports=airports,
                                       suggested_flight_number=flight_number or flight_repository.generate_flight_number(),
                                       min_date=min_date)
            
            # Get route and compute duration
            route = admin_service.get_route(origin, destination)
            if not route:
                flash('No route found for this origin-destination pair.', 'error')
                airports = flight_service.get_all_airports()
                min_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                return render_template('admin/add_flight_step1.html', 
                                       airports=airports,
                                       suggested_flight_number=flight_number,
                                       min_date=min_date)
            
            # Calculate arrival datetime
            departure_datetime, arrival_datetime = admin_service.compute_flight_times(
                departure_date, departure_time, route['duration_minutes']
            )
            
            # Store in session for next step
            session['add_flight'] = {
                'route_id': route['id'],
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'departure_time': departure_time,
                'duration_minutes': route['duration_minutes'],
                'departure_datetime': departure_datetime.isoformat(),
                'arrival_datetime': arrival_datetime.isoformat(),
                'flight_number': flight_number  # Use user-provided flight number
            }
            
            return redirect(url_for('add_flight_step2'))
        
        # Generate a suggested flight number for the form
        suggested_flight_number = flight_repository.generate_flight_number()
        airports = flight_service.get_all_airports()
        
        # Minimum date is tomorrow
        min_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        return render_template('admin/add_flight_step1.html', 
                               airports=airports,
                               suggested_flight_number=suggested_flight_number,
                               min_date=min_date)
    
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
            pilot_ids = request.form.getlist('pilot_ids')
            attendant_ids = request.form.getlist('attendant_ids')
            
            if not aircraft_id:
                flash('Please select an aircraft.', 'error')
                return redirect(url_for('add_flight_step2'))
            
            # Get aircraft to determine crew requirements
            aircraft = admin_service.get_airplane_by_id(aircraft_id)
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
        
        # Get aircraft details for seat counts
        aircraft = admin_service.get_airplane_by_id(flight_data['aircraft_id'])
        if not aircraft:
            flash('Aircraft not found.', 'error')
            return redirect(url_for('add_flight_step2'))
        
        # Get pilot and attendant names for display
        pilot_names = []
        for pid in flight_data.get('pilot_ids', []):
            pilot = crew_repository.get_pilot_by_id(pid)
            if pilot:
                pilot_names.append(f"{pilot['FirstName']} {pilot['SecondName']}")
        
        attendant_names = []
        for aid in flight_data.get('attendant_ids', []):
            attendant = crew_repository.get_attendant_by_id(aid)
            if attendant:
                attendant_names.append(f"{attendant['FirstName']} {attendant['SecondName']}")
        
        flight_data['pilot_names'] = pilot_names
        flight_data['attendant_names'] = attendant_names
        
        # Calculate seat counts from aircraft configuration
        seat_counts = {
            'economy': aircraft.get('economy_seats', 0),
            'business': aircraft.get('business_seats', 0),
            'total': aircraft.get('total_seats', 0)
        }
        
        # Add aircraft info to flight_data for display
        flight_data['aircraft_type'] = aircraft.get('Manufacturer', 'Unknown')
        flight_data['aircraft_registration'] = f"TAU-{flight_data['aircraft_id']}"
        
        # Suggested prices based on flight duration (simple formula)
        duration_hours = flight_data.get('duration_minutes', 120) / 60
        suggested_prices = {
            'economy': round(50 + (duration_hours * 30), 2),
            'business': round(150 + (duration_hours * 80), 2) if is_large else 0
        }
        
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
                                       is_large=is_large,
                                       seat_counts=seat_counts,
                                       suggested_prices=suggested_prices)
            
            if is_large:
                try:
                    business_price = float(business_price)
                    if business_price <= 0:
                        raise ValueError()
                except (ValueError, TypeError):
                    flash('Please enter a valid business price.', 'error')
                    return render_template('admin/add_flight_step3.html',
                                           flight_data=flight_data,
                                           is_large=is_large,
                                           seat_counts=seat_counts,
                                           suggested_prices=suggested_prices)
            
            # Create the flight
            try:
                # Parse departure datetime to extract date and time
                departure_dt = datetime.fromisoformat(flight_data['departure_datetime'])
                departure_date_str = departure_dt.strftime('%Y-%m-%d')
                departure_hour_str = departure_dt.strftime('%H:%M')
                
                flight_id = admin_service.create_flight(
                    airplane_id=flight_data['aircraft_id'],
                    origin=flight_data['origin'],
                    destination=flight_data['destination'],
                    departure_date=departure_date_str,
                    departure_hour=departure_hour_str,
                    duration=flight_data['duration_minutes'],
                    economy_price=economy_price,
                    business_price=business_price,
                    pilot_ids=flight_data['pilot_ids'],
                    attendant_ids=flight_data['attendant_ids'],
                    manager_id=session.get('user_id'),
                    flight_id=flight_data.get('flight_number')
                )
                
                # Clear session data
                session.pop('add_flight', None)
                
                flash('Flight created successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                flash(f'Error creating flight: {str(e)}', 'error')
                return render_template('admin/add_flight_step3.html',
                                       flight_data=flight_data,
                                       is_large=is_large,
                                       seat_counts=seat_counts,
                                       suggested_prices=suggested_prices)
        
        return render_template('admin/add_flight_step3.html',
                               flight_data=flight_data,
                               is_large=is_large,
                               seat_counts=seat_counts,
                               suggested_prices=suggested_prices)
    
    @app.route('/admin/flights/<flight_id>/cancel', methods=['GET', 'POST'])
    @manager_required
    def cancel_flight(flight_id):
        """Cancel a flight (72h rule applies)."""
        airplane_id = request.args.get('airplane_id')
        flight = flight_service.get_flight_details(flight_id, airplane_id)
        
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
