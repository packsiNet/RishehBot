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
        [InlineKeyboardButton("پیگیری سفارش", callback_data="NAV:ORDERS")],
        [InlineKeyboardButton("همیار ریشه", callback_data="NAV:HELPER")],
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


def helper_menu_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("نگران وضعیت سلامتشون هستم", callback_data="HELPER:CATEGORY:HEALTH")],
        [InlineKeyboardButton("میخوام بگم بیادشونم", callback_data="HELPER:CATEGORY:REMINDER")],
        [InlineKeyboardButton("کاری دارن که من از راه دور نمیتوانم انجام دهم", callback_data="HELPER:CATEGORY:TASK")],
        [InlineKeyboardButton("میخوام خوشحالشون کنم", callback_data="HELPER:CATEGORY:JOY")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="BACK:MAIN")],
    ]
    return InlineKeyboardMarkup(buttons)


def helper_options_kb(category_key: str, count: int = 3) -> InlineKeyboardMarkup:
    """Build numeric options (1..count) for a helper category."""
    row: List[InlineKeyboardButton] = []
    for i in range(1, count + 1):
        row.append(
            InlineKeyboardButton(str(i), callback_data=f"HELPER:OPTION:{category_key}:{i}")
        )
    buttons = [row, [InlineKeyboardButton("⬅️ بازگشت", callback_data="HELPER:BACK:MENU")]]
    return InlineKeyboardMarkup(buttons)


def helper_confirm_kb(category_key: str, idx: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("ثبت سفارش", callback_data=f"HELPER:CONFIRM:{category_key}:{idx}")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=f"HELPER:BACK:OPTIONS:{category_key}")],
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
        [InlineKeyboardButton("سفارشات درحال انجام", callback_data="ORDERS:FILTER:ACTIVE")],
        [InlineKeyboardButton("سفارشات انجام شده", callback_data="ORDERS:FILTER:DONE")],
        [InlineKeyboardButton("سفارشات کنسل شده", callback_data="ORDERS:FILTER:CANCEL")],
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

