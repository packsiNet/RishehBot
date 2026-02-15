"""
Order tracking section handlers.
"""

from __future__ import annotations

from typing import List

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from db.database import get_session
from db.crud import (
    get_orders_by_status as db_get_orders_by_status,
    get_orders_by_statuses as db_get_orders_by_statuses,
    find_order as db_find_order,
    get_or_create_user_by_telegram,
)
from keyboards import orders_menu_kb, orders_list_kb, orders_named_list_kb


STATUS_GROUPS = {
    "ACTIVE": {
        "name": "سفارشات در دست بررسی",
        "statuses": ["بررسی شده", "در دست اقدام", "درحال انجام"],
    },
    "DONE": {
        "name": "سفارشات پایان یافته",
        "statuses": ["انجام شده", "رد شده"],
    },
}


async def open_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show orders filter menu."""
    query = update.callback_query
    await query.answer()
    text = (
        "پیگیری سفارش\n\n"
        "یکی از گروه‌های زیر را انتخاب کنید تا لیست سفارش‌ها نمایش داده شود."
    )
    await query.edit_message_text(text, reply_markup=orders_menu_kb(), parse_mode=ParseMode.HTML)
    return 1


async def orders_filter_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """List orders for the selected status filter."""
    query = update.callback_query
    await query.answer()
    _, _, filt = query.data.split(":", 2)
    telegram_id = query.from_user.id
    group = STATUS_GROUPS.get(filt)
    statuses = group["statuses"] if group else []
    async with get_session() as session:
        user_row = await get_or_create_user_by_telegram(session, telegram_id, update_if_exists=False)
        orders = await db_get_orders_by_statuses(session, user_row.id, statuses)
    if not orders:
        await query.edit_message_text(
            f"هیچ سفارشی در «{(group and group['name']) or '—'}» یافت نشد.",
            reply_markup=orders_menu_kb(),
            parse_mode=ParseMode.HTML,
        )
        return 1
    entries: List[tuple[str, str]] = [
        ((o.option_title if (o.option_title and o.option_title.strip()) else o.tracking_code), o.tracking_code)
        for o in orders
    ]
    await query.edit_message_text(
        "سفارش خود را انتخاب کنید:", reply_markup=orders_named_list_kb(entries), parse_mode=ParseMode.HTML
    )
    # Store current list for back navigation if needed
    context.user_data["orders_list_status"] = filt
    return 1


async def order_code_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show status details for the selected tracking code."""
    query = update.callback_query
    await query.answer()
    _, _, code = query.data.split(":", 2)
    telegram_id = query.from_user.id
    async with get_session() as session:
        user_row = await get_or_create_user_by_telegram(session, telegram_id, update_if_exists=False)
        order = await db_find_order(session, user_row.id, code)
    if not order:
        await query.edit_message_text(
            "سفارش موردنظر پیدا نشد.", reply_markup=orders_menu_kb(), parse_mode=ParseMode.HTML
        )
        return 1
    status_text = order.status
    text = f"وضعیت سفارش {order.tracking_code}: {status_text}"
    # Rebuild last list for back
    filt = context.user_data.get("orders_list_status")
    group = STATUS_GROUPS.get(filt)
    if group:
        async with get_session() as session:
            ords = await db_get_orders_by_statuses(session, user_row.id, group["statuses"])
            entries = [
                ((o.option_title if (o.option_title and o.option_title.strip()) else o.tracking_code), o.tracking_code)
                for o in ords
            ]
        kb = orders_named_list_kb(entries)
    else:
        kb = orders_menu_kb()
    await query.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    return 1

