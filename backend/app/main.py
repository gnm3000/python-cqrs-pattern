import logging

from api.routes import employees
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .dependencies import get_db

# Structured logging (JSON-like) so behavior logs quedan parseables.
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        fmt='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    )
)
logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
# Show per-query timings in console for the read-side behaviors (DEBUG for timing).
logging.getLogger("mediator.timing").setLevel(logging.DEBUG)

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
