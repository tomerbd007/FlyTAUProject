"""
FLYTAU Crew Repository
Database access for crew assignments (Pilots and Flight Attendants)

Schema:
- Pilot: Id (PK), FirstName, SecondName, LongFlightsTraining, etc.
- FlightAttendant: Id (PK), FirstName, SecondName, LongFlightsTraining, etc.
- Pilot_has_Flights: Pilot_Id, Flights_FlightId, Flights_Airplanes_AirplaneId (junction)
- FlightAttendant_has_Flights: FlightAttendant_Id, Flights_FlightId, Flights_Airplanes_AirplaneId (junction)
"""
from app.db import execute_query


# ============ SINGLE CREW MEMBER LOOKUP ============

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


# ============ PILOT CREW OPERATIONS ============

def get_available_pilots(departure_date, require_long_flight_cert=False, exclude_flight_id=None, exclude_airplane_id=None):
    """
    Get pilots not assigned to flights on the given date.
    
    Args:
        departure_date: Date to check (DATE or 'YYYY-MM-DD')
        require_long_flight_cert: If True, only return pilots with LongFlightsTraining=1
        exclude_flight_id: Flight ID to exclude from conflict check (for editing)
        exclude_airplane_id: Airplane ID to exclude from conflict check (for editing)
    """
    cert_condition = "AND p.LongFlightsTraining = 1" if require_long_flight_cert else ""
    
    # Build exclusion condition for the flight being edited
    if exclude_flight_id and exclude_airplane_id:
        exclude_condition = "AND NOT (f.FlightId = %s AND f.Airplanes_AirplaneId = %s)"
        sql = f"""
            SELECT p.Id as id, p.FirstName as first_name, p.SecondName as last_name, 
                   p.Id as employee_code, p.LongFlightsTraining as long_flight_cert
            FROM Pilot p
            WHERE p.Id NOT IN (
                SELECT pf.Pilot_Id
                FROM Pilot_has_Flights pf
                JOIN Flights f ON pf.Flights_FlightId = f.FlightId 
                    AND pf.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
                WHERE f.DepartureDate = %s
                  AND f.Status != 'cancelled'
                  {exclude_condition}
            )
            {cert_condition}
            ORDER BY p.SecondName, p.FirstName
        """
        return execute_query(sql, (departure_date, exclude_flight_id, exclude_airplane_id))
    else:
        sql = f"""
            SELECT p.Id as id, p.FirstName as first_name, p.SecondName as last_name, 
                   p.Id as employee_code, p.LongFlightsTraining as long_flight_cert
            FROM Pilot p
            WHERE p.Id NOT IN (
                SELECT pf.Pilot_Id
                FROM Pilot_has_Flights pf
                JOIN Flights f ON pf.Flights_FlightId = f.FlightId 
                    AND pf.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
                WHERE f.DepartureDate = %s
                  AND f.Status != 'cancelled'
            )
            {cert_condition}
            ORDER BY p.SecondName, p.FirstName
        """
        return execute_query(sql, (departure_date,))


def get_pilots_for_flight(flight_id, airplane_id):
    """Get all pilots assigned to a specific flight."""
    sql = """
        SELECT p.Id, p.FirstName, p.SecondName, p.LongFlightsTraining, p.PhoneNum
        FROM Pilot p
        JOIN Pilot_has_Flights pf ON p.Id = pf.Pilot_Id
        WHERE pf.Flights_FlightId = %s 
          AND pf.Flights_Airplanes_AirplaneId = %s
        ORDER BY p.SecondName, p.FirstName
    """
    return execute_query(sql, (flight_id, airplane_id))


def assign_pilot_to_flight(pilot_id, flight_id, airplane_id):
    """Assign a pilot to a flight."""
    sql = """
        INSERT INTO Pilot_has_Flights (Pilot_Id, Flights_FlightId, Flights_Airplanes_AirplaneId)
        VALUES (%s, %s, %s)
    """
    return execute_query(sql, (pilot_id, flight_id, airplane_id), commit=True)


def remove_pilot_from_flight(pilot_id, flight_id, airplane_id):
    """Remove a pilot assignment from a flight."""
    sql = """
        DELETE FROM Pilot_has_Flights 
        WHERE Pilot_Id = %s 
          AND Flights_FlightId = %s 
          AND Flights_Airplanes_AirplaneId = %s
    """
    return execute_query(sql, (pilot_id, flight_id, airplane_id), commit=True)


def delete_all_pilots_from_flight(flight_id, airplane_id):
    """Remove all pilot assignments from a flight."""
    sql = """
        DELETE FROM Pilot_has_Flights 
        WHERE Flights_FlightId = %s AND Flights_Airplanes_AirplaneId = %s
    """
    return execute_query(sql, (flight_id, airplane_id), commit=True)


