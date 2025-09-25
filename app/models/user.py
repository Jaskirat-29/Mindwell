from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    COUNSELOR = "counselor"
    ADMIN = "admin"

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anonymous_id = Column(String(64), unique=True, index=True)  # For privacy
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    
    # Profile Information (encrypted)
    institution_code = Column(String(50), index=True)
    year_of_study = Column(Integer)
    department = Column(String(100))
    preferred_language = Column(String(10), default="en")
    
    # Status and Metadata
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    is_anonymous = Column(Boolean, default=True)
    last_risk_assessment = Column(Enum(RiskLevel), default=RiskLevel.LOW)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())
