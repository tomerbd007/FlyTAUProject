# FLYTAU - Flight Management System

**Databases Systems Design and Information Systems Engineering Project**  
Tel Aviv University

---

## 🚀 Deploy to AWS Elastic Beanstalk

This section covers deploying FLYTAU to AWS Elastic Beanstalk with an RDS MySQL database.

### Prerequisites

- AWS Account
- Python 3.9+
- AWS EB CLI installed

### Step 1: Install EB CLI

```bash
pip install awsebcli
```

Verify installation:

```bash
eb --version
```

### Step 2: Initialize Elastic Beanstalk

Navigate to the project root and run:

```bash
eb init
```

When prompted:
- **Region**: Select `il-central-1` (Tel Aviv / Israel) or your preferred region
- **Application name**: `flytau` (or your choice)
- **Platform**: Select `Python`
- **Platform version**: Select `Python 3.9` or later
- **SSH**: Yes (create a new KeyPair if needed)

### Step 3: AWS Credentials (if prompted)

If EB CLI asks for credentials:

1. Go to **AWS Console → IAM → Users → Create user**
2. Attach policy: `AdministratorAccess` (or more restricted policies for production)
3. Go to **Security credentials → Create access key → CLI use case**
4. Copy the **Access Key ID** and **Secret Access Key** (you can only copy the secret once!)
5. Paste them into the EB CLI prompts

### Step 4: Create the Environment

```bash
eb create flytau-env
```

When prompted:
- Select a load balancer type (choose `application` for most cases)
- Create/select a KeyPair for SSH access

Wait for the environment to be created (this takes several minutes).

### Step 5: Enable RDS Database

1. Go to **AWS Console → Elastic Beanstalk → Environments → flytau-env**
2. Click **Configuration** in the left sidebar
3. Find **Database** section → Click **Edit**
4. Configure:
   - **Engine**: `mysql`
   - **Engine version**: `8.0` (or latest)
   - **Instance class**: `db.t3.micro` (free tier eligible)
   - **Storage**: `5 GB`
   - **Username**: Choose a username (e.g., `flytau_admin`)
   - **Password**: Choose a strong password (save it!)
5. Click **Apply**

Wait for the database to be created (this takes several minutes).

> **Note**: AWS EB automatically sets these environment variables when RDS is enabled:
> - `RDS_HOSTNAME` - Database endpoint
> - `RDS_PORT` - Database port (3306)
> - `RDS_USERNAME` - Database username
> - `RDS_PASSWORD` - Database password
> - `RDS_DB_NAME` - Database name

### Step 6: Set Additional Environment Variables (Optional)

Go to **Configuration → Software → Edit → Environment properties**:

| Property | Value |
|----------|-------|
| `SECRET_KEY` | A long random string for Flask sessions |

Click **Apply**.

### Step 7: Deploy the Application

```bash
eb deploy
```

### Step 8: Open the Application

```bash
eb open
```

### Step 9: Initialize the Database Tables

Visit these URLs **once** to set up the database:

1. **Create tables**: `https://<your-domain>/setup_db`
2. **Load seed data**: `https://<your-domain>/setup_db_seed`

You should see "Success!" messages.

> ⚠️ **IMPORTANT**: After setup, remove or protect the `/setup_db` and `/setup_db_seed` routes in `application.py` and redeploy for security.

### Step 10: Verify Deployment

1. Visit your application URL
2. Try logging in with test accounts (see below)
3. Check the admin panel at `/admin/login`

### Useful EB Commands

```bash
# View application status
eb status

# View recent logs
eb logs

# SSH into the EC2 instance
eb ssh

# View environment health
eb health

# Terminate the environment (CAREFUL - deletes RDS too!)
eb terminate

# List all environments
eb list
```

### Troubleshooting

**500 Internal Server Error**:
```bash
eb logs
```
Check the logs for Python errors.

**Database connection issues**:
- Verify RDS is running in AWS Console → RDS → Databases
- Check environment variables in Configuration → Software

**Session issues**:
- The app uses filesystem sessions stored in `flask_session_data/`
- This directory is created automatically

---

## Overview

FLYTAU is a Flask-based web application for flight booking and management. It includes:

- **Customer Portal**: Search flights, select seats, book tickets, manage orders
- **Guest Booking**: Book without registration using booking code + email
- **Admin Panel**: Manage flights, assign crew, cancel flights, view reports

## Tech Stack

- **Backend**: Python 3.9+, Flask
- **Database**: MySQL 8.0+ (designed with MySQL Workbench)
- **Frontend**: HTML5, CSS3 (no JavaScript)
- **Authentication**: Session-based with bcrypt password hashing

## Project Structure

