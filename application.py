#!/usr/bin/env python3
"""
FLYTAU Application Entry Point for AWS Elastic Beanstalk

This file is named 'application.py' and the Flask instance is named 'application'
to match AWS Elastic Beanstalk's default WSGI expectations.

Run locally with:
    python application.py

Or for production with gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5001 "application:application"
"""

import os
from datetime import timedelta
from flask import Flask
from flask_session import Session

from app.config import Config
from app import db
from app.routes import register_routes
from app import register_error_handlers


# ---------------------------------------------------------------------------
# Flask-Session filesystem directory setup
# ---------------------------------------------------------------------------
session_dir = os.path.join(os.getcwd(), "flask_session_data")
if not os.path.exists(session_dir):
    os.makedirs(session_dir)


# ---------------------------------------------------------------------------
# Create and configure the Flask application
# ---------------------------------------------------------------------------
application = Flask(__name__, 
                    template_folder='app/templates',
                    static_folder='app/static')
application.config.from_object(Config)

# Flask-Session filesystem backend configuration
application.config.update(
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR=session_dir,
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_REFRESH_EACH_REQUEST=True,
    SESSION_COOKIE_SECURE=False  # Set to True if using HTTPS
)

# Initialize Flask-Session
Session(application)

# Initialize database connection pool
db.init_app(application)

# Register all routes
register_routes(application)

# Register error handlers
register_error_handlers(application)


# ---------------------------------------------------------------------------
# TEMPORARY: Database setup route for AWS EB deployment
# Remove or disable this route after initial database setup!
# ---------------------------------------------------------------------------
@application.route("/setup_db")
def setup_db():
    """
    Initialize database tables from SQL schema file.
    
    WARNING: This is a TEMPORARY route for initial deployment.
    Remove or protect this route after database setup is complete!
    
    Usage: Visit https://<your-domain>/setup_db after deployment
    """
    try:
        # Try multiple possible schema file locations
        schema_files = [
            "flytau_schema.sql",  # Project root (preferred for EB)
            "sql/00_schema.sql",  # Original location
        ]
        
        sql_script = None
        used_file = None
        
        for schema_file in schema_files:
            if os.path.exists(schema_file):
                with open(schema_file, "r") as f:
                    sql_script = f.read()
                used_file = schema_file
                break
        
        if sql_script is None:
            return "Error: No schema file found. Checked: " + ", ".join(schema_files), 404
        
        # Execute the SQL script
        conn = db.get_db()
        cursor = conn.cursor()
        
        try:
            # Execute multi-statement SQL
            for result in cursor.execute(sql_script, multi=True):
                pass  # Consume all results
            conn.commit()
        finally:
            cursor.close()
        
        return f"Success! Tables created from {used_file}."
    except Exception as e:
        return f"Error running SQL file: {str(e)}", 500


