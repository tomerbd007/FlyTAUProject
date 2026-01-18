-- =============================================================================
-- FLYTAU Fixed Seed Data (FULL REVISED VERSION)
-- =============================================================================
-- 
-- RULES:
-- - Large aircraft (has business class): 3 pilots + 6 flight attendants
-- - Small aircraft (no business class): 2 pilots + 3 flight attendants
-- - Long flights (>6 hours = >360 minutes): need large aircraft
-- - Crew must have LongFlightsTraining=TRUE for flights >6 hours
-- - Aircraft/crew available for next flight if at same location
-- =============================================================================

USE flytau;

-- Disable foreign keys temporarily to allow truncating linked tables
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE Managers_edits_Flights;
TRUNCATE TABLE FlightAttendant_has_Flights;
TRUNCATE TABLE Pilot_has_Flights;
TRUNCATE TABLE Tickets;
TRUNCATE TABLE orders;
TRUNCATE TABLE Flights;
TRUNCATE TABLE Airplanes;
TRUNCATE TABLE Pilot;
TRUNCATE TABLE FlightAttendant;
TRUNCATE TABLE RegisteredCustomer;
TRUNCATE TABLE GuestCustomer;
TRUNCATE TABLE Managers;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- MANAGERS
-- -----------------------------------------------------------------------------
INSERT INTO Managers (ManagerId, Password, FirstName, SecondName, PhoneNum, JoinDate, Street, City, HouseNum) VALUES
('M001', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'David', 'Cohen', '["972-54-1234567"]', '2018-05-01', 'Main St', 'Tel Aviv', '10'),
('M002', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'Sarah', 'Levi', '["972-50-7654321"]', '2019-09-15', 'Derech Ben Gurion', 'Jerusalem', '20')
AS new_m
ON DUPLICATE KEY UPDATE
  Password = new_m.Password,
  FirstName = new_m.FirstName,
  SecondName = new_m.SecondName,
  PhoneNum = new_m.PhoneNum,
  JoinDate = new_m.JoinDate,
  Street = new_m.Street,
  City = new_m.City,
  HouseNum = new_m.HouseNum;

-- -----------------------------------------------------------------------------
-- PILOTS (16 total: 10 assigned + 6 unassigned at TLV)
-- Long flight trained pilots: P001-P006 (for flights >6h)
-- Short flight only pilots: P007-P016
-- Unassigned pilots (at TLV base): P011-P016
-- -----------------------------------------------------------------------------
INSERT INTO Pilot (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining, JoinDate, Street, City, HouseNum) VALUES
-- Assigned pilots (will fly scheduled flights)
('P001', 'Yossi', 'Mizrahi', '["972-52-1111111"]', TRUE, '2016-02-01', 'Pilot Ave', 'Tel Aviv', '12'),
('P002', 'Avi', 'Goldberg', '["972-54-2222222"]', TRUE, '2016-03-10', 'Pilot Ave', 'Tel Aviv', '14'),
('P003', 'Moshe', 'Peretz', '["972-50-3333333"]', TRUE, '2017-05-20', 'Aviation Rd', 'Tel Aviv', '16'),
('P004', 'Dan', 'Shapiro', '["972-52-4444444"]', TRUE, '2018-01-15', 'Aviation Rd', 'Tel Aviv', '18'),
('P005', 'Eitan', 'Rosen', '["972-54-5555555"]', TRUE, '2019-06-30', 'Pilot St', 'Haifa', '4'),
('P006', 'Uri', 'Katz', '["972-50-6666666"]', TRUE, '2015-12-01', 'Pilot St', 'Haifa', '6'),
('P007', 'Noam', 'Ben-David', '["972-52-7777777"]', FALSE, '2020-07-01', 'Crew Ln', 'Netanya', '3'),
('P008', 'Gal', 'Friedman', '["972-54-8888888"]', FALSE, '2021-04-12', 'Crew Ln', 'Netanya', '5'),
('P009', 'Oren', 'Levy', '["972-50-9999999"]', FALSE, '2019-09-09', 'Air St', 'Ramat Gan', '8'),
('P010', 'Tal', 'Avraham', '["972-52-1010101"]', FALSE, '2020-11-11', 'Air St', 'Ramat Gan', '10'),
-- Unassigned pilots at TLV base (6 new - 4 with long flight training = 2/3)
('P011', 'Alon', 'Baruch', '["972-52-1111101"]', TRUE, '2020-03-15', 'Ben Gurion St', 'Tel Aviv', '22'),
('P012', 'Benny', 'Carmel', '["972-54-1212101"]', TRUE, '2019-07-20', 'Ben Gurion St', 'Tel Aviv', '24'),
('P013', 'Chaim', 'Dayan', '["972-50-1313101"]', TRUE, '2021-01-10', 'Airport Rd', 'Tel Aviv', '26'),
('P014', 'David', 'Eyal', '["972-52-1414101"]', TRUE, '2020-09-05', 'Airport Rd', 'Tel Aviv', '28'),
('P015', 'Ehud', 'Fein', '["972-54-1515101"]', FALSE, '2022-02-28', 'Hashalom St', 'Tel Aviv', '30'),
('P016', 'Felix', 'Golan', '["972-50-1616101"]', FALSE, '2021-06-15', 'Hashalom St', 'Tel Aviv', '32')
AS new_p
ON DUPLICATE KEY UPDATE
  FirstName = new_p.FirstName,
  SecondName = new_p.SecondName,
  PhoneNum = new_p.PhoneNum,
  LongFlightsTraining = new_p.LongFlightsTraining,
  JoinDate = new_p.JoinDate,
  Street = new_p.Street,
  City = new_p.City,
  HouseNum = new_p.HouseNum;

