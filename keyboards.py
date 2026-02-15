"""
Inline keyboard builders for the bot.

All keyboards use Persian (RTL-friendly) labels.
"""

from __future__ import annotations

from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    """Main menu with three actions."""
    buttons = [
        [InlineKeyboardButton("همیــار ریـشه", callback_data="NAV:HELPER")],
        [InlineKeyboardButton("پیگیـری سفارش", callback_data="NAV:ORDERS")],
        [InlineKeyboardButton("دربـاره ریـشه", callback_data="NAV:ABOUT")],
    ]
    return InlineKeyboardMarkup(buttons)


def admin_main_menu() -> InlineKeyboardMarkup:
    """Admin main menu with access to global orders list."""
    buttons = [
        [InlineKeyboardButton("لیست سفارشات ثبت شده", callback_data="NAV:ADMIN_ORDERS")],
        [InlineKeyboardButton("مدیریت کاربران", callback_data="NAV:ADMIN_USERS")],
        [InlineKeyboardButton("درباره ریشه", callback_data="NAV:ABOUT")],
    ]
    return InlineKeyboardMarkup(buttons)


def back_to_main_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")]])


def about_menu_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("اعتبار ریشه", callback_data="ABOUT:CRED")],
        [InlineKeyboardButton("ریشه در ایران", callback_data="ABOUT:IRAN")],
        [InlineKeyboardButton("کانال تلگرام", callback_data="ABOUT:CHANNEL")],
        [InlineKeyboardButton("وبسایت", callback_data="ABOUT:WEBSITE")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")],
    ]
    return InlineKeyboardMarkup(buttons)


def channel_kb(url: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("مشاهده کانال", url=url)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="NAV:ABOUT")],
    ]
    return InlineKeyboardMarkup(buttons)


def website_kb(url: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("مشاهده وبسایت", url=url)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="NAV:ABOUT")],
    ]
    return InlineKeyboardMarkup(buttons)


def helper_menu_kb(categories: List[tuple[int, str]]) -> InlineKeyboardMarkup:
    buttons: List[List[InlineKeyboardButton]] = []
    for cid, title in categories:
        buttons.append([InlineKeyboardButton(title, callback_data=f"HELPER:CATEGORY_ID:{cid}")])
    buttons.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")])
    return InlineKeyboardMarkup(buttons)


def helper_options_kb(category_id: int, count: int = 3) -> InlineKeyboardMarkup:
    """Build numeric options (1..count) for a helper category."""
    row: List[InlineKeyboardButton] = []
    for i in range(1, count + 1):
        row.append(
            InlineKeyboardButton(str(i), callback_data=f"HELPER:OPTION:{category_id}:{i}")
        )
    buttons = [row, [InlineKeyboardButton("⬅️ بازگشت", callback_data="HELPER:BACK:MENU")]]
    return InlineKeyboardMarkup(buttons)


def helper_confirm_kb(category_id: int, idx: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("ثبت سفارش", callback_data=f"HELPER:CONFIRM:{category_id}:{idx}")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=f"HELPER:BACK:OPTIONS:{category_id}")],
    ]
    return InlineKeyboardMarkup(buttons)


def after_confirm_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="BACK:MAIN")],
        [InlineKeyboardButton("پیگیری سفارش", callback_data="NAV:ORDERS")],
    ]
    return InlineKeyboardMarkup(buttons)


def orders_menu_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("سفارشات در دست بررسی", callback_data="ORDERS:FILTER:ACTIVE")],
        [InlineKeyboardButton("سفارشات پایان یافته", callback_data="ORDERS:FILTER:DONE")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")],
    ]
    return InlineKeyboardMarkup(buttons)


def orders_list_kb(tracking_codes: List[str]) -> InlineKeyboardMarkup:
    """Build a vertical list of tracking code buttons with a back."""
    buttons: List[List[InlineKeyboardButton]] = []
    for code in tracking_codes:
        buttons.append([InlineKeyboardButton(code, callback_data=f"ORDERS:CODE:{code}")])
    buttons.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="ORDERS:BACK:MENU")])
    return InlineKeyboardMarkup(buttons)


def orders_named_list_kb(entries: List[tuple[str, str]]) -> InlineKeyboardMarkup:
    """Build a vertical list where each button shows a label but links to a tracking code.

    entries: list of (label, tracking_code)
    """
    buttons: List[List[InlineKeyboardButton]] = []
    for label, code in entries:
        buttons.append([InlineKeyboardButton(label, callback_data=f"ORDERS:CODE:{code}")])
    buttons.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="ORDERS:BACK:MENU")])
    return InlineKeyboardMarkup(buttons)


