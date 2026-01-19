"""Everything to do with orders - checkout, viewing bookings, cancellations, guest lookup."""
from flask import render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from app.services import order_service, flight_service
from app.utils.decorators import login_required, customer_or_guest


def register_order_routes(app):
    """Hooks up all the order-related URLs."""
    
    @app.route('/checkout', methods=['GET', 'POST'])
    @customer_or_guest
    def checkout():
        """Checkout page - confirm selected seats and enter passenger details."""
        # Check if user is a manager (managers cannot purchase tickets)
        if session.get('role') == 'manager':
            flash('Managers are not allowed to purchase tickets.', 'error')
            return redirect(url_for('flights'))
        
        checkout_data = session.get('checkout')
        if not checkout_data:
            flash('No seats selected. Please select your seats first.', 'warning')
            return redirect(url_for('flights'))
        
        flight_id = checkout_data['flight_id']
        airplane_id = checkout_data.get('airplane_id')
        selected_seats = checkout_data['seats']
        
        # Get flight details
        flight = flight_service.get_flight_details(flight_id, airplane_id)
        if not flight:
            flash('Flight not found.', 'error')
            session.pop('checkout', None)
            return redirect(url_for('flights'))
        
        # Check if flight is still available for booking
        if flight.get('Status') != 'active':
            flash('This flight is no longer available for booking.', 'error')
            session.pop('checkout', None)
            return redirect(url_for('flights'))
        
        # Get seat details with prices
        seats_info = flight_service.get_seats_by_codes(flight_id, airplane_id, selected_seats)
        
        if request.method == 'POST':
            # Guest info if not logged in as customer
            guest_email = None
            guest_first_name = None
            guest_last_name = None
            guest_phone = None
            registered_email = None
            
            if session.get('user_id') and session.get('role') == 'customer':
                # Logged in customer - use their email
                registered_email = session.get('email')
            else:
                # Guest checkout - collect their info
                guest_first_name = request.form.get('first_name', '').strip()
                guest_last_name = request.form.get('last_name', '').strip()
                guest_email = request.form.get('email', '').strip()
                guest_phone = request.form.get('phone', '').strip() or None
                
                if not guest_first_name:
                    flash('Please enter your first name.', 'error')
                    return render_template('orders/checkout.html',
                                           flight=flight,
                                           seats=seats_info,
                                           total=sum(s['price'] for s in seats_info))
                if not guest_last_name:
                    flash('Please enter your last name.', 'error')
                    return render_template('orders/checkout.html',
                                           flight=flight,
                                           seats=seats_info,
                                           total=sum(s['price'] for s in seats_info))
                if not guest_email:
                    flash('Please enter your email address.', 'error')
                    return render_template('orders/checkout.html',
                                           flight=flight,
                                           seats=seats_info,
                                           total=sum(s['price'] for s in seats_info))
            
            # Prepare seats for order service (needs row, seat, class format)
            order_seats = []
            for seat in seats_info:
                order_seats.append({
                    'row': seat['row'],
                    'seat': seat['col'],
                    'class': seat['seat_class']
                })
            
            # Create order
            try:
                booking_code = order_service.create_order(
                    flight_id=flight_id,
                    airplane_id=airplane_id,
                    selected_seats=order_seats,
                    economy_price=flight.get('EconomyPrice') or 0,
                    business_price=flight.get('BusinessPrice') or 0,
                    registered_email=registered_email,
                    guest_email=guest_email,
                    guest_first_name=guest_first_name,
                    guest_last_name=guest_last_name,
                    guest_phone=guest_phone
                )
                
                # Clear checkout session
                session.pop('checkout', None)
                
                flash('Your order has been confirmed!', 'success')
                return redirect(url_for('order_confirmation', booking_code=booking_code))
            except ValueError as e:
                flash(str(e), 'error')
                return render_template('orders/checkout.html',
                                       flight=flight,
                                       seats=seats_info,
                                       total=sum(s['price'] for s in seats_info))
        
        return render_template('orders/checkout.html',
                               flight=flight,
                               seats=seats_info,
                               total=sum(s['price'] for s in seats_info))
    
    @app.route('/orders/<booking_code>')
    def order_confirmation(booking_code):
        """Order confirmation/receipt page."""
        order = order_service.get_order_with_tickets(booking_code)
        
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('index'))

        # Build view model with parsed datetimes for template safety
        from datetime import datetime, timedelta
        dep_date = order.get('DepartureDate')
        dep_hour = order.get('DepartureHour')
        duration_minutes = order.get('Duration') or 0

        if isinstance(dep_date, str):
            dep_date_obj = datetime.strptime(dep_date, '%Y-%m-%d').date()
        else:
            dep_date_obj = dep_date

        if dep_hour:
            if isinstance(dep_hour, str):
                parts = dep_hour.split(':')
                dep_time_obj = datetime.strptime(f"{parts[0]}:{parts[1]}", '%H:%M').time()
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
        arrival_dt = departure_dt + timedelta(minutes=int(duration_minutes))

        email = order.get('RegisteredCustomer_UniqueMail') or order.get('GuestCustomer_UniqueMail') or session.get('email', '')
        customer_name = session.get('name') if session.get('role') == 'customer' else None
        
        # Check if order can still be modified (36h rule)
        can_cancel = order_service.can_cancel_order(order)

        order_vm = {
            'booking_code': order.get('UniqueOrderCode'),
            'flight_number': order.get('Flights_FlightId'),
            'flight_id': order.get('Flights_FlightId'),
            'airplane_id': order.get('Flights_Airplanes_AirplaneId'),
            'origin': order.get('OriginPort'),
            'destination': order.get('DestPort'),
            'departure_time': departure_dt,
            'arrival_time': arrival_dt,
            'total_amount': float(order.get('TotalCost') or 0),
            'status': (order.get('Status') or '').lower(),
            'email': email,
            'customer_name': customer_name,
            'can_cancel': can_cancel,
        }

        tickets_vm = []
        for t in order.get('tickets', []):
            tickets_vm.append({
                'seat_number': t.get('SeatCode') or f"{t.get('RowNum', '')}{t.get('Seat', '')}",
                'seat_class': t.get('Class', 'economy'),
                'price': float(t.get('Price') or 0)
            })
        
        return render_template('orders/confirmation.html', order=order_vm, tickets=tickets_vm)
    
    @app.route('/orders')
    @login_required
    def my_orders():
        """List customer's orders."""
        if session.get('role') != 'customer':
            flash('Access denied.', 'error')
            return redirect(url_for('index'))
        
        status_filter = request.args.get('status', '')
        customer_email = session.get('email', '')
        orders_raw = order_service.get_customer_orders(customer_email, is_registered=True, status_filter=status_filter) or []

        # Build a safe view model with parsed datetimes and cancellation eligibility
        orders = []
        for o in orders_raw:
            dep_date = o.get('DepartureDate')
            dep_hour = o.get('DepartureHour')

            if isinstance(dep_date, str):
                dep_date_obj = datetime.strptime(dep_date, '%Y-%m-%d').date()
            else:
                dep_date_obj = dep_date

            if dep_hour:
                if isinstance(dep_hour, str):
                    parts = dep_hour.split(':')
                    dep_time_obj = datetime.strptime(f"{parts[0]}:{parts[1]}", '%H:%M').time()
                elif hasattr(dep_hour, 'seconds'):
                    total_seconds = int(dep_hour.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    dep_time_obj = datetime.strptime(f"{hours}:{minutes}", '%H:%M').time()
                else:
                    dep_time_obj = datetime.min.time()
            else:
                dep_time_obj = datetime.min.time()

            dep_dt = datetime.combine(dep_date_obj, dep_time_obj) if dep_date_obj else None

            can_cancel = False
            try:
                can_cancel = order_service.can_cancel_order(o)
            except Exception:
                can_cancel = False

            orders.append({
                'booking_code': o.get('UniqueOrderCode'),
                'status': (o.get('Status') or '').lower(),
                'origin': o.get('OriginPort'),
                'destination': o.get('DestPort'),
                'departure_time': dep_dt,
                'ticket_count': o.get('TicketCount', 0),
                'total_amount': float(o.get('TotalCost') or 0),
                'flight_number': o.get('Flights_FlightId'),
                'flight_id': o.get('Flights_FlightId'),
                'airplane_id': o.get('Flights_Airplanes_AirplaneId'),
                'can_cancel': can_cancel
            })

        # Show most imminent flights first
        orders.sort(key=lambda x: x.get('departure_time') or datetime.min, reverse=True)

        return render_template('orders/my_orders.html',
                               orders=orders,
                               current_filter=status_filter)
    
    @app.route('/orders/<booking_code>/cancel', methods=['GET', 'POST'])
    @login_required
    def customer_cancel_order(booking_code):
        """Cancel confirmation page and handler for logged-in customers."""
        if session.get('role') != 'customer':
            flash('Access denied.', 'error')
            return redirect(url_for('index'))

        booking_code = booking_code.strip().upper()
        email = session.get('email', '').strip().lower()

        if not booking_code:
            flash('Missing booking code.', 'error')
            return redirect(url_for('my_orders'))

        # Get order details for confirmation page
        order = order_service.get_order_with_tickets(booking_code)
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('my_orders'))
        
        # Verify ownership
        owner_email = order.get('RegisteredCustomer_UniqueMail') or order.get('GuestCustomer_UniqueMail')
        if not owner_email or owner_email.lower() != email.lower():
            flash('Access denied.', 'error')
            return redirect(url_for('my_orders'))
        
        # Check if cancellation is allowed
        if not order_service.can_cancel_order(order):
            flash('This order cannot be canceled. Cancellations must be made at least 36 hours before departure.', 'error')
            return redirect(url_for('my_orders'))
        
        # Calculate fee and refund for display
        fee, refund = order_service.calculate_cancellation_fee(order['TotalCost'])

        if request.method == 'POST':
            try:
                original_cost, fee, refund = order_service.cancel_order(booking_code, email)
                flash(f'Order canceled. Refund amount: ${refund:.2f} (5% fee: ${fee:.2f})', 'success')
            except ValueError as e:
                flash(str(e), 'error')
            return redirect(url_for('my_orders'))
        
        # Build order view model for template
        order_vm = {
            'booking_code': booking_code,
            'flight_number': order.get('Flights_FlightId'),
            'origin': order.get('OriginPort'),
            'destination': order.get('DestPort'),
            'departure_time': None,
            'ticket_count': len(order.get('tickets', [])),
            'total_amount': float(order.get('TotalCost') or 0)
        }
        
        # Parse departure datetime
        departure_date = order.get('DepartureDate')
        departure_hour = order.get('DepartureHour')
        if departure_date:
            if isinstance(departure_date, str):
                departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
            if departure_hour:
                if hasattr(departure_hour, 'total_seconds'):
                    total_seconds = int(departure_hour.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    order_vm['departure_time'] = datetime.combine(
                        departure_date,
                        datetime.strptime(f"{hours}:{minutes}", '%H:%M').time()
                    )
                elif isinstance(departure_hour, str):
                    try:
                        time_str = departure_hour[:5] if len(departure_hour) > 5 else departure_hour
                        order_vm['departure_time'] = datetime.combine(
                            departure_date,
                            datetime.strptime(time_str, '%H:%M').time()
                        )
                    except ValueError:
                        order_vm['departure_time'] = datetime.combine(departure_date, datetime.min.time())
        
        return render_template('orders/cancel_confirm.html',
                               order=order_vm,
                               cancellation_fee=fee,
                               refund_amount=refund,
                               is_guest=False)
    
    @app.route('/orders/<int:order_id>/detail')
    @login_required
    def order_detail(order_id):
        """Order detail page."""
        if session.get('role') != 'customer':
            flash('Access denied.', 'error')
            return redirect(url_for('index'))
        
        order = order_service.get_order_with_lines(order_id)
        
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('my_orders'))
        
        # Verify ownership
        if order['customer_id'] != session['user_id']:
            flash('Access denied.', 'error')
            return redirect(url_for('my_orders'))
        
        # Check if cancellation is allowed
        can_cancel = order_service.can_cancel_order(order)
        
        return render_template('orders/order_detail.html',
                               order=order,
                               can_cancel=can_cancel)
    
    @app.route('/orders/<int:order_id>/cancel', methods=['GET', 'POST'])
    @login_required
    def cancel_order(order_id):
        """Cancel an order."""
        if session.get('role') != 'customer':
            flash('Access denied.', 'error')
            return redirect(url_for('index'))
        
        order = order_service.get_order_with_lines(order_id)
        
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('my_orders'))
        
        # Verify ownership
        if order['customer_id'] != session['user_id']:
            flash('Access denied.', 'error')
            return redirect(url_for('my_orders'))
        
        # Check if cancellation is allowed
        if not order_service.can_cancel_order(order):
            flash('This order cannot be canceled. Cancellations must be made at least 36 hours before departure.', 'error')
            return redirect(url_for('order_detail', order_id=order_id))
        
        # Calculate cancellation fee
        fee, refund = order_service.calculate_cancellation_fee(order['paid_total'])
        
        if request.method == 'POST':
            try:
                order_service.cancel_order(order_id, session['user_id'])
                flash(f'Order canceled. Refund amount: ${refund:.2f} (5% cancellation fee: ${fee:.2f})', 'success')
                return redirect(url_for('my_orders'))
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('order_detail', order_id=order_id))
        
        return render_template('orders/cancel_confirm.html',
                               order=order,
                               fee=fee,
                               refund=refund)
    
    @app.route('/guest/lookup', methods=['GET', 'POST'])
    def guest_lookup():
        """Guest order lookup by booking code and email."""
        if request.method == 'POST':
            booking_code = request.form.get('booking_code', '').strip().upper()
            email = request.form.get('email', '').strip().lower()
            
            if not booking_code or not email:
                flash('Please enter both booking code and email.', 'error')
                return render_template('orders/guest_lookup.html')
            
            order = order_service.get_order_for_guest(booking_code, email)
            
            if not order:
                flash('No order found with that booking code and email.', 'error')
                return render_template('orders/guest_lookup.html')
            
            # Build a view model that matches the order_detail template expectations
            dep_date = order.get('DepartureDate')
            dep_time_raw = order.get('DepartureHour')
            duration_minutes = order.get('Duration') or 0

            # Parse departure datetime safely
            departure_dt = None
            if dep_date:
                if isinstance(dep_date, str):
                    dep_date_obj = datetime.strptime(dep_date, '%Y-%m-%d').date()
                else:
                    dep_date_obj = dep_date

                if dep_time_raw:
                    if isinstance(dep_time_raw, str):
                        time_parts = dep_time_raw.split(':')
                        dep_time_obj = datetime.strptime(f"{time_parts[0]}:{time_parts[1]}", '%H:%M').time()
                    elif hasattr(dep_time_raw, 'seconds'):
                        total_seconds = int(dep_time_raw.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        dep_time_obj = datetime.strptime(f"{hours}:{minutes}", '%H:%M').time()
                    else:
                        dep_time_obj = datetime.min.time()
                else:
                    dep_time_obj = datetime.min.time()

                departure_dt = datetime.combine(dep_date_obj, dep_time_obj)
            else:
                departure_dt = datetime.now()

            arrival_dt = departure_dt + timedelta(minutes=int(duration_minutes))

            contact_email = order.get('RegisteredCustomer_UniqueMail') or order.get('GuestCustomer_UniqueMail') or email
            can_cancel = departure_dt > datetime.now() + timedelta(hours=36)

            # Determine display status - show 'done' for completed flights
            raw_status = (order.get('Status') or 'unknown').lower()
            if raw_status == 'confirmed' and departure_dt < datetime.now():
                display_status = 'done'
            else:
                display_status = raw_status

            order_vm = {
                'booking_code': order.get('UniqueOrderCode'),
                'status': display_status,
                'email': contact_email,
                'flight_number': order.get('Flights_FlightId'),
                'aircraft_type': order.get('Manufacturer'),
                'departure_time': departure_dt,
                'arrival_time': arrival_dt,
                'duration_minutes': int(duration_minutes) if duration_minutes is not None else 0,
                'origin': order.get('OriginPort'),
                'destination': order.get('DestPort'),
                'total_amount': float(order.get('TotalCost') or 0),
                'refund_amount': None,
                'can_cancel': can_cancel,
                'cancel_deadline': departure_dt - timedelta(hours=36),
                'id': None,
                'created_at': departure_dt,
            }

            tickets_vm = []
            for t in order.get('tickets', []):
                seat_number = f"{t.get('RowNum', '')}{t.get('Seat', '')}"
                tickets_vm.append({
                    'seat_number': seat_number,
                    'seat_class': t.get('Class', 'economy'),
                    'status': (order.get('Status') or 'confirmed').lower(),
                    'price': float(t.get('Price') or 0)
                })
            
            return render_template('orders/order_detail.html',
                                   order=order_vm,
                                   tickets=tickets_vm,
                                   is_guest=True)
        
        return render_template('orders/guest_lookup.html')

    @app.route('/guest/orders/<booking_code>/cancel', methods=['GET', 'POST'])
    def guest_cancel_order(booking_code):
        """Cancel confirmation page and handler for guest users."""
        booking_code = booking_code.strip().upper()
        email = request.args.get('email', '').strip().lower() or request.form.get('email', '').strip().lower()

        if not booking_code or not email:
            flash('Booking code and email are required.', 'error')
            return redirect(url_for('guest_lookup'))

        # Get order details for confirmation page
        order = order_service.get_order_with_tickets(booking_code)
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('guest_lookup'))
        
        # Verify ownership
        owner_email = order.get('RegisteredCustomer_UniqueMail') or order.get('GuestCustomer_UniqueMail')
        if not owner_email or owner_email.lower() != email.lower():
            flash('Invalid booking code or email.', 'error')
            return redirect(url_for('guest_lookup'))
        
        # Check if cancellation is allowed
        if not order_service.can_cancel_order(order):
            flash('This order cannot be canceled. Cancellations must be made at least 36 hours before departure.', 'error')
            return redirect(url_for('guest_lookup'))
        
        # Calculate fee and refund for display
        fee, refund = order_service.calculate_cancellation_fee(order['TotalCost'])

        if request.method == 'POST':
            try:
                original_cost, fee, refund = order_service.cancel_order(booking_code, email)
                # Build success view model for cancel success page
                success_vm = {
                    'booking_code': booking_code,
                    'email': email,
                    'flight_number': order.get('Flights_FlightId'),
                    'total_amount': float(original_cost),
                    'cancellation_fee': float(fee),
                    'refund_amount': float(refund)
                }
                return render_template('orders/cancel_success.html',
                                       order=success_vm,
                                       is_guest=True)
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('guest_lookup'))
        
        # Build order view model for template
        order_vm = {
            'booking_code': booking_code,
            'flight_number': order.get('Flights_FlightId'),
            'origin': order.get('OriginPort'),
            'destination': order.get('DestPort'),
            'departure_time': None,
            'ticket_count': len(order.get('tickets', [])),
            'total_amount': float(order.get('TotalCost') or 0),
            'email': email
        }
        
        # Parse departure datetime
        departure_date = order.get('DepartureDate')
        departure_hour = order.get('DepartureHour')
        if departure_date:
            if isinstance(departure_date, str):
                departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
            if departure_hour:
                if hasattr(departure_hour, 'total_seconds'):
                    total_seconds = int(departure_hour.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    order_vm['departure_time'] = datetime.combine(
                        departure_date,
                        datetime.strptime(f"{hours}:{minutes}", '%H:%M').time()
                    )
                elif isinstance(departure_hour, str):
                    try:
                        time_str = departure_hour[:5] if len(departure_hour) > 5 else departure_hour
                        order_vm['departure_time'] = datetime.combine(
                            departure_date,
                            datetime.strptime(time_str, '%H:%M').time()
                        )
                    except ValueError:
                        order_vm['departure_time'] = datetime.combine(departure_date, datetime.min.time())
        
        return render_template('orders/cancel_confirm.html',
                               order=order_vm,
                               cancellation_fee=fee,
                               refund_amount=refund,
                               is_guest=True,
                               guest_email=email)

    @app.route('/orders/<booking_code>/edit-seats', methods=['GET', 'POST'])
    @login_required
    def edit_order_seats(booking_code):
        """Edit seats for an existing order."""
        if session.get('role') != 'customer':
            flash('Access denied.', 'error')
            return redirect(url_for('index'))

        # Get the order
        order = order_service.get_order_with_tickets(booking_code.upper())
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('my_orders'))

        # Verify ownership
        owner_email = order.get('RegisteredCustomer_UniqueMail') or order.get('GuestCustomer_UniqueMail')
        if not owner_email or owner_email.lower() != session.get('email', '').lower():
            flash('Access denied.', 'error')
            return redirect(url_for('my_orders'))

        # Check if order can still be modified (36h rule)
        if not order_service.can_cancel_order(order):
            flash('This order can no longer be modified (less than 36 hours before departure).', 'error')
            return redirect(url_for('my_orders'))

        flight_id = order.get('Flights_FlightId')
        airplane_id = order.get('Flights_Airplanes_AirplaneId')

        # Get flight details
        flight = flight_service.get_flight_details(flight_id, airplane_id)
        if not flight:
            flash('Flight not found.', 'error')
            return redirect(url_for('my_orders'))

        if request.method == 'POST':
            selected_seats = request.form.getlist('seats')

            if not selected_seats:
                flash('Please select at least one seat.', 'warning')
                return redirect(url_for('edit_order_seats', booking_code=booking_code))

            try:
                order_service.update_order_seats(booking_code.upper(), selected_seats, flight)
                flash('Your seats have been updated successfully!', 'success')
                return redirect(url_for('order_confirmation', booking_code=booking_code))
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('edit_order_seats', booking_code=booking_code))

        # Get current seats for this order to pre-select them
        current_seats = [f"{t.get('RowNum')}{t.get('Seat')}" for t in order.get('tickets', [])]

        # Build seat map - exclude current seats so they appear as available
        seat_map = flight_service.build_seat_map(flight_id, airplane_id, exclude_seats=current_seats)

        return render_template('flights/seat_selection.html',
                               flight=flight,
                               seat_map=seat_map,
                               edit_mode=True,
                               booking_code=booking_code,
                               current_seats=current_seats)