-- -----------------------------------------------------------------------------
-- FLIGHT ATTENDANTS (32 total: 20 assigned + 12 unassigned at TLV)
-- Long flight trained: A001-A012 (for flights >6h)
-- Short flight only: A013-A032
-- Unassigned attendants (at TLV base): A021-A032
-- -----------------------------------------------------------------------------
INSERT INTO FlightAttendant (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining, JoinDate, Street, City, HouseNum) VALUES
-- Assigned flight attendants (will fly scheduled flights)
('A001', 'Maya', 'Stern', '["972-50-1111111"]', TRUE, '2017-03-01', 'Cabin Rd', 'Tel Aviv', '2'),
('A002', 'Noa', 'Klein', '["972-52-1212121"]', TRUE, '2018-04-10', 'Cabin Rd', 'Tel Aviv', '4'),
('A003', 'Shira', 'Wolf', '["972-54-1313131"]', TRUE, '2017-05-12', 'Service St', 'Haifa', '6'),
('A004', 'Yael', 'Berger', '["972-50-1414141"]', TRUE, '2019-01-20', 'Service St', 'Haifa', '8'),
('A005', 'Tamar', 'Fischer', '["972-52-1515151"]', TRUE, '2019-06-05', 'Cabin Ave', 'Netanya', '3'),
('A006', 'Liora', 'Schwartz', '["972-54-1616161"]', TRUE, '2016-07-07', 'Cabin Ave', 'Netanya', '5'),
('A007', 'Dana', 'Weiss', '["972-50-1717171"]', TRUE, '2018-10-10', 'Crew St', 'Beersheba', '11'),
('A008', 'Ronit', 'Newman', '["972-52-1818181"]', TRUE, '2020-02-02', 'Crew St', 'Beersheba', '13'),
('A009', 'Michal', 'Gross', '["972-54-1919191"]', TRUE, '2017-08-08', 'Flight Rd', 'Ramat Gan', '7'),
('A010', 'Efrat', 'Blum', '["972-50-2020202"]', TRUE, '2018-11-11', 'Flight Rd', 'Ramat Gan', '9'),
('A011', 'Hila', 'Marcus', '["972-52-2121212"]', TRUE, '2016-12-12', 'Service Ln', 'Herzliya', '2'),
('A012', 'Keren', 'Simon', '["972-54-2222223"]', TRUE, '2019-03-03', 'Service Ln', 'Herzliya', '4'),
('A013', 'Inbar', 'Green', '["972-50-2323232"]', FALSE, '2021-01-01', 'Cabin Ct', 'Ramla', '1'),
('A014', 'Amit', 'Silver', '["972-52-2424242"]', FALSE, '2021-05-05', 'Cabin Ct', 'Ramla', '3'),
('A015', 'Sivan', 'Bloom', '["972-54-2525252"]', FALSE, '2022-02-02', 'Crew Blvd', 'Afula', '6'),
('A016', 'Rotem', 'Fine', '["972-50-2626262"]', FALSE, '2020-09-09', 'Crew Blvd', 'Afula', '8'),
('A017', 'Gili', 'Hart', '["972-52-2727272"]', FALSE, '2019-07-07', 'Cabin Way', 'Kfar Saba', '12'),
('A018', 'Lior', 'Stone', '["972-54-2828282"]', FALSE, '2018-06-06', 'Cabin Way', 'Kfar Saba', '14'),
('A019', 'Adi', 'Glass', '["972-50-2929292"]', FALSE, '2020-10-10', 'Flight Ave', 'Eilat', '9'),
('A020', 'Chen', 'Gold', '["972-52-3030303"]', FALSE, '2019-09-09', 'Flight Ave', 'Eilat', '11'),
-- Unassigned flight attendants at TLV base (12 new - 8 with long flight training = 2/3)
('A021', 'Orly', 'Haim', '["972-50-3131313"]', TRUE, '2020-04-15', 'Ben Gurion St', 'Tel Aviv', '40'),
('A022', 'Pnina', 'Ilan', '["972-52-3232323"]', TRUE, '2019-08-20', 'Ben Gurion St', 'Tel Aviv', '42'),
('A023', 'Rachel', 'Jacob', '["972-54-3333313"]', TRUE, '2021-02-10', 'Airport Rd', 'Tel Aviv', '44'),
('A024', 'Sara', 'Kaplan', '["972-50-3434343"]', TRUE, '2020-10-05', 'Airport Rd', 'Tel Aviv', '46'),
('A025', 'Tali', 'Levin', '["972-52-3535353"]', TRUE, '2022-03-28', 'Hashalom St', 'Tel Aviv', '48'),
('A026', 'Uria', 'Mann', '["972-54-3636363"]', TRUE, '2021-07-15', 'Hashalom St', 'Tel Aviv', '50'),
('A027', 'Vered', 'Naor', '["972-50-3737373"]', TRUE, '2020-05-20', 'Rothschild Blvd', 'Tel Aviv', '52'),
('A028', 'Yarden', 'Oz', '["972-52-3838383"]', TRUE, '2019-11-10', 'Rothschild Blvd', 'Tel Aviv', '54'),
('A029', 'Ziva', 'Pearl', '["972-54-3939393"]', FALSE, '2021-09-05', 'Dizengoff St', 'Tel Aviv', '56'),
('A030', 'Ayala', 'Roth', '["972-50-4040404"]', FALSE, '2022-01-25', 'Dizengoff St', 'Tel Aviv', '58'),
('A031', 'Batya', 'Segal', '["972-52-4141414"]', FALSE, '2020-06-30', 'Allenby St', 'Tel Aviv', '60'),
('A032', 'Carmit', 'Tal', '["972-54-4242424"]', FALSE, '2021-03-15', 'Allenby St', 'Tel Aviv', '62')
AS new_fa
ON DUPLICATE KEY UPDATE
  FirstName = new_fa.FirstName,
  SecondName = new_fa.SecondName,
  PhoneNum = new_fa.PhoneNum,
  LongFlightsTraining = new_fa.LongFlightsTraining,
  JoinDate = new_fa.JoinDate,
  Street = new_fa.Street,
  City = new_fa.City,
  HouseNum = new_fa.HouseNum;

