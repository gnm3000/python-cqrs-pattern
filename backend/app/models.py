from sqlalchemy import Boolean, Column, Float, Integer, String

from .database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)
    address = Column(String(200), nullable=False)
    in_vacation = Column(Boolean, default=False, nullable=False)


class ReadEmployee(Base):
    __tablename__ = "read_employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)
    address = Column(String(200), nullable=False)
    in_vacation = Column(Boolean, default=False, nullable=False)
