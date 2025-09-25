from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List
import json
from datetime import datetime
from app.core.database import get_db
from app.core.cache import cache
from app.api.auth import get_current_user
from app.models.user import User
from app.models.session import ChatSession
from app.services.ai_service import ai_service
import asyncio

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    mood_score: float
    risk_level: str
    crisis_alert: bool

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_data: ChatMessage,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Handle AI chat conversation"""
    
    # Analyze message with AI service
    analysis = await ai_service.analyze_message(chat_data.message)
    
    # Get or create chat session
    session = None
    if chat_data.session_id:
        session = await db.get(ChatSession, chat_data.session_id)
    
    if not session:
        session = ChatSession(
            user_id=current_user.id,
            conversation_history=[],
            mood_scores=[],
            crisis_flags=[]
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
    
    # Update conversation history
    conversation_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_message": chat_data.message,
        "ai_response": analysis["recommended_response"],
        "mood_score": analysis["mood_score"],
        "risk_level": analysis["risk_level"]
    }
    
    session.conversation_history.append(conversation_entry)
    session.mood_scores.append(analysis["mood_score"])
    session.message_count += 1
    
    # Handle crisis situation
    crisis_alert = analysis["risk_level"] in ["high", "critical"]
    if crisis_alert:
        session.crisis_flags.append({
            "timestamp": datetime.utcnow().isoformat(),
            "indicators": analysis["crisis_indicators"],
            "risk_level": analysis["risk_level"]
        })
        
        # Trigger emergency response in background
        background_tasks.add_task(handle_crisis_response, current_user.id, analysis)
    
    # Update session in database
    await db.commit()
    
    # Cache recent conversation for quick access
    cache_key = f"chat_session:{session.id}"
    await cache.set(cache_key, {
        "conversation_history": session.conversation_history[-10:],  # Last 10 messages
        "current_mood": analysis["mood_score"],
        "risk_level": analysis["risk_level"]
    })
    
    return ChatResponse(
        response=analysis["recommended_response"],
        session_id=str(session.id),
        mood_score=analysis["mood_score"],
        risk_level=analysis["risk_level"],
        crisis_alert=crisis_alert
    )

async def handle_crisis_response(user_id: str, analysis: dict):
    """Handle crisis situation - notify counselors, log incident"""
    # This would typically:
    # 1. Notify available counselors
    # 2. Send alert to admin dashboard
    # 3. Log crisis incident
    # 4. Potentially contact emergency services
    pass

@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get chat session history"""
    
    # Check cache first
    cache_key = f"chat_session:{session_id}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Fetch from database
    session = await db.get(ChatSession, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "conversation_history": session.conversation_history,
        "mood_scores": session.mood_scores,
        "session_stats": {
            "duration_minutes": session.duration_minutes,
            "message_count": session.message_count,
            "average_mood": sum(session.mood_scores) / len(session.mood_scores) if session.mood_scores else 0
        }
    }
