-- Monthly Aircraft Activity Report
-- Shows flight activity summary per aircraft per month

SELECT
  month,
  aircraft,
  SUM(flights_completed) AS flights_completed,
  SUM(flights_canceled) AS flights_canceled,
  ROUND(SUM(flights_completed) * 100.0 / NULLIF(SUM(total),0),1) AS utilization_pct,
  most_common_route
FROM (
  SELECT
    DATE_FORMAT(f.DepartureDate, '%Y-%m') AS month,
    CONCAT(ap.Manufacturer, ' ', ap.AirplaneId) AS aircraft,
    CASE WHEN f.Status = 'occurred' THEN 1 ELSE 0 END AS flights_completed,
    CASE WHEN f.Status = 'canceled' THEN 1 ELSE 0 END AS flights_canceled,
    1 AS total,
    (
      SELECT CONCAT(inner_f.OriginPort, ' → ', inner_f.DestPort)
      FROM Flights inner_f
      WHERE inner_f.Airplanes_AirplaneId = f.Airplanes_AirplaneId
        AND DATE_FORMAT(inner_f.DepartureDate, '%Y-%m') = DATE_FORMAT(f.DepartureDate, '%Y-%m')
      GROUP BY inner_f.OriginPort, inner_f.DestPort
      ORDER BY COUNT(*) DESC
      LIMIT 1
    ) AS most_common_route
  FROM Flights f
  JOIN Airplanes ap ON f.Airplanes_AirplaneId = ap.AirplaneId
) AS sub
GROUP BY month, aircraft, most_common_route
ORDER BY month DESC, aircraft;