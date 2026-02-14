"""
Helper (همیار ریشه) section handlers.
"""

from __future__ import annotations

import random
from typing import Dict, List

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from data.mock_data import add_order
from keyboards import helper_menu_kb, helper_options_kb, helper_confirm_kb, after_confirm_kb


# Category descriptions and numeric options
CATEGORY_DESC: Dict[str, str] = {
    "HEALTH": "گزینه‌های مرتبط با پیگیری وضعیت سلامتی:",
    "REMINDER": "گزینه‌های مرتبط با یادآوری‌های مهربانانه:",
    "TASK": "گزینه‌های مرتبط با انجام کارهای ضروری:",
    "JOY": "گزینه‌های مرتبط با ایجاد لحظات خوشحال‌کننده:",
}


CATEGORY_OPTIONS: Dict[str, List[str]] = {
    "HEALTH": [
        "هماهنگی تماس پزشک",
        "یادآوری مصرف دارو",
        "چک‌این روزانه",
    ],
    "REMINDER": [
        "ارسال پیام محبت‌آمیز",
        "یادآوری رویداد خانوادگی",
        "خبرگیری کوتاه",
    ],
    "TASK": [
        "هماهنگی امور بانکی",
        "پرداخت قبوض",
        "پیگیری مراجعه حضوری",
    ],
    "JOY": [
        "ارسال هدیه کوچک",
        "هماهنگی تماس تصویری",
        "ترتیب یک غافلگیری",
    ],
}


async def open_helper_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show helper categories."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("همیار ریشه\n\nیک دسته‌بندی را انتخاب کنید.", reply_markup=helper_menu_kb(), parse_mode=ParseMode.HTML)
    return 1


async def helper_category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show options for selected category."""
    query = update.callback_query
    await query.answer()
    _, _, category_key = query.data.split(":", 2)
    context.user_data["helper_category"] = category_key
    desc = CATEGORY_DESC.get(category_key, "گزینه‌های مرتبط:")
    opts = CATEGORY_OPTIONS.get(category_key, [])
    options_text = "\n".join([f"{i+1}- {opt}" for i, opt in enumerate(opts)])
    text = f"{desc}\n\n{options_text}\n\nلطفاً یکی از گزینه‌های عددی را انتخاب کنید."
    await query.edit_message_text(text, reply_markup=helper_options_kb(category_key, len(opts)), parse_mode=ParseMode.HTML)
    return 1


async def helper_option_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prepare confirmation for a selected option."""
    query = update.callback_query
    await query.answer()
    _, _, category_key, idx_str = query.data.split(":", 3)
    idx = int(idx_str)
    context.user_data["helper_option_idx"] = idx
    option_list = CATEGORY_OPTIONS.get(category_key, [])
    chosen = option_list[idx - 1] if 0 < idx <= len(option_list) else "گزینه"
    text = (
        f"خلاصه درخواست شما:\n\n"
        f"دسته‌بندی: {CATEGORY_DESC.get(category_key, '—')}\n"
        f"گزینه انتخابی: {chosen}\n\n"
        "برای ثبت سفارش، دکمه زیر را انتخاب کنید."
    )
    await query.edit_message_text(text, reply_markup=helper_confirm_kb(category_key, idx), parse_mode=ParseMode.HTML)
    return 1


def _generate_tracking_code() -> str:
    return f"{random.randint(100000, 999999)}"


async def helper_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save order in mock DB and show confirmation with tracking code."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    tracking_code = _generate_tracking_code()
    add_order(user_id, {"tracking_code": tracking_code, "status": "درحال انجام"})
    text = (
        "سفارش شما ثبت شد ✅\n\n"
        f"کد پیگیری: {tracking_code}\n"
        "پشتیبانی ریشه تا یکساعت آینده با شما تماس خواهد گرفت."
    )
    await query.edit_message_text(text, reply_markup=after_confirm_kb(), parse_mode=ParseMode.HTML)
    return 1


async def helper_back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Back to helper category menu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("همیار ریشه\n\nیک دسته‌بندی را انتخاب کنید.", reply_markup=helper_menu_kb(), parse_mode=ParseMode.HTML)
    return 1


async def helper_back_to_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Back to options of the current category."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    category_key = parts[-1]
    desc = CATEGORY_DESC.get(category_key, "گزینه‌های مرتبط:")
    opts = CATEGORY_OPTIONS.get(category_key, [])
    options_text = "\n".join([f"{i+1}- {opt}" for i, opt in enumerate(opts)])
    text = f"{desc}\n\n{options_text}\n\nلطفاً یکی از گزینه‌های عددی را انتخاب کنید."
    await query.edit_message_text(text, reply_markup=helper_options_kb(category_key, len(opts)), parse_mode=ParseMode.HTML)
    return 1

