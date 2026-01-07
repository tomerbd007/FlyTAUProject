-- Revenue by Aircraft Report
-- Shows total revenue grouped by manufacturer, aircraft size, and seat class

SELECT 
    a.manufacturer,
    a.size,
    fs.seat_class,
    SUM(ol.price) AS total_revenue
FROM order_lines ol
JOIN flight_seats fs ON ol.flight_seat_id = fs.id
JOIN flights f ON fs.flight_id = f.id
JOIN aircraft a ON f.aircraft_id = a.id
JOIN orders o ON ol.order_id = o.id
WHERE o.status IN ('active', 'done')
GROUP BY a.manufacturer, a.size, fs.seat_class
ORDER BY a.manufacturer, a.size, fs.seat_class;
