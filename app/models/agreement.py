from sqlalchemy import Column, Integer, Float, DateTime, Enum, Text, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class AgreementStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    expired = "expired"
    terminated = "terminated"
    renewed = "renewed"


class RentalAgreement(Base):
    __tablename__ = "rental_agreements"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    # Agreement Terms
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    monthly_rent = Column(Float, nullable=False)
    security_deposit = Column(Float, nullable=False)
    maintenance_charges = Column(Float, default=0.0)
    notice_period_days = Column(Integer, default=30)

    # Financials
    security_deposit_paid = Column(Boolean, default=False)
    security_deposit_refunded = Column(Boolean, default=False)
    security_deposit_deduction = Column(Float, default=0.0)
    deduction_reason = Column(Text, nullable=True)

    # Rent Payment Day
    rent_due_day = Column(Integer, default=1)  # day of month rent is due
    late_fee_per_day = Column(Float, default=0.0)

    # Status & Notes
    status = Column(Enum(AgreementStatus), default=AgreementStatus.draft)
    terms_and_conditions = Column(Text, nullable=True)
    special_conditions = Column(Text, nullable=True)
    agreement_document = Column(String(500), nullable=True)  # file path

    # Termination
    terminated_at = Column(DateTime, nullable=True)
    termination_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    property = relationship("Property", back_populates="agreements")
    tenant = relationship("Tenant", back_populates="agreements")
    payments = relationship("Payment", back_populates="agreement", cascade="all, delete-orphan")
