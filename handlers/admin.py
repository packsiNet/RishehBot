"""
Admin-specific handlers: list all orders by status and inspect details.
"""

from __future__ import annotations

from typing import List

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from db.database import get_session
from db.crud import get_all_orders_by_status, find_order_by_code, update_order_status_by_code
from keyboards import admin_orders_menu_kb, admin_orders_list_kb, admin_order_actions_kb, admin_status_menu_kb


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
        user = None
        if order:
            # fetch user info explicitly to avoid lazy load after session
            from sqlalchemy import select
            res = await session.execute(select(type(order).user).where(type(order).id == order.id))
            # fallback if the above isn't reliable; get by FK
            user = order.user if hasattr(order, "user") else None
    if not order:
        await query.edit_message_text(
            "سفارش موردنظر پیدا نشد.", reply_markup=admin_orders_menu_kb(), parse_mode=ParseMode.HTML
        )
        return 1
    full_name = getattr(user, "full_name", "—") if user else "—"
    username = getattr(user, "username", None) if user else None
    phone = getattr(user, "phone_number", "—") if user else "—"
    text = (
        f"مشخصات کاربر:\n"
        f"نام کامل: {full_name}\n"
        f"نام‌کاربری: {username or '—'}\n"
        f"موبایل: {phone}\n\n"
        f"جزئیات سفارش:\n"
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
        kb = admin_order_actions_kb(username, code)
    else:
        kb = admin_order_actions_kb(username, code)
    await query.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    return 1


async def open_status_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, code = query.data.split(":", 2)
    await query.edit_message_text("انتخاب وضعیت جدید:", reply_markup=admin_status_menu_kb(code), parse_mode=ParseMode.HTML)
    return 1


STATUS_LABELS = {
    "REVIEWED": "بررسی شده",
    "REJECTED": "رد شده",
    "IN_PROGRESS": "در دست اقدام",
    "DONE": "انجام شده",
}


async def set_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, code, key = query.data.split(":", 3)
    label = STATUS_LABELS.get(key, key)
    async with get_session() as session:
        ok = await update_order_status_by_code(session, code, label)
    if not ok:
        await query.edit_message_text("به‌روزرسانی وضعیت ناموفق بود.", reply_markup=admin_orders_menu_kb(), parse_mode=ParseMode.HTML)
        return 1
    # After update, show details again
    # Reuse order detail view
    update.effective_message.callback_data = f"ORDERS_ADMIN:CODE:{code}"
    return await admin_order_code_selected(update, context)
