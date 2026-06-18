from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.property import Property, PropertyStatus
from app.models.tenant import Tenant, TenantStatus
from app.models.agreement import RentalAgreement, AgreementStatus
from app.models.payment import Payment, PaymentStatus
from app.models.maintenance import MaintenanceRequest, MaintenanceStatus
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Reports"])


@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get full dashboard overview for the current owner"""
    owner_id = current_user.id

    # Property stats
    total_properties = db.query(Property).filter(Property.owner_id == owner_id).count()
    vacant = db.query(Property).filter(
        Property.owner_id == owner_id, Property.status == PropertyStatus.vacant
    ).count()
    occupied = db.query(Property).filter(
        Property.owner_id == owner_id, Property.status == PropertyStatus.occupied
    ).count()
    under_maintenance = db.query(Property).filter(
        Property.owner_id == owner_id, Property.status == PropertyStatus.maintenance
    ).count()

    # Agreement stats
    active_agreements = db.query(RentalAgreement).join(Property).filter(
        Property.owner_id == owner_id,
        RentalAgreement.status == AgreementStatus.active
    ).count()

    # Agreements expiring soon (30 days)
    threshold = datetime.utcnow() + timedelta(days=30)
    expiring_soon = db.query(RentalAgreement).join(Property).filter(
        Property.owner_id == owner_id,
        RentalAgreement.status == AgreementStatus.active,
        RentalAgreement.end_date <= threshold
    ).count()

    # Payment stats this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    monthly_collected = db.query(func.sum(Payment.amount_paid)).join(
        RentalAgreement
    ).join(Property).filter(
        Property.owner_id == owner_id,
        Payment.status == PaymentStatus.paid,
        Payment.paid_date >= month_start
    ).scalar() or 0

    # Total overdue amount
    total_overdue = db.query(func.sum(Payment.amount_due)).join(
        RentalAgreement
    ).join(Property).filter(
        Property.owner_id == owner_id,
        Payment.status == PaymentStatus.overdue
    ).scalar() or 0

    # Pending payments count
    pending_payments = db.query(Payment).join(RentalAgreement).join(Property).filter(
        Property.owner_id == owner_id,
        Payment.status.in_([PaymentStatus.pending, PaymentStatus.overdue])
    ).count()

    # Open maintenance requests
    open_maintenance = db.query(MaintenanceRequest).join(Property).filter(
        Property.owner_id == owner_id,
        MaintenanceRequest.status.in_([MaintenanceStatus.open, MaintenanceStatus.in_progress])
    ).count()

    return {
        "properties": {
            "total": total_properties,
            "vacant": vacant,
            "occupied": occupied,
            "under_maintenance": under_maintenance,
            "occupancy_rate": round((occupied / total_properties * 100), 1) if total_properties else 0
        },
        "agreements": {
            "active": active_agreements,
            "expiring_within_30_days": expiring_soon,
        },
        "payments": {
            "collected_this_month": round(monthly_collected, 2),
            "total_overdue": round(total_overdue, 2),
            "pending_count": pending_payments,
        },
        "maintenance": {
            "open_requests": open_maintenance,
        }
    }


@router.get("/revenue")
def get_revenue_report(
    year: int = Query(default=datetime.utcnow().year),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly revenue report for a given year"""
    monthly_data = []
    for month in range(1, 13):
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)

        collected = db.query(func.sum(Payment.amount_paid)).join(
            RentalAgreement
        ).join(Property).filter(
            Property.owner_id == current_user.id,
            Payment.status == PaymentStatus.paid,
            Payment.paid_date >= month_start,
            Payment.paid_date < month_end
        ).scalar() or 0

        monthly_data.append({
            "month": month_start.strftime("%B"),
            "month_number": month,
            "revenue": round(collected, 2)
        })

    total = sum(m["revenue"] for m in monthly_data)
    return {
        "year": year,
        "total_revenue": round(total, 2),
        "monthly_breakdown": monthly_data
    }
