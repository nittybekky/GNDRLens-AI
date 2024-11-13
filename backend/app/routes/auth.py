from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel


from ..models.user import User
from ..utils.security import hash_password, verify_password, create_access_token
# Update this line in app/routes/auth.py
from ..models.base import get_db

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserCreate(BaseModel):
    email: str
    password: str
    role: str

@router.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    if user_data.role not in ["HR", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    return {"msg": "User registered successfully"}


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
