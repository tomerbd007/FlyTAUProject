-- =============================================================================
-- FLYTAU Fixed Seed Data (idempotent)
-- Use: mysql -u root -p flytau < sql/01_seed_fixed.sql
-- This seed is safe to re-run: main tables use INSERT ... AS alias ... ON DUPLICATE KEY UPDATE
-- Association tables use INSERT IGNORE to skip duplicate link rows.
-- =============================================================================

USE flytau;

-- =============================================================================
-- AIRPORTS (Global) - with coordinates for distance calculations
-- =============================================================================
INSERT INTO Airports (Code, Name, City, Country, Latitude, Longitude) VALUES
-- Middle East
('TLV', 'Ben Gurion International Airport', 'Tel Aviv', 'Israel', 32.0114, 34.8855),
('DXB', 'Dubai International Airport', 'Dubai', 'UAE', 25.2532, 55.3657),
('AUH', 'Abu Dhabi International Airport', 'Abu Dhabi', 'UAE', 24.4330, 54.6511),
('DOH', 'Hamad International Airport', 'Doha', 'Qatar', 25.2731, 51.6081),
('RUH', 'King Khalid International Airport', 'Riyadh', 'Saudi Arabia', 24.9578, 46.6989),
('JED', 'King Abdulaziz International Airport', 'Jeddah', 'Saudi Arabia', 21.6796, 39.1566),
('AMM', 'Queen Alia International Airport', 'Amman', 'Jordan', 31.7226, 35.9932),
('CAI', 'Cairo International Airport', 'Cairo', 'Egypt', 30.1219, 31.4056),
('IST', 'Istanbul Airport', 'Istanbul', 'Turkey', 41.2753, 28.7519),
('BEY', 'Beirut–Rafic Hariri International Airport', 'Beirut', 'Lebanon', 33.8209, 35.4884),
('BAH', 'Bahrain International Airport', 'Manama', 'Bahrain', 26.2708, 50.6336),
('KWI', 'Kuwait International Airport', 'Kuwait City', 'Kuwait', 29.2266, 47.9689),
('MCT', 'Muscat International Airport', 'Muscat', 'Oman', 23.5933, 58.2844),
-- Europe
('LHR', 'Heathrow Airport', 'London', 'United Kingdom', 51.4700, -0.4543),
('CDG', 'Charles de Gaulle Airport', 'Paris', 'France', 49.0097, 2.5479),
('FRA', 'Frankfurt Airport', 'Frankfurt', 'Germany', 50.0379, 8.5622),
('AMS', 'Amsterdam Schiphol Airport', 'Amsterdam', 'Netherlands', 52.3105, 4.7683),
('FCO', 'Leonardo da Vinci International Airport', 'Rome', 'Italy', 41.8003, 12.2389),
('MAD', 'Adolfo Suárez Madrid–Barajas Airport', 'Madrid', 'Spain', 40.4983, -3.5676),
('BCN', 'Barcelona–El Prat Airport', 'Barcelona', 'Spain', 41.2974, 2.0833),
('ATH', 'Athens International Airport', 'Athens', 'Greece', 37.9364, 23.9445),
('VIE', 'Vienna International Airport', 'Vienna', 'Austria', 48.1103, 16.5697),
('ZRH', 'Zurich Airport', 'Zurich', 'Switzerland', 47.4582, 8.5555),
('MUC', 'Munich Airport', 'Munich', 'Germany', 48.3537, 11.7750),
('CPH', 'Copenhagen Airport', 'Copenhagen', 'Denmark', 55.6180, 12.6508),
('PRG', 'Václav Havel Airport Prague', 'Prague', 'Czech Republic', 50.1008, 14.2600),
-- Americas
('JFK', 'John F. Kennedy International Airport', 'New York', 'USA', 40.6413, -73.7781),
('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA', 33.9416, -118.4085),
('MIA', 'Miami International Airport', 'Miami', 'USA', 25.7959, -80.2870),
('ORD', 'O''Hare International Airport', 'Chicago', 'USA', 41.9742, -87.9073),
('SFO', 'San Francisco International Airport', 'San Francisco', 'USA', 37.6213, -122.3790),
('YYZ', 'Toronto Pearson International Airport', 'Toronto', 'Canada', 43.6777, -79.6248),
('GRU', 'São Paulo/Guarulhos International Airport', 'São Paulo', 'Brazil', -23.4356, -46.4731),
('MEX', 'Mexico City International Airport', 'Mexico City', 'Mexico', 19.4361, -99.0719),
-- Asia Pacific
('HND', 'Haneda Airport', 'Tokyo', 'Japan', 35.5494, 139.7798),
('NRT', 'Narita International Airport', 'Tokyo', 'Japan', 35.7720, 140.3929),
('SIN', 'Singapore Changi Airport', 'Singapore', 'Singapore', 1.3644, 103.9915),
('HKG', 'Hong Kong International Airport', 'Hong Kong', 'China', 22.3080, 113.9185),
('PEK', 'Beijing Capital International Airport', 'Beijing', 'China', 40.0799, 116.6031),
('PVG', 'Shanghai Pudong International Airport', 'Shanghai', 'China', 31.1443, 121.8083),
('ICN', 'Incheon International Airport', 'Seoul', 'South Korea', 37.4602, 126.4407),
('BKK', 'Suvarnabhumi Airport', 'Bangkok', 'Thailand', 13.6900, 100.7501),
('DEL', 'Indira Gandhi International Airport', 'New Delhi', 'India', 28.5562, 77.1000),
('BOM', 'Chhatrapati Shivaji International Airport', 'Mumbai', 'India', 19.0896, 72.8656),
('SYD', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia', -33.9399, 151.1753),
('MEL', 'Melbourne Airport', 'Melbourne', 'Australia', -37.6690, 144.8410),
-- Africa
('JNB', 'O.R. Tambo International Airport', 'Johannesburg', 'South Africa', -26.1367, 28.2411),
('CPT', 'Cape Town International Airport', 'Cape Town', 'South Africa', -33.9715, 18.6021),
('ADD', 'Addis Ababa Bole International Airport', 'Addis Ababa', 'Ethiopia', 8.9779, 38.7993),
('NBO', 'Jomo Kenyatta International Airport', 'Nairobi', 'Kenya', -1.3192, 36.9278);

-- =============================================================================
-- MANAGERS (2)
-- Password: password123
-- =============================================================================
INSERT INTO Managers (ManagerId, Password, FirstName, SecondName, PhoneNum) VALUES
('M001', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'David', 'Cohen', '["972-54-1234567"]'),
('M002', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'Sarah', 'Levi', '["972-50-7654321"]');

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
('customer1@gmail.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', '["972-54-1111111"]', 'P123456', 'John', 'Doe', '1985-06-15', '2020-01-01'),
('customer2@gmail.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', '["972-54-2222222"]', 'P789012', 'Jane', 'Smith', '1990-09-22', '2021-02-15')
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
('guest1@gmail.com', '["972-50-0000000"]', 'Guest', 'User')
AS new_guest (UniqueMail, PhoneNum, FirstName, SecondName)
ON DUPLICATE KEY UPDATE
  PhoneNum = new_guest.PhoneNum,
  FirstName = new_guest.FirstName,
  SecondName = new_guest.SecondName;

-- -----------------------------------------------------------------------------
-- AIRPLANES (standardized "rows cols" format)
-- -----------------------------------------------------------------------------
INSERT INTO Airplanes (AirplaneId, Manufacturer, `Couch (Rows, Cols)`, `Business (Rows, Cols)`) VALUES
('PLANE-001', 'Boeing', '20 6', '5 4'),
('PLANE-002', 'Boeing', '20 6', '5 4'),
('PLANE-003', 'Airbus', '25 6', '6 4'),
('PLANE-004', 'Airbus', '22 6', '5 4'),
('PLANE-005', 'Dassault', '10 4', NULL),
('PLANE-006', 'Dassault', '8 4', NULL)
AS new_airplanes (AirplaneId, Manufacturer, `Couch (Rows, Cols)`, `Business (Rows, Cols)`)
ON DUPLICATE KEY UPDATE
  Manufacturer = new_airplanes.Manufacturer,
  `Couch (Rows, Cols)` = new_airplanes.`Couch (Rows, Cols)`,
  `Business (Rows, Cols)` = new_airplanes.`Business (Rows, Cols)`;

-- -----------------------------------------------------------------------------
-- FLIGHTS
-- -----------------------------------------------------------------------------
INSERT INTO Flights (FlightId, Airplanes_AirplaneId, OriginPort, DestPort, DepartureDate, DepartureHour, Duration, Status, EconomyPrice, BusinessPrice) VALUES
('FT101', 'A001', 'TLV', 'JFK', '2026-02-15', '08:00:00', 660, 'active', 500.00, 1500.00),
('FT102', 'A003', 'TLV', 'LHR', '2026-02-16', '10:00:00', 300, 'active', 300.00, 900.00),
('FT103', 'A005', 'TLV', 'CDG', '2026-02-17', '14:00:00', 270, 'active', 250.00, NULL),
('FT104', 'A002', 'TLV', 'ATH', '2026-02-18', '06:00:00', 120, 'active', 150.00, 450.00);

-- =============================================================================
-- ADDITIONAL FUTURE FLIGHTS (mixed statuses)
-- =============================================================================
INSERT INTO Flights (FlightId, Airplanes_AirplaneId, OriginPort, DestPort, DepartureDate, DepartureHour, Duration, Status, EconomyPrice, BusinessPrice) VALUES
('FT201', 'A001', 'TLV', 'JFK', '2026-02-05', '08:45:00', 640, 'active',   520.00, 1550.00),
('FT202', 'A003', 'TLV', 'LHR', '2026-02-06', '10:15:00', 305, 'active',   310.00,  910.00),
('FT203', 'A002', 'TLV', 'ATH', '2026-02-07', '06:20:00', 125, 'active',   155.00,  460.00),
('FT204', 'A004', 'TLV', 'CDG', '2026-02-08', '13:40:00', 280, 'active',   265.00,  820.00),
('FT205', 'A003', 'TLV', 'AMS', '2026-02-09', '09:05:00', 290, 'active',   275.00,  840.00),
('FT206', 'A005', 'TLV', 'BCN', '2026-03-01', '11:10:00', 285, 'inactive', 240.00,   NULL),
('FT207', 'A006', 'TLV', 'FRA', '2026-03-02', '15:25:00', 255, 'inactive', 260.00,   NULL),
('FT208', 'A001', 'TLV', 'IST', '2026-03-03', '07:55:00', 150, 'inactive', 170.00,  520.00),
('FT209', 'A004', 'TLV', 'VIE', '2026-03-04', '12:35:00', 225, 'inactive', 230.00,  690.00),
('FT210', 'A002', 'TLV', 'CAI', '2026-03-05', '18:10:00',  95, 'inactive', 140.00,  420.00);

-- =============================================================================
-- PILOT ASSIGNMENTS
-- =============================================================================
INSERT INTO Pilot_has_Flights (Pilot_Id, Flights_FlightId) VALUES
('P001', 'FT101'),
('P002', 'FT101'),
('P003', 'FT101'),
('P004', 'FT102'),
('P005', 'FT102'),
('P007', 'FT103'),
('P008', 'FT103'),
('P009', 'FT104'),
('P010', 'FT104');

-- =============================================================================
-- FLIGHT ATTENDANT ASSIGNMENTS
-- =============================================================================
INSERT INTO FlightAttendant_has_Flights (FlightAttendant_Id, Flights_FlightId) VALUES
('A001', 'FT101'),
('A002', 'FT101'),
('A003', 'FT101'),
('A004', 'FT101'),
('A005', 'FT101'),
('A006', 'FT101'),
('A007', 'FT102'),
('A008', 'FT102'),
('A009', 'FT102'),
('A010', 'FT102'),
('A013', 'FT103'),
('A014', 'FT103'),
('A015', 'FT103'),
('A016', 'FT104'),
('A017', 'FT104'),
('A018', 'FT104'),
('A019', 'FT104');

-- =============================================================================
-- ORDERS (2 confirmed)
-- =============================================================================
INSERT INTO orders (UniqueOrderCode, Flights_FlightId, TotalCost, Status, GuestCustomer_UniqueMail, RegisteredCustomer_UniqueMail) VALUES
('FLY-ABC123', 'FT101', 1000.00, 'confirmed', NULL, 'customer1@example.com'),
('FLY-DEF456', 'FT102', 900.00, 'confirmed', NULL, 'customer2@example.com');

-- =============================================================================
-- TICKETS
-- =============================================================================
INSERT INTO Tickets (orders_UniqueOrderCode, RowNum, Seat, Class) VALUES
('FLY-ABC123', 6, 'A', 'economy'),
('FLY-ABC123', 6, 'B', 'economy'),
('FLY-DEF456', 1, 'A', 'business');

-- =============================================================================
-- MANAGER EDITS (audit trail)
-- =============================================================================
INSERT INTO Managers_edits_Flights (Managers_ManagerId, Flights_FlightId) VALUES
('M001', 'FT101'),
('M001', 'FT102'),
('M002', 'FT103'),
('M002', 'FT104');

-- =============================================================================
-- ROUTES - All airport combinations with calculated durations
-- Generated automatically using Haversine formula
-- Duration = (distance_km / 850 km/h) * 60 + 45 min overhead
-- Total: 2450 routes (50 airports × 49 destinations)
-- =============================================================================
-- Routes are loaded from routes_seed.sql via SOURCE command or can be
-- concatenated during database initialization

-- -----------------------------------------------------------------------------
-- TICKETS (skip duplicates)
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Tickets (orders_UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId, RowNum, Seat, Class, Price) VALUES
('FLY-ABC123', 'FT101', 'PLANE-001', 6, 'A', 'economy', 500.00),
('FLY-ABC123', 'FT101', 'PLANE-001', 6, 'B', 'economy', 500.00),
('FLY-DEF456', 'FT102', 'PLANE-003', 1, 'A', 'business', 900.00),
('FLY-DEF768', 'FT102', 'PLANE-003', 24, 'A', 'economy', 900.00),
('FLY-ABC001', 'FT104', 'PLANE-002', 10, 'A', 'economy', 500.00),
('FLY-ABC002', 'FT104', 'PLANE-002', 10, 'B', 'economy', 500.00),
('FLY-DEF003', 'FT104', 'PLANE-002', 4, 'C', 'business', 900.00);

-- -----------------------------------------------------------------------------
-- MANAGER EDITS (skip duplicates)
-- -----------------------------------------------------------------------------
INSERT IGNORE INTO Managers_edits_Flights (Managers_ManagerId, Flights_FlightId, Flights_Airplanes_AirplaneId) VALUES
('M001', 'FT101', 'PLANE-001'),
('M001', 'FT102', 'PLANE-003'),
('M002', 'FT103', 'PLANE-005'),
('M002', 'FT104', 'PLANE-002');

-- -----------------------------------------------------------------------------
-- Seed data complete
-- =============================================================================