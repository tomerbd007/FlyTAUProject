-- Monthly Aircraft Activity Report
-- Shows flight activity summary per aircraft per month

SELECT 
    DATE_FORMAT(f.departure_datetime, '%Y-%m') AS month,
    CONCAT(a.manufacturer, ' ', a.registration) AS aircraft,
    SUM(CASE WHEN f.status = 'done' THEN 1 ELSE 0 END) AS flights_completed,
    SUM(CASE WHEN f.status = 'cancelled' THEN 1 ELSE 0 END) AS flights_canceled,
    ROUND(
        SUM(CASE WHEN f.status = 'occurred' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(COUNT(*), 0),
        1
    ) AS utilization_pct,
    (
        SELECT CONCAT(r2.origin, ' → ', r2.destination)
        FROM flights f2
        JOIN routes r2 ON f2.route_id = r2.id
        WHERE f2.aircraft_id = a.id
          AND DATE_FORMAT(f2.departure_datetime, '%Y-%m') = DATE_FORMAT(f.departure_datetime, '%Y-%m')
        GROUP BY r2.id, r2.origin, r2.destination
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) AS most_common_route
FROM flights f
JOIN aircraft a ON f.aircraft_id = a.id
JOIN routes r ON f.route_id = r.id
GROUP BY DATE_FORMAT(f.departure_datetime, '%Y-%m'), a.id, a.manufacturer, a.registration
ORDER BY month DESC, aircraft;
