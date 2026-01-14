-- Cumulative flight hours per employee, separated by flight length
-- Short flight: <= 6 hours (360 minutes)
-- Long flight: > 6 hours
SELECT 
    EmployeeID,
    FullName,
    Role,
    SUM(ShortHours) AS CumulativeShortHours,
    SUM(LongHours) AS CumulativeLongHours
FROM (
    -- Pilots: Short Flights
    SELECT p.Id AS EmployeeID, CONCAT(p.FirstName, ' ', p.SecondName) AS FullName, 'Pilot' AS Role, f.Duration/60 AS ShortHours, 0 AS LongHours
    FROM Pilot p
    JOIN Pilot_has_Flights phf ON p.Id = phf.Pilot_Id
    JOIN Flights f ON phf.Flights_FlightId = f.FlightId
    WHERE f.Duration <= 360

    UNION ALL

    -- Pilots: Long Flights
    SELECT p.Id, CONCAT(p.FirstName, ' ', p.SecondName), 'Pilot', 0, f.Duration/60
    FROM Pilot p
    JOIN Pilot_has_Flights phf ON p.Id = phf.Pilot_Id
    JOIN Flights f ON phf.Flights_FlightId = f.FlightId
    WHERE f.Duration > 360

    UNION ALL

    -- Flight Attendants: Short Flights
    SELECT fa.Id, CONCAT(fa.FirstName, ' ', fa.SecondName), 'Flight Attendant', f.Duration/60, 0
    FROM FlightAttendant fa
    JOIN FlightAttendant_has_Flights fahf ON fa.Id = fahf.FlightAttendant_Id
    JOIN Flights f ON fahf.Flights_FlightId = f.FlightId
    WHERE f.Duration <= 360

    UNION ALL

    -- Flight Attendants: Long Flights
    SELECT fa.Id, CONCAT(fa.FirstName, ' ', fa.SecondName), 'Flight Attendant', 0, f.Duration/60
    FROM FlightAttendant fa
    JOIN FlightAttendant_has_Flights fahf ON fa.Id = fahf.FlightAttendant_Id
    JOIN Flights f ON fahf.Flights_FlightId = f.FlightId
    WHERE f.Duration > 360
) AS RawData
GROUP BY EmployeeID, FullName, Role;