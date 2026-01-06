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


# ============ PILOT CREW OPERATIONS ============

def get_available_pilots(departure_date, require_long_flight_cert=False):
    """
    Get pilots not assigned to flights on the given date.
    
    Args:
        departure_date: Date to check (DATE or 'YYYY-MM-DD')
        require_long_flight_cert: If True, only return pilots with LongFlightsTraining=1
    """
    cert_condition = "AND p.LongFlightsTraining = 1" if require_long_flight_cert else ""
    sql = f"""
        SELECT p.Id, p.FirstName, p.SecondName, p.LongFlightsTraining
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

def get_available_flight_attendants(departure_date, require_long_flight_cert=False):
    """
    Get flight attendants not assigned to flights on the given date.
    
    Args:
        departure_date: Date to check (DATE or 'YYYY-MM-DD')
        require_long_flight_cert: If True, only return attendants with LongFlightsTraining=1
    """
    cert_condition = "AND fa.LongFlightsTraining = 1" if require_long_flight_cert else ""
    sql = f"""
        SELECT fa.Id, fa.FirstName, fa.SecondName, fa.LongFlightsTraining
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