@application.route("/reset_db")
def reset_db():
    """
    Truncate all data tables (keeps schema and routes intact).
    Visit this BEFORE /setup_db_seed to start fresh.
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor()
        
        # Disable FK checks, truncate in dependency order, re-enable
        truncate_sql = """
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
        """
        
        for result in cursor.execute(truncate_sql, multi=True):
            pass
        
        cursor.close()
        return "Success! All data tables truncated. Now visit /setup_db_seed to reload data."
    except Exception as e:
        import traceback
        return f"Error: {str(e)}<br><pre>{traceback.format_exc()}</pre>", 500


@application.route("/setup_db_seed")
def setup_db_seed():
    """
    Load seed data into the database using direct Python INSERT statements.
    This avoids file I/O and SQL script parsing for faster execution.
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor()
        
        # Disable FK checks, truncate tables, re-enable
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for tbl in ['Managers_edits_Flights', 'FlightAttendant_has_Flights', 'Pilot_has_Flights', 
                    'Tickets', 'orders', 'Flights', 'Airplanes', 'Pilot', 'FlightAttendant',
                    'RegisteredCustomer', 'GuestCustomer', 'Managers']:
            cursor.execute(f"TRUNCATE TABLE {tbl}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        
        # -- MANAGERS --
        cursor.execute("""INSERT INTO Managers (ManagerId, Password, FirstName, SecondName, PhoneNum, JoinDate, Street, City, HouseNum) VALUES
            ('M001', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'David', 'Cohen', '["972-54-1234567"]', '2018-05-01', 'Main St', 'Tel Aviv', '10'),
            ('M002', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', 'Sarah', 'Levi', '["972-50-7654321"]', '2019-09-15', 'Derech Ben Gurion', 'Jerusalem', '20')""")
        conn.commit()
        
        # -- PILOTS --
        cursor.execute("""INSERT INTO Pilot (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining, JoinDate, Street, City, HouseNum) VALUES
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
            ('P011', 'Alon', 'Baruch', '["972-52-1111101"]', TRUE, '2020-03-15', 'Ben Gurion St', 'Tel Aviv', '22'),
            ('P012', 'Benny', 'Carmel', '["972-54-1212101"]', TRUE, '2019-07-20', 'Ben Gurion St', 'Tel Aviv', '24'),
            ('P013', 'Chaim', 'Dayan', '["972-50-1313101"]', TRUE, '2021-01-10', 'Airport Rd', 'Tel Aviv', '26'),
            ('P014', 'David', 'Eyal', '["972-52-1414101"]', TRUE, '2020-09-05', 'Airport Rd', 'Tel Aviv', '28'),
            ('P015', 'Ehud', 'Fein', '["972-54-1515101"]', FALSE, '2022-02-28', 'Hashalom St', 'Tel Aviv', '30'),
            ('P016', 'Felix', 'Golan', '["972-50-1616101"]', FALSE, '2021-06-15', 'Hashalom St', 'Tel Aviv', '32')""")
        conn.commit()
        
        # -- FLIGHT ATTENDANTS --
        cursor.execute("""INSERT INTO FlightAttendant (Id, FirstName, SecondName, PhoneNum, LongFlightsTraining, JoinDate, Street, City, HouseNum) VALUES
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
            ('A032', 'Carmit', 'Tal', '["972-54-4242424"]', FALSE, '2021-03-15', 'Allenby St', 'Tel Aviv', '62')""")
        conn.commit()
        
        # -- CUSTOMERS --
        cursor.execute("""INSERT INTO RegisteredCustomer (UniqueMail, Password, PhoneNum, PassportNum, FirstName, SecondName, BirthDate, RegistrationDate) VALUES
            ('customer1@gmail.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', '["972-54-1111111"]', 'P123456', 'John', 'Doe', '1985-06-15', '2020-01-01'),
            ('customer2@gmail.com', '$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6', '["972-54-2222222"]', 'P789012', 'Jane', 'Smith', '1990-09-22', '2021-02-15')""")
        cursor.execute("""INSERT INTO GuestCustomer (UniqueMail, PhoneNum, FirstName, SecondName) VALUES
            ('guest1@gmail.com', '["972-50-0000000"]', 'Guest', 'User')""")
        conn.commit()
        
        # -- AIRPLANES --
        cursor.execute("""INSERT INTO Airplanes (AirplaneId, PurchaseDate, Manufacturer, CouchRows, CouchCols, BusinessRows, BusinessCols) VALUES
            ('PLANE-001', '2018-03-15', 'Boeing', 18, 7, 6, 4),
            ('PLANE-002', '2019-07-22', 'Boeing', 8, 4, 0, 0),
            ('PLANE-003', '2017-11-08', 'Airbus', 20, 7, 6, 4),
            ('PLANE-004', '2020-02-14', 'Airbus', 9, 4, 0, 0),
            ('PLANE-005', '2021-06-30', 'Dassault', 18, 7, 6, 4),
            ('PLANE-006', '2022-01-10', 'Dassault', 22, 4, 0, 0),
            ('PLANE-007', '2023-05-20', 'Boeing', 24, 7, 6, 4),
            ('PLANE-008', '2024-02-10', 'Airbus', 10, 4, 0, 0)""")
        conn.commit()
        
        # -- FLIGHTS --
        cursor.execute("""INSERT INTO Flights (FlightId, Airplanes_AirplaneId, OriginPort, DestPort, DepartureDate, DepartureHour, Duration, Status, EconomyPrice, BusinessPrice) VALUES
            ('FT201', 'PLANE-001', 'TLV', 'LHR', '2025-09-10', '07:00:00', 298, 'done', 350.00, 1100.00),
            ('FT202', 'PLANE-002', 'TLV', 'ATH', '2025-09-15', '09:30:00', 129, 'done', 180.00, NULL),
            ('FT203', 'PLANE-003', 'TLV', 'CDG', '2025-10-05', '06:00:00', 277, 'done', 320.00, 980.00),
            ('FT204', 'PLANE-005', 'TLV', 'FRA', '2025-10-20', '14:00:00', 253, 'done', 300.00, 920.00),
            ('FT101', 'PLANE-001', 'TLV', 'JFK', '2025-11-15', '08:00:00', 660, 'done', 500.00, 1500.00),
            ('FT102', 'PLANE-003', 'TLV', 'LAX', '2025-11-20', '06:30:00', 780, 'done', 550.00, 1600.00),
            ('FT103', 'PLANE-002', 'TLV', 'LCA', '2025-11-29', '22:00:00', 40, 'cancelled', 120.00, NULL),
            ('FT104', 'PLANE-004', 'TLV', 'RUH', '2026-01-21', '20:00:00', 160, 'active', 150.00, NULL),
            ('FT205', 'PLANE-006', 'TLV', 'CAI', '2026-01-25', '11:00:00', 73, 'active', 120.00, NULL),
            ('FT206', 'PLANE-005', 'TLV', 'BCN', '2026-02-10', '08:30:00', 262, 'active', 280.00, 850.00),
            ('FT207', 'PLANE-001', 'TLV', 'AMS', '2026-02-18', '10:00:00', 279, 'active', 310.00, 950.00)""")
        conn.commit()
        
        # -- CREW ASSIGNMENTS --
        cursor.execute("""INSERT IGNORE INTO Pilot_has_Flights (Pilot_Id, Flights_FlightId) VALUES
            ('P001', 'FT201'), ('P002', 'FT201'), ('P003', 'FT201'),
            ('P007', 'FT202'), ('P008', 'FT202'),
            ('P004', 'FT203'), ('P005', 'FT203'), ('P006', 'FT203'),
            ('P001', 'FT204'), ('P002', 'FT204'), ('P003', 'FT204'),
            ('P001', 'FT101'), ('P002', 'FT101'), ('P003', 'FT101'),
            ('P004', 'FT102'), ('P005', 'FT102'), ('P006', 'FT102'),
            ('P007', 'FT103'), ('P008', 'FT103'),
            ('P009', 'FT104'), ('P010', 'FT104'),
            ('P007', 'FT205'), ('P008', 'FT205'),
            ('P001', 'FT206'), ('P002', 'FT206'), ('P003', 'FT206'),
            ('P004', 'FT207'), ('P005', 'FT207'), ('P006', 'FT207')""")
        cursor.execute("""INSERT IGNORE INTO FlightAttendant_has_Flights (FlightAttendant_Id, Flights_FlightId) VALUES
            ('A001', 'FT201'), ('A002', 'FT201'), ('A003', 'FT201'), ('A004', 'FT201'), ('A005', 'FT201'), ('A006', 'FT201'),
            ('A013', 'FT202'), ('A014', 'FT202'), ('A015', 'FT202'),
            ('A007', 'FT203'), ('A008', 'FT203'), ('A009', 'FT203'), ('A010', 'FT203'), ('A011', 'FT203'), ('A012', 'FT203'),
            ('A001', 'FT204'), ('A002', 'FT204'), ('A003', 'FT204'), ('A004', 'FT204'), ('A005', 'FT204'), ('A006', 'FT204'),
            ('A001', 'FT101'), ('A002', 'FT101'), ('A003', 'FT101'), ('A004', 'FT101'), ('A005', 'FT101'), ('A006', 'FT101'),
            ('A007', 'FT102'), ('A008', 'FT102'), ('A009', 'FT102'), ('A010', 'FT102'), ('A011', 'FT102'), ('A012', 'FT102'),
            ('A013', 'FT103'), ('A014', 'FT103'), ('A015', 'FT103'),
            ('A016', 'FT104'), ('A017', 'FT104'), ('A018', 'FT104'),
            ('A019', 'FT205'), ('A020', 'FT205'), ('A013', 'FT205'),
            ('A001', 'FT206'), ('A002', 'FT206'), ('A003', 'FT206'), ('A004', 'FT206'), ('A005', 'FT206'), ('A006', 'FT206'),
            ('A007', 'FT207'), ('A008', 'FT207'), ('A009', 'FT207'), ('A010', 'FT207'), ('A011', 'FT207'), ('A012', 'FT207')""")
        conn.commit()
        
        # -- ORDERS --
        cursor.execute("""INSERT INTO orders (UniqueOrderCode, Flights_FlightId, TotalCost, Status, GuestCustomer_UniqueMail, RegisteredCustomer_UniqueMail) VALUES
            ('ORD-SEP01', 'FT201', 700.00, 'confirmed', NULL, 'customer1@gmail.com'),
            ('ORD-SEP02', 'FT201', 1100.00, 'confirmed', NULL, 'customer2@gmail.com'),
            ('ORD-SEP03', 'FT202', 180.00, 'confirmed', 'guest1@gmail.com', NULL),
            ('ORD-SEP04', 'FT202', 9.00, 'customer_canceled', NULL, 'customer1@gmail.com'),
            ('ORD-OCT01', 'FT203', 640.00, 'confirmed', NULL, 'customer2@gmail.com'),
            ('ORD-OCT02', 'FT203', 16.00, 'customer_canceled', NULL, 'customer1@gmail.com'),
            ('ORD-OCT03', 'FT204', 920.00, 'confirmed', NULL, 'customer2@gmail.com'),
            ('ORD-OCT04', 'FT204', 300.00, 'confirmed', 'guest1@gmail.com', NULL),
            ('FLY-ABC123', 'FT101', 1000.00, 'confirmed', NULL, 'customer1@gmail.com'),
            ('FLY-DEF456', 'FT102', 1600.00, 'confirmed', NULL, 'customer2@gmail.com'),
            ('FLY-DEF768', 'FT102', 550.00, 'confirmed', 'guest1@gmail.com', NULL),
            ('FLY-ABC001', 'FT104', 15.00, 'customer_canceled', NULL, 'customer1@gmail.com'),
            ('FLY-ABC002', 'FT104', 150.00, 'confirmed', NULL, 'customer2@gmail.com'),
            ('FLY-DEF003', 'FT104', 7.50, 'customer_canceled', NULL, 'customer1@gmail.com'),
            ('ORD-JAN01', 'FT205', 240.00, 'confirmed', NULL, 'customer1@gmail.com'),
            ('ORD-JAN02', 'FT205', 6.00, 'customer_canceled', 'guest1@gmail.com', NULL),
            ('ORD-FEB01', 'FT206', 850.00, 'confirmed', NULL, 'customer2@gmail.com'),
            ('ORD-FEB02', 'FT206', 280.00, 'confirmed', NULL, 'customer1@gmail.com'),
            ('ORD-FEB03', 'FT207', 620.00, 'confirmed', 'guest1@gmail.com', NULL),
            ('ORD-FEB04', 'FT207', 15.50, 'customer_canceled', NULL, 'customer2@gmail.com')""")
        conn.commit()
        
        # -- TICKETS --
        cursor.execute("""INSERT IGNORE INTO Tickets (orders_UniqueOrderCode, RowNum, Seat, Class) VALUES
            ('ORD-SEP01', 5, 'A', 'economy'), ('ORD-SEP01', 5, 'B', 'economy'),
            ('ORD-SEP02', 1, 'A', 'business'),
            ('ORD-SEP03', 8, 'A', 'economy'),
            ('ORD-SEP04', 8, 'B', 'economy'),
            ('ORD-OCT01', 3, 'A', 'economy'), ('ORD-OCT01', 3, 'B', 'economy'),
            ('ORD-OCT02', 10, 'A', 'economy'),
            ('ORD-OCT03', 1, 'A', 'business'),
            ('ORD-OCT04', 12, 'A', 'economy'),
            ('FLY-ABC123', 7, 'A', 'economy'), ('FLY-ABC123', 7, 'B', 'economy'),
            ('FLY-DEF456', 1, 'A', 'business'),
            ('FLY-DEF768', 24, 'A', 'economy'),
            ('FLY-ABC001', 5, 'A', 'economy'), ('FLY-ABC001', 5, 'B', 'economy'),
            ('FLY-ABC002', 8, 'A', 'economy'),
            ('FLY-DEF003', 4, 'C', 'economy'),
            ('ORD-JAN01', 6, 'A', 'economy'), ('ORD-JAN01', 6, 'B', 'economy'),
            ('ORD-JAN02', 9, 'A', 'economy'),
            ('ORD-FEB01', 1, 'A', 'business'),
            ('ORD-FEB02', 15, 'A', 'economy'),
            ('ORD-FEB03', 4, 'A', 'economy'), ('ORD-FEB03', 4, 'B', 'economy'),
            ('ORD-FEB04', 18, 'A', 'economy')""")
        conn.commit()
        
        # -- MANAGER EDITS --
        cursor.execute("""INSERT IGNORE INTO Managers_edits_Flights (Managers_ManagerId, Flights_FlightId) VALUES
            ('M001', 'FT101'), ('M001', 'FT102'), ('M002', 'FT103'), ('M002', 'FT104'),
            ('M001', 'FT201'), ('M001', 'FT202'), ('M002', 'FT203'), ('M002', 'FT204'),
            ('M001', 'FT205'), ('M002', 'FT206'), ('M001', 'FT207')""")
        conn.commit()
        
        cursor.close()
        return "Success! All seed data loaded."
    except Exception as e:
        import traceback
        return f"Error: {str(e)}<br><pre>{traceback.format_exc()}</pre>", 500


@application.route("/seed_status")
def seed_status():
    """Check current data counts."""
    try:
        conn = db.get_db()
        cursor = conn.cursor(dictionary=True)
        
        tables = ['Managers', 'Pilot', 'FlightAttendant', 'Airplanes', 'Flights', 'orders', 'Tickets', 'Routes']
        counts = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
                counts[table] = cursor.fetchone()['cnt']
            except:
                counts[table] = 'error'
        
        cursor.close()
        
        result = "<br>".join([f"{k}: {v}" for k, v in counts.items()])
        return f"<h3>Data Counts:</h3>{result}"
    except Exception as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Local development server
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    application.run(
        host='127.0.0.1',
        port=5001,  # Changed from 5000 - macOS uses 5000 for AirPlay
        debug=False,  # Disabled to avoid conda/venv ctypes conflict
        use_reloader=False
    )
