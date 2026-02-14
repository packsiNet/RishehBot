from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Order, Category, Item, User


async def create_order(
    session: AsyncSession,
    user_id: int,
    tracking_code: str,
    status: str,
    category_key: str | None = None,
    option_title: str | None = None,
) -> None:
    o = Order(
        user_id=user_id,
        tracking_code=tracking_code,
        status=status,
        category_key=category_key,
        option_title=option_title,
    )
    session.add(o)
    await session.commit()


async def get_orders_by_status(session: AsyncSession, user_id: int, status: str) -> List[Order]:
    stmt = select(Order).where(Order.user_id == user_id, Order.status == status).order_by(Order.id.desc())
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def find_order(session: AsyncSession, user_id: int, tracking_code: str) -> Optional[Order]:
    stmt = select(Order).where(Order.user_id == user_id, Order.tracking_code == tracking_code)
    res = await session.execute(stmt)
    return res.scalars().first()


async def get_categories(session: AsyncSession) -> List[Category]:
    stmt = select(Category).order_by(Category.id.asc())
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def get_items_by_category(session: AsyncSession, category_id: int) -> List[Item]:
    stmt = select(Item).where(Item.category_id == category_id).order_by(Item.id.asc())
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def get_category_by_id(session: AsyncSession, category_id: int) -> Optional[Category]:
    stmt = select(Category).where(Category.id == category_id)
    res = await session.execute(stmt)
    return res.scalars().first()


async def get_or_create_user_by_telegram(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    default_role_id: int = 2,
) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id)
    res = await session.execute(stmt)
    user = res.scalars().first()
    if user:
        # Update basic fields if changed
        changed = False
        if username is not None and user.username != username:
            user.username = username
            changed = True
        if full_name is not None and user.full_name != full_name:
            user.full_name = full_name
            changed = True
        if phone_number is not None and user.phone_number != phone_number:
            user.phone_number = phone_number
            changed = True
        if changed:
            await session.commit()
        return user
    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
        phone_number=phone_number,
        role_id=default_role_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_phone(session: AsyncSession, user: User, phone_number: str) -> None:
    user.phone_number = phone_number
    await session.commit()


async def get_all_orders_by_status(session: AsyncSession, status: str) -> List[Order]:
    stmt = select(Order).where(Order.status == status).order_by(Order.id.desc())
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def find_order_by_code(session: AsyncSession, tracking_code: str) -> Optional[Order]:
    stmt = select(Order).where(Order.tracking_code == tracking_code)
    res = await session.execute(stmt)
    return res.scalars().first()
