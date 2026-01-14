-- Monthly purchase cancellation rate
-- Only shows the month and the final calculated percentage
SELECT 
    TotalData.OrderMonth,
    ROUND((IFNULL(CancelledData.CancelledCount, 0) * 100.0) / TotalData.TotalCount, 2) AS CancellationRatePercent
FROM (
    -- Sub-query: Count total orders per month
    SELECT MONTH(DepartureDate) AS OrderMonth, COUNT(*) AS TotalCount
    FROM orders o
    JOIN Flights f ON o.Flights_FlightId = f.FlightId
    GROUP BY MONTH(DepartureDate)
) AS TotalData
LEFT JOIN (
    -- Sub-query: Count only cancelled orders per month
    SELECT MONTH(DepartureDate) AS OrderMonth, COUNT(*) AS CancelledCount
    FROM orders o
    JOIN Flights f ON o.Flights_FlightId = f.FlightId
    WHERE o.Status = 'cancelled'
    GROUP BY MONTH(DepartureDate)
) AS CancelledData ON TotalData.OrderMonth = CancelledData.OrderMonth
ORDER BY TotalData.OrderMonth;