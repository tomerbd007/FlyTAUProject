-- Monthly Activity Summary per Airplane
SELECT 
    MainStats.AirplaneId,
    MainStats.FlightMonth,
    MainStats.FlightsPerformed,
    MainStats.FlightsCancelled,
    -- Utilization percentage: (Performed Flights / 30 Days) * 100
    ROUND((MainStats.FlightsPerformed / 30.0) * 100, 2) AS UtilizationRatePercent,
    -- Dominant Route
    (SELECT CONCAT(f3.OriginPort, '-', f3.DestPort)
     FROM Flights f3
     WHERE f3.Airplanes_AirplaneId = MainStats.AirplaneId 
       AND MONTH(f3.DepartureDate) = MainStats.FlightMonth
     GROUP BY f3.OriginPort, f3.DestPort
     ORDER BY COUNT(*) DESC
     LIMIT 1) AS DominantRoute
FROM (
    -- Sub-query to count Performed and Cancelled flights
    SELECT 
        a.AirplaneId,
        MONTH(f.DepartureDate) AS FlightMonth,
        SUM(CASE WHEN f.Status = 'active' THEN 1 ELSE 0 END) AS FlightsPerformed,
        SUM(CASE WHEN f.Status = 'cancelled' THEN 1 ELSE 0 END) AS FlightsCancelled
    FROM Airplanes a
    JOIN Flights f ON a.AirplaneId = f.Airplanes_AirplaneId
    GROUP BY a.AirplaneId, MONTH(f.DepartureDate)
) AS MainStats;