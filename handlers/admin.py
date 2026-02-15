"""
Admin-specific handlers: list all orders by status and inspect details.
"""

from __future__ import annotations

from typing import List

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from db.database import get_session
from db.crud import (
    get_all_orders_by_status,
    find_order_by_code,
    update_order_status_by_code,
    count_orders_by_status,
    get_orders_paged_by_status,
)
from keyboards import (
    admin_orders_menu_kb,
    admin_orders_list_kb,
    admin_order_actions_kb,
    admin_status_menu_kb,
    admin_users_menu_kb,
    admin_users_list_kb,
    admin_user_actions_kb,
    admin_items_menu_kb,
    admin_named_orders_list_kb,
)
from db.models import User
from db.crud import (
    count_users,
    get_users_paged,
    get_user_by_id,
    set_user_admin,
    set_user_role,
    get_all_items,
    count_orders_by_statuses_and_item,
    get_orders_paged_by_statuses_and_item,
)


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


# Admin group definitions
ADMIN_GROUPS = {
    "NEW": {
        "name": "سفارشات جدید",
        "statuses": ["درحال انجام"],
    },
    "INREVIEW": {
        "name": "سفارشات در دست بررسی",
        "statuses": ["بررسی شده", "در دست اقدام"],
    },
    "DONE": {
        "name": "سفارشات انجام شده",
        "statuses": ["انجام شده", "رد شده"],
    },
}


async def admin_orders_group_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, group_key = query.data.split(":", 2)
    if group_key not in ADMIN_GROUPS:
        await query.edit_message_text("گروه نامعتبر است.", reply_markup=admin_orders_menu_kb(), parse_mode=ParseMode.HTML)
        return 1
    async with get_session() as session:
        items = await get_all_items(session)
    pairs = [(it.id, it.title) for it in items]
    title = ADMIN_GROUPS[group_key]["name"]
    await query.edit_message_text(f"{title}\n\nیک آیتم را انتخاب کنید:", reply_markup=admin_items_menu_kb(pairs, group_key), parse_mode=ParseMode.HTML)
    return 1


PAGE_SIZE_GROUP_ITEM = 10


async def admin_orders_group_item_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, group_key, item_id_str, page_str = query.data.split(":", 4)
    item_id = int(item_id_str)
    page = int(page_str)
    group = ADMIN_GROUPS.get(group_key)
    if not group:
        await query.edit_message_text("گروه نامعتبر است.", reply_markup=admin_orders_menu_kb(), parse_mode=ParseMode.HTML)
        return 1
    statuses = group["statuses"]
    # Need item title for filtering orders.option_title
    async with get_session() as session:
        from db.models import Item
        from sqlalchemy import select
        res = await session.execute(select(Item).where(Item.id == item_id))
        item = res.scalars().first()
        if not item:
            await query.edit_message_text("آیتم پیدا نشد.", reply_markup=admin_orders_menu_kb(), parse_mode=ParseMode.HTML)
            return 1
        offset = page * PAGE_SIZE_GROUP_ITEM
        total = await count_orders_by_statuses_and_item(session, statuses, item.title)
        orders = await get_orders_paged_by_statuses_and_item(session, statuses, item.title, offset, PAGE_SIZE_GROUP_ITEM)
        # Fetch users for label building
        user_ids = list({o.user_id for o in orders})
        users = {}
        if user_ids:
            from sqlalchemy import select as _select
            resu = await session.execute(_select(User).where(User.id.in_(user_ids)))
            for u in resu.scalars().all():
                users[u.id] = u
    # Build labels: full name, else @username, else tracking code
    entries: List[tuple[str, str]] = []
    for o in orders:
        u = users.get(o.user_id)
        if u and u.full_name and u.full_name.strip():
            label = u.full_name.strip()
        elif u and u.username and str(u.username).strip():
            label = f"@{u.username.strip()}"
        else:
            label = o.tracking_code
        entries.append((label, o.tracking_code))
    has_prev = page > 0
    has_next = (page * PAGE_SIZE_GROUP_ITEM + len(orders)) < total
    title = ADMIN_GROUPS[group_key]["name"]
    await query.edit_message_text(
        f"{title} → {item.title}\n\nسفارش را انتخاب کنید:",
        reply_markup=admin_named_orders_list_kb(entries, group_key, item_id, page, has_prev, has_next),
        parse_mode=ParseMode.HTML,
    )
    return 1


async def open_admin_users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("مدیریت کاربران", reply_markup=admin_users_menu_kb(), parse_mode=ParseMode.HTML)
    return 1


PAGE_SIZE = 10


async def open_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0) -> int:
    query = update.callback_query
    await query.answer()
    offset = page * PAGE_SIZE
    async with get_session() as session:
        total = await count_users(session)
        users = await get_users_paged(session, offset, PAGE_SIZE)
    btns: List[tuple[int, str]] = []
    for u in users:
        if u.full_name and u.full_name.strip():
            label = u.full_name.strip()
        elif u.username and str(u.username).strip():
            label = f"@{u.username.strip()}"
        else:
            label = "کاربر ناشناس"
        btns.append((u.id, label))
    has_prev = page > 0
    has_next = (offset + PAGE_SIZE) < total
    header = f"تعداد کل کاربران: {total}\n\nسفارش‌دهندگان ثبت‌شده:" if total else "کاربری یافت نشد."
    await query.edit_message_text(header, reply_markup=admin_users_list_kb(btns, page, has_prev, has_next), parse_mode=ParseMode.HTML)
    return 1


