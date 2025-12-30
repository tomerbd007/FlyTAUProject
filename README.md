# FLYTAU - Flight Management System

**Databases Systems Design and Information Systems Engineering Project**  
Tel Aviv University

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
│   ├── 01_seed.sql           # Initial seed data
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
python3 -m venv venv
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
mysql -u root -p flytau < sql/01_seed.sql
```

#### Option B: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your MySQL server
3. File → Open SQL Script → Select `sql/00_schema.sql`
4. Execute the script (⚡ button)
5. Open and execute `sql/01_seed.sql`

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
