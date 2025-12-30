-- Flight Hours per Employee Report
-- Shows cumulative flight hours for each crew member, split by short/long flights
-- Short flight: <= 6 hours (360 minutes)
-- Long flight: > 6 hours

SELECT 
    e.employee_code,
    CONCAT(e.first_name, ' ', e.last_name) AS name,
    e.role,
    ROUND(SUM(
        CASE 
            WHEN TIMESTAMPDIFF(MINUTE, f.departure_datetime, f.arrival_datetime) <= 360 
            THEN TIMESTAMPDIFF(MINUTE, f.departure_datetime, f.arrival_datetime) / 60.0 
            ELSE 0 
        END
    ), 1) AS short_flight_hours,
    ROUND(SUM(
        CASE 
            WHEN TIMESTAMPDIFF(MINUTE, f.departure_datetime, f.arrival_datetime) > 360 
            THEN TIMESTAMPDIFF(MINUTE, f.departure_datetime, f.arrival_datetime) / 60.0 
            ELSE 0 
        END
    ), 1) AS long_flight_hours,
    ROUND(SUM(
        TIMESTAMPDIFF(MINUTE, f.departure_datetime, f.arrival_datetime) / 60.0
    ), 1) AS total_hours
FROM employees e
JOIN crew_assignments ca ON e.id = ca.employee_id
JOIN flights f ON ca.flight_id = f.id
WHERE f.status IN ('occurred', 'active')
  AND e.role IN ('pilot', 'attendant')
GROUP BY e.id, e.employee_code, e.first_name, e.last_name, e.role
ORDER BY total_hours DESC;
