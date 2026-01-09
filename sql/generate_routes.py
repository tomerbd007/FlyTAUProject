#!/usr/bin/env python3
"""
Generate Routes SQL seed data for all airport combinations.
Uses Haversine formula to calculate distances and derive flight durations.
"""
import math

# Airport coordinates (latitude, longitude) - real data
AIRPORT_COORDS = {
    # Middle East
    'TLV': (32.0114, 34.8855),   # Tel Aviv
    'DXB': (25.2532, 55.3657),   # Dubai
    'AUH': (24.4330, 54.6511),   # Abu Dhabi
    'DOH': (25.2731, 51.6081),   # Doha
    'RUH': (24.9578, 46.6989),   # Riyadh
    'JED': (21.6796, 39.1566),   # Jeddah
    'AMM': (31.7226, 35.9932),   # Amman
    'CAI': (30.1219, 31.4056),   # Cairo
    'IST': (41.2753, 28.7519),   # Istanbul
    'BEY': (33.8209, 35.4884),   # Beirut
    'BAH': (26.2708, 50.6336),   # Bahrain
    'KWI': (29.2266, 47.9689),   # Kuwait
    'MCT': (23.5933, 58.2844),   # Muscat
    # Europe
    'LHR': (51.4700, -0.4543),   # London Heathrow
    'CDG': (49.0097, 2.5479),    # Paris CDG
    'FRA': (50.0379, 8.5622),    # Frankfurt
    'AMS': (52.3105, 4.7683),    # Amsterdam
    'FCO': (41.8003, 12.2389),   # Rome
    'MAD': (40.4983, -3.5676),   # Madrid
    'BCN': (41.2974, 2.0833),    # Barcelona
    'ATH': (37.9364, 23.9445),   # Athens
    'VIE': (48.1103, 16.5697),   # Vienna
    'ZRH': (47.4582, 8.5555),    # Zurich
    'MUC': (48.3537, 11.7750),   # Munich
    'CPH': (55.6180, 12.6508),   # Copenhagen
    'PRG': (50.1008, 14.2600),   # Prague
    # Americas
    'JFK': (40.6413, -73.7781),  # New York JFK
    'LAX': (33.9416, -118.4085), # Los Angeles
    'MIA': (25.7959, -80.2870),  # Miami
    'ORD': (41.9742, -87.9073),  # Chicago O'Hare
    'SFO': (37.6213, -122.3790), # San Francisco
    'YYZ': (43.6777, -79.6248),  # Toronto
    'GRU': (-23.4356, -46.4731), # São Paulo
    'MEX': (19.4361, -99.0719),  # Mexico City
    # Asia Pacific
    'HND': (35.5494, 139.7798),  # Tokyo Haneda
    'NRT': (35.7720, 140.3929),  # Tokyo Narita
    'SIN': (1.3644, 103.9915),   # Singapore
    'HKG': (22.3080, 113.9185),  # Hong Kong
    'PEK': (40.0799, 116.6031),  # Beijing
    'PVG': (31.1443, 121.8083),  # Shanghai
    'ICN': (37.4602, 126.4407),  # Seoul Incheon
    'BKK': (13.6900, 100.7501),  # Bangkok
    'DEL': (28.5562, 77.1000),   # New Delhi
    'BOM': (19.0896, 72.8656),   # Mumbai
    'SYD': (-33.9399, 151.1753), # Sydney
    'MEL': (-37.6690, 144.8410), # Melbourne
    # Africa
    'JNB': (-26.1367, 28.2411),  # Johannesburg
    'CPT': (-33.9715, 18.6021),  # Cape Town
    'ADD': (8.9779, 38.7993),    # Addis Ababa
    'NBO': (-1.3192, 36.9278),   # Nairobi
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def calculate_flight_duration(distance_km):
    """
    Calculate flight duration in minutes.
    Formula: (distance / cruise_speed) * 60 + overhead
    - Average cruise speed: 850 km/h
    - Overhead (taxi, takeoff, landing): 45 minutes
    """
    cruise_speed = 850  # km/h
    overhead_minutes = 45  # taxi, takeoff, landing
    
    flight_time = (distance_km / cruise_speed) * 60 + overhead_minutes
    return int(round(flight_time))

def generate_routes_sql():
    """Generate SQL INSERT statements for all route combinations."""
    airports = list(AIRPORT_COORDS.keys())
    routes = []
    
    # Generate all combinations (A->B and B->A are separate routes)
    for origin in airports:
        for dest in airports:
            if origin != dest:
                lat1, lon1 = AIRPORT_COORDS[origin]
                lat2, lon2 = AIRPORT_COORDS[dest]
                
                distance = haversine_distance(lat1, lon1, lat2, lon2)
                duration = calculate_flight_duration(distance)
                
                routes.append((origin, dest, duration, int(round(distance))))
    
    # Generate SQL
    sql_lines = [
        "-- =============================================================================",
        "-- ROUTES - All airport combinations with calculated durations",
        "-- Generated automatically using Haversine formula",
        "-- Duration = (distance_km / 850 km/h) * 60 + 45 min overhead",
        "-- =============================================================================",
        "INSERT INTO Routes (OriginPort, DestPort, DurationMinutes, DistanceKm) VALUES"
    ]
    
    # Add route values
    for i, (origin, dest, duration, distance) in enumerate(routes):
        comma = "," if i < len(routes) - 1 else ";"
        sql_lines.append(f"('{origin}', '{dest}', {duration}, {distance}){comma}")
    
    return "\n".join(sql_lines)

if __name__ == "__main__":
    import os
    sql = generate_routes_sql()
    
    # Write to file in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "routes_seed.sql")
    with open(output_path, "w") as f:
        f.write(sql)
    
    print(f"Generated {len(AIRPORT_COORDS) * (len(AIRPORT_COORDS) - 1)} routes")
    print(f"SQL saved to {output_path}")
