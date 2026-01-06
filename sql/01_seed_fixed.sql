-- =============================================================================
-- FLYTAU Fixed Seed Data (idempotent)
-- Use: mysql -u root -p flytau < sql/01_seed_fixed.sql
-- This seed is safe to re-run: main tables use INSERT ... AS alias ... ON DUPLICATE KEY UPDATE
-- Association tables use INSERT IGNORE to skip duplicate link rows.
-- =============================================================================

USE flytau;

-- -----------------------------------------------------------------------------
-- MANAGERS
-- -----------------------------------------------------------------------------
INSERT INTO Managers (ManagerId, Password, FirstName, SecondName, PhoneNum, JoinDate, Street, City, HouseNum) VALUES
('M001', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'David', 'Cohen', '["972-54-1234567"]', '2018-05-01', 'Main St', 'Tel Aviv', '10'),
('M002', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'Sarah', 'Levi', '["972-50-7654321"]', '2019-09-15', 'Derech Ben Gurion', 'Jerusalem', '20')
AS new_managers (ManagerId, Password, FirstName, SecondName, PhoneNum, JoinDate, Street, City, HouseNum)
ON DUPLICATE KEY UPDATE
  Password = new_managers.Password,
  FirstName = new_managers.FirstName,
  SecondName = new_managers.SecondName,
  PhoneNum = new_managers.PhoneNum,
  JoinDate = new_managers.JoinDate,
  Street = new_managers.Street,
  City = new_managers.City,
  HouseNum = new_managers.HouseNum;

-- -----------------------------------------------------------------------------
-- PILOTS
-- -----------------------------------------------------------------------------
INSERT INTO Pilot (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining, JoinDate, Street, City, HouseNum) VALUES
('P001', 'Yossi', 'Mizrahi', '["972-52-1111111"]', TRUE, '2016-02-01', 'Pilot Ave', 'Tel Aviv', '12'),
('P002', 'Avi', 'Goldberg', '["972-54-2222222"]', TRUE, '2016-03-10', 'Pilot Ave', 'Tel Aviv', '14'),
('P003', 'Moshe', 'Peretz', '["972-50-3333333"]', TRUE, '2017-05-20', 'Aviation Rd', 'Tel Aviv', '16'),
('P004', 'Dan', 'Shapiro', '["972-52-4444444"]', TRUE, '2018-01-15', 'Aviation Rd', 'Tel Aviv', '18'),
('P005', 'Eitan', 'Rosen', '["972-54-5555555"]', TRUE, '2019-06-30', 'Pilot St', 'Haifa', '4'),
('P006', 'Uri', 'Katz', '["972-50-6666666"]', TRUE, '2015-12-01', 'Pilot St', 'Haifa', '6'),
('P007', 'Noam', 'Ben-David', '["972-52-7777777"]', FALSE, '2020-07-01', 'Crew Ln', 'Netanya', '3'),
('P008', 'Gal', 'Friedman', '["972-54-8888888"]', FALSE, '2021-04-12', 'Crew Ln', 'Netanya', '5'),
('P009', 'Oren', 'Levy', '["972-50-9999999"]', FALSE, '2019-09-09', 'Air St', 'Ramat Gan', '8'),
('P010', 'Tal', 'Avraham', '["972-52-1010101"]', FALSE, '2020-11-11', 'Air St', 'Ramat Gan', '10')
AS new_pilots (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining, JoinDate, Street, City, HouseNum)
ON DUPLICATE KEY UPDATE
  FirstName = new_pilots.FirstName,
  SecondName = new_pilots.SecondName,
  PhoneNum = new_pilots.PhoneNum,
  LongFlightsTraining = new_pilots.LongFlightsTraining,
  JoinDate = new_pilots.JoinDate,
  Street = new_pilots.Street,
  City = new_pilots.City,
  HouseNum = new_pilots.HouseNum;

