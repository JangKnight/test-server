from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import db_dependency
from routers.auth import user_dependency

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/todos")
async def manage_todos(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    result = await db.execute(select(models.Todos))
    return result.scalars().all()

@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    result = await db.execute(select(models.Todos).where(models.Todos.id == todo_id))
    todo = result.scalars().first()
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    await db.delete(todo)
    await db.commit()
    result = await db.execute(select(models.Todos))
    return result.scalars().all()

@router.get("/users")
async def manage_users(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    result = await db.execute(select(models.Users))
    return result.scalars().all()

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    result = await db.execute(select(models.Users).where(models.Users.id == user_id))
    user_to_delete = result.scalars().first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    await db.delete(user_to_delete)
    await db.commit()
    result = await db.execute(select(models.Users))
    return result.scalars().all()
