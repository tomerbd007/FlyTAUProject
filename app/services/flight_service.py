"""Everything related to finding flights, checking seats, and managing availability."""
from datetime import datetime, timedelta
from app.repositories import flight_repository, aircraft_repository


MIN_LAYOVER_MINUTES = 60
MAX_LAYOVER_HOURS = 12


def get_all_airports():
    """Fetches the full airport list."""
    return flight_repository.get_all_airports()


def get_airport_by_code(code):
    """Looks up a specific airport by its code (like TLV, JFK, etc)."""
    return flight_repository.get_airport_by_code(code)


def get_all_cities():
    """Gets all the cities we actually fly to/from."""
    return flight_repository.get_all_unique_cities()


def get_all_routes():
    """Returns every origin-destination combo we have."""
    return flight_repository.get_all_routes()


def search_available_flights(departure_date=None, origin=None, destination=None, include_indirect=True):
    """Main flight search - finds direct flights and connecting options."""
    results = []
    
    # Search for direct flights
    direct_flights = flight_repository.search_flights(
        departure_date=departure_date,
        origin=origin,
        destination=destination,
        status='active'
    )
    
    # Process direct flights
    for flight in direct_flights:
        processed = _process_flight(flight)
        processed['is_direct'] = True
        processed['flights'] = [processed.copy()]
        processed['total_duration'] = processed['Duration']
        processed['stops'] = 0
        results.append(processed)
    
    # Search for indirect flights if origin and destination are provided
    if include_indirect and origin and destination:
        indirect_results = _search_indirect_flights(
            departure_date=departure_date,
            origin=origin,
            destination=destination
        )
        results.extend(indirect_results)
    
    # Sort results: direct flights first, then by total duration
    results.sort(key=lambda x: (not x['is_direct'], x.get('total_duration', 0)))
    
    return results


def _process_flight(flight):
    """
    Takes a raw flight from the DB and enriches it with seat info,
    calculates arrival time, etc. Returns a nicer dict to work with.
    """
    flight = dict(flight)
    
    # Get seat availability
    availability = flight_repository.get_seat_availability(
        flight['FlightId'], 
        flight['Airplanes_AirplaneId']
    )
    flight['seat_availability'] = availability
    
    # Calculate total available seats
    total_available = 0
    if availability:
        for class_info in availability.values():
            if class_info:
                total_available += class_info.get('available', 0)
    flight['total_available_seats'] = total_available
    
    # Calculate arrival time
    try:
        dep_hour = flight.get('DepartureHour', '00:00')
        if isinstance(dep_hour, str):
            hour_parts = dep_hour.split(':')
            dep_minutes = int(hour_parts[0]) * 60 + int(hour_parts[1]) if len(hour_parts) >= 2 else 0
        else:
            dep_minutes = 0
        
        duration = flight.get('Duration', 0) or 0
        arrival_minutes = dep_minutes + duration
        
        # Calculate arrival day offset
        arrival_day_offset = arrival_minutes // (24 * 60)
        arrival_minutes = arrival_minutes % (24 * 60)
        
        arrival_hour = arrival_minutes // 60
        arrival_min = arrival_minutes % 60
        flight['ArrivalHour'] = f"{arrival_hour:02d}:{arrival_min:02d}"
        flight['arrival_day_offset'] = arrival_day_offset
    except (ValueError, TypeError):
        flight['ArrivalHour'] = None
        flight['arrival_day_offset'] = 0
    
    return flight


