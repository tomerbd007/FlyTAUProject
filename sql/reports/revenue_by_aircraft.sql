-- Revenue by Airplane Capacity, Manufacturer, and Cabin Class
-- Revenue by Airplane Size (Logic based), Manufacturer, and Cabin Class
-- Large Airplane: Has Business class rows
-- Revenue by Airplane Size, Manufacturer, and Cabin Class
-- NOTE: This query returns results ONLY for combinations where at least one ticket was sold.
-- If a specific class (e.g., Boeing Business) has 0 tickets in the 'Tickets' table, 
-- it will not appear in the final report due to the INNER JOIN logic.
-- Small Airplane: Business class rows are NULL or 0

SELECT 
    AirplaneSize,
    Manufacturer,
    CabinClass,
    SUM(Revenue) AS TotalRevenue
FROM (
    -- Sub-query for LARGE airplanes (BusinessRows is not null and > 0)
    SELECT 
        'Large' AS AirplaneSize,
        a.Manufacturer,
        t.Class AS CabinClass,
        -- We get the price based on ticket class directly
        (SELECT f.EconomyPrice FROM Flights f WHERE f.FlightId = o.Flights_FlightId AND t.Class = 'economy'
         UNION 
         SELECT f.BusinessPrice FROM Flights f WHERE f.FlightId = o.Flights_FlightId AND t.Class = 'business') AS Revenue
    FROM Airplanes a
    JOIN Flights f ON a.AirplaneId = f.Airplanes_AirplaneId
    JOIN orders o ON f.FlightId = o.Flights_FlightId
    JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
    WHERE a.BusinessRows IS NOT NULL AND a.BusinessRows > 0

    UNION ALL

    -- Sub-query for SMALL airplanes (BusinessRows is null or 0)
    SELECT 
        'Small' AS AirplaneSize,
        a.Manufacturer,
        t.Class AS CabinClass,
        f.EconomyPrice AS Revenue
    FROM Airplanes a
    JOIN Flights f ON a.AirplaneId = f.Airplanes_AirplaneId
    JOIN orders o ON f.FlightId = o.Flights_FlightId
    JOIN Tickets t ON o.UniqueOrderCode = t.orders_UniqueOrderCode
    WHERE a.BusinessRows IS NULL OR a.BusinessRows = 0
) AS RevenueData
GROUP BY AirplaneSize, Manufacturer, CabinClass;