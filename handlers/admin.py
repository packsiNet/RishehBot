"""
Admin-specific handlers: list all orders by status and inspect details.
"""

from __future__ import annotations

from typing import List

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from db.database import get_session
from db.crud import get_all_orders_by_status, find_order_by_code
from keyboards import admin_orders_menu_kb, admin_orders_list_kb


STATUS_MAP = {
    "ACTIVE": "درحال انجام",
    "DONE": "انجام شده",
    "CANCEL": "کنسل شده",
}


async def open_admin_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "مدیریت سفارش‌ها\n\n"
        "یکی از گروه‌های زیر را انتخاب کنید تا لیست تمام سفارش‌ها نمایش داده شود."
    )
    await query.edit_message_text(text, reply_markup=admin_orders_menu_kb(), parse_mode=ParseMode.HTML)
    return 1


async def admin_orders_filter_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, filt = query.data.split(":", 2)
    fa_status = STATUS_MAP.get(filt, "")
    async with get_session() as session:
        orders = await get_all_orders_by_status(session, fa_status)
    if not orders:
        await query.edit_message_text(
            f"هیچ سفارشی با وضعیت «{fa_status or '—'}» یافت نشد.",
            reply_markup=admin_orders_menu_kb(),
            parse_mode=ParseMode.HTML,
        )
        return 1
    codes: List[str] = [o.tracking_code for o in orders]
    await query.edit_message_text(
        "سفارش خود را انتخاب کنید:", reply_markup=admin_orders_list_kb(codes), parse_mode=ParseMode.HTML
    )
    context.user_data["admin_orders_list_status"] = filt
    return 1


async def admin_order_code_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, code = query.data.split(":", 2)
    async with get_session() as session:
        order = await find_order_by_code(session, code)
    if not order:
        await query.edit_message_text(
            "سفارش موردنظر پیدا نشد.", reply_markup=admin_orders_menu_kb(), parse_mode=ParseMode.HTML
        )
        return 1
    # Show minimal details; can be expanded to include user info if needed
    text = (
        f"کد پیگیری: {order.tracking_code}\n"
        f"وضعیت: {order.status}\n"
        f"دسته: {order.category_key or '—'}\n"
        f"آیتم: {order.option_title or '—'}\n"
    )
    # Rebuild last list for back
    filt = context.user_data.get("admin_orders_list_status")
    fa_status = STATUS_MAP.get(filt, "")
    if fa_status:
        async with get_session() as session:
            codes = [o.tracking_code for o in await get_all_orders_by_status(session, fa_status)]
        kb = admin_orders_list_kb(codes)
    else:
        kb = admin_orders_menu_kb()
    await query.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    return 1

