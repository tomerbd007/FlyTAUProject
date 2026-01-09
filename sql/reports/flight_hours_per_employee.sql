-- Flight Hours per Employee Report
-- Shows cumulative flight hours for each crew member, split by short/long flights
-- Short flight: <= 6 hours (360 minutes)
-- Long flight: > 6 hours

SELECT
  emp.employee_id,
  emp.name,
  emp.role,
  ROUND(SUM(CASE WHEN f.Duration <= 360 THEN f.Duration/60.0 ELSE 0 END), 1) AS short_flight_hours,
  ROUND(SUM(CASE WHEN f.Duration > 360 THEN f.Duration/60.0 ELSE 0 END), 1) AS long_flight_hours,
  ROUND(SUM(f.Duration/60.0), 1) AS total_hours
FROM (
  SELECT p.Id AS employee_id,
         CONCAT(p.FirstName, ' ', p.SecondName) AS name,
         'pilot' AS role,
         phf.Flights_FlightId AS FlightId,
         phf.Flights_Airplanes_AirplaneId AS AirplaneId
  FROM Pilot p
  JOIN Pilot_has_Flights phf ON p.Id = phf.Pilot_Id

  UNION ALL

  SELECT fa.Id AS employee_id,
         CONCAT(fa.FirstName, ' ', fa.SecondName) AS name,
         'attendant' AS role,
         fahf.Flights_FlightId AS FlightId,
         fahf.Flights_Airplanes_AirplaneId AS AirplaneId
  FROM FlightAttendant fa
  JOIN FlightAttendant_has_Flights fahf ON fa.Id = fahf.FlightAttendant_Id
) AS emp
JOIN Flights f
  ON emp.FlightId = f.FlightId
  AND emp.AirplaneId = f.Airplanes_AirplaneId
WHERE f.Status IN ('occurred','active')
GROUP BY emp.employee_id, emp.name, emp.role
ORDER BY total_hours DESC;