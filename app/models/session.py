from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    session_type = Column(String(50), default="ai_chat")  # ai_chat, peer_support, counselor
    
    # Session Data
    conversation_history = Column(JSON)
    mood_scores = Column(JSON)  # Track mood throughout session
    crisis_flags = Column(JSON)  # Any crisis indicators detected
    
    # Metadata
    duration_minutes = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 scale
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
