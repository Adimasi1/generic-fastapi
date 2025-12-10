from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas import UserCreate, UserRead, Token
from app.services.user_service import create_user, verify_password, get_user_by_email
from app.auth import create_access_token
from app.database import get_db
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register(user_in:UserCreate, db: Session = Depends(get_db)):
  email=user_in.email
  if get_user_by_email(db, email): # check if the user is already in the database
    raise HTTPException(status_code=400, detail="Email already exists")
  return create_user(db, user_in)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
  user = get_user_by_email(db, form_data.username)
  if not user:
      raise HTTPException(status_code=401, detail="Invalid credentials")
  if not verify_password(form_data.password, user.hashed_password):
      raise HTTPException(status_code=401, detail="Invalid credentials")
  token = create_access_token(user.id)
  return Token(access_token=token)