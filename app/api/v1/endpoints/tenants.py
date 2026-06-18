from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.tenant import Tenant, TenantStatus
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantOut
from app.core.security import get_current_user

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("/", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
def create_tenant(
    data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new tenant"""
    existing = db.query(Tenant).filter(Tenant.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tenant with this email already exists")

    tenant = Tenant(**data.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("/", response_model=List[TenantOut])
def list_tenants(
    status: Optional[TenantStatus] = Query(None),
    search: Optional[str] = Query(None, description="Search by name, email or phone"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all tenants"""
    query = db.query(Tenant)

    if status:
        query = query.filter(Tenant.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Tenant.full_name.ilike(search_term) |
            Tenant.email.ilike(search_term) |
            Tenant.phone.ilike(search_term)
        )

    return query.offset(skip).limit(limit).all()


@router.get("/{tenant_id}", response_model=TenantOut)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a tenant by ID"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.put("/{tenant_id}", response_model=TenantOut)
def update_tenant(
    tenant_id: int,
    data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update tenant details"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a tenant record"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    from app.models.agreement import RentalAgreement, AgreementStatus
    active = db.query(RentalAgreement).filter(
        RentalAgreement.tenant_id == tenant_id,
        RentalAgreement.status == AgreementStatus.active
    ).first()
    if active:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete tenant with an active rental agreement"
        )

    db.delete(tenant)
    db.commit()


@router.get("/{tenant_id}/history", response_model=dict)
def get_tenant_history(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get full rental and payment history for a tenant"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    from app.models.agreement import RentalAgreement
    from app.models.payment import Payment, PaymentStatus
    from app.schemas.agreement import AgreementOut
    from app.schemas.payment import PaymentOut

    agreements = db.query(RentalAgreement).filter(
        RentalAgreement.tenant_id == tenant_id
    ).all()

    total_paid = db.query(Payment).join(RentalAgreement).filter(
        RentalAgreement.tenant_id == tenant_id,
        Payment.status == PaymentStatus.paid
    ).with_entities(Payment.amount_paid).all()

    return {
        "tenant": TenantOut.model_validate(tenant).model_dump(),
        "total_agreements": len(agreements),
        "total_paid": sum(p[0] for p in total_paid),
        "agreements": [AgreementOut.model_validate(a).model_dump() for a in agreements]
    }
