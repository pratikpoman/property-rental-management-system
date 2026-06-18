from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.property import PropertyType, PropertyStatus


class PropertyBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    property_type: PropertyType
    address: str
    city: str
    state: str
    zip_code: Optional[str] = None
    bedrooms: int = Field(default=1, ge=0)
    bathrooms: int = Field(default=1, ge=0)
    area_sqft: Optional[float] = None
    floor_number: Optional[int] = None
    total_floors: Optional[int] = None
    monthly_rent: float = Field(..., gt=0)
    security_deposit: float = Field(..., ge=0)
    maintenance_charges: float = Field(default=0.0, ge=0)
    amenities: Optional[str] = None
    is_furnished: bool = False
    parking_available: bool = False


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area_sqft: Optional[float] = None
    monthly_rent: Optional[float] = None
    security_deposit: Optional[float] = None
    maintenance_charges: Optional[float] = None
    amenities: Optional[str] = None
    is_furnished: Optional[bool] = None
    parking_available: Optional[bool] = None


class PropertyOut(PropertyBase):
    id: int
    owner_id: int
    status: PropertyStatus
    created_at: datetime

    class Config:
        from_attributes = True


class PropertyFilter(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None
    min_rent: Optional[float] = None
    max_rent: Optional[float] = None
    bedrooms: Optional[int] = None
    is_furnished: Optional[bool] = None
