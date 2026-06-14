import os, base64, bcrypt, models
from fastapi import APIRouter, Depends, HTTPException, status, security
from pydantic import BaseModel, Field
from sqlalchemy import select
from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from database import db_dependency
from dotenv import load_dotenv
load_dotenv(override=True)



router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
oauth = security.OAuth2PasswordRequestForm
bearer = security.OAuth2PasswordBearer(tokenUrl='/api/auth/token')
# openssl rand -hex 32
SK = os.getenv("SK")
key = bytes.fromhex(SK)
ALGO = 'HS256'
ALLOWED_SIGNUP_ROLES = {"user", "admin"}
ROLE_OVERRIDE_SECRET = os.getenv("ROLE_OVERRIDE_SECRET")

b64_str = base64.b64encode(key).decode('utf-8')
b64url_str = base64.urlsafe_b64encode(key).decode('utf-8').rstrip('=')




async def auth(username: str, password: str, db: db_dependency):
    statement = select(models.Users).filter(models.Users.username == username)
    result = await db.execute(statement)
    user = result.scalars().first()
    if not user:
        return False
    if not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        return False
    return user

async def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    claims = {'sub': username, 'id': user_id, 'role': role, 'exp': expires}
    return jwt.encode(claims, key, algorithm=ALGO)

async def get_current_user(token: Annotated[str, Depends(bearer)], db: db_dependency):
    try:
        payload = jwt.decode(token, key, algorithms=[ALGO])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username, "id": user_id, "role": role}
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
user_dependency = Annotated[dict, Depends(get_current_user)]


class CreateUserRequest(BaseModel):
    email: str = Field(min_length=1, max_length=256)
    username: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=1, max_length=256)
    first_name: str = Field(min_length=1, max_length=256)
    last_name: str = Field(min_length=1, max_length=256)
    role: Optional[str] = Field(default="user", min_length=1, max_length=256) 
    role_secret: Optional[str] = Field(default=None, max_length=256)  




@router.post("")
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    
    if not create_user_request.email.strip() or not create_user_request.username.strip() or not create_user_request.password.strip():
        raise HTTPException(status_code=400, detail="Email, username, and password are required and cannot be empty")
    
    if create_user_request.role.strip().lower() not in ALLOWED_SIGNUP_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    if create_user_request.role.strip().lower() == "admin":
        if not ROLE_OVERRIDE_SECRET or create_user_request.role_secret != ROLE_OVERRIDE_SECRET:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to assign this role",
            )
    
    statement = select(models.Users).filter(models.Users.email == create_user_request.email)
    result = await db.execute(statement)
    userCheck = result.scalars().first()
    if userCheck:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    statement = select(models.Users).filter(models.Users.username == create_user_request.username)
    result = await db.execute(statement)
    userCheck = result.scalars().first()
    if userCheck:
        raise HTTPException(status_code=400, detail="User with this username already exists")

    # hpw = bcrypt.hashpw(encoded_pw, salt)
    hashed_pw = bcrypt.hashpw(create_user_request.password.encode("utf-8"), bcrypt.gensalt())

    user = models.Users(
        email=create_user_request.email.strip(),
        username=create_user_request.username.strip(),
        hashed_password=hashed_pw.decode("utf-8"),
        first_name=create_user_request.first_name.strip(),
        last_name=create_user_request.last_name.strip(),
        role=create_user_request.role.strip().lower() if create_user_request.role else "user"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": "User created successfully", "user": user}


@router.post("/token")
async def login(form_data: Annotated[oauth, Depends()], db: db_dependency):
    user = await auth(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = await create_access_token(user.username, user.id, user.role, timedelta(minutes=30))
    return {"message": "login successful", "access_token":  token, "token_type": "bearer"}
