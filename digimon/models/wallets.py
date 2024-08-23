from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, Relationship

from . import users

class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance : float
    
class CreatedWallet(BaseWallet):
    pass

class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int
    user_id: int
    
    
    
class DBWallet(BaseWallet, SQLModel, table=True):
    __tablename__ = "wallets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: int = Field(default=None, foreign_key="users.id")
    # user: users.DBUser | None = Relationship()
    user: users.DBUser | None = Relationship(back_populates="wallets")


class WalletList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    wallets: list[Wallet]
    page: int
    page_size: int
    size_per_page: int