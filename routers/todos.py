from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import db_dependency
from routers.auth import user_dependency

router = APIRouter()

class TodosRequest(BaseModel):
    title: str
    description: Optional[str] = Field(min_length=1, max_length=256, default=None)
    priority: Optional[int] = Field(gt=0, lt=6, default=1)
    completed: Optional[bool] = Field(default=False)

@router.get("/")
async def read_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    result = await db.execute(select(models.Todos).where(models.Todos.owner_id == user.get("id")))
    return result.scalars().all()

@router.get("/todos/{todo_id}")
async def read_todo(todo_id: int, db: db_dependency, user: user_dependency):
    result = await db.execute(select(models.Todos).where(models.Todos.id == todo_id).where(models.Todos.owner_id == user.get("id")))
    todo = result.scalars().first()
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    if todo.owner_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{user.get('username')} does not have access to todo with id {todo_id}")
    return todo

@router.post("/todos")
async def create_todo(todo: TodosRequest, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    new_todo = models.Todos(**todo.model_dump(), owner_id=user.get("id"))
    db.add(new_todo)
    await db.commit()
    result = await db.execute(select(models.Todos).where(models.Todos.owner_id == user.get("id")))
    return result.scalars().all()

@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: db_dependency, user: user_dependency):
    result = await db.execute(select(models.Todos).where(models.Todos.id == todo_id).where(models.Todos.owner_id == user.get("id")))
    todo = result.scalars().first()
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    if todo.owner_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{user.get('username')} does not own todo with id {todo_id}")
    await db.delete(todo)
    await db.commit()
    result = await db.execute(select(models.Todos).where(models.Todos.owner_id == user.get("id")))
    return result.scalars().all()

@router.put("/todos/{todo_id}")
# user must send entire object even if fields are not changed as the entire object will be replaced with what is sent
async def update_todo(todo_id: int, todo: TodosRequest, db: db_dependency, user: user_dependency):
    result = await db.execute(select(models.Todos).where(models.Todos.id == todo_id).where(models.Todos.owner_id == user.get("id")))
    todo_to_update = result.scalars().first()
    if not todo_to_update:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    if todo_to_update.owner_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{user.get('username')} does not own todo with id {todo_id}")
    todo_to_update.title = todo.title
    if todo.description:
        todo_to_update.description = todo.description
    if todo.priority:
        todo_to_update.priority = todo.priority
    if todo.completed is not None:
        todo_to_update.completed = todo.completed
    await db.commit()
    result = await db.execute(select(models.Todos).where(models.Todos.owner_id == user.get("id")))
    return result.scalars().all()