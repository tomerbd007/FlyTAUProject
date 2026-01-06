-- =============================================================================
-- LEGACY ORIGINAL SEED REMOVED
-- The original seed archive `sql/01_seed_legacy.sql` has been permanently deleted.
-- Use `sql/01_seed_fixed.sql` to seed the database (idempotent, preferred).
-- =============================================================================

-- Original content archived and removed from this file.

-- =============================================================================
-- MANAGERS (2)
-- Password: password123
-- =============================================================================
INSERT INTO Managers (ManagerId, Password, FirstName, SecondName, PhoneNum) VALUES
('M001', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'David', 'Cohen', '["972-54-1234567"]'),
('M002', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'Sarah', 'Levi', '["972-50-7654321"]')
AS new_managers (ManagerId, Password, FirstName, SecondName, PhoneNum)
ON DUPLICATE KEY UPDATE
	Password = new_managers.Password,
	FirstName = new_managers.FirstName,
	SecondName = new_managers.SecondName,
	PhoneNum = new_managers.PhoneNum;

-- =============================================================================
-- PILOTS (10) - 6 certified for long flights
-- =============================================================================
INSERT INTO Pilot (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining) VALUES
('P001', 'Yossi', 'Mizrahi', '["972-52-1111111"]', TRUE),
('P002', 'Avi', 'Goldberg', '["972-54-2222222"]', TRUE),
('P003', 'Moshe', 'Peretz', '["972-50-3333333"]', TRUE),
('P004', 'Dan', 'Shapiro', '["972-52-4444444"]', TRUE),
('P005', 'Eitan', 'Rosen', '["972-54-5555555"]', TRUE),
('P006', 'Uri', 'Katz', '["972-50-6666666"]', TRUE),
('P007', 'Noam', 'Ben-David', '["972-52-7777777"]', FALSE),
('P008', 'Gal', 'Friedman', '["972-54-8888888"]', FALSE),
('P009', 'Oren', 'Levy', '["972-50-9999999"]', FALSE),
('P010', 'Tal', 'Avraham', '["972-52-1010101"]', FALSE)
AS new_pilots (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining)
ON DUPLICATE KEY UPDATE
	FirstName = new_pilots.FirstName,
	SecondName = new_pilots.SecondName,
	PhoneNum = new_pilots.PhoneNum,
	LongFlightsTraining = new_pilots.LongFlightsTraining;

-- =============================================================================
-- FLIGHT ATTENDANTS (20) - 12 certified for long flights
-- =============================================================================
INSERT INTO FlightAttendant (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining) VALUES
('A001', 'Maya', 'Stern', '["972-50-1111111"]', TRUE),
('A002', 'Noa', 'Klein', '["972-52-1212121"]', TRUE),
('A003', 'Shira', 'Wolf', '["972-54-1313131"]', TRUE),
('A004', 'Yael', 'Berger', '["972-50-1414141"]', TRUE),
('A005', 'Tamar', 'Fischer', '["972-52-1515151"]', TRUE),
('A006', 'Liora', 'Schwartz', '["972-54-1616161"]', TRUE),
('A007', 'Dana', 'Weiss', '["972-50-1717171"]', TRUE),
('A008', 'Ronit', 'Newman', '["972-52-1818181"]', TRUE),
('A009', 'Michal', 'Gross', '["972-54-1919191"]', TRUE),
('A010', 'Efrat', 'Blum', '["972-50-2020202"]', TRUE),
('A011', 'Hila', 'Marcus', '["972-52-2121212"]', TRUE),
('A012', 'Keren', 'Simon', '["972-54-2222223"]', TRUE),
('A013', 'Inbar', 'Green', '["972-50-2323232"]', FALSE),
('A014', 'Amit', 'Silver', '["972-52-2424242"]', FALSE),
('A015', 'Sivan', 'Bloom', '["972-54-2525252"]', FALSE),
('A016', 'Rotem', 'Fine', '["972-50-2626262"]', FALSE),
('A017', 'Gili', 'Hart', '["972-52-2727272"]', FALSE),
('A018', 'Lior', 'Stone', '["972-54-2828282"]', FALSE),
('A019', 'Adi', 'Glass', '["972-50-2929292"]', FALSE),
('A020', 'Chen', 'Gold', '["972-52-3030303"]', FALSE)
AS new_fas (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining)
ON DUPLICATE KEY UPDATE
	FirstName = new_fas.FirstName,
	SecondName = new_fas.SecondName,
	PhoneNum = new_fas.PhoneNum,
	LongFlightsTraining = new_fas.LongFlightsTraining;

