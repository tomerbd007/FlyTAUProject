"""Database access for crew assignments (pilots and flight attendants)."""
from app.db import execute_query


def get_pilot_by_id(pilot_id):
    """Get a single pilot by ID."""
    sql = "SELECT Id, FirstName, SecondName, LongFlightsTraining, PhoneNum FROM Pilot WHERE Id = %s"
    results = execute_query(sql, (pilot_id,))
    return results[0] if results else None


def get_attendant_by_id(attendant_id):
    """Get a single flight attendant by ID."""
    sql = "SELECT Id, FirstName, SecondName, LongFlightsTraining, PhoneNum FROM FlightAttendant WHERE Id = %s"
    results = execute_query(sql, (attendant_id,))
    return results[0] if results else None


HOME_BASE_AIRPORT = 'TLV'


def get_pilot_location_at_time(pilot_id, at_datetime):
    """Find where a pilot will be at a given time based on flight history."""
    sql = """
        SELECT f.DestPort
        FROM Pilot_has_Flights pf
        JOIN Flights f ON pf.Flights_FlightId = f.FlightId
        WHERE pf.Pilot_Id = %s
          AND f.Status IN ('active', 'full', 'done')
          AND DATE_ADD(TIMESTAMP(f.DepartureDate, f.DepartureHour), INTERVAL f.Duration MINUTE) <= %s
        ORDER BY DATE_ADD(TIMESTAMP(f.DepartureDate, f.DepartureHour), INTERVAL f.Duration MINUTE) DESC
        LIMIT 1
    """
    result = execute_query(sql, (pilot_id, at_datetime), fetch_one=True)
    
    if result:
        return result['DestPort']
    return HOME_BASE_AIRPORT


def get_attendant_location_at_time(attendant_id, at_datetime):
    """Find where an attendant will be at a given time based on flight history."""
    sql = """
        SELECT f.DestPort
        FROM FlightAttendant_has_Flights faf
        JOIN Flights f ON faf.Flights_FlightId = f.FlightId
        WHERE faf.FlightAttendant_Id = %s
          AND f.Status IN ('active', 'full', 'done')
          AND DATE_ADD(TIMESTAMP(f.DepartureDate, f.DepartureHour), INTERVAL f.Duration MINUTE) <= %s
        ORDER BY DATE_ADD(TIMESTAMP(f.DepartureDate, f.DepartureHour), INTERVAL f.Duration MINUTE) DESC
        LIMIT 1
    """
    result = execute_query(sql, (attendant_id, at_datetime), fetch_one=True)
    
    if result:
        return result['DestPort']
    return HOME_BASE_AIRPORT


def get_available_pilots(departure_datetime, arrival_datetime, origin_airport=None, 
                         require_long_flight_cert=False, exclude_flight_id=None):
    """Get pilots available during time range and at origin airport."""
    cert_condition = "AND p.LongFlightsTraining = 1" if require_long_flight_cert else ""
    
    # Build exclusion condition for the flight being edited
    exclude_condition = ""
    params = [arrival_datetime, departure_datetime]
    
    if exclude_flight_id:
        exclude_condition = "AND NOT (f.FlightId = %s)"
        params.append(exclude_flight_id)
    
    # Use time overlap check instead of date check
    # A flight overlaps if: existing_departure < new_arrival AND existing_arrival > new_departure
    sql = f"""
        SELECT p.Id as id, p.FirstName as first_name, p.SecondName as last_name, 
               p.Id as employee_code, p.LongFlightsTraining as long_flight_cert
        FROM Pilot p
        WHERE p.Id NOT IN (
            SELECT pf.Pilot_Id
            FROM Pilot_has_Flights pf
            JOIN Flights f ON pf.Flights_FlightId = f.FlightId
            WHERE f.Status != 'cancelled'
              AND TIMESTAMP(f.DepartureDate, f.DepartureHour) < %s
              AND DATE_ADD(TIMESTAMP(f.DepartureDate, f.DepartureHour), INTERVAL f.Duration MINUTE) > %s
              {exclude_condition}
        )
        {cert_condition}
        ORDER BY p.SecondName, p.FirstName
    """
    
    pilots = execute_query(sql, tuple(params))
    
    if not pilots:
        return []
    
    # Filter by location if origin_airport specified
    if origin_airport:
        available_pilots = []
        for pilot in pilots:
            pilot_dict = dict(pilot)
            pilot_location = get_pilot_location_at_time(pilot_dict['id'], departure_datetime)
            if pilot_location == origin_airport:
                pilot_dict['current_location'] = pilot_location
                available_pilots.append(pilot_dict)
        return available_pilots
    
    return [dict(p) for p in pilots]


