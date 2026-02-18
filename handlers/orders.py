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
from keyboards import orders_menu_kb, orders_list_kb, orders_named_list_kb, orders_done_detail_kb
from datetime import datetime


STATUS_GROUPS = {
    "ACTIVE": {
        "name": "سفارش‌های درحال انجام",
        "statuses": ["بررسی شده", "در دست اقدام", "درحال انجام"],
    },
    "DONE": {
        "name": "سفارش‌های تکمیل شده",
        "statuses": ["انجام شده", "رد شده"],
    },
}


async def open_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show orders filter menu with summary counts."""
    query = update.callback_query
    await query.answer()
    telegram_id = query.from_user.id
    active_count = 0
    done_count = 0
    try:
        async with get_session() as session:
            user_row = await get_or_create_user_by_telegram(session, telegram_id, update_if_exists=False)
            if user_row:
                active_orders = await db_get_orders_by_statuses(session, user_row.id, STATUS_GROUPS["ACTIVE"]["statuses"])
                done_orders = await db_get_orders_by_statuses(session, user_row.id, STATUS_GROUPS["DONE"]["statuses"])
                active_count = len(active_orders)
                done_count = len(done_orders)
    except Exception:
        pass

    text = (
        "🔄 همراهی همیشه برقراره!\n"
        "اگه قبلاً از ریشه خدمتی گرفتی یا سفارشی ثبت کردی،\n"
        "اینجا می‌تونی وضعیتش رو ببینی 👀\n\n"
        f"📊 وضعیت سفارش‌ها:\n"
        f"- ⏳ درحال انجام: {active_count}\n"
        f"- ✅ تکمیل شده: {done_count}"
    )
    await query.edit_message_text(text, reply_markup=orders_menu_kb(), parse_mode=ParseMode.HTML)
    return 1


def _format_jalali(dt: datetime | None) -> str:
    if not dt:
        return "—"
    try:
        import jdatetime
        return jdatetime.datetime.fromgregorian(datetime=dt).strftime("%Y/%m/%d %H:%M")
    except Exception:
        try:
            return dt.strftime("%Y/%m/%d %H:%M")
        except Exception:
            return str(dt)


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
    if filt == "ACTIVE":
        header = (
            "شما توی این بخش می‌تونید سفارشات درحال انجام‌تون رو ببینید 👀 و از وضعیتشون مطلع بشید."
        )
    elif filt == "DONE":
        header = (
            "توی این بخش می‌تونی سفارش‌هایی که با موفقیت انجام شدن رو ببینی 📋\n"
            "همراه با زمان دقیق انجام ⏰ و مشخصات کامل هر خدمت 📄\n"
            "اگه بخوای، می‌تونی همون سفارش رو دوباره ثبت کنی 🔁"
        )
    else:
        header = "سفارش خود را انتخاب کنید:"
    await query.edit_message_text(header, reply_markup=orders_named_list_kb(entries), parse_mode=ParseMode.HTML)
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
    created = _format_jalali(getattr(order, "created_at", None))
    name = order.option_title if (order.option_title and order.option_title.strip()) else "—"
    text = (
        f"🔢 شماره سفارش: {order.tracking_code}\n"
        f"📌 نام سفارش: {name}\n"
        f"📅 تاریخ ثبت: {created}\n"
        f"📍 وضعیت: {status_text}"
    )
    # Rebuild last list for back or provide DONE detail actions
    filt = context.user_data.get("orders_list_status")
    group = STATUS_GROUPS.get(filt)
    if group and filt == "DONE":
        kb = orders_done_detail_kb(order.tracking_code)
    elif group:
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


async def orders_reorder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, code = query.data.split(":", 2)
    telegram_id = query.from_user.id
    async with get_session() as session:
        user_row = await get_or_create_user_by_telegram(session, telegram_id, update_if_exists=False)
        old = await db_find_order(session, user_row.id, code)
        if not old:
            await query.edit_message_text("سفارش موردنظر پیدا نشد.", reply_markup=orders_menu_kb(), parse_mode=ParseMode.HTML)
            return 1
    from db.crud import create_order as _create
    from random import randint
    new_code = f"{randint(100000, 999999)}"
    async with get_session() as session:
        await _create(session, user_row.id, new_code, "درحال انجام", category_key=old.category_key, option_title=old.option_title)
    text = (
        "سفارش جدید با همان مشخصات ثبت شد ✅\n\n"
        f"کد پیگیری: {new_code}\n"
        "پشتیبانی ریشه تا یکساعت آینده با شما تماس خواهد گرفت."
    )
    await query.edit_message_text(text, reply_markup=orders_menu_kb(), parse_mode=ParseMode.HTML)
    return 1

