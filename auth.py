from datetime import datetime, timedelta
from typing import Optional
import jwt
import requests
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel
from database import SessionLocal, User
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv

load_dotenv()

# Password hashing context
# Using bcrypt but with additional error handling for compatibility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# Security scheme for API docs
security = HTTPBearer()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password, ensuring it doesn't exceed bcrypt length limits"""
    # Bcrypt has a 72-byte password limit, so we truncate if necessary
    truncated_password = password[:72] if len(password) > 72 else password
    return pwd_context.hash(truncated_password)

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user by username and password"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(security)) -> User:
    """Get the current user from the token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == token_data.username).first()
        if user is None:
            raise credentials_exception
        return user
    finally:
        db.close()

def register_user(db: Session, user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )

    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )


class GitHubLoginRequest(BaseModel):
    code: str


def get_or_create_github_user(db: Session, github_user_data: dict):
    """Get existing user by GitHub ID or create a new one"""
    # Check if user already exists by GitHub ID
    user = db.query(User).filter(User.github_id == str(github_user_data['id'])).first()

    if user:
        return user

    # Check if user exists by email
    user = db.query(User).filter(User.email == github_user_data['email']).first()

    if user:
        # Update with GitHub ID
        user.github_id = str(github_user_data['id'])
        db.commit()
        db.refresh(user)
        return user

    # Create new user
    username = github_user_data.get('login', github_user_data.get('email', '').split('@')[0])
    full_name = github_user_data.get('name', username)

    # Ensure username is unique
    existing_username = db.query(User).filter(User.username == username).first()
    counter = 1
    original_username = username
    while existing_username:
        username = f"{original_username}{counter}"
        existing_username = db.query(User).filter(User.username == username).first()
        counter += 1

    db_user = User(
        username=username,
        email=github_user_data.get('email', ''),
        full_name=full_name,
        github_id=str(github_user_data['id'])
    )

    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        # Fallback: create user with different username
        db_user = User(
            username=f"github_user_{github_user_data['id']}",
            email=github_user_data.get('email', ''),
            full_name=full_name,
            github_id=str(github_user_data['id'])
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


async def github_login(code: str):
    """Handle GitHub OAuth login flow"""
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub OAuth not configured"
        )

    # Exchange code for access token
    token_response = requests.post(
        'https://github.com/login/oauth/access_token',
        data={
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
        },
        headers={'Accept': 'application/json'}
    )

    token_data = token_response.json()
    access_token = token_data.get('access_token')

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid GitHub authorization code"
        )

    # Get user info from GitHub
    user_response = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'token {access_token}'}
    )

    github_user_data = user_response.json()

    # Get user's email if not included in basic profile
    if not github_user_data.get('email'):
        emails_response = requests.get(
            'https://api.github.com/user/emails',
            headers={'Authorization': f'token {access_token}'}
        )
        emails = emails_response.json()
        primary_email = next((email['email'] for email in emails if email['primary']), None)
        github_user_data['email'] = primary_email or ''

    # Get or create user in our database
    db = SessionLocal()
    try:
        user = get_or_create_github_user(db, github_user_data)

        # Create access token
        access_token = create_access_token(data={"sub": user.username})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "github_id": user.github_id
            }
        }
    finally:
        db.close()