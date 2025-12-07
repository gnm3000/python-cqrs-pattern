from collections.abc import Generator

import pytest
from app.database import Base
from app.main import app, get_db
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker[Session](autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def override_get_db() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)

    def _get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def test_full_employee_crud_flow(client: TestClient) -> None:
    payload = {
        "name": "Jane",
        "lastname": "Doe",
        "salary": 75000.0,
        "address": "123 Main St",
        "in_vacation": False,
    }

    create_response = client.post("/employees", json=payload)
    assert create_response.status_code == 201
    employee = create_response.json()
    assert employee["id"] == 1
    assert employee["name"] == payload["name"]
    assert employee["in_vacation"] is False

    list_response = client.get("/employees")
    assert list_response.status_code == 200
    employees = list_response.json()
    assert len(employees) == 1

    update_payload = {**payload, "in_vacation": True}
    update_response = client.put("/employees/1", json=update_payload)
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["in_vacation"] is True

    delete_response = client.delete("/employees/1")
    assert delete_response.status_code == 204

    final_list = client.get("/employees")
    assert final_list.status_code == 200
    assert final_list.json() == []
