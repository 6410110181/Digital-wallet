from fastapi import APIRouter, HTTPException, Depends

from typing import Optional, Annotated
from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models import (
    Wallet,
    CreatedWallet,
    UpdatedWallet,
    WalletList,
    DBWallet,
    engine,
    get_session,
)

router = APIRouter(prefix="/wallets")

@router.post("")
async def create_wallet(
    wallet: CreatedWallet,
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> Wallet:
    print("create_wallet", wallet)
    data = wallet.dict()
    dbwallet = DBWallet(**data)

    session.add(dbwallet)
    await session.commit()
    await session.refresh(dbwallet)

    # return wallet.parse_obj(dbwallet.dict())
    return Wallet.from_orm(dbwallet)

@router.get("")
async def read_wallets(
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> WalletList:
    result = await session.exec(select(DBWallet))
    if result:
        wallets = result.all()
        return WalletList.from_orm(dict(wallets=wallets, page_size=0, page=0, size_per_page=0))
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.get("/{wallet_id}")
async def read_wallet(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> Wallet:
    db_wallet = await session.get(DBWallet, wallet_id)
    if db_wallet:
        return Wallet.from_orm(db_wallet)
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.put("/{wallet_id}")
async def update_wallet(
    wallet_id: int,
    wallet: UpdatedWallet,
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> Wallet:
    data = wallet.dict()

    db_wallet = await session.get(DBWallet, wallet_id)
    
    if db_wallet:
        print("update_wallet", wallet)
        db_wallet.sqlmodel_update(data)
        session.add(db_wallet)
        await session.commit()
        await session.refresh(db_wallet)
        return Wallet.from_orm(db_wallet)
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.delete("/{wallet_id}")
async def delete_wallet(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> dict:

    db_wallet = await session.get(DBWallet, wallet_id)
    if db_wallet:
        await session.delete(db_wallet)
        await session.commit()
        return dict(message="delete success")
    raise HTTPException(status_code=404, detail="Wallet not found")
