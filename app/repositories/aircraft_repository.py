"""Database access for airplanes and seat configurations."""
from app.db import execute_query


def get_airplane_by_id(airplane_id):
    """Get airplane with computed seat configuration."""
    sql = """
        SELECT AirplaneId, PurchaseDate, Manufacturer, 
               CouchRows, CouchCols, BusinessRows, BusinessCols
        FROM Airplanes
        WHERE AirplaneId = %s
    """
    result = execute_query(sql, (airplane_id,), fetch_one=True)
    if result:
        result = dict(result)
        # Read seat configurations directly from INT columns
        economy_rows = result.get('CouchRows') or 0
        economy_cols = result.get('CouchCols') or 0
        business_rows = result.get('BusinessRows') or 0
        business_cols = result.get('BusinessCols') or 0
        
        result['economy_rows'] = economy_rows
        result['economy_cols'] = economy_cols
        result['business_rows'] = business_rows
        result['business_cols'] = business_cols
        result['economy_seats'] = economy_rows * economy_cols
        result['business_seats'] = business_rows * business_cols
        result['total_seats'] = result['economy_seats'] + result['business_seats']
        
        # Determine size: Big = has Business class, Small = no Business class
        result['size'] = 'large' if result['business_seats'] > 0 else 'small'
    return result


def get_all_airplanes():
    """Get all airplanes with seat configurations."""
    sql = """
        SELECT AirplaneId, PurchaseDate, Manufacturer, 
               CouchRows, CouchCols, BusinessRows, BusinessCols
        FROM Airplanes
        ORDER BY Manufacturer, AirplaneId
    """
    results = execute_query(sql)
    if not results:
        return []
    
    parsed_results = []
    for row in results:
        airplane = dict(row)
        economy_rows = airplane.get('CouchRows') or 0
        economy_cols = airplane.get('CouchCols') or 0
        business_rows = airplane.get('BusinessRows') or 0
        business_cols = airplane.get('BusinessCols') or 0
        
        airplane['economy_rows'] = economy_rows
        airplane['economy_cols'] = economy_cols
        airplane['business_rows'] = business_rows
        airplane['business_cols'] = business_cols
        airplane['economy_seats'] = economy_rows * economy_cols
        airplane['business_seats'] = business_rows * business_cols
        airplane['total_seats'] = airplane['economy_seats'] + airplane['business_seats']
        # Determine size: Big = has Business class, Small = no Business class
        airplane['size'] = 'large' if airplane['business_seats'] > 0 else 'small'
        parsed_results.append(airplane)
    
    return parsed_results


# Default home base airport (where aircraft start if no flight history)
HOME_BASE_AIRPORT = 'TLV'


def get_aircraft_location_at_time(airplane_id, at_datetime):
    """Find where an aircraft will be at a given time based on flight history."""
    sql = """
        SELECT f.DestPort
        FROM Flights f
        WHERE f.Airplanes_AirplaneId = %s
          AND f.Status IN ('active', 'full', 'done')
          AND DATE_ADD(TIMESTAMP(f.DepartureDate, f.DepartureHour), INTERVAL f.Duration MINUTE) <= %s
        ORDER BY DATE_ADD(TIMESTAMP(f.DepartureDate, f.DepartureHour), INTERVAL f.Duration MINUTE) DESC
        LIMIT 1
    """
    result = execute_query(sql, (airplane_id, at_datetime), fetch_one=True)
    
    if result:
        return result['DestPort']
    return HOME_BASE_AIRPORT