def get_pilots_for_flight(flight_id, airplane_id=None):
    """Get all pilots assigned to a specific flight."""
    sql = """
        SELECT p.Id, p.FirstName, p.SecondName, p.LongFlightsTraining, p.PhoneNum
        FROM Pilot p
        JOIN Pilot_has_Flights pf ON p.Id = pf.Pilot_Id
        WHERE pf.Flights_FlightId = %s
        ORDER BY p.SecondName, p.FirstName
    """
    return execute_query(sql, (flight_id,))


def assign_pilot_to_flight(pilot_id, flight_id, airplane_id=None):
    """Assign a pilot to a flight."""
    sql = """
        INSERT INTO Pilot_has_Flights (Pilot_Id, Flights_FlightId)
        VALUES (%s, %s)
    """
    return execute_query(sql, (pilot_id, flight_id), commit=True)


def remove_pilot_from_flight(pilot_id, flight_id, airplane_id=None):
    """Remove a pilot assignment from a flight."""
    sql = """
        DELETE FROM Pilot_has_Flights 
        WHERE Pilot_Id = %s 
          AND Flights_FlightId = %s
    """
    return execute_query(sql, (pilot_id, flight_id), commit=True)


def delete_all_pilots_from_flight(flight_id, airplane_id=None):
    """Remove all pilot assignments from a flight."""
    sql = """
        DELETE FROM Pilot_has_Flights 
        WHERE Flights_FlightId = %s
    """
    return execute_query(sql, (flight_id,), commit=True)


def get_available_flight_attendants(departure_datetime, arrival_datetime, origin_airport=None,
                                    require_long_flight_cert=False, exclude_flight_id=None):
    """Get flight attendants available during time range and at origin airport."""
    cert_condition = "AND fa.LongFlightsTraining = 1" if require_long_flight_cert else ""
    
    # Build exclusion condition for the flight being edited
    exclude_condition = ""
    params = [arrival_datetime, departure_datetime]
    
    if exclude_flight_id:
        exclude_condition = "AND NOT (f.FlightId = %s)"
        params.append(exclude_flight_id)
    
    # Use time overlap check instead of date check
    # A flight overlaps if: existing_departure < new_arrival AND existing_arrival > new_departure
    sql = f"""
        SELECT fa.Id as id, fa.FirstName as first_name, fa.SecondName as last_name,
               fa.Id as employee_code, fa.LongFlightsTraining as long_flight_cert
        FROM FlightAttendant fa
        WHERE fa.Id NOT IN (
            SELECT faf.FlightAttendant_Id
            FROM FlightAttendant_has_Flights faf
            JOIN Flights f ON faf.Flights_FlightId = f.FlightId
            WHERE f.Status != 'cancelled'
              AND TIMESTAMP(f.DepartureDate, f.DepartureHour) < %s
              AND DATE_ADD(TIMESTAMP(f.DepartureDate, f.DepartureHour), INTERVAL f.Duration MINUTE) > %s
              {exclude_condition}
        )
        {cert_condition}
        ORDER BY fa.SecondName, fa.FirstName
    """
    
    attendants = execute_query(sql, tuple(params))
    
    if not attendants:
        return []
    
    # Filter by location if origin_airport specified
    if origin_airport:
        available_attendants = []
        for attendant in attendants:
            attendant_dict = dict(attendant)
            attendant_location = get_attendant_location_at_time(attendant_dict['id'], departure_datetime)
            if attendant_location == origin_airport:
                attendant_dict['current_location'] = attendant_location
                available_attendants.append(attendant_dict)
        return available_attendants
    
    return [dict(a) for a in attendants]


def get_attendants_for_flight(flight_id, airplane_id=None):
    """Get all flight attendants assigned to a specific flight."""
    sql = """
        SELECT fa.Id, fa.FirstName, fa.SecondName, fa.LongFlightsTraining, fa.PhoneNum
        FROM FlightAttendant fa
        JOIN FlightAttendant_has_Flights faf ON fa.Id = faf.FlightAttendant_Id
        WHERE faf.Flights_FlightId = %s
        ORDER BY fa.SecondName, fa.FirstName
    """
    return execute_query(sql, (flight_id,))


