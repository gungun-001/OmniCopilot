from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import get_db
import models
from utils.auth_utils import get_password_hash, verify_password, create_access_token

router = APIRouter()

# --- Schemas ---
class UserSignup(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Routes ---

@router.post("/signup")
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    # 1. Check if passwords match
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # 2. Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 3. Create new user
    new_user = models.User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}

@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # 1. Find user
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # 2. Create JWT
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        }
    }

class AuthGoogleRequest(BaseModel):
    code: str

@router.post("/google")
async def auth_google(request: AuthGoogleRequest):
    return {
        "message": "Google authentication successful (Mocked for now)",
        "token": "mock_jwt_token_for_user"
    }