def get_available_airplanes(departure_datetime, arrival_datetime, origin_airport=None):
    """Get airplanes not assigned to flights during the time range and at the origin airport."""
    # Get all airplanes
    sql_all = """
        SELECT a.AirplaneId, a.PurchaseDate, a.Manufacturer, 
               a.CouchRows, a.CouchCols, a.BusinessRows, a.BusinessCols
        FROM Airplanes a
        ORDER BY a.Manufacturer, a.AirplaneId
    """
    all_airplanes = execute_query(sql_all)
    if not all_airplanes:
        return []
    
    # Get busy airplane IDs (those with overlapping flights)
    # A flight overlaps if: existing_departure < new_arrival AND existing_arrival > new_departure
    sql_busy = """
        SELECT DISTINCT f.Airplanes_AirplaneId
        FROM Flights f
        WHERE f.Status IN ('active', 'full')
          AND (
              -- Calculate existing flight's departure datetime
              TIMESTAMP(f.DepartureDate, f.DepartureHour) < %s
              AND 
              -- Calculate existing flight's arrival datetime (departure + duration minutes)
              DATE_ADD(TIMESTAMP(f.DepartureDate, f.DepartureHour), INTERVAL f.Duration MINUTE) > %s
          )
    """
    busy_results = execute_query(sql_busy, (arrival_datetime, departure_datetime))
    busy_ids = set(row['Airplanes_AirplaneId'] for row in busy_results) if busy_results else set()
    
    parsed_results = []
    for row in all_airplanes:
        airplane = dict(row)
        # Skip if airplane is busy
        if airplane['AirplaneId'] in busy_ids:
            continue
            
        economy_rows = airplane.get('CouchRows') or 0
        economy_cols = airplane.get('CouchCols') or 0
        business_rows = airplane.get('BusinessRows') or 0
        business_cols = airplane.get('BusinessCols') or 0
        
        airplane['economy_rows'] = economy_rows
        airplane['economy_cols'] = economy_cols
        airplane['business_rows'] = business_rows
        airplane['business_cols'] = business_cols
        airplane['economy_seats'] = economy_rows * economy_cols
        airplane['business_seats'] = business_rows * business_cols
        airplane['total_seats'] = airplane['economy_seats'] + airplane['business_seats']
        # Determine size: Big = has Business class, Small = no Business class
        airplane['size'] = 'large' if airplane['business_seats'] > 0 else 'small'
        
        # Check location if origin_airport specified
        if origin_airport:
            aircraft_location = get_aircraft_location_at_time(airplane['AirplaneId'], departure_datetime)
            if aircraft_location != origin_airport:
                continue  # Skip aircraft not at origin
            airplane['current_location'] = aircraft_location
        
        parsed_results.append(airplane)
    
    return parsed_results


def count_airplanes():
    """Count total airplanes."""
    sql = "SELECT COUNT(*) AS count FROM Airplanes"
    result = execute_query(sql, fetch_one=True)
    return result['count'] if result else 0


def create_airplane(airplane_id, purchase_date, manufacturer, economy_rows, economy_cols, business_rows=0, business_cols=0):
    """Create a new airplane."""
    sql = """
        INSERT INTO Airplanes (AirplaneId, PurchaseDate, Manufacturer, CouchRows, CouchCols, BusinessRows, BusinessCols)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        execute_query(sql, (airplane_id, purchase_date, manufacturer, economy_rows, economy_cols, business_rows, business_cols), commit=True)
        return True
    except Exception as e:
        print(f"Error creating airplane: {e}")
        return False


def airplane_exists(airplane_id):
    """Check if an airplane with the given ID exists."""
    sql = "SELECT 1 FROM Airplanes WHERE AirplaneId = %s"
    result = execute_query(sql, (airplane_id,), fetch_one=True)
    return result is not None


def generate_seat_map(airplane_id):
    """Generate a virtual seat map from the airplane's seat configuration."""
    airplane = get_airplane_by_id(airplane_id)
    if not airplane:
        return []
    
    seats = []
    col_letters = 'ABCDEFGHIJ'  # Up to 10 columns
    
    # Generate business class seats (rows come first)
    business_rows = airplane['business_rows']
    business_cols = airplane['business_cols']
    for row in range(1, business_rows + 1):
        for col_idx in range(business_cols):
            col_letter = col_letters[col_idx] if col_idx < len(col_letters) else str(col_idx + 1)
            seats.append({
                'seat_code': f"{row}{col_letter}",
                'seat_class': 'business',
                'row_num': row,
                'col_letter': col_letter
            })
    
    # Generate economy class seats (rows continue after business)
    economy_rows = airplane['economy_rows']
    economy_cols = airplane['economy_cols']
    start_row = business_rows + 1
    for row in range(start_row, start_row + economy_rows):
        for col_idx in range(economy_cols):
            col_letter = col_letters[col_idx] if col_idx < len(col_letters) else str(col_idx + 1)
            seats.append({
                'seat_code': f"{row}{col_letter}",
                'seat_class': 'economy',
                'row_num': row,
                'col_letter': col_letter
            })
    
    return seats