# ============ FLIGHT ATTENDANT CREW OPERATIONS ============

def get_available_flight_attendants(departure_date, require_long_flight_cert=False, exclude_flight_id=None, exclude_airplane_id=None):
    """
    Get flight attendants not assigned to flights on the given date.
    
    Args:
        departure_date: Date to check (DATE or 'YYYY-MM-DD')
        require_long_flight_cert: If True, only return attendants with LongFlightsTraining=1
        exclude_flight_id: Flight ID to exclude from conflict check (for editing)
        exclude_airplane_id: Airplane ID to exclude from conflict check (for editing)
    """
    cert_condition = "AND fa.LongFlightsTraining = 1" if require_long_flight_cert else ""
    
    # Build exclusion condition for the flight being edited
    if exclude_flight_id and exclude_airplane_id:
        exclude_condition = "AND NOT (f.FlightId = %s AND f.Airplanes_AirplaneId = %s)"
        sql = f"""
            SELECT fa.Id as id, fa.FirstName as first_name, fa.SecondName as last_name,
                   fa.Id as employee_code, fa.LongFlightsTraining as long_flight_cert
            FROM FlightAttendant fa
            WHERE fa.Id NOT IN (
                SELECT faf.FlightAttendant_Id
                FROM FlightAttendant_has_Flights faf
                JOIN Flights f ON faf.Flights_FlightId = f.FlightId 
                    AND faf.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
                WHERE f.DepartureDate = %s
                  AND f.Status != 'cancelled'
                  {exclude_condition}
            )
            {cert_condition}
            ORDER BY fa.SecondName, fa.FirstName
        """
        return execute_query(sql, (departure_date, exclude_flight_id, exclude_airplane_id))
    else:
        sql = f"""
            SELECT fa.Id as id, fa.FirstName as first_name, fa.SecondName as last_name,
                   fa.Id as employee_code, fa.LongFlightsTraining as long_flight_cert
            FROM FlightAttendant fa
            WHERE fa.Id NOT IN (
                SELECT faf.FlightAttendant_Id
                FROM FlightAttendant_has_Flights faf
                JOIN Flights f ON faf.Flights_FlightId = f.FlightId 
                    AND faf.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
                WHERE f.DepartureDate = %s
                  AND f.Status != 'cancelled'
            )
            {cert_condition}
            ORDER BY fa.SecondName, fa.FirstName
        """
        return execute_query(sql, (departure_date,))


def get_attendants_for_flight(flight_id, airplane_id):
    """Get all flight attendants assigned to a specific flight."""
    sql = """
        SELECT fa.Id, fa.FirstName, fa.SecondName, fa.LongFlightsTraining, fa.PhoneNum
        FROM FlightAttendant fa
        JOIN FlightAttendant_has_Flights faf ON fa.Id = faf.FlightAttendant_Id
        WHERE faf.Flights_FlightId = %s 
          AND faf.Flights_Airplanes_AirplaneId = %s
        ORDER BY fa.SecondName, fa.FirstName
    """
    return execute_query(sql, (flight_id, airplane_id))


def assign_attendant_to_flight(attendant_id, flight_id, airplane_id):
    """Assign a flight attendant to a flight."""
    sql = """
        INSERT INTO FlightAttendant_has_Flights (FlightAttendant_Id, Flights_FlightId, Flights_Airplanes_AirplaneId)
        VALUES (%s, %s, %s)
    """
    return execute_query(sql, (attendant_id, flight_id, airplane_id), commit=True)


def remove_attendant_from_flight(attendant_id, flight_id, airplane_id):
    """Remove a flight attendant assignment from a flight."""
    sql = """
        DELETE FROM FlightAttendant_has_Flights 
        WHERE FlightAttendant_Id = %s 
          AND Flights_FlightId = %s 
          AND Flights_Airplanes_AirplaneId = %s
    """
    return execute_query(sql, (attendant_id, flight_id, airplane_id), commit=True)


def delete_all_attendants_from_flight(flight_id, airplane_id):
    """Remove all flight attendant assignments from a flight."""
    sql = """
        DELETE FROM FlightAttendant_has_Flights 
        WHERE Flights_FlightId = %s AND Flights_Airplanes_AirplaneId = %s
    """
    return execute_query(sql, (flight_id, airplane_id), commit=True)


# ============ COMBINED CREW OPERATIONS ============

def get_all_crew_for_flight(flight_id, airplane_id):
    """
    Get all crew (pilots + attendants) assigned to a flight.
    
    Returns dict with 'pilots' and 'attendants' lists.
    """
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
