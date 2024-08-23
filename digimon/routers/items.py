from fastapi import APIRouter, HTTPException, Depends, Query, status

from typing import Optional, Annotated

from sqlmodel import Field, SQLModel, create_engine, Session, select, func
from sqlmodel.ext.asyncio.session import AsyncSession

import math

from ..models import Item, CreatedItem, UpdatedItem, ItemList, DBItem, engine, DBMerchant, get_session, User
from .. import deps


router = APIRouter(prefix="/items")

SIZE_PER_PAGE = 50

@router.post("")
async def create_item(
    item_info: CreatedItem,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> Item | None:

    
    if current_user.role != "merchant" :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You not merchant"
        )
        
    statement = select(DBMerchant).where(DBMerchant.user_id == current_user.id)
    result = await session.exec(statement)
    dbmerchant = result.one_or_none()
    
    dbitem = DBItem.from_orm(item_info)
    dbitem.user = current_user
    
    dbitem.merchant_id = dbmerchant.id
    
    session.add(dbitem)
    await session.commit()
    await session.refresh(dbitem)

    return Item.from_orm(dbitem)


@router.get("/page/{page}")
async def read_items(
    page: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ItemList:
    result = await session.exec(
        select(DBItem).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
        )
    items = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(DBItem.id)))).first()
            / SIZE_PER_PAGE
        )
    )
    return ItemList.from_orm(
        dict(items=items, page_count=page_count, page=page, size_per_page=SIZE_PER_PAGE)
    )

@router.get("/page/{page}/page_size/{page_size}")
async def read_items(
    page: int,
    page_size: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ItemList:
    result = await session.exec(
        select(DBItem).offset((page - 1) * page_size).limit(page_size)
        )
    items = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(DBItem.id)))).first()
            / page_size
        )
    )
    return ItemList.from_orm(
        dict(items=items, page_count=page_count, page=page, size_per_page=page_size)
    )

@router.get("/item_id/{item_id}")
async def read_item(
    item_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    ) -> Item:
    db_item = await session.get(DBItem, item_id)
    if db_item:
        print(">>>", db_item)
        return Item.from_orm(db_item)

    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/{item_id}")
async def update_item(
    item_id: int,
    item: UpdatedItem,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Item:
    data = item.dict()
    db_item = await session.get(DBItem, item_id)
    if db_item:
        db_item.sqlmodel_update(data)
        session.add(db_item)
        await session.commit()
        await session.refresh(db_item)

        return Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    db_item = await session.get(DBItem, item_id)
    if db_item:
        await session.delete(db_item)
        await session.commit()
        
        return dict(message="delete success")
    raise HTTPException(status_code=404, detail="Item not found")