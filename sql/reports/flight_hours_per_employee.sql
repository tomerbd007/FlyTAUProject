-- Cumulative flight hours per employee, separated by flight length
-- Only counts 'active' flights (cancelled flights are excluded)
-- Short flight: <= 6 hours (360 minutes) | Long flight: > 6 hours
SELECT 
    EmployeeID,
    FullName,
    Role,
    SUM(ShortHours) AS CumulativeShortHours,
    SUM(LongHours) AS CumulativeLongHours
FROM (
    -- Pilots: Short Active Flights
    SELECT p.Id AS EmployeeID, CONCAT(p.FirstName, ' ', p.SecondName) AS FullName, 'Pilot' AS Role, f.Duration/60 AS ShortHours, 0 AS LongHours
    FROM Pilot p
    JOIN Pilot_has_Flights phf ON p.Id = phf.Pilot_Id
    JOIN Flights f ON phf.Flights_FlightId = f.FlightId
    WHERE f.Duration <= 360 AND f.Status = 'active'

    UNION ALL

    -- Pilots: Long Active Flights
    SELECT p.Id, CONCAT(p.FirstName, ' ', p.SecondName), 'Pilot', 0, f.Duration/60
    FROM Pilot p
    JOIN Pilot_has_Flights phf ON p.Id = phf.Pilot_Id
    JOIN Flights f ON phf.Flights_FlightId = f.FlightId
    WHERE f.Duration > 360 AND f.Status = 'active'

    UNION ALL

    -- Flight Attendants: Short Active Flights
    SELECT fa.Id, CONCAT(fa.FirstName, ' ', fa.SecondName), 'Flight Attendant', f.Duration/60, 0
    FROM FlightAttendant fa
    JOIN FlightAttendant_has_Flights fahf ON fa.Id = fahf.FlightAttendant_Id
    JOIN Flights f ON fahf.Flights_FlightId = f.FlightId
    WHERE f.Duration <= 360 AND f.Status = 'active'

    UNION ALL

    -- Flight Attendants: Long Active Flights
    SELECT fa.Id, CONCAT(fa.FirstName, ' ', fa.SecondName), 'Flight Attendant', 0, f.Duration/60
    FROM FlightAttendant fa
    JOIN FlightAttendant_has_Flights fahf ON fa.Id = fahf.FlightAttendant_Id
    JOIN Flights f ON fahf.Flights_FlightId = f.FlightId
    WHERE f.Duration > 360 AND f.Status = 'active'
) AS RawData
GROUP BY EmployeeID, FullName, Role;