from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.models.agreement import RentalAgreement
from app.models.property import Property
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate, PaymentUpdate, PaymentOut,
    PaymentRecord, PaymentSummary
)
from app.core.security import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])


def _verify_agreement_access(agreement_id: int, owner_id: int, db: Session) -> RentalAgreement:
    agreement = db.query(RentalAgreement).join(Property).filter(
        RentalAgreement.id == agreement_id,
        Property.owner_id == owner_id
    ).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found or access denied")
    return agreement


@router.post("/", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a payment record (e.g. rent due for a month)"""
    _verify_agreement_access(data.agreement_id, current_user.id, db)

    payment = Payment(**data.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/", response_model=List[PaymentOut])
def list_payments(
    agreement_id: Optional[int] = Query(None),
    status: Optional[PaymentStatus] = Query(None),
    payment_type: Optional[PaymentType] = Query(None),
    for_month: Optional[str] = Query(None, description="Filter by month YYYY-MM"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List payments for current owner's properties"""
    query = db.query(Payment).join(RentalAgreement).join(Property).filter(
        Property.owner_id == current_user.id
    )
    if agreement_id:
        query = query.filter(Payment.agreement_id == agreement_id)
    if status:
        query = query.filter(Payment.status == status)
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    if for_month:
        query = query.filter(Payment.for_month == for_month)

    return query.order_by(Payment.due_date.desc()).offset(skip).limit(limit).all()


@router.get("/overdue", response_model=List[PaymentOut])
def get_overdue_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all overdue payments"""
    now = datetime.utcnow()
    payments = db.query(Payment).join(RentalAgreement).join(Property).filter(
        Property.owner_id == current_user.id,
        Payment.status.in_([PaymentStatus.pending, PaymentStatus.partial]),
        Payment.due_date < now
    ).all()

    # Auto-mark as overdue
    for p in payments:
        p.status = PaymentStatus.overdue
    db.commit()

    return payments


@router.get("/summary", response_model=PaymentSummary)
def get_payment_summary(
    agreement_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment summary stats"""
    query = db.query(Payment).join(RentalAgreement).join(Property).filter(
        Property.owner_id == current_user.id
    )
    if agreement_id:
        query = query.filter(Payment.agreement_id == agreement_id)

    payments = query.all()
    return {
        "total_due": sum(p.amount_due for p in payments),
        "total_paid": sum(p.amount_paid for p in payments if p.status == PaymentStatus.paid),
        "total_pending": sum(p.amount_due for p in payments if p.status == PaymentStatus.pending),
        "total_overdue": sum(p.amount_due for p in payments if p.status == PaymentStatus.overdue),
        "total_late_fees": sum(p.late_fee for p in payments),
    }


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific payment"""
    payment = db.query(Payment).join(RentalAgreement).join(Property).filter(
        Payment.id == payment_id,
        Property.owner_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.patch("/{payment_id}/record", response_model=PaymentOut)
def record_payment(
    payment_id: int,
    data: PaymentRecord,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record an actual payment received"""
    payment = db.query(Payment).join(RentalAgreement).join(Property).filter(
        Payment.id == payment_id,
        Property.owner_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status == PaymentStatus.paid:
        raise HTTPException(status_code=400, detail="Payment already marked as paid")

    payment.amount_paid = data.amount_paid
    payment.payment_mode = data.payment_mode
    payment.paid_date = data.paid_date or datetime.utcnow()
    payment.transaction_id = data.transaction_id
    payment.cheque_number = data.cheque_number
    if data.remarks:
        payment.remarks = data.remarks

    # Calculate late fee if overdue
    if payment.paid_date > payment.due_date:
        days_late = (payment.paid_date - payment.due_date).days
        agreement = db.query(RentalAgreement).filter(
            RentalAgreement.id == payment.agreement_id
        ).first()
        payment.late_fee = days_late * agreement.late_fee_per_day

    # Determine status
    if data.amount_paid >= payment.amount_due:
        payment.status = PaymentStatus.paid
    else:
        payment.status = PaymentStatus.partial

    db.commit()
    db.refresh(payment)
    return payment


@router.put("/{payment_id}", response_model=PaymentOut)
def update_payment(
    payment_id: int,
    data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update payment record"""
    payment = db.query(Payment).join(RentalAgreement).join(Property).filter(
        Payment.id == payment_id,
        Property.owner_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)

    db.commit()
    db.refresh(payment)
    return payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a payment record"""
    payment = db.query(Payment).join(RentalAgreement).join(Property).filter(
        Payment.id == payment_id,
        Property.owner_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status == PaymentStatus.paid:
        raise HTTPException(status_code=400, detail="Cannot delete a paid payment record")

    db.delete(payment)
    db.commit()
