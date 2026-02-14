from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Order


async def create_order(session: AsyncSession, user_id: int, tracking_code: str, status: str, category_key: str | None = None, option_title: str | None = None) -> None:
    o = Order(user_id=user_id, tracking_code=tracking_code, status=status, category_key=category_key, option_title=option_title)
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
