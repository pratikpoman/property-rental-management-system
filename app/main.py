from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.v1 import api_router
from app.db.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Create upload directory if not exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Property Rental Management System API",
    version="1.0.0",
    description="""
# Property Rental Management System

A complete backend solution for Property & Facility Management.

## Features

### Authentication
- User Registration
- User Login
- JWT Authentication
- Access Token & Refresh Token

### Property Management
- Create Property
- Update Property
- Delete Property
- Get Property Details
- Search & Filter Properties

### Tenant Management
- Add Tenant
- Update Tenant
- Delete Tenant
- View Tenant Details

### Rental Agreements
- Create Agreement
- View Agreements
- Renew Agreements
- Terminate Agreements

### Payment Management
- Record Payments
- Payment History
- Overdue Payment Tracking
- Revenue Reports

### Maintenance Requests
- Create Maintenance Request
- Assign Requests
- Update Status
- Close Requests

### Dashboard
- Occupancy Rate
- Total Revenue
- Active Tenants
- Pending Payments
- Maintenance Statistics

## Authentication

Use JWT Bearer Token:

Authorization: Bearer <access_token>
""",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(
    api_router,
    prefix="/api/v1"
)

# Static Files
app.mount(
    "/uploads",
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads"
)

# Root Endpoint
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Property Rental Management System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi_json": "/openapi.json",
        "api_base_url": "/api/v1",
        "status": "Live on Render"
    }

# Health Check
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": "Property Rental Management System",
        "version": "1.0.0"
    }

# Startup Event
@app.on_event("startup")
async def startup_event():
    print("Property Rental Management System Started")

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    print("Property Rental Management System Stopped")