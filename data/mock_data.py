"""
In-memory mock database for orders.

Structure:
orders = {
    user_id: [
        {"tracking_code": "123456", "status": "درحال انجام"}
    ]
}
"""

from __future__ import annotations

from typing import Dict, List, TypedDict


class Order(TypedDict):
    tracking_code: str
    status: str


# Global in-memory store
ORDERS_DB: Dict[int, List[Order]] = {}


def add_order(user_id: int, order: Order) -> None:
    """Append a new order to user bucket."""
    bucket = ORDERS_DB.setdefault(user_id, [])
    bucket.append(order)


def get_orders_by_status(user_id: int, status: str) -> List[Order]:
    """Return orders of a user filtered by status."""
    return [o for o in ORDERS_DB.get(user_id, []) if o.get("status") == status]


def find_order(user_id: int, tracking_code: str) -> Order | None:
    """Find a specific order for user by tracking code."""
    for o in ORDERS_DB.get(user_id, []):
        if o.get("tracking_code") == tracking_code:
            return o
    return None

