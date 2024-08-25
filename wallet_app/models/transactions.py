from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, Relationship


class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    item_id: int

    description: str | None = None
    
    
    
class CreatedTransaction(BaseTransaction):
    pass

class UpdatedTransaction(BaseTransaction):
    pass

class Transaction(BaseTransaction):
    id: int
    price: float
    merchant_id: int
    customer_id: int
    
    
class DBTransaction(BaseTransaction, SQLModel, table=True):
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    price: float = Field(default=None)
    
    merchant_id: int = Field(default=None)
    
    customer_id: int = Field(default=None)
    
    

class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    transactions: list[Transaction]
    page: int
    page_size: int
    size_per_page: int