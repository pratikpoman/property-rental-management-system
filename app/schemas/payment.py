from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.payment import PaymentType, PaymentMode, PaymentStatus


class PaymentBase(BaseModel):
    agreement_id: int
    payment_type: PaymentType = PaymentType.rent
    amount_due: float = Field(..., gt=0)
    due_date: datetime
    for_month: Optional[str] = None  # "YYYY-MM"
    remarks: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentRecord(BaseModel):
    """Schema for recording an actual payment"""
    amount_paid: float = Field(..., gt=0)
    payment_mode: PaymentMode
    paid_date: Optional[datetime] = None
    transaction_id: Optional[str] = None
    cheque_number: Optional[str] = None
    remarks: Optional[str] = None


class PaymentUpdate(BaseModel):
    amount_paid: Optional[float] = None
    payment_mode: Optional[PaymentMode] = None
    paid_date: Optional[datetime] = None
    transaction_id: Optional[str] = None
    cheque_number: Optional[str] = None
    status: Optional[PaymentStatus] = None
    remarks: Optional[str] = None
    late_fee: Optional[float] = None


class PaymentOut(PaymentBase):
    id: int
    amount_paid: float
    late_fee: float
    paid_date: Optional[datetime]
    payment_mode: Optional[PaymentMode]
    transaction_id: Optional[str]
    cheque_number: Optional[str]
    status: PaymentStatus
    receipt_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentSummary(BaseModel):
    total_due: float
    total_paid: float
    total_pending: float
    total_overdue: float
    total_late_fees: float
