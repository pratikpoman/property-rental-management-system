from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.maintenance import MaintenanceRequest, MaintenanceStatus, MaintenancePriority
from app.models.property import Property
from app.models.user import User
from app.schemas.maintenance import (
    MaintenanceCreate, MaintenanceUpdate, MaintenanceOut, MaintenanceResolve
)
from app.core.security import get_current_user

router = APIRouter(prefix="/maintenance", tags=["Maintenance Requests"])


@router.post("/", response_model=MaintenanceOut, status_code=status.HTTP_201_CREATED)
def create_request(
    data: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new maintenance request"""
    prop = db.query(Property).filter(
        Property.id == data.property_id,
        Property.owner_id == current_user.id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    request = MaintenanceRequest(**data.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/", response_model=List[MaintenanceOut])
def list_requests(
    property_id: Optional[int] = Query(None),
    status: Optional[MaintenanceStatus] = Query(None),
    priority: Optional[MaintenancePriority] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all maintenance requests for current owner's properties"""
    query = db.query(MaintenanceRequest).join(Property).filter(
        Property.owner_id == current_user.id
    )
    if property_id:
        query = query.filter(MaintenanceRequest.property_id == property_id)
    if status:
        query = query.filter(MaintenanceRequest.status == status)
    if priority:
        query = query.filter(MaintenanceRequest.priority == priority)

    return query.order_by(MaintenanceRequest.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{request_id}", response_model=MaintenanceOut)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific maintenance request"""
    request = db.query(MaintenanceRequest).join(Property).filter(
        MaintenanceRequest.id == request_id,
        Property.owner_id == current_user.id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    return request


@router.put("/{request_id}", response_model=MaintenanceOut)
def update_request(
    request_id: int,
    data: MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update maintenance request details or status"""
    request = db.query(MaintenanceRequest).join(Property).filter(
        MaintenanceRequest.id == request_id,
        Property.owner_id == current_user.id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)
    return request


@router.patch("/{request_id}/resolve", response_model=MaintenanceOut)
def resolve_request(
    request_id: int,
    data: MaintenanceResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a maintenance request as resolved"""
    request = db.query(MaintenanceRequest).join(Property).filter(
        MaintenanceRequest.id == request_id,
        Property.owner_id == current_user.id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    if request.status == MaintenanceStatus.resolved:
        raise HTTPException(status_code=400, detail="Request already resolved")

    request.status = MaintenanceStatus.resolved
    request.resolution_notes = data.resolution_notes
    request.repair_cost = data.repair_cost
    request.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(request)
    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a maintenance request"""
    request = db.query(MaintenanceRequest).join(Property).filter(
        MaintenanceRequest.id == request_id,
        Property.owner_id == current_user.id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")

    db.delete(request)
    db.commit()
