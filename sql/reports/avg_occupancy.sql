-- Average Occupancy Report
-- Shows seat occupancy percentage for completed flights

SELECT 
    f.flight_number,
    DATE(f.departure_datetime) AS flight_date,
    CONCAT(r.origin, ' → ', r.destination) AS route,
    COUNT(CASE WHEN fs.status = 'sold' THEN 1 END) AS sold_seats,
    COUNT(fs.id) AS total_seats,
    ROUND(
        COUNT(CASE WHEN fs.status = 'sold' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(fs.id), 0), 
        1
    ) AS occupancy_pct
FROM flights f
JOIN routes r ON f.route_id = r.id
JOIN flight_seats fs ON f.id = fs.flight_id
WHERE f.status = 'occurred'
GROUP BY f.id, f.flight_number, f.departure_datetime, r.origin, r.destination
ORDER BY f.departure_datetime DESC;