-- -----------------------------------------------------------------------------
-- REGISTERED CUSTOMERS
-- -----------------------------------------------------------------------------
INSERT INTO RegisteredCustomer (UniqueMail, Password, PhoneNum, PassportNum, FirstName, SecondName, BirthDate, RegistrationDate) VALUES
('customer1@gmail.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', '["972-54-1111111"]', 'P123456', 'John', 'Doe', '1985-06-15', '2020-01-01'),
('customer2@gmail.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', '["972-54-2222222"]', 'P789012', 'Jane', 'Smith', '1990-09-22', '2021-02-15')
AS new_reg
ON DUPLICATE KEY UPDATE
  Password = new_reg.Password,
  PhoneNum = new_reg.PhoneNum,
  PassportNum = new_reg.PassportNum,
  FirstName = new_reg.FirstName,
  SecondName = new_reg.SecondName,
  BirthDate = new_reg.BirthDate,
  RegistrationDate = new_reg.RegistrationDate;

-- -----------------------------------------------------------------------------
-- GUEST CUSTOMERS
-- -----------------------------------------------------------------------------
INSERT INTO GuestCustomer (UniqueMail, PhoneNum, FirstName, SecondName) VALUES
('guest1@gmail.com', '["972-50-0000000"]', 'Guest', 'User')
AS new_g
ON DUPLICATE KEY UPDATE
  PhoneNum = new_g.PhoneNum,
  FirstName = new_g.FirstName,
  SecondName = new_g.SecondName;

