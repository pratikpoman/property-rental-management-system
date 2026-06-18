from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.tenant import TenantStatus, IDProofType


class TenantBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: str
    alternate_phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    permanent_address: Optional[str] = None
    current_address: Optional[str] = None
    id_proof_type: Optional[IDProofType] = None
    id_proof_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    occupation: Optional[str] = None
    employer_name: Optional[str] = None
    monthly_income: Optional[int] = None
    notes: Optional[str] = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    current_address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    occupation: Optional[str] = None
    employer_name: Optional[str] = None
    monthly_income: Optional[int] = None
    status: Optional[TenantStatus] = None
    notes: Optional[str] = None


class TenantOut(TenantBase):
    id: int
    status: TenantStatus
    created_at: datetime

    class Config:
        from_attributes = True
