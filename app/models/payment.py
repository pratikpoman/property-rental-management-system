from sqlalchemy import Column, Integer, Float, DateTime, Enum, Text, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class PaymentType(str, enum.Enum):
    rent = "rent"
    security_deposit = "security_deposit"
    maintenance = "maintenance"
    late_fee = "late_fee"
    other = "other"


class PaymentMode(str, enum.Enum):
    cash = "cash"
    bank_transfer = "bank_transfer"
    upi = "upi"
    cheque = "cheque"
    online = "online"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"
    partial = "partial"
    waived = "waived"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    agreement_id = Column(Integer, ForeignKey("rental_agreements.id", ondelete="CASCADE"), nullable=False)

    payment_type = Column(Enum(PaymentType), default=PaymentType.rent, nullable=False)
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    late_fee = Column(Float, default=0.0)

    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)

    payment_mode = Column(Enum(PaymentMode), nullable=True)
    transaction_id = Column(String(200), nullable=True)
    cheque_number = Column(String(100), nullable=True)

    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    remarks = Column(Text, nullable=True)
    receipt_path = Column(String(500), nullable=True)

    # For rent: which month this payment covers
    for_month = Column(String(20), nullable=True)  # e.g. "2024-01"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    agreement = relationship("RentalAgreement", back_populates="payments")