def _search_indirect_flights(departure_date, origin, destination):
    """Looks for connecting flights with one layover."""
    indirect_results = []
    
    # Get all flights departing from origin on the given date (first leg)
    first_leg_flights = flight_repository.search_flights(
        departure_date=departure_date,
        origin=origin,
        status='active'
    )
    
    if not first_leg_flights:
        return []
    
    # For each first leg, find connecting flights to destination
    for first_leg in first_leg_flights:
        # Skip if first leg already goes to destination (that's a direct flight)
        if first_leg['DestPort'] == destination:
            continue
        
        connection_city = first_leg['DestPort']
        
        # Calculate arrival time of first leg
        first_arrival = _calculate_arrival_datetime(
            first_leg['DepartureDate'],
            first_leg['DepartureHour'],
            first_leg['Duration']
        )
        
        if not first_arrival:
            continue
        
        # Find second leg flights from connection city to destination
        # Check same day and next day for connections
        for day_offset in range(2):  # Check departure day and next day
            check_date = first_arrival.date() + timedelta(days=day_offset)
            
            second_leg_flights = flight_repository.search_flights(
                departure_date=check_date.strftime('%Y-%m-%d'),
                origin=connection_city,
                destination=destination,
                status='active'
            )
            
            for second_leg in second_leg_flights:
                # Calculate departure time of second leg
                second_departure = _parse_datetime(
                    second_leg['DepartureDate'],
                    second_leg['DepartureHour']
                )
                
                if not second_departure:
                    continue
                
                # Check layover time is acceptable
                layover = second_departure - first_arrival
                layover_minutes = layover.total_seconds() / 60
                
                if layover_minutes < MIN_LAYOVER_MINUTES:
                    continue  # Not enough time to connect
                    
                if layover_minutes > MAX_LAYOVER_HOURS * 60:
                    continue  # Too long of a layover
                
                # Process both flights
                processed_first = _process_flight(first_leg)
                processed_second = _process_flight(second_leg)
                
                # Check both legs have available seats
                if processed_first['total_available_seats'] == 0:
                    continue
                if processed_second['total_available_seats'] == 0:
                    continue
                
                # Calculate total duration including layover
                total_duration = first_leg['Duration'] + int(layover_minutes) + second_leg['Duration']
                
                # Build the indirect flight result
                indirect_result = {
                    'is_direct': False,
                    'stops': 1,
                    'connection_city': connection_city,
                    'layover_minutes': int(layover_minutes),
                    'total_duration': total_duration,
                    'flights': [processed_first, processed_second],
                    # Summary fields from first leg
                    'FlightId': f"{processed_first['FlightId']}+{processed_second['FlightId']}",
                    'OriginPort': origin,
                    'DestPort': destination,
                    'DepartureDate': processed_first['DepartureDate'],
                    'DepartureHour': processed_first['DepartureHour'],
                    'ArrivalHour': processed_second.get('ArrivalHour'),
                    # Combined pricing (sum of both legs, use min available class)
                    'EconomyPrice': float(processed_first.get('EconomyPrice') or 0) + float(processed_second.get('EconomyPrice') or 0),
                    'BusinessPrice': float(processed_first.get('BusinessPrice') or 0) + float(processed_second.get('BusinessPrice') or 0),
                    # Use min available seats from either leg
                    'total_available_seats': min(
                        processed_first['total_available_seats'],
                        processed_second['total_available_seats']
                    ),
                    'seat_availability': _combine_seat_availability(
                        processed_first.get('seat_availability'),
                        processed_second.get('seat_availability')
                    )
                }
                
                indirect_results.append(indirect_result)
    
    return indirect_results


def _calculate_arrival_datetime(departure_date, departure_hour, duration_minutes):
    """Figures out when the plane lands based on departure + flight time."""
    departure = _parse_datetime(departure_date, departure_hour)
    if departure and duration_minutes:
        return departure + timedelta(minutes=duration_minutes)
    return None


def _parse_datetime(date_val, time_str):
    """Combines a date and time string into a proper datetime object."""
    try:
        if isinstance(date_val, str):
            date_obj = datetime.strptime(date_val, '%Y-%m-%d').date()
        else:
            date_obj = date_val
        
        if isinstance(time_str, str):
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
        else:
            hour = 0
            minute = 0
        
        return datetime.combine(date_obj, datetime.min.time().replace(hour=hour, minute=minute))
    except (ValueError, TypeError, AttributeError):
        return None