-- -----------------------------------------------------------------------------
-- AIRPLANES (8 total: 6 assigned + 2 unassigned at TLV)
-- Large aircraft (has business class): PLANE-001, PLANE-003, PLANE-005
-- Small aircraft (no business class): PLANE-002, PLANE-004, PLANE-006
-- Unassigned at TLV base: PLANE-007, PLANE-008
-- -----------------------------------------------------------------------------
INSERT INTO Airplanes (AirplaneId, PurchaseDate, Manufacturer, CouchRows, CouchCols, BusinessRows, BusinessCols) VALUES
-- Assigned aircraft
('PLANE-001', '2018-03-15', 'Boeing', 18, 7, 6, 4),     -- Large: 126 economy + 24 business = 150 seats
('PLANE-002', '2019-07-22', 'Boeing', 8, 4, 0, 0),      -- Small: 32 economy seats
('PLANE-003', '2017-11-08', 'Airbus', 20, 7, 6, 4),     -- Large: 140 economy + 24 business = 164 seats
('PLANE-004', '2020-02-14', 'Airbus', 9, 4, 0, 0),      -- Small: 36 economy seats
('PLANE-005', '2021-06-30', 'Dassault', 18, 7, 6, 4),   -- Large: 126 economy + 24 business = 150 seats
('PLANE-006', '2022-01-10', 'Bombardier', 22, 4, 0, 0), -- Small: 88 economy seats
-- Unassigned aircraft at TLV base (2 new)
('PLANE-007', '2023-05-20', 'Boeing', 24, 7, 6, 4),    -- Large: 168 economy + 24 business = 192 seats
('PLANE-008', '2024-02-10', 'Airbus', 10, 4, 0, 0)     -- Small: 40 economy seats
AS new_air
ON DUPLICATE KEY UPDATE
  PurchaseDate = new_air.PurchaseDate,
  Manufacturer = new_air.Manufacturer,
  CouchRows = new_air.CouchRows,
  CouchCols = new_air.CouchCols,
  BusinessRows = new_air.BusinessRows,
  BusinessCols = new_air.BusinessCols;

-- -----------------------------------------------------------------------------
-- FLIGHTS (5 months: Sep, Oct, Nov 2025, Jan, Feb 2026)
-- All flights depart from TLV (our base) so aircraft/crew are always available
-- Long flights (>360 min) use large aircraft with long-flight trained crew
-- -----------------------------------------------------------------------------
INSERT INTO Flights (FlightId, Airplanes_AirplaneId, OriginPort, DestPort, DepartureDate, DepartureHour, Duration, Status, EconomyPrice, BusinessPrice) VALUES
-- September 2025 - PLANE-001 (Large) and PLANE-002 (Small)
('FT201', 'PLANE-001', 'TLV', 'LHR', '2025-09-10', '07:00:00', 298, 'done', 350.00, 1100.00),  -- 4h58m, Large, 3P+6FA
('FT202', 'PLANE-002', 'TLV', 'ATH', '2025-09-15', '09:30:00', 129, 'done', 180.00, NULL),     -- 2h09m, Small, 2P+3FA

-- October 2025 - PLANE-003 (Large) and PLANE-005 (Large)
('FT203', 'PLANE-003', 'TLV', 'CDG', '2025-10-05', '06:00:00', 277, 'done', 320.00, 980.00),   -- 4h37m, Large, 3P+6FA
('FT204', 'PLANE-005', 'TLV', 'FRA', '2025-10-20', '14:00:00', 253, 'done', 300.00, 920.00),   -- 4h13m, Large, 3P+6FA

-- November 2025 - Long flights need large aircraft with trained crew
('FT101', 'PLANE-001', 'TLV', 'JFK', '2025-11-15', '08:00:00', 660, 'done', 500.00, 1500.00),  -- 11h, LONG, Large, 3P+6FA (trained)
('FT102', 'PLANE-003', 'TLV', 'LAX', '2025-11-20', '06:30:00', 780, 'done', 550.00, 1600.00),  -- 13h, LONG, Large, 3P+6FA (trained)
('FT103', 'PLANE-002', 'TLV', 'LCA', '2025-11-29', '22:00:00', 40, 'cancelled', 120.00, NULL), -- 40m, Small, 2P+3FA (cancelled)

