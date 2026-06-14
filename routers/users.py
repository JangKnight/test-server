from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from fastapi import FastAPI, Depends, HTTPException
import os, base64, bcrypt
import models
from database import db_dependency
from routers.auth import user_dependency

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1)
    new_password: str = Field(min_length=1)

# get current logged in user details
@router.get("")
async def read_user(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    result = await db.execute(select(models.Users).where(models.Users.id == user.get("id")))
    user_details = result.scalars().first()
    if not user_details:
        raise HTTPException(status_code=404, detail=f"User with id {user.get('id')} not found")
    if user_details.id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{user.get('username')} does not have access to details of user with id {user.get('id')}")
    return user_details


@router.put("/pw")
async def change_password(request: ChangePasswordRequest, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    result = await db.execute(select(models.Users).where(models.Users.id == user.get("id")))
    user_details = result.scalars().first()
    if not user_details:
        raise HTTPException(status_code=404, detail=f"User with id {user.get('id')} not found")
    if user_details.id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{user.get('username')} does not have access to change password of user with id {user.get('id')}")
    if not bcrypt.checkpw(request.old_password.encode("utf-8"), user_details.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Old password is incorrect")
    hashed_pw = bcrypt.hashpw(request.new_password.encode("utf-8"), bcrypt.gensalt())
    user_details.hashed_password = hashed_pw.decode("utf-8")
    db.add(user_details)
    await db.commit()
    return {"message": "password changed successfully"}
