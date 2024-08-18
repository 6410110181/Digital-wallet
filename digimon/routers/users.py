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
    user_id: str,
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
    user = models.DBUser.from_orm(user_info)
    await user.set_password(user_info.password)
    user.role = models.UserRole.merchant
    
    session.add(user)

    # create new merchant
    dbmerchant = models.DBMerchant(**merchant_info.dict())
    dbmerchant.user = user

    session.add(dbmerchant)
    await session.commit()
    
    await session.refresh(user)
    await session.refresh(dbmerchant)
    return models.Merchant.from_orm(dbmerchant)

@router.post("/register_customer")
async def register_customer(
    user_info: models.RegisteredUser,
    customer_info: models.CreatedCustomer,
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
    user = models.DBUser.from_orm(user_info)
    await user.set_password(user_info.password)
    user.role = models.UserRole.customer
    
    session.add(user)

    # create new customer
    dbcustomer = models.DBCustomer(**customer_info.dict())
    dbcustomer.user = user

    session.add(dbcustomer)
    await session.commit()
    
    await session.refresh(user)
    await session.refresh(dbcustomer)

    return models.Customer.from_orm(dbcustomer)



@router.put("/{user_id}/change_password")
async def change_password(
    user_id: str,
    password_update: models.ChangedPassword,
    current_user: models.User = Depends(deps.get_current_user),
) -> dict():

    result = await session.get(models.DBUser, user_id)

    if user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    if not user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    user.set_password(password_update.new_password)
    session.add(user)
    await session.commit()


@router.put("/{user_id}/update")
async def update(
    request: Request,
    user_id: str,
    user_update: models.UpdatedUser,
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:

    user = await session.get(models.DBUser, user_id)

    if user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    if not user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    user.update(**set_dict)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
