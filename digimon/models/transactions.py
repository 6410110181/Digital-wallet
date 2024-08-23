from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel


class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    item_id: int
    name: str
    description: str | None = None
    
    merchant_id: int
    customer_id: int
    
class CreatedTransaction(BaseTransaction):
    pass

class UpdatedTransaction(BaseTransaction):
    pass

class Transaction(BaseTransaction):
    id: int
    
class DBTransaction(BaseTransaction, SQLModel, table=True):
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    item_id: int = Field(default=None, foreign_key="items.item_id")
    
    
class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    transactions: list[Transaction]
    page: int
    page_size: int
    size_per_page: int