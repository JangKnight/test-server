from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String

from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=False)
    priority = Column(Integer, default=1)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    def __init__(
        self,
        title: str,
        description: str = None,
        priority: int = 1,
        completed: bool = False,
        owner_id: int = None,
    ):
        self.title = title
        self.description = description
        self.priority = priority
        self.completed = completed
        self.owner_id = owner_id


class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)  # dedup key
    event_name = Column(String, index=True)
    event_type = Column(String)
    timestamp = Column(DateTime)
    received_at = Column(DateTime, default=datetime.utcnow)
    anonymous_id = Column(String, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    session_id = Column(String, index=True)
    context = Column(JSON, nullable=True)
    properties = Column(JSON, nullable=True)
