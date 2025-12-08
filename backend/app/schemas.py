from pydantic import BaseModel, Field


class EmployeeBase(BaseModel):
    name: str = Field(..., max_length=100)
    lastname: str = Field(..., max_length=100)
    salary: float
    address: str = Field(..., max_length=200)
    in_vacation: bool = False

    class Config(BaseModel.Config):  # type: ignore[override]
        orm_mode = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    id: int
