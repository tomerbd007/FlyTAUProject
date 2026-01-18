-- Revenue Report by Airplane Size, Manufacturer, and Cabin Class
-- Considering: 5% cancellation fee for users, 0 revenue for manager-cancelled flights, and size logic.

SELECT 
    AirplaneSize,
    Manufacturer,
    CabinClass,
    SUM(ActualRevenue) AS TotalRevenue
FROM (
    -- SUB-QUERY 1: Revenue from ACTIVE flights and CONFIRMED orders (Full price)
    SELECT 
        (SELECT 'Large' FROM Airplanes a2 WHERE a2.AirplaneId = a.AirplaneId AND a2.BusinessRows > 0 
         UNION SELECT 'Small' FROM Airplanes a2 WHERE a2.AirplaneId = a.AirplaneId AND (a2.BusinessRows IS NULL OR a2.BusinessRows = 0)) AS AirplaneSize,
        a.Manufacturer,
        t.Class AS CabinClass,
        -- Full price
        (SELECT f2.EconomyPrice FROM Flights f2 WHERE f2.FlightId = f.FlightId AND t.Class = 'economy'
         UNION SELECT f2.BusinessPrice FROM Flights f2 WHERE f2.FlightId = f.FlightId AND t.Class = 'business') AS ActualRevenue
    FROM Airplanes a
    JOIN Flights f ON a.AirplaneId = f.Airplanes_AirplaneId
    JOIN orders o ON f.FlightId = o.Flights_FlightId
    JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
    WHERE f.Status = 'active' AND o.Status = 'confirmed'

    UNION ALL

    -- SUB-QUERY 2: Revenue from CANCELLED orders (5% of original price)
    -- This applies only if the FLIGHT itself is still active
    SELECT 
        (SELECT 'Large' FROM Airplanes a2 WHERE a2.AirplaneId = a.AirplaneId AND a2.BusinessRows > 0 
         UNION SELECT 'Small' FROM Airplanes a2 WHERE a2.AirplaneId = a.AirplaneId AND (a2.BusinessRows IS NULL OR a2.BusinessRows = 0)) AS AirplaneSize,
        a.Manufacturer,
        t.Class AS CabinClass,
        -- 5% Cancellation Fee
        (SELECT f2.EconomyPrice * 0.05 FROM Flights f2 WHERE f2.FlightId = f.FlightId AND t.Class = 'economy'
         UNION SELECT f2.BusinessPrice * 0.05 FROM Flights f2 WHERE f2.FlightId = f.FlightId AND t.Class = 'business') AS ActualRevenue
    FROM Airplanes a
    JOIN Flights f ON a.AirplaneId = f.Airplanes_AirplaneId
    JOIN orders o ON f.FlightId = o.Flights_FlightId
    JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
    WHERE f.Status = 'active' AND o.Status = 'cancelled'

    -- NOTE: Flights with status 'cancelled' (by managers) are ignored 
    -- because their revenue is 0 as per your instructions.
) AS RevenueData
GROUP BY AirplaneSize, Manufacturer, CabinClass;