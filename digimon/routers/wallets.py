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
    User,
    engine,
    get_session,
)

from .. import deps

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

    result = await session.exec(
        select(DBWallet).where(DBWallet.id == wallet_id),
    )
    dbwallet = result.one_or_none()

    if dbwallet:
        return Wallet.from_orm(dbwallet)
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.put("")
async def update_wallet(
    wallet: UpdatedWallet,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(deps.get_current_user),
    ) -> Wallet:
    
    result = await session.exec(
        select(DBWallet).where(DBWallet.user_id == current_user.id)
    )

    dbwallet = result.one_or_none()
    
    
    if dbwallet:
        print("update_wallet", wallet)
        dbwallet.sqlmodel_update(wallet)
        session.add(dbwallet)
        await session.commit()
        await session.refresh(dbwallet)
        return Wallet.from_orm(dbwallet)
    raise HTTPException(status_code=404, detail="Wallet not found")


@router.put("add")
async def add_balance(
    balance: UpdatedWallet,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(deps.get_current_user),
    ) -> Wallet:
    
    
    result = await session.exec(
        select(DBWallet).where(DBWallet.user_id == current_user.id)
    )

    dbwallet = result.one_or_none()
    
    balance.balance += dbwallet.balance
    
    
    if dbwallet:
        dbwallet.sqlmodel_update(balance)
        session.add(dbwallet)
        await session.commit()
        await session.refresh(dbwallet)
        return Wallet.from_orm(dbwallet)
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.put("sub")
async def sub_balance(
    balance: UpdatedWallet,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(deps.get_current_user),
    ) -> Wallet:
    
    
    result = await session.exec(
        select(DBWallet).where(DBWallet.user_id == current_user.id)
    )
    dbwallet = result.one_or_none()
    
    dbwallet.balance -= balance.balance
    
    
    if dbwallet:
        dbwallet.sqlmodel_update(balance)
        session.add(dbwallet)
        await session.commit()
        await session.refresh(dbwallet)
        return Wallet.from_orm(dbwallet)
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.delete("/{wallet_id}")
async def delete_wallet(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> dict:

    result = await session.exec(
        select(DBWallet).where(DBWallet.id == wallet_id)
    )
    dbwallet = result.one_or_none()

    if dbwallet:
        await session.delete(dbwallet)
        await session.commit()
        return dict(message="delete success")
    raise HTTPException(status_code=404, detail="Wallet not found")
