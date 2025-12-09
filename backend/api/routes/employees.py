from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

import msgpack
from app import models, schemas
from app.dependencies import get_db
from application.commands.employees import (
    CreateEmployeeCommand,
    DeleteEmployeeCommand,
    UpdateEmployeeCommand,
)
from application.mediator.mediator import Mediator
from application.mediator.registry import create_mediator
from application.queries.employees import GetEmployeeByIdQuery, GetEmployeesQuery
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

router = APIRouter(prefix="/employees", tags=["employees"])


def get_mediator(db: Session = Depends(get_db)) -> Mediator:
    mediator = create_mediator(db)
    return mediator


def _compute_etag(payload: Sequence[Any]) -> str:
    packed = msgpack.packb(payload, use_bin_type=True)
    # BLAKE2b is fast and suitable for non-cryptographic content hashing (ETag).
    return hashlib.blake2b(packed, digest_size=16).hexdigest()


@router.get("", response_model=list[schemas.Employee])
def list_employees(
    request: Request, response: Response, mediator: Mediator = Depends(get_mediator)
) -> list[models.Employee]:
    employees = mediator.send(GetEmployeesQuery())
    etag = _compute_etag(employees)
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers={"ETag": etag})
    response.headers["ETag"] = etag
    return employees


@router.get("/{employee_id}", response_model=schemas.Employee)
def read_employee(employee_id: int, mediator: Mediator = Depends(get_mediator)) -> models.Employee:
    employee: models.Employee | None = mediator.send(GetEmployeeByIdQuery(employee_id))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("", response_model=schemas.Employee, status_code=201)
def create_new_employee(
    payload: schemas.EmployeeCreate, mediator: Mediator = Depends(get_mediator)
) -> models.Employee:
    return mediator.send(CreateEmployeeCommand(payload))


@router.put("/{employee_id}", response_model=schemas.Employee)
def update_existing_employee(
    employee_id: int, payload: schemas.EmployeeUpdate, mediator: Mediator = Depends(get_mediator)
) -> models.Employee:
    employee: models.Employee | None = mediator.send(UpdateEmployeeCommand(employee_id, payload))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.delete("/{employee_id}", status_code=204, response_class=Response)
def delete_employee(employee_id: int, mediator: Mediator = Depends(get_mediator)) -> Response:
    employee: models.Employee | None = mediator.send(DeleteEmployeeCommand(employee_id))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return Response(status_code=204)
