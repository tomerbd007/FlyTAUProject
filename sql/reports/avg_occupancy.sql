-- Average Occupancy Report
-- Shows seat occupancy percentage for completed flights

SELECT 
    AVG(OccupancyRate) AS AverageOccupancyRate
FROM (
    SELECT 
        f.FlightId,    
        (a.CouchRows * a.CouchCols + a.BusinessRows * a.BusinessCols) AS TotalCapacity,
        COUNT(t.TicketId) AS TicketsSold,
        (COUNT(t.TicketId) / (a.CouchRows * a.CouchCols + a.BusinessRows * a.BusinessCols)) * 100 AS OccupancyRate
    FROM 
        flytau.Flights f
    JOIN 
        flytau.Airplanes a ON f.Airplanes_AirplaneId = a.AirplaneId
    LEFT JOIN 
        flytau.orders o ON f.FlightId = o.Flights_FlightId
    LEFT JOIN 
        flytau.Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
    GROUP BY 
        f.FlightId, TotalCapacity
) AS FlightStats;