from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class PropertyType(str, enum.Enum):
    apartment = "apartment"
    villa = "villa"
    commercial = "commercial"
    studio = "studio"
    house = "house"


class PropertyStatus(str, enum.Enum):
    vacant = "vacant"
    occupied = "occupied"
    maintenance = "maintenance"
    unavailable = "unavailable"


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    property_type = Column(Enum(PropertyType), nullable=False)
    status = Column(Enum(PropertyStatus), default=PropertyStatus.vacant)

    # Location
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=True)

    # Details
    bedrooms = Column(Integer, default=1)
    bathrooms = Column(Integer, default=1)
    area_sqft = Column(Float, nullable=True)
    floor_number = Column(Integer, nullable=True)
    total_floors = Column(Integer, nullable=True)

    # Financials
    monthly_rent = Column(Float, nullable=False)
    security_deposit = Column(Float, nullable=False)
    maintenance_charges = Column(Float, default=0.0)

    # Amenities (comma-separated)
    amenities = Column(Text, nullable=True)
    is_furnished = Column(Boolean, default=False)
    parking_available = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="properties")
    agreements = relationship("RentalAgreement", back_populates="property", cascade="all, delete-orphan")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property", cascade="all, delete-orphan")
