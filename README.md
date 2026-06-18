# Property Rental Management System — Backend

FastAPI backend with JWT authentication for managing properties, tenants, rental agreements, and payments.

---

## 🚀 Quick Start

### 1. Clone & Setup Virtual Environment
```bash
cd property_rental
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials and secret key
```

### 3. Create PostgreSQL Database
```sql
CREATE DATABASE property_rental_db;
```

### 4. Run Migrations
```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

### 5. Seed Test Data (Optional)
```bash
python seed.py
# Creates: owner (raj@example.com / password123), 2 properties, 1 tenant
```

### 6. Start the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access the API
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 📁 Project Structure

```
property_rental/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py          # Router aggregator
│   │       └── endpoints/
│   │           ├── auth.py          # Login, register, token refresh
│   │           ├── properties.py    # Property CRUD + filters
│   │           ├── tenants.py       # Tenant CRUD + history
│   │           ├── agreements.py    # Rental agreements lifecycle
│   │           ├── payments.py      # Payment tracking + recording
│   │           ├── maintenance.py   # Maintenance requests
│   │           └── dashboard.py     # Overview + revenue reports
│   ├── core/
│   │   ├── config.py               # Settings from .env
│   │   └── security.py             # JWT, password hashing, auth deps
│   ├── db/
│   │   └── database.py             # SQLAlchemy engine + session
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── property.py
│   │   ├── tenant.py
│   │   ├── agreement.py
│   │   ├── payment.py
│   │   └── maintenance.py
│   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── property.py
│   │   ├── tenant.py
│   │   ├── agreement.py
│   │   ├── payment.py
│   │   └── maintenance.py
│   └── main.py                     # App entry point
├── alembic/                        # Database migration files
├── seed.py                         # Test data seeder
├── requirements.txt
├── alembic.ini
└── .env.example
```

---

## 🔑 API Endpoints Summary

### Authentication `/api/v1/auth`
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new owner/admin |
| POST | `/login` | Get JWT tokens |
| POST | `/refresh` | Refresh access token |
| GET | `/me` | Get current user |

### Properties `/api/v1/properties`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List with filters (city, type, rent, etc.) |
| POST | `/` | Create new property |
| GET | `/{id}` | Get property details |
| PUT | `/{id}` | Update property |
| DELETE | `/{id}` | Delete property |
| PATCH | `/{id}/status` | Change availability status |

### Tenants `/api/v1/tenants`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List with search & status filter |
| POST | `/` | Create new tenant |
| GET | `/{id}` | Get tenant details |
| PUT | `/{id}` | Update tenant |
| DELETE | `/{id}` | Delete tenant |
| GET | `/{id}/history` | Full rental & payment history |

### Agreements `/api/v1/agreements`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List with filters |
| POST | `/` | Create draft agreement |
| GET | `/expiring-soon` | Agreements expiring in N days |
| GET | `/{id}` | Get agreement |
| PUT | `/{id}` | Update draft agreement |
| PATCH | `/{id}/activate` | Activate agreement |
| PATCH | `/{id}/terminate` | Terminate agreement |

### Payments `/api/v1/payments`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List with filters |
| POST | `/` | Create payment record |
| GET | `/overdue` | All overdue payments |
| GET | `/summary` | Totals (due, paid, pending, overdue) |
| PATCH | `/{id}/record` | Record payment received |
| PUT | `/{id}` | Update payment |
| DELETE | `/{id}` | Delete pending payment |

### Maintenance `/api/v1/maintenance`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List with filters |
| POST | `/` | Create request |
| PUT | `/{id}` | Update request |
| PATCH | `/{id}/resolve` | Mark as resolved |
| DELETE | `/{id}` | Delete request |

### Dashboard `/api/v1/dashboard`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/overview` | Full dashboard stats |
| GET | `/revenue` | Monthly revenue by year |

---

## 🔐 Authentication

All endpoints (except `/register` and `/login`) require a Bearer token:
```
Authorization: Bearer <access_token>
```

Tokens expire in 30 minutes. Use `/auth/refresh` with the refresh token to get a new access token.

---

## 🧪 Testing the API

Using the seeded data:
```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "raj@example.com", "password": "password123"}'

# 2. Use the returned access_token in subsequent requests
curl http://localhost:8000/api/v1/dashboard/overview \
  -H "Authorization: Bearer <access_token>"
```