def assign_attendant_to_flight(attendant_id, flight_id, airplane_id=None):
    """Assign a flight attendant to a flight."""
    sql = """
        INSERT INTO FlightAttendant_has_Flights (FlightAttendant_Id, Flights_FlightId)
        VALUES (%s, %s)
    """
    return execute_query(sql, (attendant_id, flight_id), commit=True)


def remove_attendant_from_flight(attendant_id, flight_id, airplane_id=None):
    """Remove a flight attendant assignment from a flight."""
    sql = """
        DELETE FROM FlightAttendant_has_Flights 
        WHERE FlightAttendant_Id = %s 
          AND Flights_FlightId = %s
    """
    return execute_query(sql, (attendant_id, flight_id), commit=True)


def delete_all_attendants_from_flight(flight_id, airplane_id=None):
    """Remove all flight attendant assignments from a flight."""
    sql = """
        DELETE FROM FlightAttendant_has_Flights 
        WHERE Flights_FlightId = %s
    """
    return execute_query(sql, (flight_id,), commit=True)


def get_all_crew_for_flight(flight_id, airplane_id):
    """Get all crew (pilots + attendants) assigned to a flight."""
    pilots = get_pilots_for_flight(flight_id, airplane_id)
    attendants = get_attendants_for_flight(flight_id, airplane_id)
    
    return {
        'pilots': pilots if pilots else [],
        'attendants': attendants if attendants else []
    }


def delete_all_crew_from_flight(flight_id, airplane_id):
    """Remove all crew assignments (pilots + attendants) from a flight."""
    delete_all_pilots_from_flight(flight_id, airplane_id)
    delete_all_attendants_from_flight(flight_id, airplane_id)


def count_pilots():
    """Count total pilots."""
    sql = "SELECT COUNT(*) AS count FROM Pilot"
    result = execute_query(sql, fetch_one=True)
    return result['count'] if result else 0


def count_flight_attendants():
    """Count total flight attendants."""
    sql = "SELECT COUNT(*) AS count FROM FlightAttendant"
    result = execute_query(sql, fetch_one=True)
    return result['count'] if result else 0


def count_crew():
    """Count total crew members (pilots + attendants)."""
    return count_pilots() + count_flight_attendants()


def get_all_pilots():
    """Get all pilots."""
    sql = """
        SELECT Id, FirstName, SecondName, LongFlightsTraining, JoinDate, PhoneNum
        FROM Pilot
        ORDER BY SecondName, FirstName
    """
    return execute_query(sql)


def get_all_flight_attendants():
    """Get all flight attendants."""
    sql = """
        SELECT Id, FirstName, SecondName, LongFlightsTraining, JoinDate, PhoneNum
        FROM FlightAttendant
        ORDER BY SecondName, FirstName
    """
    return execute_query(sql)


def create_pilot(pilot_id, first_name, last_name, phone, join_date, long_flights_training=False, street=None, city=None, house_num=None):
    """Create a new pilot."""
    import json
    phone_json = json.dumps([phone]) if phone else None
    
    sql = """
        INSERT INTO Pilot (Id, FirstName, SecondName, PhoneNum, JoinDate, LongFlightsTraining, Street, City, HouseNum)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        execute_query(sql, (pilot_id, first_name, last_name, phone_json, join_date, 
                           1 if long_flights_training else 0, street, city, house_num), commit=True)
        return True
    except Exception as e:
        print(f"Error creating pilot: {e}")
        return False


def pilot_exists(pilot_id):
    """Check if a pilot with the given ID exists."""
    sql = "SELECT 1 FROM Pilot WHERE Id = %s"
    result = execute_query(sql, (pilot_id,), fetch_one=True)
    return result is not None


def create_flight_attendant(attendant_id, first_name, last_name, phone, join_date, long_flights_training=False, street=None, city=None, house_num=None):
    """Create a new flight attendant."""
    import json
    phone_json = json.dumps([phone]) if phone else None
    
    sql = """
        INSERT INTO FlightAttendant (Id, FirstName, SecondName, PhoneNum, JoinDate, LongFlightsTraining, Street, City, HouseNum)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        execute_query(sql, (attendant_id, first_name, last_name, phone_json, join_date,
                           1 if long_flights_training else 0, street, city, house_num), commit=True)
        return True
    except Exception as e:
        print(f"Error creating flight attendant: {e}")
        return False


def flight_attendant_exists(attendant_id):
    """Check if a flight attendant with the given ID exists."""
    sql = "SELECT 1 FROM FlightAttendant WHERE Id = %s"
    result = execute_query(sql, (attendant_id,), fetch_one=True)
    return result is not None
