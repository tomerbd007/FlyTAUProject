"""
FLYTAU Aircraft Repository
Database access for Airplanes

Schema:
- Airplanes: AirplaneId (PK), PurchaseDate, Manufacturer, `Couch (Rows, Cols)`, `Business (Rows, Cols)`

Note: Seat configuration is stored as VARCHAR in format "rows,cols" (e.g., "20,6" for 20 rows, 6 columns)
- `Couch (Rows, Cols)` = Economy class seating
- `Business (Rows, Cols)` = Business class seating
"""
from app.db import execute_query


def parse_seat_config(config_str):
    """
    Parse seat configuration string "rows,cols" or "rows cols" into tuple (rows, cols).
    
    Args:
        config_str: String like "20,6" or "(20,6)" or "20, 6" or "20 6"
    
    Returns:
        Tuple of (rows, cols) as integers, or (0, 0) if parsing fails
    """
    if not config_str:
        return (0, 0)
    try:
        # Remove parentheses and extra spaces
        cleaned = config_str.replace('(', '').replace(')', '').strip()
        # Split by comma or space
        if ',' in cleaned:
            parts = cleaned.split(',')
        else:
            parts = cleaned.split()
        if len(parts) >= 2:
            return (int(parts[0].strip()), int(parts[1].strip()))
    except (ValueError, IndexError):
        pass
    return (0, 0)


def get_airplane_by_id(airplane_id):
    """
    Get airplane by AirplaneId.
    
    Returns dict with parsed seat configuration:
        - AirplaneId, PurchaseDate, Manufacturer
        - economy_rows, economy_cols (parsed from `Couch (Rows, Cols)`)
        - business_rows, business_cols (parsed from `Business (Rows, Cols)`)
        - total_seats (computed)
    """
    sql = """
        SELECT AirplaneId, PurchaseDate, Manufacturer, 
               `Couch (Rows, Cols)` as EconomyConfig,
               `Business (Rows, Cols)` as BusinessConfig
        FROM Airplanes
        WHERE AirplaneId = %s
    """
    result = execute_query(sql, (airplane_id,), fetch_one=True)
    if result:
        result = dict(result)
        # Parse seat configurations
        economy_rows, economy_cols = parse_seat_config(result.get('EconomyConfig'))
        business_rows, business_cols = parse_seat_config(result.get('BusinessConfig'))
        
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
    """Get all airplanes with parsed seat configurations."""
    sql = """
        SELECT AirplaneId, PurchaseDate, Manufacturer, 
               `Couch (Rows, Cols)` as EconomyConfig,
               `Business (Rows, Cols)` as BusinessConfig
        FROM Airplanes
        ORDER BY Manufacturer, AirplaneId
    """
    results = execute_query(sql)
    if not results:
        return []
    
    parsed_results = []
    for row in results:
        airplane = dict(row)
        economy_rows, economy_cols = parse_seat_config(airplane.get('EconomyConfig'))
        business_rows, business_cols = parse_seat_config(airplane.get('BusinessConfig'))
        
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


def get_available_airplanes(departure_date):
    """
    Get airplanes not assigned to flights on the given date.
    
    Args:
        departure_date: Date to check availability (DATE or string 'YYYY-MM-DD')
    """
    sql = """
        SELECT a.AirplaneId, a.PurchaseDate, a.Manufacturer, 
               a.`Couch (Rows, Cols)` as EconomyConfig,
               a.`Business (Rows, Cols)` as BusinessConfig
        FROM Airplanes a
        WHERE a.AirplaneId NOT IN (
            SELECT f.Airplanes_AirplaneId
            FROM Flights f
            WHERE f.Status IN ('active', 'full')
              AND f.DepartureDate = %s
        )
        ORDER BY a.Manufacturer, a.AirplaneId
    """
    results = execute_query(sql, (departure_date,))
    if not results:
        return []
    
    parsed_results = []
    for row in results:
        airplane = dict(row)
        economy_rows, economy_cols = parse_seat_config(airplane.get('EconomyConfig'))
        business_rows, business_cols = parse_seat_config(airplane.get('BusinessConfig'))
        
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


def count_airplanes():
    """Count total airplanes."""
    sql = "SELECT COUNT(*) AS count FROM Airplanes"
    result = execute_query(sql, fetch_one=True)
    return result['count'] if result else 0


def generate_seat_map(airplane_id):
    """
    Generate a virtual seat map for an airplane based on its seat configuration.
    
    This doesn't query a seat_map table - it generates seats dynamically from
    the airplane's `Couch (Rows, Cols)` and `Business (Rows, Cols)` config.
    
    Returns list of seat dicts:
        - seat_code: e.g., "1A", "10F"
        - seat_class: "business" or "economy"
        - row_num: Row number (1-based)
        - col_letter: Column letter (A, B, C, etc.)
    """
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
