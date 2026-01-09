-- =============================================================
-- Monthly Cancellation Rate: safe, self-contained script
-- Paste into MySQL Workbench and run against the `flytau` schema
-- =============================================================

USE flytau;

-- 1) Ensure CreatedAt column exists (runs ALTER only if needed)
SET @cnt := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE table_schema = 'flytau' AND table_name = 'orders' AND column_name = 'CreatedAt'
);
SELECT @cnt AS CreatedAt_exists;

SET @stmt := IF(@cnt = 0,
  'ALTER TABLE orders ADD COLUMN CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP',
  'SELECT \"CreatedAt already exists\" AS note'
);
PREPARE conditional_stmt FROM @stmt;
EXECUTE conditional_stmt;
DEALLOCATE PREPARE conditional_stmt;

-- 2) Diagnostics - check data & statuses
SELECT COUNT(*) AS total_orders FROM orders;
SELECT COUNT(*) AS canceled_orders FROM orders WHERE Status IN ('customer_canceled','system_canceled');
SELECT DISTINCT(Status) AS statuses FROM orders;
SELECT UniqueOrderCode, Status, CreatedAt FROM orders ORDER BY CreatedAt DESC LIMIT 20;

-- 3) OPTIONAL - backfill realistic CreatedAt values for seeded data
-- Uncomment and adjust as needed. These are examples; run only if you want to change data.
-- Example: set CreatedAt to related flight DepatureDate +/- random days (for seeded orders)
-- UPDATE orders o
-- JOIN Flights f ON o.Flights_FlightId = f.FlightId AND o.Flights_Airplanes_AirplaneId = f.Airplanes_AirplaneId
-- SET o.CreatedAt = DATE_SUB(CONCAT(f.DepartureDate, ' 09:00:00'), INTERVAL FLOOR(RAND()*30) DAY)
-- WHERE o.CreatedAt IS NOT NULL AND o.UniqueOrderCode LIKE 'FLY-%';

-- 4) OPTIONAL - simulate canceled orders for testing (reversible)
-- Uncomment one of these to test the report:
-- a) Mark an existing order as canceled:
-- UPDATE orders SET Status = 'customer_canceled' WHERE UniqueOrderCode = 'FLY-ABC123';
-- b) Insert a test canceled order (adjust values as needed):
-- INSERT INTO orders (UniqueOrderCode, TotalCost, Class, Status, RegisteredCustomer_UniqueMail, Flights_FlightId, Flights_Airplanes_AirplaneId, CreatedAt)
-- VALUES ('TEST-CNL-001', 120.00, 'economy', 'customer_canceled', 'customer1@example.com', 'FT101', 'A001', '2025-12-15 10:00:00');

-- 5) Final monthly cancellation-rate report
SELECT
  DATE_FORMAT(CreatedAt, '%Y-%m') AS month,
  COUNT(*) AS total_orders,
  SUM(CASE WHEN Status IN ('customer_canceled','system_canceled') THEN 1 ELSE 0 END) AS canceled_orders,
  ROUND(
    SUM(CASE WHEN Status IN ('customer_canceled','system_canceled') THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*),0),
    1
  ) AS cancellation_rate_pct
FROM orders
GROUP BY DATE_FORMAT(CreatedAt, '%Y-%m')
ORDER BY month DESC
LIMIT 0,1000;

-- =============================================================
-- End of script
-- =============================================================