```
FLYTAU/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration (dev/prod/test)
│   ├── db.py                 # MySQL connector wrapper
│   ├── routes/               # Route handlers
│   │   ├── auth_routes.py    # Login, register, logout
│   │   ├── flight_routes.py  # Search, details, seat selection
│   │   ├── order_routes.py   # Checkout, orders, cancellation
│   │   ├── admin_routes.py   # Flight management
│   │   └── report_routes.py  # Reports
│   ├── services/             # Business logic layer
│   ├── repositories/         # Database access layer
│   ├── utils/                # Helpers, decorators, validators
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # CSS, images
├── sql/
│   ├── 00_schema.sql         # Database schema
│   ├── 01_seed_fixed.sql    # Initial seed data (idempotent, preferred)
│   └── reports/              # Report SQL queries
├── tests/                    # Unit tests
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Prerequisites

- Python 3.9 or higher
- MySQL 8.0 or higher
- MySQL Workbench (for database design)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/tomerbd007/FlyTAUProject.git
cd FlyTAUProject
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```
SECRET_KEY=your-secure-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=flytau
```

### 5. Initialize Database

#### Option A: Using MySQL command line

```bash
mysql -u root -p < sql/00_schema.sql
mysql -u root -p flytau < sql/01_seed_fixed.sql
```

#### Option B: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your MySQL server
3. File → Open SQL Script → Select `sql/00_schema.sql`
4. Execute the script (⚡ button)
5. Open and execute `sql/01_seed_fixed.sql` (idempotent, safe to re-run)

### 6. Run the Application

```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

Or create a `run.py`:

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

Then run:

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Test Accounts

After loading seed data, you can log in with:

### Customers
- **Email**: `customer1@example.com`
- **Password**: `password123`

### Managers
- **Employee Code**: `M001`
- **Password**: `password123`

## Features

### Public Features (Guest/Customer)
- Search flights by date, origin, destination
- View flight details and seat availability
- Select seats from interactive seat map
- Book as guest (with email) or logged-in customer
- View booking confirmation with booking code

### Customer Features
- View order history with status filter
- Cancel orders (36 hours before departure, 5% fee)
- Look up orders by booking code + email

### Manager Features
- View all flights with status filter
- Add new flights (3-step wizard):
  1. Select date/time and route
  2. Choose aircraft and assign crew
  3. Set ticket prices
- Cancel flights (72 hours before departure)
- View reports:
  - Average flight occupancy
  - Revenue by aircraft
  - Flight hours per employee
  - Monthly cancellation rate
  - Monthly aircraft activity

## Business Rules

| Rule | Enforcement |
|------|-------------|
| Managers cannot purchase tickets | Service layer + route guards |
| 36h cancellation window for orders | Service layer time check |
| 72h cancellation window for flights | Service layer time check |
| 5% cancellation fee | Calculated in service |
| Small aircraft: short flights only | Validated during flight creation |
| Crew certification for long flights | Filtered in crew selection |
| Crew count: Large=3P+6A, Small=2P+3A | Validated before flight creation |

## Database Schema

See `sql/00_schema.sql` for complete schema. Main tables:

- `customers` - Registered customers
- `employees` - Managers, pilots, attendants
- `aircraft` - Fleet with seat configuration
- `seat_map` - Template seats per aircraft
- `routes` - Origin-destination with duration
- `flights` - Scheduled flights
- `flight_seats` - Seats per flight instance
- `crew_assignments` - Crew assigned to flights
- `orders` - Bookings
- `order_lines` - Individual tickets
- `airports` - Airport details

## API Endpoints

### Authentication
- `GET/POST /register` - Customer registration
- `GET/POST /login` - Customer login
- `GET/POST /admin/login` - Manager login
- `GET /logout` - Logout

### Flights
- `GET /flights` - Search form
- `GET /flights/search` - Search results
- `GET /flights/<id>` - Flight details
- `GET/POST /flights/<id>/seats` - Seat selection

### Orders
- `GET/POST /checkout` - Checkout flow
- `GET /orders/<booking_code>` - Confirmation
- `GET /orders` - Customer's orders
- `GET /orders/<id>/detail` - Order detail
- `GET/POST /orders/<id>/cancel` - Cancel order
- `GET/POST /guest/lookup` - Guest order lookup

### Admin
- `GET /admin` - Dashboard
- `GET /admin/flights` - Flight list
- `GET/POST /admin/flights/add` - Add flight (step 1)
- `GET/POST /admin/flights/add/crew` - Add flight (step 2)
- `GET/POST /admin/flights/add/pricing` - Add flight (step 3)
- `GET/POST /admin/flights/<id>/cancel` - Cancel flight

