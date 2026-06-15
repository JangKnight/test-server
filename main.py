import os
from contextlib import asynccontextmanager
from typing import Annotated, Optional

import aio_pika
from fastapi import Depends, FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, SessionLocal, engine, get_db, init_db
from models import Todos, Users
from routers import admin, auth, events, todos, users

base_dir = os.path.dirname(os.path.abspath(__file__))
favicon_path = os.path.join(base_dir, "favicon.ico")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.declare_queue("events", durable=True)
    app.state.rabbit_channel = channel
    yield
    await connection.close()


app = FastAPI(
    title="TAPI",
    description="Todos API built with FastAPI and PostgreSQL",
    version="2.2.2",
    lifespan=lifespan,
    root_path="/api",
    docs_url=None,
    redoc_url=None,
)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(events.router)

Instrumentator().instrument(app).expose(app, include_in_schema=False)

# -----Configs-----
origins = [
    "localhost",
    "anthonysjhenry.com",
    "www.anthonysjhenry.com",
    "server",
    "client",
]
allowed_hosts = [
    "localhost",
    "*.anthonysjhenry.com",
    "anthonysjhenry.com",
    "client",
    "server",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts,
)
# -----End of Configs-----


# -----Additional Routes(not included in OpenAPI schema)-----
@app.get("/healthy", include_in_schema=False)
async def healthy():
    return {"status": "healthy", "message": "TAPI is healthy and running"}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        title=app.title,
        openapi_url="/api/openapi.json",
        swagger_favicon_url="./favicon.ico",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/api/openapi.json",
        title=app.title,
        redoc_favicon_url="/favicon.ico",
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


# -----End of Additional Routes-----
