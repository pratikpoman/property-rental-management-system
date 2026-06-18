from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.agreement import AgreementStatus


class AgreementBase(BaseModel):
    property_id: int
    tenant_id: int
    start_date: datetime
    end_date: datetime
    monthly_rent: float = Field(..., gt=0)
    security_deposit: float = Field(..., ge=0)
    maintenance_charges: float = Field(default=0.0, ge=0)
    notice_period_days: int = Field(default=30, ge=0)
    rent_due_day: int = Field(default=1, ge=1, le=28)
    late_fee_per_day: float = Field(default=0.0, ge=0)
    terms_and_conditions: Optional[str] = None
    special_conditions: Optional[str] = None


class AgreementCreate(AgreementBase):
    pass


class AgreementUpdate(BaseModel):
    end_date: Optional[datetime] = None
    monthly_rent: Optional[float] = None
    maintenance_charges: Optional[float] = None
    notice_period_days: Optional[int] = None
    rent_due_day: Optional[int] = None
    late_fee_per_day: Optional[float] = None
    terms_and_conditions: Optional[str] = None
    special_conditions: Optional[str] = None
    status: Optional[AgreementStatus] = None


class AgreementActivate(BaseModel):
    security_deposit_paid: bool = True


class AgreementTerminate(BaseModel):
    termination_reason: str
    security_deposit_deduction: float = Field(default=0.0, ge=0)
    deduction_reason: Optional[str] = None


class AgreementOut(AgreementBase):
    id: int
    status: AgreementStatus
    security_deposit_paid: bool
    security_deposit_refunded: bool
    security_deposit_deduction: float
    terminated_at: Optional[datetime]
    termination_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
