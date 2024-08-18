from fastapi import APIRouter, HTTPException, Depends

from typing import Optional, Annotated
from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models import (
    Transaction,
    CreatedTransaction,
    UpdatedTransaction,
    TransactionList,
    DBTransaction,
    engine,
    get_session
)

router = APIRouter(prefix="/transactions")

@router.post("")
async def create_transaction(
    transaction: CreatedTransaction,
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> Transaction:
    print("create_transaction", transaction)
    data = transaction.dict()
    dbtransaction = DBTransaction(**data)
    session.add(dbtransaction)
    await session.commit()
    await session.refresh(dbtransaction)

    # return transaction.parse_obj(dbtransaction.dict())
    return Transaction.from_orm(dbtransaction)

@router.get("")
async def read_transactions(
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> TransactionList:
    result = await session.exec(select(DBTransaction))
    if result:
        transactions = result.all()
        return TransactionList.from_orm(dict(transactions=transactions, page_size=0, page=0, size_per_page=0))
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.get("/{transaction_id}")
async def read_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> Transaction:
    db_transaction = await session.get(DBTransaction, transaction_id)
    if db_transaction:
        return Transaction.from_orm(db_transaction)
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: int, 
    transaction: UpdatedTransaction,
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> Transaction:
    data = transaction.dict()
    db_transaction = await session.get(DBTransaction, transaction_id)
    if db_transaction:
        print("update_transaction", transaction)
        db_transaction.sqlmodel_update(data)
        session.add(db_transaction)
        await session.commit()
        await session.refresh(db_transaction)
        return Transaction.from_orm(db_transaction)
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> dict:
    db_transaction = await session.get(DBTransaction, transaction_id)
    if db_transaction:
        await session.delete(db_transaction)
        await session.commit()
        return dict(message="delete success")
    raise HTTPException(status_code=404, detail="Transaction not found")


