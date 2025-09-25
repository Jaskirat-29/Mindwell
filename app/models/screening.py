from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class ScreeningResult(Base):
    __tablename__ = "screening_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    
    # Screening Scores
    phq9_score = Column(Integer, nullable=True)  # Depression
    gad7_score = Column(Integer, nullable=True)  # Anxiety
    stress_score = Column(Integer, nullable=True)  # Academic stress
    sleep_score = Column(Integer, nullable=True)  # Sleep quality
    
    # Risk Assessment
    overall_risk_score = Column(Float)
    risk_level = Column(Enum(RiskLevel))
    risk_factors = Column(JSON)  # List of identified risk factors
    
    # Recommendations
    recommended_actions = Column(JSON)
    referral_needed = Column(Boolean, default=False)
    
    # Timestamps
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="screening_results")
