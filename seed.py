"""
Seed script to populate the database with test data.
Run: python seed.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine, Base
from app.models import *
from app.core.security import get_password_hash
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def seed():
    print("🌱 Seeding database...")

    # Create owner user
    owner = User(
        full_name="Raj Sharma",
        email="raj@example.com",
        phone="9876543210",
        role=UserRole.owner,
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db.add(owner)
    db.flush()

    # Create properties
    p1 = Property(
        owner_id=owner.id,
        title="2BHK Apartment in Pune",
        description="Spacious apartment in Koregaon Park",
        property_type=PropertyType.apartment,
        status=PropertyStatus.vacant,
        address="101, Green Valley, Koregaon Park",
        city="Pune", state="Maharashtra", zip_code="411001",
        bedrooms=2, bathrooms=2, area_sqft=950,
        monthly_rent=25000, security_deposit=50000,
        maintenance_charges=2000,
        amenities="Gym, Swimming Pool, Parking, Lift",
        is_furnished=True, parking_available=True
    )
    p2 = Property(
        owner_id=owner.id,
        title="Studio in Hinjewadi",
        description="Modern studio near IT hub",
        property_type=PropertyType.studio,
        status=PropertyStatus.occupied,
        address="55, Phase 1, Hinjewadi",
        city="Pune", state="Maharashtra", zip_code="411057",
        bedrooms=1, bathrooms=1, area_sqft=450,
        monthly_rent=12000, security_deposit=24000,
        maintenance_charges=500,
        amenities="24x7 Security, Power Backup",
        is_furnished=False, parking_available=False
    )
    db.add_all([p1, p2])
    db.flush()

    # Create tenant
    tenant = Tenant(
        full_name="Priya Mehta",
        email="priya@example.com",
        phone="9988776655",
        permanent_address="123, MG Road, Mumbai",
        id_proof_type=IDProofType.aadhar,
        id_proof_number="1234-5678-9012",
        occupation="Software Engineer",
        employer_name="TechCorp India",
        monthly_income=80000,
        emergency_contact_name="Rahul Mehta",
        emergency_contact_phone="9988776644",
        emergency_contact_relation="Brother",
        status=TenantStatus.active
    )
    db.add(tenant)
    db.flush()

    # Create active agreement for p2
    start = datetime.utcnow() - timedelta(days=90)
    end = start + timedelta(days=365)
    agreement = RentalAgreement(
        property_id=p2.id,
        tenant_id=tenant.id,
        start_date=start,
        end_date=end,
        monthly_rent=12000,
        security_deposit=24000,
        maintenance_charges=500,
        notice_period_days=30,
        rent_due_day=5,
        late_fee_per_day=100,
        status=AgreementStatus.active,
        security_deposit_paid=True,
        terms_and_conditions="Standard residential lease terms apply."
    )
    db.add(agreement)
    db.flush()

    # Add payment records for last 3 months
    for i in range(3):
        due = start + timedelta(days=30 * i)
        payment = Payment(
            agreement_id=agreement.id,
            payment_type=PaymentType.rent,
            amount_due=12000,
            amount_paid=12000,
            due_date=due,
            paid_date=due + timedelta(days=2),
            payment_mode=PaymentMode.upi,
            transaction_id=f"TXN{1000 + i}",
            status=PaymentStatus.paid,
            for_month=due.strftime("%Y-%m"),
            remarks="Paid via Google Pay"
        )
        db.add(payment)

    # Add maintenance request
    maintenance = MaintenanceRequest(
        property_id=p2.id,
        tenant_id=tenant.id,
        title="Water Leakage in Bathroom",
        description="There is a water leak from the overhead tank pipe",
        category="Plumbing",
        priority=MaintenancePriority.high,
        status=MaintenanceStatus.open
    )
    db.add(maintenance)

    db.commit()
    print("✅ Seeding complete!")
    print(f"   Owner: raj@example.com / password123")
    print(f"   Properties: {p1.title}, {p2.title}")
    print(f"   Tenant: {tenant.full_name}")
    db.close()


if __name__ == "__main__":
    seed()
