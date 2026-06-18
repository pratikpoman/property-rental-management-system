from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.agreement import RentalAgreement, AgreementStatus
from app.models.property import Property, PropertyStatus
from app.models.user import User
from app.schemas.agreement import (
    AgreementCreate, AgreementUpdate, AgreementOut,
    AgreementActivate, AgreementTerminate
)
from app.core.security import get_current_user

router = APIRouter(prefix="/agreements", tags=["Rental Agreements"])


def _verify_property_owner(property_id: int, owner_id: int, db: Session) -> Property:
    prop = db.query(Property).filter(
        Property.id == property_id,
        Property.owner_id == owner_id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found or access denied")
    return prop


@router.post("/", response_model=AgreementOut, status_code=status.HTTP_201_CREATED)
def create_agreement(
    data: AgreementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new rental agreement (starts as draft)"""
    prop = _verify_property_owner(data.property_id, current_user.id, db)

    # Check no active agreement exists for this property
    existing_active = db.query(RentalAgreement).filter(
        RentalAgreement.property_id == data.property_id,
        RentalAgreement.status == AgreementStatus.active
    ).first()
    if existing_active:
        raise HTTPException(
            status_code=400,
            detail="Property already has an active rental agreement"
        )

    if data.start_date >= data.end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    agreement = RentalAgreement(**data.model_dump())
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return agreement


@router.get("/", response_model=List[AgreementOut])
def list_agreements(
    status: Optional[AgreementStatus] = Query(None),
    property_id: Optional[int] = Query(None),
    tenant_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all agreements for properties owned by current user"""
    query = db.query(RentalAgreement).join(Property).filter(
        Property.owner_id == current_user.id
    )
    if status:
        query = query.filter(RentalAgreement.status == status)
    if property_id:
        query = query.filter(RentalAgreement.property_id == property_id)
    if tenant_id:
        query = query.filter(RentalAgreement.tenant_id == tenant_id)

    return query.offset(skip).limit(limit).all()


@router.get("/expiring-soon", response_model=List[AgreementOut])
def get_expiring_agreements(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active agreements expiring within the next N days"""
    from datetime import timedelta
    threshold = datetime.utcnow() + timedelta(days=days)

    return db.query(RentalAgreement).join(Property).filter(
        Property.owner_id == current_user.id,
        RentalAgreement.status == AgreementStatus.active,
        RentalAgreement.end_date <= threshold
    ).all()


@router.get("/{agreement_id}", response_model=AgreementOut)
def get_agreement(
    agreement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific agreement"""
    agreement = db.query(RentalAgreement).join(Property).filter(
        RentalAgreement.id == agreement_id,
        Property.owner_id == current_user.id
    ).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    return agreement


@router.put("/{agreement_id}", response_model=AgreementOut)
def update_agreement(
    agreement_id: int,
    data: AgreementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a draft agreement"""
    agreement = db.query(RentalAgreement).join(Property).filter(
        RentalAgreement.id == agreement_id,
        Property.owner_id == current_user.id
    ).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    if agreement.status not in (AgreementStatus.draft,):
        raise HTTPException(status_code=400, detail="Only draft agreements can be updated")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agreement, field, value)

    db.commit()
    db.refresh(agreement)
    return agreement


@router.patch("/{agreement_id}/activate", response_model=AgreementOut)
def activate_agreement(
    agreement_id: int,
    data: AgreementActivate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate a draft agreement"""
    agreement = db.query(RentalAgreement).join(Property).filter(
        RentalAgreement.id == agreement_id,
        Property.owner_id == current_user.id
    ).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    if agreement.status != AgreementStatus.draft:
        raise HTTPException(status_code=400, detail="Only draft agreements can be activated")

    agreement.status = AgreementStatus.active
    agreement.security_deposit_paid = data.security_deposit_paid

    # Mark property as occupied
    prop = db.query(Property).filter(Property.id == agreement.property_id).first()
    prop.status = PropertyStatus.occupied

    db.commit()
    db.refresh(agreement)
    return agreement


@router.patch("/{agreement_id}/terminate", response_model=AgreementOut)
def terminate_agreement(
    agreement_id: int,
    data: AgreementTerminate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Terminate an active agreement"""
    agreement = db.query(RentalAgreement).join(Property).filter(
        RentalAgreement.id == agreement_id,
        Property.owner_id == current_user.id
    ).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    if agreement.status != AgreementStatus.active:
        raise HTTPException(status_code=400, detail="Only active agreements can be terminated")

    agreement.status = AgreementStatus.terminated
    agreement.terminated_at = datetime.utcnow()
    agreement.termination_reason = data.termination_reason
    agreement.security_deposit_deduction = data.security_deposit_deduction
    agreement.deduction_reason = data.deduction_reason

    # Mark property as vacant
    prop = db.query(Property).filter(Property.id == agreement.property_id).first()
    prop.status = PropertyStatus.vacant

    db.commit()
    db.refresh(agreement)
    return agreement