def _combine_seat_availability(avail1, avail2):
    """For connecting flights, takes the smaller seat count between the two legs."""
    if not avail1:
        return avail2
    if not avail2:
        return avail1
    
    combined = {}
    for seat_class in set(list(avail1.keys()) + list(avail2.keys())):
        a1 = avail1.get(seat_class, {}) or {}
        a2 = avail2.get(seat_class, {}) or {}
        
        combined[seat_class] = {
            'available': min(a1.get('available', 0), a2.get('available', 0)),
            'total': min(a1.get('total', 0), a2.get('total', 0))
        }
    
    return combined


def get_flight_details(flight_id, airplane_id):
    """Gets all the info about a flight - aircraft, pricing, seat availability."""
    flight = flight_repository.get_flight_by_id(flight_id, airplane_id)
    if flight:
        flight = dict(flight)
        flight['seat_availability'] = flight_repository.get_seat_availability(flight_id, airplane_id)
        
        # Calculate arrival time from departure + duration
        departure_hour = flight.get('DepartureHour')
        duration = flight.get('Duration', 0)
        
        if departure_hour and duration:
            from datetime import datetime, timedelta
            
            # Handle timedelta or string departure hour
            if hasattr(departure_hour, 'total_seconds'):
                total_seconds = int(departure_hour.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                departure_hour = f"{hours:02d}:{minutes:02d}"
            elif isinstance(departure_hour, str) and len(departure_hour) > 5:
                departure_hour = departure_hour[:5]  # Normalize HH:MM:SS to HH:MM
            
            try:
                dep_time = datetime.strptime(str(departure_hour), "%H:%M")
                arrival_time = dep_time + timedelta(minutes=int(duration))
                flight['ArrivalHour'] = arrival_time.strftime("%H:%M")
            except (ValueError, TypeError):
                flight['ArrivalHour'] = None
        else:
            flight['ArrivalHour'] = None
            
    return flight


def get_seat_availability(flight_id, airplane_id):
    """How many seats are left in each class."""
    return flight_repository.get_seat_availability(flight_id, airplane_id)


def get_taken_seats(flight_id, airplane_id):
    """Returns which seats are already booked."""
    return flight_repository.get_taken_seats(flight_id, airplane_id)


def get_available_seats_for_class(flight_id, airplane_id, seat_class):
    """Lists all the open seats in a specific class (business or economy)."""
    # Get airplane seat configuration
    airplane = aircraft_repository.get_airplane_by_id(airplane_id)
    if not airplane:
        return []
    
    # Get taken seats for this flight
    taken_seats = flight_repository.get_taken_seats(flight_id, airplane_id)
    taken_set = {(t['RowNum'], t['Seat']) for t in taken_seats}
    
    available = []
    
    if seat_class == 'business' and airplane.get('business_rows'):
        rows = airplane['business_rows']
        cols = airplane['business_cols']
        for row in range(1, rows + 1):
            for col_idx in range(cols):
                col_letter = chr(65 + col_idx)  # A, B, C, ...
                if (row, col_letter) not in taken_set:
                    available.append({
                        'row': row,
                        'seat': col_letter,
                        'seat_code': f"{row}{col_letter}",
                        'class': 'business'
                    })
    
    elif seat_class == 'economy':
        # Economy rows start after business rows
        start_row = (airplane.get('business_rows') or 0) + 1
        rows = airplane.get('economy_rows', 0)
        cols = airplane.get('economy_cols', 0)
        
        for row in range(start_row, start_row + rows):
            for col_idx in range(cols):
                col_letter = chr(65 + col_idx)
                if (row, col_letter) not in taken_set:
                    available.append({
                        'row': row,
                        'seat': col_letter,
                        'seat_code': f"{row}{col_letter}",
                        'class': 'economy'
                    })
    
    return available


def get_seats_by_codes(flight_id, airplane_id, seat_codes):
    """Takes seat codes like '1A', '2B' and returns all their details with pricing."""
    import re
    
    # Get flight for pricing info
    flight = flight_repository.get_flight_by_id(flight_id, airplane_id)
    if not flight:
        return []
    
    # Get airplane to determine business class row boundaries
    airplane = aircraft_repository.get_airplane_by_id(airplane_id)
    if not airplane:
        return []
    
    business_rows = airplane.get('business_rows', 0) or 0
    business_price = float(flight.get('BusinessPrice') or 0)
    economy_price = float(flight.get('EconomyPrice') or 0)
    
    seats_info = []
    for seat_code in seat_codes:
        # Parse seat code like "1A" into row number and column letter
        match = re.match(r'^(\d+)([A-Z])$', seat_code.upper())
        if match:
            row = int(match.group(1))
            col = match.group(2)
            
            # Determine class based on row number
            if row <= business_rows:
                seat_class = 'business'
                price = business_price
            else:
                seat_class = 'economy'
                price = economy_price
            
            seats_info.append({
                'code': seat_code.upper(),
                'row': row,
                'col': col,
                'seat_class': seat_class,
                'price': price
            })
    
    return seats_info


def build_seat_map(flight_id, airplane_id, exclude_seats=None):
    """Builds the seat grid for the UI. Can exclude certain seats from being marked taken."""
    airplane = aircraft_repository.get_airplane_by_id(airplane_id)
    if not airplane:
        return None
    
    taken_seats = flight_repository.get_taken_seats(flight_id, airplane_id)
    
    # Build exclusion set from exclude_seats parameter
    exclude_set = set()
    if exclude_seats:
        for seat_code in exclude_seats:
            # Parse seat code like "1A" into (1, 'A')
            import re
            match = re.match(r'^(\d+)([A-Z])$', seat_code.upper())
            if match:
                exclude_set.add((int(match.group(1)), match.group(2)))
    
    taken_set = {(t['RowNum'], t['Seat']) for t in taken_seats if (t['RowNum'], t['Seat']) not in exclude_set}
    
    seat_map = {
        'business': None,
        'economy': {'rows': {}}
    }
    
    # Build business class section
    if airplane.get('business_rows'):
        seat_map['business'] = {'rows': {}}
        for row in range(1, airplane['business_rows'] + 1):
            seat_map['business']['rows'][row] = []
            for col_idx in range(airplane['business_cols']):
                col_letter = chr(65 + col_idx)
                status = 'taken' if (row, col_letter) in taken_set else 'available'
                seat_map['business']['rows'][row].append({
                    'code': f"{row}{col_letter}",
                    'col': col_letter,
                    'status': status
                })
    
    # Build economy class section
    start_row = (airplane.get('business_rows') or 0) + 1
    for row in range(start_row, start_row + airplane.get('economy_rows', 0)):
        seat_map['economy']['rows'][row] = []
        for col_idx in range(airplane.get('economy_cols', 0)):
            col_letter = chr(65 + col_idx)
            status = 'taken' if (row, col_letter) in taken_set else 'available'
            seat_map['economy']['rows'][row].append({
                'code': f"{row}{col_letter}",
                'col': col_letter,
                'status': status
            })
    
    return seat_map


def update_flight_status(flight_id, new_status):
    """Changes the status of a flight (active, full, cancelled, etc)."""
    flight_repository.update_flight_status(flight_id, new_status)


def check_flight_full(flight_id, airplane_id):
    """
    Sees if every seat is booked and marks the flight as 'full' if so.
    """
    availability = get_seat_availability(flight_id, airplane_id)
    
    total_available = 0
    for seat_class in availability.values():
        if seat_class:
            total_available += seat_class.get('available', 0)
    
    if total_available == 0:
        update_flight_status(flight_id, 'full')
