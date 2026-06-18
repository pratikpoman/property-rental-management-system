from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.maintenance import MaintenancePriority, MaintenanceStatus


class MaintenanceBase(BaseModel):
    property_id: int
    title: str = Field(..., min_length=3, max_length=200)
    description: str
    category: Optional[str] = None
    priority: MaintenancePriority = MaintenancePriority.medium


class MaintenanceCreate(MaintenanceBase):
    tenant_id: Optional[int] = None


class MaintenanceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[MaintenancePriority] = None
    status: Optional[MaintenanceStatus] = None
    resolution_notes: Optional[str] = None
    repair_cost: Optional[int] = None


class MaintenanceResolve(BaseModel):
    resolution_notes: str
    repair_cost: int = Field(default=0, ge=0)


class MaintenanceOut(MaintenanceBase):
    id: int
    tenant_id: Optional[int]
    status: MaintenanceStatus
    resolution_notes: Optional[str]
    resolved_at: Optional[datetime]
    repair_cost: int
    created_at: datetime

    class Config:
        from_attributes = True
