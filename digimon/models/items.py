from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, Relationship

from . import users
from . import merchants


class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    price: float = 0.00
    tax: float | None = None
    
    


class CreatedItem(BaseItem):
    pass


class UpdatedItem(BaseItem):
    pass


class Item(BaseItem):
    id: int

    merchant_id: int
    user_id: int
    

class DBItem(BaseItem, SQLModel, table=True):
    __tablename__ = "items"
    
    id: Optional[int] = Field(default=None, primary_key=True)

    
    merchant_id: int = Field(default=None, foreign_key="merchants.id")
    # # merchant: merchants.DBMerchant | None = Relationship()
    merchant: merchants.DBMerchant | None = Relationship(back_populates="items")
    
    user_id: int = Field(default=None, foreign_key="users.id")
    # user: users.DBUser | None = Relationship()
    user: users.DBUser | None = Relationship(back_populates="items")
    
    
    
    

class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    items: list[Item]
    page: int
    page_count: int
    size_per_page: int

