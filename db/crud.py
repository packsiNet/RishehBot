from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Order, Category, Item


async def create_order(
    session: AsyncSession,
    user_id: int,
    tracking_code: str,
    status: str,
    category_key: str | None = None,
    option_title: str | None = None,
    phone_number: str | None = None,
    full_name: str | None = None,
    username: str | None = None,
) -> None:
    o = Order(
        user_id=user_id,
        tracking_code=tracking_code,
        status=status,
        category_key=category_key,
        option_title=option_title,
        phone_number=phone_number,
        full_name=full_name,
        username=username,
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
