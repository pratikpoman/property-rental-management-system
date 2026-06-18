from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class TenantStatus(str, enum.Enum):
    active = "active"
    former = "former"
    blacklisted = "blacklisted"


class IDProofType(str, enum.Enum):
    aadhar = "aadhar"
    passport = "passport"
    driving_license = "driving_license"
    voter_id = "voter_id"
    pan_card = "pan_card"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Personal Info
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    alternate_phone = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)

    # Address
    permanent_address = Column(Text, nullable=True)
    current_address = Column(Text, nullable=True)

    # ID Proof
    id_proof_type = Column(Enum(IDProofType), nullable=True)
    id_proof_number = Column(String(100), nullable=True)
    id_proof_document = Column(String(500), nullable=True)  # file path

    # Emergency Contact
    emergency_contact_name = Column(String(150), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relation = Column(String(50), nullable=True)

    # Professional Info
    occupation = Column(String(100), nullable=True)
    employer_name = Column(String(200), nullable=True)
    monthly_income = Column(Integer, nullable=True)

    # Status
    status = Column(Enum(TenantStatus), default=TenantStatus.active)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="tenant_profile")
    agreements = relationship("RentalAgreement", back_populates="tenant", cascade="all, delete-orphan")