-- January 2026 - PLANE-004 (Small) and PLANE-006 (Small)
('FT104', 'PLANE-004', 'TLV', 'RUH', '2026-01-21', '20:00:00', 160, 'active', 150.00, NULL),   -- 2h40m, Small, 2P+3FA
('FT205', 'PLANE-006', 'TLV', 'CAI', '2026-01-25', '11:00:00', 73, 'active', 120.00, NULL),    -- 1h13m, Small, 2P+3FA

-- February 2026 - PLANE-005 (Large) and PLANE-001 (Large)
('FT206', 'PLANE-005', 'TLV', 'BCN', '2026-02-10', '08:30:00', 262, 'active', 280.00, 850.00), -- 4h22m, Large, 3P+6FA
('FT207', 'PLANE-001', 'TLV', 'AMS', '2026-02-18', '10:00:00', 279, 'active', 310.00, 950.00)  -- 4h39m, Large, 3P+6FA
AS new_f
ON DUPLICATE KEY UPDATE
  Airplanes_AirplaneId = new_f.Airplanes_AirplaneId,
  OriginPort = new_f.OriginPort,
  DestPort = new_f.DestPort,
  DepartureDate = new_f.DepartureDate,
  DepartureHour = new_f.DepartureHour,
  Duration = new_f.Duration,
  Status = new_f.Status,
  EconomyPrice = new_f.EconomyPrice,
  BusinessPrice = new_f.BusinessPrice;

-- -----------------------------------------------------------------------------
-- CREW ASSIGNMENTS
-- Large aircraft: 3 pilots + 6 flight attendants
-- Small aircraft: 2 pilots + 3 flight attendants
-- Long flights (>360 min): crew must have LongFlightsTraining=TRUE
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Pilot_has_Flights (Pilot_Id, Flights_FlightId) VALUES
-- FT201: Large aircraft, 3 pilots (P001, P002, P003)
('P001', 'FT201'), ('P002', 'FT201'), ('P003', 'FT201'),
-- FT202: Small aircraft, 2 pilots (P007, P008)
('P007', 'FT202'), ('P008', 'FT202'),
-- FT203: Large aircraft, 3 pilots (P004, P005, P006)
('P004', 'FT203'), ('P005', 'FT203'), ('P006', 'FT203'),
-- FT204: Large aircraft, 3 pilots (P001, P002, P003) - available after FT201
('P001', 'FT204'), ('P002', 'FT204'), ('P003', 'FT204'),
-- FT101: LONG flight (>6h), Large aircraft, 3 TRAINED pilots (P001, P002, P003)
('P001', 'FT101'), ('P002', 'FT101'), ('P003', 'FT101'),
-- FT102: LONG flight (>6h), Large aircraft, 3 TRAINED pilots (P004, P005, P006)
('P004', 'FT102'), ('P005', 'FT102'), ('P006', 'FT102'),
-- FT103: Small aircraft, 2 pilots (P007, P008) - cancelled but still assigned
('P007', 'FT103'), ('P008', 'FT103'),
-- FT104: Small aircraft, 2 pilots (P009, P010)
('P009', 'FT104'), ('P010', 'FT104'),
-- FT205: Small aircraft, 2 pilots (P007, P008)
('P007', 'FT205'), ('P008', 'FT205'),
-- FT206: Large aircraft, 3 pilots (P001, P002, P003)
('P001', 'FT206'), ('P002', 'FT206'), ('P003', 'FT206'),
-- FT207: Large aircraft, 3 pilots (P004, P005, P006)
('P004', 'FT207'), ('P005', 'FT207'), ('P006', 'FT207');

