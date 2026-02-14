"""
Order tracking section handlers.
"""

from __future__ import annotations

from typing import List

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from db.database import get_session
from db.crud import get_orders_by_status as db_get_orders_by_status, find_order as db_find_order
from keyboards import orders_menu_kb, orders_list_kb


STATUS_MAP = {
    "ACTIVE": "درحال انجام",
    "DONE": "انجام شده",
    "CANCEL": "کنسل شده",
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
    user_id = query.from_user.id
    fa_status = STATUS_MAP.get(filt, "")
    async with get_session() as session:
        orders = await db_get_orders_by_status(session, user_id, fa_status)
    if not orders:
        await query.edit_message_text(
            f"هیچ سفارشی با وضعیت «{fa_status or '—'}» یافت نشد.",
            reply_markup=orders_menu_kb(),
            parse_mode=ParseMode.HTML,
        )
        return 1
    codes: List[str] = [o.tracking_code for o in orders]
    await query.edit_message_text(
        "سفارش خود را انتخاب کنید:",
        reply_markup=orders_list_kb(codes),
        parse_mode=ParseMode.HTML,
    )
    # Store current list for back navigation if needed
    context.user_data["orders_list_status"] = filt
    return 1


async def order_code_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show status details for the selected tracking code."""
    query = update.callback_query
    await query.answer()
    _, _, code = query.data.split(":", 2)
    user_id = query.from_user.id
    async with get_session() as session:
        order = await db_find_order(session, user_id, code)
    if not order:
        await query.edit_message_text(
            "سفارش موردنظر پیدا نشد.", reply_markup=orders_menu_kb(), parse_mode=ParseMode.HTML
        )
        return 1
    status_text = order.status
    text = f"وضعیت سفارش {order.tracking_code}: {status_text}"
    # Rebuild last list for back
    filt = context.user_data.get("orders_list_status")
    fa_status = STATUS_MAP.get(filt, "")
    if fa_status:
        # Build codes again
        async with get_session() as session:
            codes = [o.tracking_code for o in await db_get_orders_by_status(session, user_id, fa_status)]
        kb = orders_list_kb(codes)
    else:
        kb = orders_menu_kb()
    await query.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    return 1