-- -----------------------------------------------------------------------------
-- FLIGHT ATTENDANTS (IDs renamed to FA###)
-- -----------------------------------------------------------------------------
INSERT INTO FlightAttendant (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining, JoinDate, Street, City, HouseNum) VALUES
('FA001', 'Maya', 'Stern', '["972-50-1111111"]', TRUE, '2017-03-01', 'Cabin Rd', 'Tel Aviv', '2'),
('FA002', 'Noa', 'Klein', '["972-52-1212121"]', TRUE, '2018-04-10', 'Cabin Rd', 'Tel Aviv', '4'),
('FA003', 'Shira', 'Wolf', '["972-54-1313131"]', TRUE, '2017-05-12', 'Service St', 'Haifa', '6'),
('FA004', 'Yael', 'Berger', '["972-50-1414141"]', TRUE, '2019-01-20', 'Service St', 'Haifa', '8'),
('FA005', 'Tamar', 'Fischer', '["972-52-1515151"]', TRUE, '2019-06-05', 'Cabin Ave', 'Netanya', '3'),
('FA006', 'Liora', 'Schwartz', '["972-54-1616161"]', TRUE, '2016-07-07', 'Cabin Ave', 'Netanya', '5'),
('FA007', 'Dana', 'Weiss', '["972-50-1717171"]', TRUE, '2018-10-10', 'Crew St', 'Beersheba', '11'),
('FA008', 'Ronit', 'Newman', '["972-52-1818181"]', TRUE, '2020-02-02', 'Crew St', 'Beersheba', '13'),
('FA009', 'Michal', 'Gross', '["972-54-1919191"]', TRUE, '2017-08-08', 'Flight Rd', 'Raman', '7'),
('FA010', 'Efrat', 'Blum', '["972-50-2020202"]', TRUE, '2018-11-11', 'Flight Rd', 'Raman', '9'),
('FA011', 'Hila', 'Marcus', '["972-52-2121212"]', TRUE, '2016-12-12', 'Service Ln', 'Hebron', '2'),
('FA012', 'Keren', 'Simon', '["972-54-2222223"]', TRUE, '2019-03-03', 'Service Ln', 'Hebron', '4'),
('FA013', 'Inbar', 'Green', '["972-50-2323232"]', FALSE, '2021-01-01', 'Cabin Ct', 'Ramla', '1'),
('FA014', 'Amit', 'Silver', '["972-52-2424242"]', FALSE, '2021-05-05', 'Cabin Ct', 'Ramla', '3'),
('FA015', 'Sivan', 'Bloom', '["972-54-2525252"]', FALSE, '2022-02-02', 'Crew Blvd', 'Afula', '6'),
('FA016', 'Rotem', 'Fine', '["972-50-2626262"]', FALSE, '2020-09-09', 'Crew Blvd', 'Afula', '8'),
('FA017', 'Gili', 'Hart', '["972-52-2727272"]', FALSE, '2019-07-07', 'Cabin Way', 'Kfar Saba', '12'),
('FA018', 'Lior', 'Stone', '["972-54-2828282"]', FALSE, '2018-06-06', 'Cabin Way', 'Kfar Saba', '14'),
('FA019', 'Adi', 'Glass', '["972-50-2929292"]', FALSE, '2020-10-10', 'Flight Ave', 'Eilat', '9'),
('FA020', 'Chen', 'Gold', '["972-52-3030303"]', FALSE, '2019-09-09', 'Flight Ave', 'Eilat', '11')
AS new_fas (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining, JoinDate, Street, City, HouseNum)
ON DUPLICATE KEY UPDATE
  FirstName = new_fas.FirstName,
  SecondName = new_fas.SecondName,
  PhoneNum = new_fas.PhoneNum,
  LongFlightsTraining = new_fas.LongFlightsTraining,
  JoinDate = new_fas.JoinDate,
  Street = new_fas.Street,
  City = new_fas.City,
  HouseNum = new_fas.HouseNum;

-- -----------------------------------------------------------------------------
-- REGISTERED CUSTOMERS
-- -----------------------------------------------------------------------------
INSERT INTO RegisteredCustomer (UniqueMail, Password, PhoneNum, PassportNum, FirstName, SecondName, BirthDate, RegistrationDate) VALUES
('customer1@example.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', '["972-54-1111111"]', 'P123456', 'John', 'Doe', '1985-06-15', '2020-01-01'),
('customer2@example.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', '["972-54-2222222"]', 'P789012', 'Jane', 'Smith', '1990-09-22', '2021-02-15')
AS new_registered (UniqueMail, Password, PhoneNum, PassportNum, FirstName, SecondName, BirthDate, RegistrationDate)
ON DUPLICATE KEY UPDATE
  Password = new_registered.Password,
  PhoneNum = new_registered.PhoneNum,
  PassportNum = new_registered.PassportNum,
  FirstName = new_registered.FirstName,
  SecondName = new_registered.SecondName,
  BirthDate = new_registered.BirthDate,
  RegistrationDate = new_registered.RegistrationDate;

-- -----------------------------------------------------------------------------
-- GUEST CUSTOMERS
-- -----------------------------------------------------------------------------
INSERT INTO GuestCustomer (UniqueMail, PhoneNum, FirstName, SecondName) VALUES
('guest1@example.com', '["972-50-0000000"]', 'Guest', 'User')
AS new_guest (UniqueMail, PhoneNum, FirstName, SecondName)
ON DUPLICATE KEY UPDATE
  PhoneNum = new_guest.PhoneNum,
  FirstName = new_guest.FirstName,
  SecondName = new_guest.SecondName;

-- -----------------------------------------------------------------------------
-- AIRPLANES (standardized "rows cols" format) with PurchaseDate
-- -----------------------------------------------------------------------------
INSERT INTO Airplanes (AirplaneId, PurchaseDate, Manufacturer, `Couch (Rows, Cols)`, `Business (Rows, Cols)`) VALUES
('BOE-001', '2015-06-01', 'Boeing', '20 6', '5 4'),
('BOE-002', '2016-07-15', 'Boeing', '20 6', '5 4'),
('AIR-003', '2018-09-10', 'Airbus', '25 6', '6 4'),
('AIR-004', '2019-04-20', 'Airbus', '22 6', '5 4'),
('DAS-005', '2014-11-30', 'Dassault', '10 4', NULL),
('DAS-006', '2013-03-22', 'Dassault', '8 4', NULL)
AS new_airplanes (AirplaneId, PurchaseDate, Manufacturer, `Couch (Rows, Cols)`, `Business (Rows, Cols)`)
ON DUPLICATE KEY UPDATE
  PurchaseDate = new_airplanes.PurchaseDate,
  Manufacturer = new_airplanes.Manufacturer,
  `Couch (Rows, Cols)` = new_airplanes.`Couch (Rows, Cols)`,
  `Business (Rows, Cols)` = new_airplanes.`Business (Rows, Cols)`;

-- -----------------------------------------------------------------------------
-- FLIGHTS (updated to use new Airplane IDs)
-- -----------------------------------------------------------------------------
INSERT INTO Flights (FlightId, Airplanes_AirplaneId, OriginPort, DestPort, DepartureDate, DepartureHour, Duration, Status, EconomyPrice, BusinessPrice) VALUES
('FT101', 'BOE-001', 'Tel Aviv', 'New York', '2025-02-15', '08:00:00', 660, 'active', 500.00, 1500.00),
('FT102', 'AIR-003', 'Tel Aviv', 'London', '2025-02-16', '10:00:00', 300, 'active', 300.00, 900.00),
('FT103', 'DAS-005', 'Tel Aviv', 'Paris', '2025-02-17', '14:00:00', 270, 'active', 250.00, NULL),
('FT104', 'BOE-002', 'Tel Aviv', 'Athens', '2025-02-18', '06:00:00', 120, 'active', 150.00, 450.00)
AS new_flights (FlightId, Airplanes_AirplaneId, OriginPort, DestPort, DepartureDate, DepartureHour, Duration, Status, EconomyPrice, BusinessPrice)
ON DUPLICATE KEY UPDATE
  Airplanes_AirplaneId = new_flights.Airplanes_AirplaneId,
  OriginPort = new_flights.OriginPort,
  DestPort = new_flights.DestPort,
  DepartureDate = new_flights.DepartureDate,
  DepartureHour = new_flights.DepartureHour,
  Duration = new_flights.Duration,
  Status = new_flights.Status,
  EconomyPrice = new_flights.EconomyPrice,
  BusinessPrice = new_flights.BusinessPrice;

-- -----------------------------------------------------------------------------
-- CREW ASSIGNMENTS (associations) - skip duplicates with INSERT IGNORE
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Pilot_has_Flights (Pilot_Id, Flights_FlightId, Flights_Airplanes_AirplaneId) VALUES
('P001', 'FT101', 'BOE-001'),
('P002', 'FT101', 'BOE-001'),
('P003', 'FT101', 'BOE-001'),
('P004', 'FT102', 'AIR-003'),
('P005', 'FT102', 'AIR-003'),
('P007', 'FT103', 'DAS-005'),
('P008', 'FT103', 'DAS-005'),
('P009', 'FT104', 'BOE-002'),
('P010', 'FT104', 'BOE-002');

INSERT IGNORE INTO FlightAttendant_has_Flights (FlightAttendant_Id, Flights_FlightId, Flights_Airplanes_AirplaneId) VALUES
('FA001', 'FT101', 'BOE-001'),
('FA002', 'FT101', 'BOE-001'),
('FA003', 'FT101', 'BOE-001'),
('FA004', 'FT101', 'BOE-001'),
('FA005', 'FT101', 'BOE-001'),
('FA006', 'FT101', 'BOE-001'),
('FA007', 'FT102', 'AIR-003'),
('FA008', 'FT102', 'AIR-003'),
('FA009', 'FT102', 'AIR-003'),
('FA010', 'FT102', 'AIR-003'),
('FA013', 'FT103', 'DAS-005'),
('FA014', 'FT103', 'DAS-005'),
('FA015', 'FT103', 'DAS-005'),
('FA016', 'FT104', 'BOE-002'),
('FA017', 'FT104', 'BOE-002'),
('FA018', 'FT104', 'BOE-002'),
('FA019', 'FT104', 'BOE-002');

-- -----------------------------------------------------------------------------
-- ORDERS (idempotent) - updated airplane IDs
-- -----------------------------------------------------------------------------
INSERT INTO orders (UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId, TotalCost, Status, GuestCustomer_UniqueMail, RegisteredCustomer_UniqueMail, Class, CreatedAt) VALUES
('FLY-ABC123', 'FT101', 'BOE-001', 1000.00, 'confirmed', NULL, 'customer1@example.com', 'economy', '2026-01-06 15:06:01'),
('FLY-DEF456', 'FT102', 'AIR-003', 900.00, 'confirmed', NULL, 'customer2@example.com', 'business', '2026-01-06 15:06:01')
AS new_orders (UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId, TotalCost, Status, GuestCustomer_UniqueMail, RegisteredCustomer_UniqueMail, Class, CreatedAt)
ON DUPLICATE KEY UPDATE
  Flights_FlightId = new_orders.Flights_FlightId,
  Flights_Airplanes_AirplaneId = new_orders.Flights_Airplanes_AirplaneId,
  TotalCost = new_orders.TotalCost,
  Status = new_orders.Status,
  GuestCustomer_UniqueMail = new_orders.GuestCustomer_UniqueMail,
  RegisteredCustomer_UniqueMail = new_orders.RegisteredCustomer_UniqueMail,
  Class = new_orders.Class,
  CreatedAt = new_orders.CreatedAt;

-- -----------------------------------------------------------------------------
-- TICKETS (skip duplicates) - updated airplane IDs
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Tickets (orders_UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId, RowNum, Seat, Class, Price) VALUES
('FLY-ABC123', 'FT101', 'BOE-001', 6, 'A', 'economy', 500.00),
('FLY-ABC123', 'FT101', 'BOE-001', 6, 'B', 'economy', 500.00),
('FLY-DEF456', 'FT102', 'AIR-003', 1, 'A', 'business', 900.00);

-- -----------------------------------------------------------------------------
-- MANAGER EDITS (skip duplicates) - updated airplane IDs
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Managers_edits_Flights (Managers_ManagerId, Flights_FlightId, Flights_Airplanes_AirplaneId) VALUES
('M001', 'FT101', 'BOE-001'),
('M001', 'FT102', 'AIR-003'),
('M002', 'FT103', 'DAS-005'),
('M002', 'FT104', 'BOE-002');

-- -----------------------------------------------------------------------------
-- Seed data complete
-- =============================================================================
