from api.routes import employees
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .dependencies import get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee CRUD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
# Re-export get_db so tests and routers can import from app.main
__all__ = ["app", "get_db"]