INSERT IGNORE INTO FlightAttendant_has_Flights (FlightAttendant_Id, Flights_FlightId) VALUES
-- FT201: Large aircraft, 6 flight attendants (A001-A006)
('A001', 'FT201'), ('A002', 'FT201'), ('A003', 'FT201'), ('A004', 'FT201'), ('A005', 'FT201'), ('A006', 'FT201'),
-- FT202: Small aircraft, 3 flight attendants (A013, A014, A015)
('A013', 'FT202'), ('A014', 'FT202'), ('A015', 'FT202'),
-- FT203: Large aircraft, 6 flight attendants (A007-A012)
('A007', 'FT203'), ('A008', 'FT203'), ('A009', 'FT203'), ('A010', 'FT203'), ('A011', 'FT203'), ('A012', 'FT203'),
-- FT204: Large aircraft, 6 flight attendants (A001-A006) - available after FT201
('A001', 'FT204'), ('A002', 'FT204'), ('A003', 'FT204'), ('A004', 'FT204'), ('A005', 'FT204'), ('A006', 'FT204'),
-- FT101: LONG flight, Large aircraft, 6 TRAINED flight attendants (A001-A006)
('A001', 'FT101'), ('A002', 'FT101'), ('A003', 'FT101'), ('A004', 'FT101'), ('A005', 'FT101'), ('A006', 'FT101'),
-- FT102: LONG flight, Large aircraft, 6 TRAINED flight attendants (A007-A012)
('A007', 'FT102'), ('A008', 'FT102'), ('A009', 'FT102'), ('A010', 'FT102'), ('A011', 'FT102'), ('A012', 'FT102'),
-- FT103: Small aircraft, 3 flight attendants (A013, A014, A015) - cancelled but still assigned
('A013', 'FT103'), ('A014', 'FT103'), ('A015', 'FT103'),
-- FT104: Small aircraft, 3 flight attendants (A016, A017, A018)
('A016', 'FT104'), ('A017', 'FT104'), ('A018', 'FT104'),
-- FT205: Small aircraft, 3 flight attendants (A019, A020, A013)
('A019', 'FT205'), ('A020', 'FT205'), ('A013', 'FT205'),
-- FT206: Large aircraft, 6 flight attendants (A001-A006)
('A001', 'FT206'), ('A002', 'FT206'), ('A003', 'FT206'), ('A004', 'FT206'), ('A005', 'FT206'), ('A006', 'FT206'),
-- FT207: Large aircraft, 6 flight attendants (A007-A012)
('A007', 'FT207'), ('A008', 'FT207'), ('A009', 'FT207'), ('A010', 'FT207'), ('A011', 'FT207'), ('A012', 'FT207');

-- -----------------------------------------------------------------------------
-- ORDERS (spread across 5 months with mix of confirmed/cancelled)
-- -----------------------------------------------------------------------------
INSERT INTO orders (UniqueOrderCode, Flights_FlightId, TotalCost, Status, GuestCustomer_UniqueMail, RegisteredCustomer_UniqueMail) VALUES
-- September 2025 orders (PLANE-001, PLANE-002)
('ORD-SEP01', 'FT201', 700.00, 'confirmed', NULL, 'customer1@gmail.com'),
('ORD-SEP02', 'FT201', 1100.00, 'confirmed', NULL, 'customer2@gmail.com'),
('ORD-SEP03', 'FT202', 180.00, 'confirmed', 'guest1@gmail.com', NULL),
('ORD-SEP04', 'FT202', 9.00, 'customer_canceled', NULL, 'customer1@gmail.com'),
-- October 2025 orders (PLANE-003, PLANE-005)
('ORD-OCT01', 'FT203', 640.00, 'confirmed', NULL, 'customer2@gmail.com'),
('ORD-OCT02', 'FT203', 16.00, 'customer_canceled', NULL, 'customer1@gmail.com'),
('ORD-OCT03', 'FT204', 920.00, 'confirmed', NULL, 'customer2@gmail.com'),
('ORD-OCT04', 'FT204', 300.00, 'confirmed', 'guest1@gmail.com', NULL),
-- November 2025 orders (PLANE-001, PLANE-003)
('FLY-ABC123', 'FT101', 1000.00, 'confirmed', NULL, 'customer1@gmail.com'),
('FLY-DEF456', 'FT102', 1600.00, 'confirmed', NULL, 'customer2@gmail.com'),
('FLY-DEF768', 'FT102', 550.00, 'confirmed', 'guest1@gmail.com', NULL),
-- January 2026 orders (PLANE-004, PLANE-006)
('FLY-ABC001', 'FT104', 15.00, 'customer_canceled', NULL, 'customer1@gmail.com'),
('FLY-ABC002', 'FT104', 150.00, 'confirmed', NULL, 'customer2@gmail.com'),
('FLY-DEF003', 'FT104', 7.50, 'customer_canceled', NULL, 'customer1@gmail.com'),
('ORD-JAN01', 'FT205', 240.00, 'confirmed', NULL, 'customer1@gmail.com'),
('ORD-JAN02', 'FT205', 6.00, 'customer_canceled', 'guest1@gmail.com', NULL),
-- February 2026 orders (PLANE-005, PLANE-001)
('ORD-FEB01', 'FT206', 850.00, 'confirmed', NULL, 'customer2@gmail.com'),
('ORD-FEB02', 'FT206', 280.00, 'confirmed', NULL, 'customer1@gmail.com'),
('ORD-FEB03', 'FT207', 620.00, 'confirmed', 'guest1@gmail.com', NULL),
('ORD-FEB04', 'FT207', 15.50, 'customer_canceled', NULL, 'customer2@gmail.com')
AS new_o
ON DUPLICATE KEY UPDATE
  Flights_FlightId = new_o.Flights_FlightId,
  TotalCost = new_o.TotalCost,
  Status = new_o.Status;

