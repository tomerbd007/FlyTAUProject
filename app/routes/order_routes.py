"""
FLYTAU Order Routes
Handles checkout, order viewing, cancellation, and guest lookup
"""
from flask import render_template, request, redirect, url_for, flash, session
from app.services import order_service, flight_service
from app.utils.decorators import login_required, customer_or_guest


def register_order_routes(app):
    """Register order routes with the Flask app."""
    
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
        selected_seats = checkout_data['seats']
        
        # Get flight details
        flight = flight_service.get_flight_details(flight_id)
        if not flight:
            flash('Flight not found.', 'error')
            session.pop('checkout', None)
            return redirect(url_for('flights'))
        
        # Get seat details with prices
        seats_info = flight_service.get_seats_by_codes(flight_id, selected_seats)
        
        if request.method == 'POST':
            # Collect passenger names for each seat
            passengers = {}
            for seat_code in selected_seats:
                passenger_name = request.form.get(f'passenger_{seat_code}', '').strip()
                if not passenger_name:
                    flash(f'Please enter passenger name for seat {seat_code}.', 'error')
                    return render_template('orders/checkout.html',
                                           flight=flight,
                                           seats=seats_info,
                                           total=sum(s['price'] for s in seats_info))
                passengers[seat_code] = passenger_name
            
            # Guest email if not logged in
            guest_email = None
            if not session.get('user_id') or session.get('role') != 'customer':
                guest_email = request.form.get('guest_email', '').strip()
                if not guest_email:
                    flash('Please enter your email address.', 'error')
                    return render_template('orders/checkout.html',
                                           flight=flight,
                                           seats=seats_info,
                                           total=sum(s['price'] for s in seats_info))
            
            # Create order
            try:
                customer_id = session.get('user_id') if session.get('role') == 'customer' else None
                booking_code = order_service.create_order(
                    flight_id=flight_id,
                    seats_info=seats_info,
                    passengers=passengers,
                    customer_id=customer_id,
                    guest_email=guest_email
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
        order = order_service.get_order_by_booking_code(booking_code)
        
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('index'))
        
        return render_template('orders/confirmation.html', order=order)
    
    @app.route('/orders')
    @login_required
    def my_orders():
        """List customer's orders."""
        if session.get('role') != 'customer':
            flash('Access denied.', 'error')
            return redirect(url_for('index'))
        
        status_filter = request.args.get('status', '')
        customer_id = session['user_id']
        
        orders = order_service.get_customer_orders(customer_id, status_filter)
        
        return render_template('orders/my_orders.html',
                               orders=orders,
                               current_filter=status_filter)
    
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
            
            return render_template('orders/order_detail.html',
                                   order=order,
                                   can_cancel=order_service.can_cancel_order(order),
                                   is_guest=True)
        
        return render_template('orders/guest_lookup.html')
