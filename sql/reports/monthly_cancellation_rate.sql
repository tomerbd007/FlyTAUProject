-- Monthly Cancellation Rate Report
-- Shows order cancellation rate per month

SELECT 
    DATE_FORMAT(created_at, '%Y-%m') AS month,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status IN ('customer_canceled', 'system_canceled') THEN 1 ELSE 0 END) AS canceled_orders,
    ROUND(
        SUM(CASE WHEN status IN ('customer_canceled', 'system_canceled') THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(COUNT(*), 0),
        1
    ) AS cancellation_rate_pct
FROM orders
GROUP BY DATE_FORMAT(created_at, '%Y-%m')
ORDER BY month DESC;
