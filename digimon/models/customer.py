from typing import Optional, List, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship

from . import users


class BaseCustomer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    tax_id: str | None = None
    user_id: int | None = 0


class CreatedCustomer(BaseCustomer):
    pass


class UpdatedCustomer(BaseCustomer):
    pass


class Customer(BaseCustomer):
    id: int


class DBCustomer(BaseCustomer, SQLModel, table=True):
    __tablename__ = "Customers"
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser | None = Relationship()


class CustomerList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    customers: list[Customer]
    page: int
    page_size: int
    size_per_page: int
