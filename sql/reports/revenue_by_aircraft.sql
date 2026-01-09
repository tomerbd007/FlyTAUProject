-- we need to calculate the revenue for each Airplane size (big or small), aircraft and department

SELECT 
    Airplanes.Manufacturer AS Airplane_Manufacturer,
    IF(Airplanes.`Business (Rows, Cols)` IS NULL, 'Small', 'Large') AS Airplane_Size,
    -- We use COALESCE or IFNULL to show 0 instead of nothing
    Tickets.Class AS Ticket_Class,
    SUM(
        CASE 
            WHEN Flights.Status = 'Cancelled' THEN 0 
            WHEN orders.Status = 'Cancelled' THEN Tickets.Price * 0.05 
            ELSE IFNULL(Tickets.Price, 0) 
        END
    ) AS Total_Revenue
FROM Airplanes
JOIN Flights ON Airplanes.AirplaneId = Flights.Airplanes_AirplaneId
LEFT JOIN Tickets ON Flights.FlightId = Tickets.Flights_FlightId
LEFT JOIN orders ON Tickets.orders_UniqueOrderCode = orders.UniqueOrderCode
GROUP BY 
    Airplane_Manufacturer, 
    Airplane_Size, 
    Ticket_Class;