### Reports
- `GET /admin/reports` - Report list
- `GET /admin/reports/occupancy` - Occupancy report
- `GET /admin/reports/revenue` - Revenue report
- `GET /admin/reports/flight-hours` - Flight hours report
- `GET /admin/reports/cancellation-rate` - Cancellation report
- `GET /admin/reports/aircraft-activity` - Aircraft activity report

## Development

### Running Tests

```bash
pytest tests/
```

### Project Conventions

- All times stored in UTC
- Passwords hashed with bcrypt (12 rounds)
- Session-based authentication (1 hour expiry)
- Form validation is server-side only (no JavaScript)

## License

This project is for educational purposes as part of Tel Aviv University coursework.

## Authors

- Tel Aviv University Database Systems Course

## Airports Seed Data

```sql
USE flytau;
CREATE TABLE IF NOT EXISTS Airports (
  Code VARCHAR(10) NOT NULL PRIMARY KEY,
  Name VARCHAR(100) NOT NULL,
  City VARCHAR(100) NOT NULL,
  Country VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

INSERT IGNORE INTO Airports (Code, Name, City, Country) VALUES
('TLV','Ben Gurion International Airport','Tel Aviv','Israel'),
('DXB','Dubai International Airport','Dubai','UAE'),
('AUH','Abu Dhabi International Airport','Abu Dhabi','UAE'),
('DOH','Hamad International Airport','Doha','Qatar'),
('RUH','King Khalid International Airport','Riyadh','Saudi Arabia'),
('JED','King Abdulaziz International Airport','Jeddah','Saudi Arabia'),
('AMM','Queen Alia International Airport','Amman','Jordan'),
('CAI','Cairo International Airport','Cairo','Egypt'),
('IST','Istanbul Airport','Istanbul','Turkey'),
('BEY','Beirut–Rafic Hariri International Airport','Beirut','Lebanon'),
('BAH','Bahrain International Airport','Manama','Bahrain'),
('KWI','Kuwait International Airport','Kuwait City','Kuwait'),
('MCT','Muscat International Airport','Muscat','Oman'),
('LHR','Heathrow Airport','London','United Kingdom'),
('CDG','Charles de Gaulle Airport','Paris','France'),
('FRA','Frankfurt Airport','Frankfurt','Germany'),
('AMS','Amsterdam Schiphol Airport','Amsterdam','Netherlands'),
('FCO','Leonardo da Vinci International Airport','Rome','Italy'),
('MAD','Adolfo Suárez Madrid–Barajas Airport','Madrid','Spain'),
('BCN','Barcelona–El Prat Airport','Barcelona','Spain'),
('ATH','Athens International Airport','Athens','Greece'),
('VIE','Vienna International Airport','Vienna','Austria'),
('ZRH','Zurich Airport','Zurich','Switzerland'),
('MUC','Munich Airport','Munich','Germany'),
('CPH','Copenhagen Airport','Copenhagen','Denmark'),
('PRG','Václav Havel Airport Prague','Prague','Czech Republic'),
('JFK','John F. Kennedy International Airport','New York','USA'),
('LAX','Los Angeles International Airport','Los Angeles','USA'),
('MIA','Miami International Airport','Miami','USA'),
('ORD','OHare International Airport','Chicago','USA'),
('SFO','San Francisco International Airport','San Francisco','USA'),
('YYZ','Toronto Pearson International Airport','Toronto','Canada'),
('GRU','São Paulo/Guarulhos International Airport','São Paulo','Brazil'),
('MEX','Mexico City International Airport','Mexico City','Mexico'),
('HND','Haneda Airport','Tokyo','Japan'),
('NRT','Narita International Airport','Tokyo','Japan'),
('SIN','Singapore Changi Airport','Singapore','Singapore'),
('HKG','Hong Kong International Airport','Hong Kong','China'),
('PEK','Beijing Capital International Airport','Beijing','China'),
('PVG','Shanghai Pudong International Airport','Shanghai','China'),
('ICN','Incheon International Airport','Seoul','South Korea'),
('BKK','Suvarnabhumi Airport','Bangkok','Thailand'),
('DEL','Indira Gandhi International Airport','New Delhi','India'),
('BOM','Chhatrapati Shivaji International Airport','Mumbai','India'),
('SYD','Sydney Kingsford Smith Airport','Sydney','Australia'),
('MEL','Melbourne Airport','Melbourne','Australia'),
('JNB','O.R. Tambo International Airport','Johannesburg','South Africa'),
('CPT','Cape Town International Airport','Cape Town','South Africa'),
('ADD','Addis Ababa Bole International Airport','Addis Ababa','Ethiopia'),
('NBO','Jomo Kenyatta International Airport','Nairobi','Kenya');
```
