-- =============================================================================
-- FLYTAU Fixed Seed Data (FULL REVISED VERSION)
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
-- FLIGHT ATTENDANTS
-- -----------------------------------------------------------------------------
INSERT INTO FlightAttendant (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining, JoinDate, Street, City, HouseNum) VALUES
('A001', 'Maya', 'Stern', '["972-50-1111111"]', TRUE, '2017-03-01', 'Cabin Rd', 'Tel Aviv', '2'),
('A002', 'Noa', 'Klein', '["972-52-1212121"]', TRUE, '2018-04-10', 'Cabin Rd', 'Tel Aviv', '4'),
('A003', 'Shira', 'Wolf', '["972-54-1313131"]', TRUE, '2017-05-12', 'Service St', 'Haifa', '6'),
('A004', 'Yael', 'Berger', '["972-50-1414141"]', TRUE, '2019-01-20', 'Service St', 'Haifa', '8'),
('A005', 'Tamar', 'Fischer', '["972-52-1515151"]', TRUE, '2019-06-05', 'Cabin Ave', 'Netanya', '3'),
('A006', 'Liora', 'Schwartz', '["972-54-1616161"]', TRUE, '2016-07-07', 'Cabin Ave', 'Netanya', '5'),
('A007', 'Dana', 'Weiss', '["972-50-1717171"]', TRUE, '2018-10-10', 'Crew St', 'Beersheba', '11'),
('A008', 'Ronit', 'Newman', '["972-52-1818181"]', TRUE, '2020-02-02', 'Crew St', 'Beersheba', '13'),
('A009', 'Michal', 'Gross', '["972-54-1919191"]', TRUE, '2017-08-08', 'Flight Rd', 'Raman', '7'),
('A010', 'Efrat', 'Blum', '["972-50-2020202"]', TRUE, '2018-11-11', 'Flight Rd', 'Raman', '9'),
('A011', 'Hila', 'Marcus', '["972-52-2121212"]', TRUE, '2016-12-12', 'Service Ln', 'Hebron', '2'),
('A012', 'Keren', 'Simon', '["972-54-2222223"]', TRUE, '2019-03-03', 'Service Ln', 'Hebron', '4'),
('A013', 'Inbar', 'Green', '["972-50-2323232"]', FALSE, '2021-01-01', 'Cabin Ct', 'Ramla', '1'),
('A014', 'Amit', 'Silver', '["972-52-2424242"]', FALSE, '2021-05-05', 'Cabin Ct', 'Ramla', '3'),
('A015', 'Sivan', 'Bloom', '["972-54-2525252"]', FALSE, '2022-02-02', 'Crew Blvd', 'Afula', '6'),
('A016', 'Rotem', 'Fine', '["972-50-2626262"]', FALSE, '2020-09-09', 'Crew Blvd', 'Afula', '8'),
('A017', 'Gili', 'Hart', '["972-52-2727272"]', FALSE, '2019-07-07', 'Cabin Way', 'Kfar Saba', '12'),
('A018', 'Lior', 'Stone', '["972-54-2828282"]', FALSE, '2018-06-06', 'Cabin Way', 'Kfar Saba', '14'),
('A019', 'Adi', 'Glass', '["972-50-2929292"]', FALSE, '2020-10-10', 'Flight Ave', 'Eilat', '9'),
('A020', 'Chen', 'Gold', '["972-52-3030303"]', FALSE, '2019-09-09', 'Flight Ave', 'Eilat', '11')
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
-- AIRPLANES (Corrected Column Names)
-- -----------------------------------------------------------------------------
INSERT INTO Airplanes (AirplaneId, Manufacturer, CouchRows, CouchCols, BusinessRows, BusinessCols) VALUES
('PLANE-001', 'Boeing', 18, 7, 6, 4),
('PLANE-002', 'Boeing', 8, 4, 0, 0),
('PLANE-003', 'Airbus', 20, 7, 6, 4),
('PLANE-004', 'Airbus', 9, 4, 0, 0),
('PLANE-005', 'Dassault', 18, 7, 6, 4),
('PLANE-006', 'Dassault', 22, 4, 0, 0)
AS new_air
ON DUPLICATE KEY UPDATE
  Manufacturer = new_air.Manufacturer,
  CouchRows = new_air.CouchRows,
  CouchCols = new_air.CouchCols,
  BusinessRows = new_air.BusinessRows,
  BusinessCols = new_air.BusinessCols;

