-- =============================================================================
-- FLYTAU Seed Data
-- Initial data for testing and development
-- =============================================================================

USE flytau;

-- =============================================================================
-- EMPLOYEES - Managers, Pilots, Attendants
-- Password for all: 'password123' (bcrypt hash)
-- =============================================================================

-- Managers (2)
INSERT INTO employees (employee_code, password_hash, first_name, last_name, role, long_flight_certified) VALUES
('M001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'David', 'Cohen', 'manager', FALSE),
('M002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Sarah', 'Levi', 'manager', FALSE);

-- Pilots (10) - 6 certified for long flights
INSERT INTO employees (employee_code, password_hash, first_name, last_name, role, long_flight_certified) VALUES
('P001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Yossi', 'Mizrahi', 'pilot', TRUE),
('P002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Avi', 'Goldberg', 'pilot', TRUE),
('P003', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Moshe', 'Peretz', 'pilot', TRUE),
('P004', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Dan', 'Shapiro', 'pilot', TRUE),
('P005', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Eitan', 'Rosen', 'pilot', TRUE),
('P006', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Uri', 'Katz', 'pilot', TRUE),
('P007', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Noam', 'Ben-David', 'pilot', FALSE),
('P008', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Gal', 'Friedman', 'pilot', FALSE),
('P009', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Oren', 'Levy', 'pilot', FALSE),
('P010', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Tal', 'Avraham', 'pilot', FALSE);

-- Attendants (20) - 12 certified for long flights
INSERT INTO employees (employee_code, password_hash, first_name, last_name, role, long_flight_certified) VALUES
('A001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Maya', 'Stern', 'attendant', TRUE),
('A002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Noa', 'Klein', 'attendant', TRUE),
('A003', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Shira', 'Wolf', 'attendant', TRUE),
('A004', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Yael', 'Berger', 'attendant', TRUE),
('A005', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Tamar', 'Fischer', 'attendant', TRUE),
('A006', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Liora', 'Schwartz', 'attendant', TRUE),
('A007', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Dana', 'Weiss', 'attendant', TRUE),
('A008', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Ronit', 'Newman', 'attendant', TRUE),
('A009', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Michal', 'Gross', 'attendant', TRUE),
('A010', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Efrat', 'Blum', 'attendant', TRUE),
('A011', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Hila', 'Marcus', 'attendant', TRUE),
('A012', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Keren', 'Simon', 'attendant', TRUE),
('A013', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Inbar', 'Green', 'attendant', FALSE),
('A014', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Amit', 'Silver', 'attendant', FALSE),
('A015', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Sivan', 'Bloom', 'attendant', FALSE),
('A016', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Rotem', 'Fine', 'attendant', FALSE),
('A017', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Gili', 'Hart', 'attendant', FALSE),
('A018', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Lior', 'Stone', 'attendant', FALSE),
('A019', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Adi', 'Glass', 'attendant', FALSE),
('A020', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Chen', 'Gold', 'attendant', FALSE);

-- =============================================================================
-- CUSTOMERS (2)
-- Password: 'password123'
-- =============================================================================
INSERT INTO customers (email, password_hash, first_name, last_name) VALUES
('customer1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'John', 'Doe'),
('customer2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4I1P3VE.X6W3E.Gy', 'Jane', 'Smith');

-- =============================================================================
-- AIRCRAFT (6) - 2 small, 4 large
-- Small: economy only (10 rows x 4 cols = 40 seats)
-- Large: business (5 rows x 4 cols = 20 seats) + economy (20 rows x 6 cols = 120 seats)
-- =============================================================================
INSERT INTO aircraft (registration, manufacturer, size, economy_rows, economy_cols, business_rows, business_cols, purchased_date) VALUES
('4X-EKA', 'Boeing', 'large', 20, 6, 5, 4, '2018-03-15'),
('4X-EKB', 'Boeing', 'large', 20, 6, 5, 4, '2019-06-20'),
('4X-EKC', 'Airbus', 'large', 25, 6, 6, 4, '2020-01-10'),
('4X-EKD', 'Airbus', 'large', 22, 6, 5, 4, '2021-08-05'),
('4X-EKE', 'Dassault', 'small', 10, 4, 0, 0, '2022-02-28'),
('4X-EKF', 'Dassault', 'small', 8, 4, 0, 0, '2023-05-12');

-- =============================================================================
-- SEAT_MAP - Generate seats for each aircraft
-- =============================================================================

-- Aircraft 1 (4X-EKA) - Boeing Large: 5 business rows (A-D), 20 economy rows (A-F)
-- Business class (rows 1-5, cols A-D)
INSERT INTO seat_map (aircraft_id, seat_code, seat_class, row_num, col_letter)
SELECT 1, CONCAT(r.num, c.letter), 'business', r.num, c.letter
FROM (SELECT 1 AS num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) r
CROSS JOIN (SELECT 'A' AS letter UNION SELECT 'B' UNION SELECT 'C' UNION SELECT 'D') c;

-- Economy class (rows 6-25, cols A-F)
INSERT INTO seat_map (aircraft_id, seat_code, seat_class, row_num, col_letter)
SELECT 1, CONCAT(r.num, c.letter), 'economy', r.num, c.letter
FROM (SELECT 6 AS num UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
      UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
      UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
      UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25) r
CROSS JOIN (SELECT 'A' AS letter UNION SELECT 'B' UNION SELECT 'C' UNION SELECT 'D' UNION SELECT 'E' UNION SELECT 'F') c;

-- Aircraft 2 (4X-EKB) - Same as Aircraft 1
INSERT INTO seat_map (aircraft_id, seat_code, seat_class, row_num, col_letter)
SELECT 2, seat_code, seat_class, row_num, col_letter FROM seat_map WHERE aircraft_id = 1;

-- Aircraft 3 (4X-EKC) - Airbus Large: 6 business rows, 25 economy rows
INSERT INTO seat_map (aircraft_id, seat_code, seat_class, row_num, col_letter)
SELECT 3, CONCAT(r.num, c.letter), 'business', r.num, c.letter
FROM (SELECT 1 AS num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) r
CROSS JOIN (SELECT 'A' AS letter UNION SELECT 'B' UNION SELECT 'C' UNION SELECT 'D') c;

INSERT INTO seat_map (aircraft_id, seat_code, seat_class, row_num, col_letter)
SELECT 3, CONCAT(r.num, c.letter), 'economy', r.num, c.letter
FROM (SELECT 7 AS num UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11
      UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15 UNION SELECT 16
      UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20 UNION SELECT 21
      UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25 UNION SELECT 26
      UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30 UNION SELECT 31) r
CROSS JOIN (SELECT 'A' AS letter UNION SELECT 'B' UNION SELECT 'C' UNION SELECT 'D' UNION SELECT 'E' UNION SELECT 'F') c;

-- Aircraft 4 (4X-EKD) - Airbus Large: 5 business rows, 22 economy rows
INSERT INTO seat_map (aircraft_id, seat_code, seat_class, row_num, col_letter)
SELECT 4, CONCAT(r.num, c.letter), 'business', r.num, c.letter
FROM (SELECT 1 AS num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) r
CROSS JOIN (SELECT 'A' AS letter UNION SELECT 'B' UNION SELECT 'C' UNION SELECT 'D') c;

INSERT INTO seat_map (aircraft_id, seat_code, seat_class, row_num, col_letter)
SELECT 4, CONCAT(r.num, c.letter), 'economy', r.num, c.letter
FROM (SELECT 6 AS num UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
      UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
      UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
      UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
      UNION SELECT 26 UNION SELECT 27) r
CROSS JOIN (SELECT 'A' AS letter UNION SELECT 'B' UNION SELECT 'C' UNION SELECT 'D' UNION SELECT 'E' UNION SELECT 'F') c;

-- Aircraft 5 (4X-EKE) - Dassault Small: 10 economy rows (A-D)
INSERT INTO seat_map (aircraft_id, seat_code, seat_class, row_num, col_letter)
SELECT 5, CONCAT(r.num, c.letter), 'economy', r.num, c.letter
FROM (SELECT 1 AS num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
      UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) r
CROSS JOIN (SELECT 'A' AS letter UNION SELECT 'B' UNION SELECT 'C' UNION SELECT 'D') c;

-- Aircraft 6 (4X-EKF) - Dassault Small: 8 economy rows (A-D)
INSERT INTO seat_map (aircraft_id, seat_code, seat_class, row_num, col_letter)
SELECT 6, CONCAT(r.num, c.letter), 'economy', r.num, c.letter
FROM (SELECT 1 AS num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
      UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8) r
CROSS JOIN (SELECT 'A' AS letter UNION SELECT 'B' UNION SELECT 'C' UNION SELECT 'D') c;

-- =============================================================================
-- ROUTES (5)
-- =============================================================================
INSERT INTO routes (origin, destination, duration_minutes) VALUES
('Tel Aviv', 'New York', 660),      -- 11 hours (long flight)
('Tel Aviv', 'London', 300),        -- 5 hours (short flight)
('Tel Aviv', 'Paris', 270),         -- 4.5 hours (short flight)
('Tel Aviv', 'Athens', 120),        -- 2 hours (short flight)
('New York', 'London', 420);        -- 7 hours (long flight)

-- =============================================================================
-- FLIGHTS (4 active)
-- =============================================================================
INSERT INTO flights (flight_number, aircraft_id, route_id, departure_datetime, arrival_datetime, status, economy_price, business_price) VALUES
('FT101', 1, 1, '2025-02-15 08:00:00', '2025-02-15 19:00:00', 'active', 500.00, 1500.00),
('FT102', 3, 2, '2025-02-16 10:00:00', '2025-02-16 15:00:00', 'active', 300.00, 900.00),
('FT103', 5, 3, '2025-02-17 14:00:00', '2025-02-17 18:30:00', 'active', 250.00, NULL),
('FT104', 2, 4, '2025-02-18 06:00:00', '2025-02-18 08:00:00', 'active', 150.00, 450.00);

-- =============================================================================
-- FLIGHT_SEATS - Copy from seat_map for each flight
-- =============================================================================
INSERT INTO flight_seats (flight_id, seat_code, seat_class, row_num, col_letter, status)
SELECT 1, seat_code, seat_class, row_num, col_letter, 'available'
FROM seat_map WHERE aircraft_id = 1;

INSERT INTO flight_seats (flight_id, seat_code, seat_class, row_num, col_letter, status)
SELECT 2, seat_code, seat_class, row_num, col_letter, 'available'
FROM seat_map WHERE aircraft_id = 3;

INSERT INTO flight_seats (flight_id, seat_code, seat_class, row_num, col_letter, status)
SELECT 3, seat_code, seat_class, row_num, col_letter, 'available'
FROM seat_map WHERE aircraft_id = 5;

INSERT INTO flight_seats (flight_id, seat_code, seat_class, row_num, col_letter, status)
SELECT 4, seat_code, seat_class, row_num, col_letter, 'available'
FROM seat_map WHERE aircraft_id = 2;

-- =============================================================================
-- CREW_ASSIGNMENTS
-- Flight 1 (Long, Large): 3 pilots + 6 attendants (long-flight certified)
-- =============================================================================
INSERT INTO crew_assignments (flight_id, employee_id) VALUES
(1, 3), (1, 4), (1, 5),  -- Pilots P001, P002, P003
(1, 13), (1, 14), (1, 15), (1, 16), (1, 17), (1, 18);  -- Attendants A001-A006

-- Flight 2 (Short, Large): 3 pilots + 6 attendants
INSERT INTO crew_assignments (flight_id, employee_id) VALUES
(2, 6), (2, 7), (2, 8),  -- Pilots P004, P005, P006
(2, 19), (2, 20), (2, 21), (2, 22), (2, 23), (2, 24);  -- Attendants A007-A012

-- Flight 3 (Short, Small): 2 pilots + 3 attendants
INSERT INTO crew_assignments (flight_id, employee_id) VALUES
(3, 9), (3, 10),  -- Pilots P007, P008
(3, 25), (3, 26), (3, 27);  -- Attendants A013-A015

-- Flight 4 (Short, Large): 3 pilots + 6 attendants
INSERT INTO crew_assignments (flight_id, employee_id) VALUES
(4, 11), (4, 12), (4, 3),  -- Pilots P009, P010, P001
(4, 28), (4, 29), (4, 30), (4, 31), (4, 32), (4, 13);  -- Attendants A016-A020, A001

-- =============================================================================
-- ORDERS (4 with various statuses)
-- =============================================================================
INSERT INTO orders (booking_code, customer_id, guest_email, paid_total, status, created_at) VALUES
('ABC12345', 1, NULL, 1000.00, 'active', '2025-01-15 10:00:00'),
('DEF67890', 2, NULL, 500.00, 'completed', '2025-01-10 14:00:00'),
('GHI11111', NULL, 'guest1@example.com', 475.00, 'customer_canceled', '2025-01-12 09:00:00'),
('JKL22222', 1, NULL, 0.00, 'system_canceled', '2025-01-14 16:00:00');

-- =============================================================================
-- ORDER_LINES and update flight_seats
-- Order 1: 2 economy seats on Flight 1
-- =============================================================================
INSERT INTO order_lines (order_id, flight_seat_id, passenger_name, price) VALUES
(1, (SELECT id FROM flight_seats WHERE flight_id = 1 AND seat_code = '10A'), 'John Doe', 500.00),
(1, (SELECT id FROM flight_seats WHERE flight_id = 1 AND seat_code = '10B'), 'Jane Doe', 500.00);

UPDATE flight_seats SET status = 'sold', order_line_id = 1 WHERE flight_id = 1 AND seat_code = '10A';
UPDATE flight_seats SET status = 'sold', order_line_id = 2 WHERE flight_id = 1 AND seat_code = '10B';

-- =============================================================================
-- Seed data complete
-- =============================================================================
