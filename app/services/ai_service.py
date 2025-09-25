import asyncio
from typing import List, Dict, Tuple
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import re
import json

class MentalHealthAI:
    def __init__(self):
        self.crisis_keywords = [
            "suicide", "kill myself", "end it all", "no point", "hopeless",
            "hurt myself", "self harm", "cutting", "overdose", "jump"
        ]
        self.anxiety_keywords = [
            "anxious", "panic", "worry", "nervous", "stress", "overwhelmed"
        ]
        self.depression_keywords = [
            "sad", "depressed", "empty", "worthless", "tired", "sleep"
        ]
        
        # Load pre-trained model (if available)
        self.classifier = None
        self.vectorizer = None
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained AI model for mental health classification"""
        try:
            with open(f"{settings.AI_MODEL_PATH}/classifier.pkl", "rb") as f:
                self.classifier = pickle.load(f)
            with open(f"{settings.AI_MODEL_PATH}/vectorizer.pkl", "rb") as f:
                self.vectorizer = pickle.load(f)
        except FileNotFoundError:
            # Use rule-based system if no trained model available
            pass
    
    async def analyze_message(self, message: str) -> Dict:
        """Analyze user message for mental health indicators"""
        analysis = {
            "sentiment": await self._analyze_sentiment(message),
            "risk_level": await self._assess_risk_level(message),
            "crisis_indicators": await self._detect_crisis(message),
            "recommended_response": await self._generate_response(message),
            "mood_score": await self._calculate_mood_score(message)
        }
        return analysis
    
    async def _analyze_sentiment(self, message: str) -> str:
        """Basic sentiment analysis"""
        message_lower = message.lower()
        positive_words = ["good", "happy", "better", "improved", "grateful"]
        negative_words = ["bad", "sad", "worse", "terrible", "awful"]
        
        pos_count = sum(1 for word in positive_words if word in message_lower)
        neg_count = sum(1 for word in negative_words if word in message_lower)
        
        if neg_count > pos_count:
            return "negative"
        elif pos_count > neg_count:
            return "positive"
        else:
            return "neutral"
    
    async def _assess_risk_level(self, message: str) -> str:
        """Assess mental health risk level"""
        message_lower = message.lower()
        
        crisis_count = sum(1 for keyword in self.crisis_keywords 
                          if keyword in message_lower)
        
        if crisis_count >= 2:
            return "critical"
        elif crisis_count == 1:
            return "high"
        elif any(keyword in message_lower for keyword in self.depression_keywords):
            return "moderate"
        else:
            return "low"
    
    async def _detect_crisis(self, message: str) -> List[str]:
        """Detect crisis indicators in message"""
        indicators = []
        message_lower = message.lower()
        
        for keyword in self.crisis_keywords:
            if keyword in message_lower:
                indicators.append(keyword)
        
        return indicators
    
    async def _generate_response(self, message: str) -> str:
        """Generate appropriate AI response"""
        risk_level = await self._assess_risk_level(message)
        
        if risk_level == "critical":
            return ("I'm very concerned about what you've shared. Your safety is important. "
                   "Please reach out to a counselor immediately or contact emergency services. "
                   "Would you like me to connect you with immediate help?")
        
        elif risk_level == "high":
            return ("Thank you for sharing this with me. It sounds like you're going through "
                   "a difficult time. I'd like to connect you with a professional counselor "
                   "who can provide proper support. In the meantime, here are some immediate "
                   "coping strategies...")
        
        elif risk_level == "moderate":
            return ("I understand you're facing some challenges. Many students experience "
                   "similar feelings. Let's explore some coping strategies and resources "
                   "that might help...")
        
        else:
            return ("Thank you for reaching out. How are you feeling today? "
                   "I'm here to listen and provide support.")
    
    async def _calculate_mood_score(self, message: str) -> float:
        """Calculate mood score from 1-10"""
        sentiment = await self._analyze_sentiment(message)
        risk_level = await self._assess_risk_level(message)
        
        base_score = 5.0
        
        if sentiment == "positive":
            base_score += 2.0
        elif sentiment == "negative":
            base_score -= 2.0
        
        if risk_level == "critical":
            base_score = min(base_score, 2.0)
        elif risk_level == "high":
            base_score = min(base_score, 3.0)
        elif risk_level == "moderate":
            base_score = min(base_score, 4.0)
        
        return max(1.0, min(10.0, base_score))

ai_service = MentalHealthAI()
