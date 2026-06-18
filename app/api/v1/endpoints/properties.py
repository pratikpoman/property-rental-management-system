from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.property import Property, PropertyStatus, PropertyType
from app.models.user import User
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyOut
from app.core.security import get_current_user

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("/", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
def create_property(
    data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new property listing"""
    prop = Property(**data.model_dump(), owner_id=current_user.id)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.get("/", response_model=List[PropertyOut])
def list_properties(
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    property_type: Optional[PropertyType] = Query(None),
    status: Optional[PropertyStatus] = Query(None),
    min_rent: Optional[float] = Query(None),
    max_rent: Optional[float] = Query(None),
    bedrooms: Optional[int] = Query(None),
    is_furnished: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all properties owned by current user with optional filters"""
    query = db.query(Property).filter(Property.owner_id == current_user.id)

    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(Property.state.ilike(f"%{state}%"))
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if status:
        query = query.filter(Property.status == status)
    if min_rent is not None:
        query = query.filter(Property.monthly_rent >= min_rent)
    if max_rent is not None:
        query = query.filter(Property.monthly_rent <= max_rent)
    if bedrooms is not None:
        query = query.filter(Property.bedrooms == bedrooms)
    if is_furnished is not None:
        query = query.filter(Property.is_furnished == is_furnished)

    return query.offset(skip).limit(limit).all()


@router.get("/{property_id}", response_model=PropertyOut)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific property by ID"""
    prop = db.query(Property).filter(
        Property.id == property_id,
        Property.owner_id == current_user.id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.put("/{property_id}", response_model=PropertyOut)
def update_property(
    property_id: int,
    data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a property"""
    prop = db.query(Property).filter(
        Property.id == property_id,
        Property.owner_id == current_user.id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prop, field, value)

    db.commit()
    db.refresh(prop)
    return prop


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a property"""
    prop = db.query(Property).filter(
        Property.id == property_id,
        Property.owner_id == current_user.id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    # Check no active agreements
    from app.models.agreement import RentalAgreement, AgreementStatus
    active = db.query(RentalAgreement).filter(
        RentalAgreement.property_id == property_id,
        RentalAgreement.status == AgreementStatus.active
    ).first()
    if active:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete property with an active rental agreement"
        )

    db.delete(prop)
    db.commit()


@router.patch("/{property_id}/status", response_model=PropertyOut)
def update_property_status(
    property_id: int,
    new_status: PropertyStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update just the status of a property"""
    prop = db.query(Property).filter(
        Property.id == property_id,
        Property.owner_id == current_user.id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    prop.status = new_status
    db.commit()
    db.refresh(prop)
    return prop
