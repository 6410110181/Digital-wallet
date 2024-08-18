from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from typing import Annotated

from .. import deps
from .. import models

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(current_user: models.User = Depends(deps.get_current_user)) -> models.User:
    return current_user


@router.get("/{user_id}")
async def get(
    user_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:

    user = await session.get(models.DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )
    return user


@router.post("/register_merchant")
async def register_merchant(
    user_info: models.RegisteredUser,
    merchant_info: models.CreatedMerchant,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Merchant:

    # check username
    user_result = await session.execute(
        select(models.DBUser).where(models.DBUser.username == user_info.username)
    )

    user = user_result.scalar_one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username already exists.",
        )

    # create new user
    dbuser = models.DBUser.from_orm(user_info)
    await dbuser.set_password(user_info.password)
    dbuser.role = models.UserRole.merchant
    
    session.add(dbuser)

    # create new merchant
    dbmerchant = models.DBMerchant.from_orm(merchant_info)
    dbmerchant.user = dbuser

    session.add(dbmerchant)
    await session.commit()
    
    await session.refresh(dbuser)
    await session.refresh(dbmerchant)

    return models.Merchant.from_orm(dbmerchant)

@router.post("/register_customer")
async def register_customer(
    user_info: models.RegisteredUser,
    customer_info: models.CreatedCustomer,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Customer:

    # check username
    user_result = await session.execute(
        select(models.DBUser).where(models.DBUser.username == user_info.username)
    )

    user = user_result.scalar_one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username already exists.",
        )

    # create new user
    dbuser = models.DBUser.from_orm(user_info)
    await dbuser.set_password(user_info.password)
    dbuser.role = models.UserRole.customer
    
    session.add(dbuser)

    # create new merchant
    dbcustomer = models.DBCustomer.from_orm(customer_info)
    dbcustomer.user = dbuser

    session.add(dbcustomer)
    await session.commit()
    
    await session.refresh(dbuser)
    await session.refresh(dbcustomer)

    return models.Customer.from_orm(dbcustomer)



@router.put("/{user_id}/change_password")
async def change_password(
    user_id: int,
    password_update: models.ChangedPassword,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:
    
    db_user = await session.get(models.DBUser, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    if not db_user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    db_user.set_password(password_update.new_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    print(password_update.current_password)
    
    return db_user,



@router.put("/{user_id}/update")
async def update(
    request: Request,
    user_id: int,
    user_update: models.UpdatedUser,
    password_update: models.ChangedPassword,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:

    result = await session.exec(
        select(models.DBUser).where(models.DBUser.id == user_id)
    )
    db_user = result.one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    if not await db_user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    db_user.sqlmodel_update(user_update)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_user = await session.get(models.DBUser, user_id)
    if db_user:
        await session.delete(db_user)
        await session.commit()
        
        
        return dict(message="delete success")
    raise HTTPException(status_code=404, detail="user not found")