-- =============================================================================
-- REGISTERED CUSTOMERS (2)
-- Password: password123
-- =============================================================================
INSERT INTO RegisteredCustomer (UniqueMail, Password, PassportNum, FirstName, SecondName, BirthDate) VALUES
('customer1@example.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'P123456', 'John', 'Doe', '1985-06-15'),
('customer2@example.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'P789012', 'Jane', 'Smith', '1990-09-22')
AS new_registered (UniqueMail, Password, PassportNum, FirstName, SecondName, BirthDate)
ON DUPLICATE KEY UPDATE
	Password = new_registered.Password,
	PassportNum = new_registered.PassportNum,
	FirstName = new_registered.FirstName,
	SecondName = new_registered.SecondName,
	BirthDate = new_registered.BirthDate;

-- =============================================================================
-- GUEST CUSTOMERS (1)
-- =============================================================================
INSERT INTO GuestCustomer (UniqueMail, FirstName, SecondName) VALUES
('guest1@example.com', 'Guest', 'User')
AS new_guest (UniqueMail, FirstName, SecondName)
ON DUPLICATE KEY UPDATE
	FirstName = new_guest.FirstName,
	SecondName = new_guest.SecondName;

-- =============================================================================
-- AIRPLANES (6)
-- =============================================================================
INSERT INTO Airplanes (AirplaneId, Manufacturer, `Couch (Rows, Cols)`, `Business (Rows, Cols)`) VALUES
('A001', 'Boeing', '20 6', '5 4'),
('A002', 'Boeing', '20 6', '5 4'),
('A003', 'Airbus', '25 6', '6 4'),
('A004', 'Airbus', '22 6', '5 4'),
('A005', 'Dassault', '10 4', NULL),
('A006', 'Dassault', '8 4', NULL)
AS new_airplanes (AirplaneId, Manufacturer, `Couch (Rows, Cols)`, `Business (Rows, Cols)`)
ON DUPLICATE KEY UPDATE
	Manufacturer = new_airplanes.Manufacturer,
	`Couch (Rows, Cols)` = new_airplanes.`Couch (Rows, Cols)`,
	`Business (Rows, Cols)` = new_airplanes.`Business (Rows, Cols)`;

-- =============================================================================
-- FLIGHTS (4 active)
-- =============================================================================
INSERT INTO Flights (FlightId, Airplanes_AirplaneId, OriginPort, DestPort, DepartureDate, DepartureHour, Duration, Status, EconomyPrice, BusinessPrice) VALUES
('FT101', 'A001', 'Tel Aviv', 'New York', '2025-02-15', '08:00:00', 660, 'active', 500.00, 1500.00),
('FT102', 'A003', 'Tel Aviv', 'London', '2025-02-16', '10:00:00', 300, 'active', 300.00, 900.00),
('FT103', 'A005', 'Tel Aviv', 'Paris', '2025-02-17', '14:00:00', 270, 'active', 250.00, NULL),
('FT104', 'A002', 'Tel Aviv', 'Athens', '2025-02-18', '06:00:00', 120, 'active', 150.00, 450.00)
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

-- =============================================================================
-- PILOT ASSIGNMENTS
-- =============================================================================
INSERT IGNORE INTO Pilot_has_Flights (Pilot_Id, Flights_FlightId, Flights_Airplanes_AirplaneId) VALUES
('P001', 'FT101', 'A001'),
('P002', 'FT101', 'A001'),
('P003', 'FT101', 'A001'),
('P004', 'FT102', 'A003'),
('P005', 'FT102', 'A003'),
('P007', 'FT103', 'A005'),
('P008', 'FT103', 'A005'),
('P009', 'FT104', 'A002'),
('P010', 'FT104', 'A002');

-- =============================================================================
-- FLIGHT ATTENDANT ASSIGNMENTS
-- =============================================================================
INSERT IGNORE INTO FlightAttendant_has_Flights (FlightAttendant_Id, Flights_FlightId, Flights_Airplanes_AirplaneId) VALUES
('A001', 'FT101', 'A001'),
('A002', 'FT101', 'A001'),
('A003', 'FT101', 'A001'),
('A004', 'FT101', 'A001'),
('A005', 'FT101', 'A001'),
('A006', 'FT101', 'A001'),
('A007', 'FT102', 'A003'),
('A008', 'FT102', 'A003'),
('A009', 'FT102', 'A003'),
('A010', 'FT102', 'A003'),
('A013', 'FT103', 'A005'),
('A014', 'FT103', 'A005'),
('A015', 'FT103', 'A005'),
('A016', 'FT104', 'A002'),
('A017', 'FT104', 'A002'),
('A018', 'FT104', 'A002'),
('A019', 'FT104', 'A002');

-- =============================================================================
-- ORDERS (2 confirmed)
-- =============================================================================
INSERT INTO orders (UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId, TotalCost, Status, GuestCustomer_UniqueMail, RegisteredCustomer_UniqueMail, Class) VALUES
('FLY-ABC123', 'FT101', 'A001', 1000.00, 'confirmed', NULL, 'customer1@example.com', 'economy'),
('FLY-DEF456', 'FT102', 'A003', 900.00, 'confirmed', NULL, 'customer2@example.com', 'business')
AS new_orders (UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId, TotalCost, Status, GuestCustomer_UniqueMail, RegisteredCustomer_UniqueMail, Class)
ON DUPLICATE KEY UPDATE
	Flights_FlightId = new_orders.Flights_FlightId,
	Flights_Airplanes_AirplaneId = new_orders.Flights_Airplanes_AirplaneId,
	TotalCost = new_orders.TotalCost,
	Status = new_orders.Status,
	GuestCustomer_UniqueMail = new_orders.GuestCustomer_UniqueMail,
	RegisteredCustomer_UniqueMail = new_orders.RegisteredCustomer_UniqueMail,
	Class = new_orders.Class;

-- =============================================================================
-- TICKETS
-- =============================================================================
INSERT IGNORE INTO Tickets (orders_UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId, RowNum, Seat, Class, Price) VALUES
('FLY-ABC123', 'FT101', 'A001', 6, 'A', 'economy', 500.00),
('FLY-ABC123', 'FT101', 'A001', 6, 'B', 'economy', 500.00),
('FLY-DEF456', 'FT102', 'A003', 1, 'A', 'business', 900.00);

-- =============================================================================
-- MANAGER EDITS (audit trail)
-- =============================================================================
INSERT IGNORE INTO Managers_edits_Flights (Managers_ManagerId, Flights_FlightId, Flights_Airplanes_AirplaneId) VALUES
('M001', 'FT101', 'A001'),
('M001', 'FT102', 'A003'),
('M002', 'FT103', 'A005'),
('M002', 'FT104', 'A002');

-- =============================================================================
-- Seed data complete
-- =============================================================================
