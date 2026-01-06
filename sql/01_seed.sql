-- =============================================================================
-- FLYTAU Seed Data
-- Initial data for testing and development
-- Password for all accounts: 'password123' (bcrypt hash)
-- =============================================================================

USE flytau;

-- =============================================================================
-- AIRPORTS (Global)
-- =============================================================================
INSERT INTO Airports (Code, Name, City, Country) VALUES
-- Middle East
('TLV', 'Ben Gurion International Airport', 'Tel Aviv', 'Israel'),
('DXB', 'Dubai International Airport', 'Dubai', 'UAE'),
('AUH', 'Abu Dhabi International Airport', 'Abu Dhabi', 'UAE'),
('DOH', 'Hamad International Airport', 'Doha', 'Qatar'),
('RUH', 'King Khalid International Airport', 'Riyadh', 'Saudi Arabia'),
('JED', 'King Abdulaziz International Airport', 'Jeddah', 'Saudi Arabia'),
('AMM', 'Queen Alia International Airport', 'Amman', 'Jordan'),
('CAI', 'Cairo International Airport', 'Cairo', 'Egypt'),
('IST', 'Istanbul Airport', 'Istanbul', 'Turkey'),
('BEY', 'Beirut–Rafic Hariri International Airport', 'Beirut', 'Lebanon'),
('BAH', 'Bahrain International Airport', 'Manama', 'Bahrain'),
('KWI', 'Kuwait International Airport', 'Kuwait City', 'Kuwait'),
('MCT', 'Muscat International Airport', 'Muscat', 'Oman'),
-- Europe
('LHR', 'Heathrow Airport', 'London', 'United Kingdom'),
('CDG', 'Charles de Gaulle Airport', 'Paris', 'France'),
('FRA', 'Frankfurt Airport', 'Frankfurt', 'Germany'),
('AMS', 'Amsterdam Schiphol Airport', 'Amsterdam', 'Netherlands'),
('FCO', 'Leonardo da Vinci International Airport', 'Rome', 'Italy'),
('MAD', 'Adolfo Suárez Madrid–Barajas Airport', 'Madrid', 'Spain'),
('BCN', 'Barcelona–El Prat Airport', 'Barcelona', 'Spain'),
('ATH', 'Athens International Airport', 'Athens', 'Greece'),
('VIE', 'Vienna International Airport', 'Vienna', 'Austria'),
('ZRH', 'Zurich Airport', 'Zurich', 'Switzerland'),
('MUC', 'Munich Airport', 'Munich', 'Germany'),
('CPH', 'Copenhagen Airport', 'Copenhagen', 'Denmark'),
('PRG', 'Václav Havel Airport Prague', 'Prague', 'Czech Republic'),
-- Americas
('JFK', 'John F. Kennedy International Airport', 'New York', 'USA'),
('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA'),
('MIA', 'Miami International Airport', 'Miami', 'USA'),
('ORD', 'O''Hare International Airport', 'Chicago', 'USA'),
('SFO', 'San Francisco International Airport', 'San Francisco', 'USA'),
('YYZ', 'Toronto Pearson International Airport', 'Toronto', 'Canada'),
('GRU', 'São Paulo/Guarulhos International Airport', 'São Paulo', 'Brazil'),
('MEX', 'Mexico City International Airport', 'Mexico City', 'Mexico'),
-- Asia Pacific
('HND', 'Haneda Airport', 'Tokyo', 'Japan'),
('NRT', 'Narita International Airport', 'Tokyo', 'Japan'),
('SIN', 'Singapore Changi Airport', 'Singapore', 'Singapore'),
('HKG', 'Hong Kong International Airport', 'Hong Kong', 'China'),
('PEK', 'Beijing Capital International Airport', 'Beijing', 'China'),
('PVG', 'Shanghai Pudong International Airport', 'Shanghai', 'China'),
('ICN', 'Incheon International Airport', 'Seoul', 'South Korea'),
('BKK', 'Suvarnabhumi Airport', 'Bangkok', 'Thailand'),
('DEL', 'Indira Gandhi International Airport', 'New Delhi', 'India'),
('BOM', 'Chhatrapati Shivaji International Airport', 'Mumbai', 'India'),
('SYD', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia'),
('MEL', 'Melbourne Airport', 'Melbourne', 'Australia'),
-- Africa
('JNB', 'O.R. Tambo International Airport', 'Johannesburg', 'South Africa'),
('CPT', 'Cape Town International Airport', 'Cape Town', 'South Africa'),
('ADD', 'Addis Ababa Bole International Airport', 'Addis Ababa', 'Ethiopia'),
('NBO', 'Jomo Kenyatta International Airport', 'Nairobi', 'Kenya');

-- =============================================================================
-- MANAGERS (2)
-- Password: password123
-- =============================================================================
INSERT INTO Managers (ManagerId, Password, FirstName, SecondName, PhoneNum) VALUES
('M001', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'David', 'Cohen', '["972-54-1234567"]'),
('M002', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'Sarah', 'Levi', '["972-50-7654321"]');

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
('P010', 'Tal', 'Avraham', '["972-52-1010101"]', FALSE);

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
('A020', 'Chen', 'Gold', '["972-52-3030303"]', FALSE);

-- =============================================================================
-- REGISTERED CUSTOMERS (2)
-- Password: password123
-- =============================================================================
INSERT INTO RegisteredCustomer (UniqueMail, Password, PassportNum, FirstName, SecondName, BirthDate) VALUES
('customer1@example.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'P123456', 'John', 'Doe', '1985-06-15'),
('customer2@example.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'P789012', 'Jane', 'Smith', '1990-09-22');

-- =============================================================================
-- GUEST CUSTOMERS (1)
-- =============================================================================
INSERT INTO GuestCustomer (UniqueMail, FirstName, SecondName) VALUES
('guest1@example.com', 'Guest', 'User');

-- =============================================================================
-- AIRPLANES (6)
-- =============================================================================
INSERT INTO Airplanes (AirplaneId, Manufacturer, `Couch (Rows, Cols)`, `Business (Rows, Cols)`) VALUES
('A001', 'Boeing', '20 6', '5 4'),
('A002', 'Boeing', '20 6', '5 4'),
('A003', 'Airbus', '25 6', '6 4'),
('A004', 'Airbus', '22 6', '5 4'),
('A005', 'Dassault', '10 4', NULL),
('A006', 'Dassault', '8 4', NULL);

-- =============================================================================
-- FLIGHTS (4 active)
-- =============================================================================
INSERT INTO Flights (FlightId, Airplanes_AirplaneId, OriginPort, DestPort, DepartureDate, DepartureHour, Duration, Status, EconomyPrice, BusinessPrice) VALUES
('FT101', 'A001', 'TLV', 'JFK', '2025-02-15', '08:00:00', 660, 'active', 500.00, 1500.00),
('FT102', 'A003', 'TLV', 'LHR', '2025-02-16', '10:00:00', 300, 'active', 300.00, 900.00),
('FT103', 'A005', 'TLV', 'CDG', '2025-02-17', '14:00:00', 270, 'active', 250.00, NULL),
('FT104', 'A002', 'TLV', 'ATH', '2025-02-18', '06:00:00', 120, 'active', 150.00, 450.00);

-- =============================================================================
-- PILOT ASSIGNMENTS
-- =============================================================================
INSERT INTO Pilot_has_Flights (Pilot_Id, Flights_FlightId, Flights_Airplanes_AirplaneId) VALUES
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
INSERT INTO FlightAttendant_has_Flights (FlightAttendant_Id, Flights_FlightId, Flights_Airplanes_AirplaneId) VALUES
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
('FLY-DEF456', 'FT102', 'A003', 900.00, 'confirmed', NULL, 'customer2@example.com', 'business');

-- =============================================================================
-- TICKETS
-- =============================================================================
INSERT INTO Tickets (orders_UniqueOrderCode, Flights_FlightId, Flights_Airplanes_AirplaneId, RowNum, Seat, Class, Price) VALUES
('FLY-ABC123', 'FT101', 'A001', 6, 'A', 'economy', 500.00),
('FLY-ABC123', 'FT101', 'A001', 6, 'B', 'economy', 500.00),
('FLY-DEF456', 'FT102', 'A003', 1, 'A', 'business', 900.00);

-- =============================================================================
-- MANAGER EDITS (audit trail)
-- =============================================================================
INSERT INTO Managers_edits_Flights (Managers_ManagerId, Flights_FlightId, Flights_Airplanes_AirplaneId) VALUES
('M001', 'FT101', 'A001'),
('M001', 'FT102', 'A003'),
('M002', 'FT103', 'A005'),
('M002', 'FT104', 'A002');

-- =============================================================================
-- Seed data complete
-- =============================================================================
