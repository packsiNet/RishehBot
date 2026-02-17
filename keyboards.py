"""
Inline keyboard builders for the bot.

All keyboards use Persian (RTL-friendly) labels.
"""

from __future__ import annotations

from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    """Main menu with revised actions."""
    buttons = [
        [InlineKeyboardButton("🚀 شروع همراهی 🚀", callback_data="NAV:HELPER")],
        [InlineKeyboardButton("📌 پیگیری سفارشاتم 📌", callback_data="NAV:ORDERS")],
        [InlineKeyboardButton("🔎 چطور به ریشه اعتماد کنم؟ 🔎", callback_data="NAV:TRUST")],
        [InlineKeyboardButton("💬 اگه نمی‌دونی؛ از من بپرس! 💬", callback_data="NAV:ASK")],
        [InlineKeyboardButton("🌿 ریشه چیه؟ 🌿", callback_data="NAV:WHATIS")],
    ]
    return InlineKeyboardMarkup(buttons)


def admin_main_menu() -> InlineKeyboardMarkup:
    """Admin main menu with access to global orders list."""
    buttons = [
        [InlineKeyboardButton("لیست سفارشات ثبت شده", callback_data="NAV:ADMIN_ORDERS")],
        [InlineKeyboardButton("مدیریت کاربران", callback_data="NAV:ADMIN_USERS")],
    ]
    return InlineKeyboardMarkup(buttons)


def back_to_main_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")]])


def channel_kb(url: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("مشاهده کانال", url=url)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")],
    ]
    return InlineKeyboardMarkup(buttons)


def website_kb(url: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("مشاهده وبسایت", url=url)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")],
    ]
    return InlineKeyboardMarkup(buttons)


# Helper v2 keyboards
def helper2_main_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("⚜️ سلامت پیشگیرانه⚜️", callback_data="HELP2:CAT:PREVENTIVE")],
        [InlineKeyboardButton("⚜️ تجربه لحظه‌های به‌یاد ماندنی از راه‌دور⚜️", callback_data="HELP2:CAT:MEMORIES")],
        [InlineKeyboardButton("⚜️ انجام نیازهای روزمره⚜️", callback_data="HELP2:CAT:DAILY")],
        [InlineKeyboardButton("⚜️ میخوام .....⚜️", callback_data="HELP2:CAT:WANT")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")],
    ]
    return InlineKeyboardMarkup(buttons)


def helper2_category_kb(category_key: str) -> InlineKeyboardMarkup:
    mapping = {
        "PREVENTIVE": [
            ("HEALTH_ASSESS", "سنجش سلامت 📋"),
            ("ALZHEIMER_SCREEN", "🧠 غربالگری آلزایمر"),
            ("SPECIAL_CHECKUPS", "چکاپ‌های تخصصی 🏥"),
            ("HOME_REDESIGN", "🏠 بازطراحی محیط زندگی سالمندان"),
        ],
        "MEMORIES": [
            ("HOSTING_EXPERIENCE", "سور (مهمان‌کردن و ساخت تجربه) 🍽️"),
            ("SURPRISE", "🎶 سورپرایز (اجرای غافلگیرکننده)"),
            ("GIFT_FLOWERS_SWEETS", "خرید هدیه، گل و شیرینی 🌸"),
        ],
        "DAILY": [
            ("DAILY_SHOPPING", "خرید روزمره 🧺"),
            ("DIGITAL_HELP", "💻 حل مشکلات دیجیتالی"),
        ],
        "WANT": [
            ("WANT_HEALTH_TRACK", "می‌خوام پیگیر وضعیت سلامت خانواده و عزیزان باشم!"),
            ("WANT_SURPRISE", "می‌خوام خانواده یا یکی از عزیزانم رو سوپرایز یا خوشحال کنم!"),
            ("WANT_SEND_GIFT", "میخوام برای خانوده یا یکی از عزیزانم هدیه، گل یا شیرینی ارسال کنم!"),
            ("WANT_REMOTE_HELP", "نیاز به همیاری دارن و من از راه دور نمی‌تونم انجامش بدم!"),
            ("WANT_NOT_FOUND", "اونی که می‌خوام اینحا نیست!"),
        ],
    }
    rows = []
    for key, label in mapping.get(category_key, []):
        rows.append([InlineKeyboardButton(label, callback_data=f"HELP2:ITEM:{category_key}:{key}")])
    rows.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="HELP2:BACK:MENU")])
    return InlineKeyboardMarkup(rows)


def helper2_item_actions_kb(category_key: str, item_key: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("ثبت سفارش", callback_data=f"HELP2:CONFIRM:{category_key}:{item_key}")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=f"HELP2:CAT:{category_key}")],
    ]
    return InlineKeyboardMarkup(buttons)


def helper2_health_assess_kb(category_key: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("ثبت سفارش 📝", callback_data=f"HELP2:CONFIRM:{category_key}:HEALTH_ASSESS")],
        [InlineKeyboardButton("💬 اگه سوال داری، از من بپرس!", callback_data="NAV:ASK")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=f"HELP2:CAT:{category_key}")],
    ]
    return InlineKeyboardMarkup(buttons)


def helper2_alzheimer_screen_kb(category_key: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("ثبت سفارش 📝", callback_data=f"HELP2:CONFIRM:{category_key}:ALZHEIMER_SCREEN")],
        [InlineKeyboardButton("💬 اگه سوال داری، از من بپرس!", callback_data="NAV:ASK")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=f"HELP2:CAT:{category_key}")],
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