-- -----------------------------------------------------------------------------
-- FLIGHTS
-- -----------------------------------------------------------------------------
INSERT INTO Flights (FlightId, Airplanes_AirplaneId, OriginPort, DestPort, DepartureDate, DepartureHour, Duration, Status, EconomyPrice, BusinessPrice) VALUES
('FT101', 'PLANE-001', 'TLV', 'JFK', '2025-11-15', '08:00:00', 660, 'active', 500.00, 1500.00),
('FT102', 'PLANE-003', 'JFK', 'LCA', '2025-11-20', '06:30:00', 600, 'active', 400.00, 1200.00),
('FT103', 'PLANE-002', 'LCA', 'TLV', '2025-11-29', '22:00:00', 40, 'cancelled', 120.00, 700.00),
('FT104', 'PLANE-004', 'TLV', 'RUH', '2026-01-21', '20:00:00', 160, 'active', 150.00, 800.00)
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
-- CREW ASSIGNMENTS (associations)
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Pilot_has_Flights (Pilot_Id, Flights_FlightId) VALUES
('P001', 'FT101'), ('P002', 'FT101'), ('P003', 'FT101'),
('P001', 'FT102'), ('P002', 'FT102'), ('P003', 'FT102'),
('P001', 'FT103'), ('P002', 'FT103'), ('P003', 'FT104');

INSERT IGNORE INTO FlightAttendant_has_Flights (FlightAttendant_Id, Flights_FlightId) VALUES
('A001', 'FT101'), ('A002', 'FT101'), ('A003', 'FT101'), ('A004', 'FT101'), ('A005', 'FT101'), ('A006', 'FT101'),
('A001', 'FT102'), ('A002', 'FT102'), ('A003', 'FT102'), ('A004', 'FT102'), ('A005', 'FT102'), ('A006', 'FT102'),
('A001', 'FT103'), ('A002', 'FT103'), ('A003', 'FT103'),
('A004', 'FT104'), ('A005', 'FT104'), ('A006', 'FT104');

-- -----------------------------------------------------------------------------
-- ORDERS
-- -----------------------------------------------------------------------------
INSERT INTO orders (UniqueOrderCode, Flights_FlightId, TotalCost, Status, GuestCustomer_UniqueMail, RegisteredCustomer_UniqueMail) VALUES
('FLY-ABC123', 'FT101', 1000.00, 'confirmed', NULL, 'customer1@gmail.com'),
('FLY-DEF456', 'FT102', 1200.00, 'confirmed', NULL, 'customer2@gmail.com'),
('FLY-DEF768', 'FT102', 400.00, 'confirmed', 'guest1@gmail.com', NULL),
('FLY-ABC001', 'FT104', 300.00, 'cancelled', NULL, 'customer1@gmail.com'),
('FLY-ABC002', 'FT104', 150.00, 'confirmed', NULL, 'customer2@gmail.com'),
('FLY-DEF003', 'FT104', 150.00, 'cancelled', NULL, 'customer1@gmail.com')
AS new_o
ON DUPLICATE KEY UPDATE
  Flights_FlightId = new_o.Flights_FlightId,
  TotalCost = new_o.TotalCost,
  Status = new_o.Status;

-- -----------------------------------------------------------------------------
-- TICKETS
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Tickets (orders_UniqueOrderCode, RowNum, Seat, Class) VALUES
('FLY-ABC123', 7, 'A', 'economy'),
('FLY-ABC123', 7, 'B', 'economy'),
('FLY-DEF456', 1, 'A', 'business'),
('FLY-DEF768', 24, 'A', 'economy'),
('FLY-ABC001', 5, 'A', 'economy'),
('FLY-ABC001', 5, 'B', 'economy'),
('FLY-ABC002', 8, 'A', 'economy'),
('FLY-DEF003', 4, 'C', 'economy');

-- -----------------------------------------------------------------------------
-- MANAGER EDITS
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Managers_edits_Flights (Managers_ManagerId, Flights_FlightId) VALUES
('M001', 'FT101'), ('M001', 'FT102'), ('M002', 'FT103'), ('M002', 'FT104');

-- Seed Complete