def admin_orders_list_kb(tracking_codes: List[str], filt: str, page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    """Build a two-column paginated list of tracking code buttons with navigation."""
    rows: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []
    for code in tracking_codes:
        row.append(InlineKeyboardButton(code, callback_data=f"ORDERS_ADMIN:CODE:{code}:{page}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav: List[InlineKeyboardButton] = []
    if has_prev:
        nav.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"ORDERS_ADMIN:PAGE:{filt}:{page-1}"))
    if has_next:
        nav.append(InlineKeyboardButton("ادامه ➡️", callback_data=f"ORDERS_ADMIN:PAGE:{filt}:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="NAV:ADMIN_ORDERS")])
    return InlineKeyboardMarkup(rows)


def admin_orders_menu_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("سفارشات جدید", callback_data="ORDERS_ADMIN:GROUP:NEW")],
        [InlineKeyboardButton("سفارشات در دست بررسی", callback_data="ORDERS_ADMIN:GROUP:INREVIEW")],
        [InlineKeyboardButton("سفارشات انجام شده", callback_data="ORDERS_ADMIN:GROUP:DONE")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")],
    ]
    return InlineKeyboardMarkup(buttons)


 


def admin_order_actions_kb(username: str | None, code: str) -> InlineKeyboardMarkup:
    buttons: List[List[InlineKeyboardButton]] = []
    buttons.append([InlineKeyboardButton("تغییر وضعیت", callback_data=f"ORDERS_ADMIN:STATUSMENU:{code}")])
    if username:
        buttons.append([InlineKeyboardButton("ارتباط با کاربر", url=f"https://t.me/{username}")])
    else:
        # اگر نام‌کاربری موجود نباشد، فقط دکمه تغییر وضعیت را نشان بده
        pass
    buttons.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="NAV:ADMIN_ORDERS")])
    return InlineKeyboardMarkup(buttons)


def admin_status_menu_kb(code: str) -> InlineKeyboardMarkup:
    # Use compact status codes for callback data; labels are Persian
    items = [
        ("REVIEWED", "بررسی شده"),
        ("REJECTED", "رد شده"),
        ("IN_PROGRESS", "در دست اقدام"),
        ("DONE", "انجام شده"),
    ]
    buttons: List[List[InlineKeyboardButton]] = []
    for key, label in items:
        buttons.append([InlineKeyboardButton(label, callback_data=f"ORDERS_ADMIN:SETSTATUS:{code}:{key}")])
    buttons.append([InlineKeyboardButton("⬅️ بازگشت", callback_data=f"ORDERS_ADMIN:CODE:{code}")])
    return InlineKeyboardMarkup(buttons)


def admin_items_menu_kb(items: List[tuple[int, str]], group_key: str) -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []
    for iid, title in items:
        row.append(InlineKeyboardButton(title, callback_data=f"ORDERS_ADMIN:GROUP_ITEM:{group_key}:{iid}:0"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="NAV:ADMIN_ORDERS")])
    return InlineKeyboardMarkup(rows)


def admin_named_orders_list_kb(entries: List[tuple[str, str]], group_key: str, item_id: int, page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    # entries: list of (label, tracking_code)
    rows: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []
    for label, code in entries:
        row.append(InlineKeyboardButton(label, callback_data=f"ORDERS_ADMIN:CODE:{code}:{page}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav: List[InlineKeyboardButton] = []
    if has_prev:
        nav.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"ORDERS_ADMIN:GROUP_ITEM_PAGE:{group_key}:{item_id}:{page-1}"))
    if has_next:
        nav.append(InlineKeyboardButton("ادامه ➡️", callback_data=f"ORDERS_ADMIN:GROUP_ITEM_PAGE:{group_key}:{item_id}:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("⬅️ بازگشت", callback_data=f"ORDERS_ADMIN:GROUP:{group_key}")])
    return InlineKeyboardMarkup(rows)


def admin_users_menu_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("لیست کاربران", callback_data="ADMIN_USERS:OPEN")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")],
    ]
    return InlineKeyboardMarkup(buttons)


def admin_users_list_kb(user_buttons: List[tuple[int, str]], page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    # Build 2 buttons per row
    rows: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []
    for uid, label in user_buttons:
        row.append(InlineKeyboardButton(label, callback_data=f"ADMIN_USERS:USER:{uid}:{page}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav_row: List[InlineKeyboardButton] = []
    if has_prev:
        nav_row.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"ADMIN_USERS:PAGE:{page-1}"))
    if has_next:
        nav_row.append(InlineKeyboardButton("ادامه ➡️", callback_data=f"ADMIN_USERS:PAGE:{page+1}"))
    if nav_row:
        rows.append(nav_row)
    rows.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="NAV:ADMIN_USERS")])
    return InlineKeyboardMarkup(rows)


def admin_user_actions_kb(user_id: int, return_page: int, current_role: int) -> InlineKeyboardMarkup:
    if current_role == 1:
        label = "تغییر به کاربر عادی"
        cb = f"ADMIN_USERS:SET_ROLE:{user_id}:2:{return_page}"
    else:
        label = "تغییر به ادمین"
        cb = f"ADMIN_USERS:SET_ROLE:{user_id}:1:{return_page}"
    buttons = [
        [InlineKeyboardButton(label, callback_data=cb)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=f"ADMIN_USERS:PAGE:{return_page}")],
    ]
    return InlineKeyboardMarkup(buttons)