async def admin_users_open(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await open_users_list(update, context, 0)


async def admin_users_change_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    _, _, page_str = query.data.split(":", 2)
    page = int(page_str)
    return await open_users_list(update, context, page)


async def admin_user_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, user_id_str, page_str = query.data.split(":", 3)
    user_id = int(user_id_str)
    page = int(page_str)
    async with get_session() as session:
        user = await get_user_by_id(session, user_id)
    if not user:
        await query.edit_message_text("کاربر یافت نشد.", reply_markup=admin_users_menu_kb(), parse_mode=ParseMode.HTML)
        return 1
    display_name = user.full_name.strip() if user.full_name and user.full_name.strip() else (f"@{user.username.strip()}" if user.username and str(user.username).strip() else "کاربر ناشناس")
    text = (
        f"مشخصات کاربر:\n"
        f"نام نمایشی: {display_name}"
    )
    await query.edit_message_text(text, reply_markup=admin_user_actions_kb(user.id, page, user.role_id), parse_mode=ParseMode.HTML)
    return 1


async def admin_set_user_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, user_id_str, role_id_str, page_str = query.data.split(":", 4)
    user_id = int(user_id_str)
    role_id = int(role_id_str)
    page = int(page_str)
    async with get_session() as session:
        ok = await set_user_role(session, user_id, role_id)
        user = await get_user_by_id(session, user_id)
    if not ok or not user:
        await query.edit_message_text("تغییر نقش ناموفق بود.", reply_markup=admin_users_menu_kb(), parse_mode=ParseMode.HTML)
        return 1
    verb = "ادمین" if role_id == 1 else "کاربر عادی"
    display_name = user.full_name.strip() if user.full_name and user.full_name.strip() else (f"@{user.username.strip()}" if user.username and str(user.username).strip() else "کاربر ناشناس")
    text = (
        f"نقش کاربر به {verb} تغییر کرد.\n\n"
        f"نام نمایشی: {display_name}"
    )
    await query.edit_message_text(text, reply_markup=admin_user_actions_kb(user.id, page, user.role_id), parse_mode=ParseMode.HTML)
    return 1


PAGE_SIZE_ORDERS = 10


async def admin_orders_filter_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, filt = query.data.split(":", 2)
    fa_status = STATUS_MAP.get(filt, "")
    page = 0
    offset = page * PAGE_SIZE_ORDERS
    async with get_session() as session:
        total = await count_orders_by_status(session, fa_status)
        orders = await get_orders_paged_by_status(session, fa_status, offset, PAGE_SIZE_ORDERS)
    if not orders and total == 0:
        await query.edit_message_text(
            f"هیچ سفارشی با وضعیت «{fa_status or '—'}» یافت نشد.",
            reply_markup=admin_orders_menu_kb(),
            parse_mode=ParseMode.HTML,
        )
        return 1
    codes: List[str] = [o.tracking_code for o in orders]
    has_prev = False
    has_next = (offset + PAGE_SIZE_ORDERS) < total
    await query.edit_message_text(
        "سفارش خود را انتخاب کنید:",
        reply_markup=admin_orders_list_kb(codes, filt, page, has_prev, has_next),
        parse_mode=ParseMode.HTML,
    )
    context.user_data["admin_orders_list_status"] = filt
    context.user_data["admin_orders_page"] = page
    return 1


async def admin_order_code_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    # ORDERS_ADMIN:CODE:<code> or ORDERS_ADMIN:CODE:<code>:<page>
    code = parts[2]
    page = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else context.user_data.get("admin_orders_page", 0)
    async with get_session() as session:
        order = await find_order_by_code(session, code)
        user = None
        if order:
            from sqlalchemy import select
            if getattr(order, "user_id", None) is not None:
                user_res = await session.execute(select(User).where(User.id == order.user_id))
                user = user_res.scalars().first()
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
    kb = admin_order_actions_kb(username, code)
    await query.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    return 1


async def admin_orders_change_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, filt, page_str = query.data.split(":", 3)
    page = int(page_str)
    fa_status = STATUS_MAP.get(filt, "")
    offset = page * PAGE_SIZE_ORDERS
    async with get_session() as session:
        total = await count_orders_by_status(session, fa_status)
        orders = await get_orders_paged_by_status(session, fa_status, offset, PAGE_SIZE_ORDERS)
    codes: List[str] = [o.tracking_code for o in orders]
    has_prev = page > 0
    has_next = (offset + PAGE_SIZE_ORDERS) < total
    await query.edit_message_text(
        "سفارش خود را انتخاب کنید:",
        reply_markup=admin_orders_list_kb(codes, filt, page, has_prev, has_next),
        parse_mode=ParseMode.HTML,
    )
    context.user_data["admin_orders_list_status"] = filt
    context.user_data["admin_orders_page"] = page
    return 1


async def open_status_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, code = query.data.split(":", 2)
    await query.edit_message_text("انتخاب وضعیت جدید:", reply_markup=admin_status_menu_kb(code), parse_mode=ParseMode.HTML)
    return 1


STATUS_LABELS = {
    "SEEN": "دیده شده",
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
        # Fetch newest order and its user to display updated details
        order = await find_order_by_code(session, code)
        user = None
        if order and getattr(order, "user_id", None) is not None:
            from sqlalchemy import select
            user_res = await session.execute(select(User).where(User.id == order.user_id))
            user = user_res.scalars().first()

    if not ok or not order:
        await query.edit_message_text("به‌روزرسانی وضعیت ناموفق بود.", reply_markup=admin_orders_menu_kb(), parse_mode=ParseMode.HTML)
        return 1

    # Show a quick alert for confirmation
    try:
        await query.answer(text=f"وضعیت سفارش به «{label}» تغییر کرد.", show_alert=True)
    except Exception:
        pass

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
    kb = admin_order_actions_kb(username, code)
    await query.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    return 1