-- -----------------------------------------------------------------------------
-- TICKETS (for all orders)
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Tickets (orders_UniqueOrderCode, RowNum, Seat, Class) VALUES
-- September tickets
('ORD-SEP01', 5, 'A', 'economy'),
('ORD-SEP01', 5, 'B', 'economy'),
('ORD-SEP02', 1, 'A', 'business'),
('ORD-SEP03', 8, 'A', 'economy'),
('ORD-SEP04', 8, 'B', 'economy'),
-- October tickets
('ORD-OCT01', 3, 'A', 'economy'),
('ORD-OCT01', 3, 'B', 'economy'),
('ORD-OCT02', 10, 'A', 'economy'),
('ORD-OCT03', 1, 'A', 'business'),
('ORD-OCT04', 12, 'A', 'economy'),
-- November tickets
('FLY-ABC123', 7, 'A', 'economy'),
('FLY-ABC123', 7, 'B', 'economy'),
('FLY-DEF456', 1, 'A', 'business'),
('FLY-DEF768', 24, 'A', 'economy'),
-- January tickets
('FLY-ABC001', 5, 'A', 'economy'),
('FLY-ABC001', 5, 'B', 'economy'),
('FLY-ABC002', 8, 'A', 'economy'),
('FLY-DEF003', 4, 'C', 'economy'),
('ORD-JAN01', 6, 'A', 'economy'),
('ORD-JAN01', 6, 'B', 'economy'),
('ORD-JAN02', 9, 'A', 'economy'),
-- February tickets
('ORD-FEB01', 1, 'A', 'business'),
('ORD-FEB02', 15, 'A', 'economy'),
('ORD-FEB03', 4, 'A', 'economy'),
('ORD-FEB03', 4, 'B', 'economy'),
('ORD-FEB04', 18, 'A', 'economy');

-- -----------------------------------------------------------------------------
-- MANAGER EDITS
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Managers_edits_Flights (Managers_ManagerId, Flights_FlightId) VALUES
('M001', 'FT101'), ('M001', 'FT102'), ('M002', 'FT103'), ('M002', 'FT104'),
('M001', 'FT201'), ('M001', 'FT202'), ('M002', 'FT203'), ('M002', 'FT204'),
('M001', 'FT205'), ('M002', 'FT206'), ('M001', 'FT207');

-- =============================================================================
-- - 8 Airplanes: 6 assigned to flights + 2 unassigned at TLV (PLANE-007, PLANE-008)
--   Manufacturers: Boeing, Airbus, Dassault only
-- - 16 Pilots: 10 assigned to flights + 6 unassigned at TLV (P011-P016)
--   Unassigned: 4/6 (67%) have long flight training
-- - 32 Flight Attendants: 20 assigned to flights + 12 unassigned at TLV (A021-A032)
--   Unassigned: 8/12 (67%) have long flight training
-- - 11 Flights across 5 months
-- - All flights depart from TLV (Ben Gurion) so crew is always available
-- - Long flights (>6h) use large aircraft with trained crew
-- - Large aircraft: 3 pilots + 6 flight attendants
-- - Small aircraft: 2 pilots + 3 flight attendants
-- - Cancelled orders use 'customer_canceled' or 'system_canceled' status
-- =============================================================================

-- Seed Complete