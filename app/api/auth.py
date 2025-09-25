from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import *
from app.models.user import User
import asyncio

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    institution_code: str
    year_of_study: int
    department: str
    preferred_language: str = "en"
    is_anonymous: bool = True

class UserResponse(BaseModel):
    id: str
    anonymous_id: str
    institution_code: str
    role: str
    is_anonymous: bool

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register new user (anonymous or with credentials)"""
    
    # Check if email already exists (if provided)
    if user_data.email:
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    # Create new user
    user = User(
        anonymous_id=generate_anonymous_id(),
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password) if user_data.password else None,
        institution_code=user_data.institution_code,
        year_of_study=user_data.year_of_study,
        department=user_data.department,
        preferred_language=user_data.preferred_language,
        is_anonymous=user_data.is_anonymous
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        anonymous_id=user.anonymous_id,
        institution_code=user.institution_code,
        role=user.role.value,
        is_anonymous=user.is_anonymous
    )

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), 
                db: AsyncSession = Depends(get_db)):
    """Login with credentials or anonymous ID"""
    
    # Try to authenticate with email/password
    if "@" in form_data.username:
        result = await db.execute(select(User).where(User.email == form_data.username))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
    else:
        # Anonymous login with anonymous_id
        result = await db.execute(select(User).where(User.anonymous_id == form_data.username))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid anonymous ID"
            )
    
    # Create access token
    access_token = create_access_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }

async def get_current_user(token: str = Depends(oauth2_scheme), 
                          db: AsyncSession = Depends(get_db)) -> User:
    """Get current authenticated user"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
