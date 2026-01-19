# ✈️ FlyTAU - Flight Management System

<p align="center">
  <strong>Database Systems Design & Information Systems Engineering</strong><br>
  Tel Aviv University
</p>

<p align="center">
  <a href="#-live-demo">Live Demo</a> •
  <a href="#-test-accounts">Test Accounts</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-tech-stack">Tech Stack</a>
</p>

---

## 🌐 Live Demo

**The application is deployed and running on AWS Elastic Beanstalk:**

🔗 **[http://flytau-env.eba-r5iqhqhu.il-central-1.elasticbeanstalk.com](http://flytau-env.eba-r5iqhqhu.il-central-1.elasticbeanstalk.com)**

---

## 🔑 Test Accounts

Use these credentials to explore the application:

### 👤 Customer Login
| Field | Value |
|-------|-------|
| Email | `customer1@gmail.com` |
| Password | `password123` |

### 👤 Customer Login (Alternative)
| Field | Value |
|-------|-------|
| Email | `customer2@gmail.com` |
| Password | `password123` |

### 🛠️ Manager Login (`/admin/login`)
| Field | Value |
|-------|-------|
| Employee Code | `M001` |
| Password | `password123` |

### 🛠️ Manager Login (Alternative)
| Field | Value |
|-------|-------|
| Employee Code | `M002` |
| Password | `password123` |

---

## 🚀 Quick Start (Run Locally)

### Prerequisites
- Python 3.9+
- MySQL 8.0+

### 1. Clone & Setup

```bash
git clone https://github.com/tomerbd007/FlyTAUProject.git
cd FlyTAUProject

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=flytau
```

### 3. Initialize Database

```bash
# Create schema and load seed data
mysql -u root -p < sql/00_schema.sql
mysql -u root -p flytau < sql/01_seed_fixed.sql
```

### 4. Run the Application

```bash
python run.py
```

Open **http://localhost:5000** in your browser.

---

## ✨ Features

### For Customers
- 🔍 Search flights by date, origin, and destination
- 💺 Interactive seat selection with real-time availability
- 🎫 Book tickets as registered user or guest
- 📋 View and manage order history
- ❌ Cancel orders (up to 36 hours before departure, 5% fee)
- 🔎 Look up guest bookings with booking code + email

### For Managers
- 📊 Dashboard with flight overview
- ➕ Add new flights (3-step wizard: route → crew → pricing)
- ✈️ Assign pilots and flight attendants to flights
- 🚫 Cancel flights (up to 72 hours before departure)
- 📈 Generate reports:
  - Average flight occupancy
  - Revenue by aircraft
  - Flight hours per employee
  - Monthly cancellation rate
  - Monthly aircraft activity

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.12, Flask 3.0 |
| **Database** | MySQL 8.0 |
| **Frontend** | HTML5, CSS3, Jinja2 |
| **Auth** | Session-based, bcrypt hashing |
| **Hosting** | AWS Elastic Beanstalk + RDS |

---

## 📁 Project Structure

```
FlyTAU/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── db.py                # Database connection pool
│   ├── routes/              # HTTP route handlers
│   │   ├── auth_routes.py   # Login, register, logout
│   │   ├── flight_routes.py # Search, details, seat selection
│   │   ├── order_routes.py  # Checkout, orders, cancellation
│   │   ├── admin_routes.py  # Flight management
│   │   └── report_routes.py # Analytics reports
│   ├── services/            # Business logic
│   ├── repositories/        # Database queries
│   ├── utils/               # Helpers & decorators
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS & images
├── sql/
│   ├── 00_schema.sql        # Database schema
│   ├── 01_seed_fixed.sql    # Sample data
│   └── reports/             # Report SQL queries
├── tests/                   # Unit tests
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 📋 Business Rules

| Rule | Description |
|------|-------------|
| **Cancellation Window** | Customers can cancel orders up to 36 hours before departure |
| **Cancellation Fee** | 5% of the order total |
| **Flight Cancellation** | Managers can cancel flights up to 72 hours before departure |
| **Crew Requirements** | Large aircraft: 3 pilots + 6 attendants, Small: 2 pilots + 3 attendants |
| **Long Flights** | Flights over 6 hours require trained crew and large aircraft |
| **Manager Restriction** | Managers cannot purchase tickets |

---

## 🗄️ Database Schema

The database follows a relational design with these main entities:

- **Airports** - Airport codes, names, and locations
- **Routes** - Origin-destination pairs with calculated durations
- **Airplanes** - Fleet with seat configurations (economy + business class)
- **Flights** - Scheduled flights with pricing and status
- **Pilot / FlightAttendant** - Crew members with certifications
- **RegisteredCustomer / GuestCustomer** - Customer accounts
- **Orders** - Bookings with status tracking
- **Tickets** - Individual seats within orders
- **Managers** - Admin users who manage flights

See [sql/00_schema.sql](sql/00_schema.sql) for the complete schema.

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/register` | Customer registration |
| GET/POST | `/login` | Customer login |
| GET/POST | `/admin/login` | Manager login |
| GET | `/logout` | Logout |

### Flights
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/flights` | Search form |
| GET | `/flights/search` | Search results |
| GET | `/flights/<id>` | Flight details |
| GET/POST | `/flights/<id>/seats` | Seat selection |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/checkout` | Checkout flow |
| GET | `/orders/<code>` | Order confirmation |
| GET | `/orders` | Customer's orders |
| GET/POST | `/orders/<id>/cancel` | Cancel order |
| GET/POST | `/guest/lookup` | Guest order lookup |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin` | Dashboard |
| GET/POST | `/admin/flights/add` | Add flight wizard |
| GET/POST | `/admin/flights/<id>/cancel` | Cancel flight |
| GET | `/admin/reports` | Report selection |
| GET | `/admin/reports/<type>` | View specific report |

---

## 🧪 Running Tests

```bash
pytest tests/
```

---

## ☁️ AWS Deployment

The application is deployed on AWS Elastic Beanstalk with:
- **Compute**: Elastic Beanstalk (Python 3.12 platform)
- **Database**: RDS MySQL 8.0
- **Region**: il-central-1 (Tel Aviv)

<details>
<summary><strong>AWS Deployment Guide</strong></summary>

### Prerequisites
- AWS Account
- AWS EB CLI (`pip install awsebcli`)

### Steps

1. **Initialize EB CLI**
   ```bash
   eb init
   # Select: il-central-1, Python 3.12, create SSH keypair
   ```

2. **Create Environment**
   ```bash
   eb create flytau-env
   ```

3. **Add RDS Database**
   - AWS Console → Elastic Beanstalk → Configuration → Database
   - Engine: MySQL 8.0, Instance: db.t3.micro

4. **Deploy**
   ```bash
   eb deploy
   ```

5. **Initialize Database**
   - Visit `/setup_db` to create tables
   - Visit `/setup_db_seed` to load sample data

### Useful Commands
```bash
eb status    # View status
eb logs      # View logs
eb ssh       # SSH into instance
eb open      # Open in browser
```

</details>

---

## 📄 License

This project was created for educational purposes as part of the Database Systems course at Tel Aviv University.

---

<p align="center">
  Made with ❤️ at Tel Aviv University
</p>
