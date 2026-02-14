"""
Helper (همیار ریشه) section handlers.
"""

from __future__ import annotations

import random
from typing import Dict, List

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from db.database import get_session
from db.crud import create_order
from keyboards import helper_menu_kb, helper_options_kb, helper_confirm_kb, after_confirm_kb
from db.database import get_session
from db.crud import get_categories, get_items_by_category, get_category_by_id, get_or_create_user_by_telegram, update_user_phone


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
    """Show helper categories from the database."""
    query = update.callback_query
    await query.answer()
    async with get_session() as session:
        cats = await get_categories(session)
    categories = [(c.id, c.title) for c in cats]
    await query.edit_message_text("همیار ریشه\n\nیک دسته‌بندی را انتخاب کنید.", reply_markup=helper_menu_kb(categories), parse_mode=ParseMode.HTML)
    return 1


async def helper_category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show options for selected category."""
    query = update.callback_query
    await query.answer()
    _, _, category_id_str = query.data.split(":", 2)
    category_id = int(category_id_str)
    context.user_data["helper_category_id"] = category_id
    async with get_session() as session:
        items = await get_items_by_category(session, category_id)
    opts = [it.title for it in items]
    options_text = "\n".join([f"{i+1}- {title}" for i, title in enumerate(opts)])
    desc = "گزینه‌های مرتبط:"
    text = f"{desc}\n\n{options_text}\n\nلطفاً یکی از گزینه‌های عددی را انتخاب کنید."
    await query.edit_message_text(text, reply_markup=helper_options_kb(category_id, len(opts)), parse_mode=ParseMode.HTML)
    return 1


async def helper_option_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prepare confirmation for a selected option."""
    query = update.callback_query
    await query.answer()
    _, _, category_id_str, idx_str = query.data.split(":", 3)
    category_id = int(category_id_str)
    idx = int(idx_str)
    context.user_data["helper_option_idx"] = idx
    context.user_data["helper_category_id"] = category_id
    async with get_session() as session:
        items = await get_items_by_category(session, category_id)
        cat = await get_category_by_id(session, category_id)
    option_list = [it.title for it in items]
    chosen = option_list[idx - 1] if 0 < idx <= len(option_list) else "گزینه"
    cat_title = cat.title if cat else "—"
    text = (
        f"خلاصه درخواست شما:\n\n"
        f"دسته‌بندی: {cat_title}\n"
        f"گزینه انتخابی: {chosen}\n\n"
        "برای ثبت سفارش، دکمه زیر را انتخاب کنید."
    )
    await query.edit_message_text(text, reply_markup=helper_confirm_kb(category_id, idx), parse_mode=ParseMode.HTML)
    return 1


def _generate_tracking_code() -> str:
    return f"{random.randint(100000, 999999)}"


async def helper_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Request user's contact before finalizing order."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    category_id = int(parts[2]) if len(parts) > 2 else context.user_data.get("helper_category_id")
    idx = int(parts[3]) if len(parts) > 3 else context.user_data.get("helper_option_idx")
    context.user_data["pending_order"] = {"category_id": category_id, "idx": idx}
    await query.edit_message_text("برای تکمیل ثبت سفارش، لطفاً شماره تماس خود را ارسال کنید.", parse_mode=ParseMode.HTML)
    contact_kb = ReplyKeyboardMarkup(
        [[KeyboardButton(text="اشتراک شماره تماس", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="اشتراک شماره تماس",
    )
    await query.message.reply_text("برای ادامه، دکمه «اشتراک شماره تماس» را بزنید.", reply_markup=contact_kb)
    return 1


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.message.contact:
        return 1
    phone = update.message.contact.phone_number
    user = update.effective_user
    telegram_id = user.id if user else None
    username = user.username if user else None
    full_name = user.full_name if user and hasattr(user, "full_name") else (f"{user.first_name} {getattr(user, 'last_name', '')}".strip() if user else None)

    pending = context.user_data.get("pending_order") or {}
    category_id = pending.get("category_id")
    idx = pending.get("idx")

    tracking_code = _generate_tracking_code()
    async with get_session() as session:
        # Upsert user and update phone
        user_row = await get_or_create_user_by_telegram(session, int(telegram_id), username=username, full_name=full_name)
        if phone:
            await update_user_phone(session, user_row, phone)
        items = await get_items_by_category(session, int(category_id)) if category_id else []
        chosen = items[idx - 1].title if isinstance(idx, int) and 0 < idx <= len(items) else None
        cat = await get_category_by_id(session, int(category_id)) if category_id else None
        cat_title = cat.title if cat else None
        await create_order(
            session,
            int(user_row.id),
            tracking_code,
            "درحال انجام",
            category_key=cat_title,
            option_title=chosen,
        )

    text = (
        "سفارش شما ثبت شد ✅\n\n"
        f"کد پیگیری: {tracking_code}\n"
        "پشتیبانی ریشه تا یکساعت آینده با شما تماس خواهد گرفت."
    )
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text("می‌توانید از گزینه‌های زیر استفاده کنید.", reply_markup=after_confirm_kb())
    context.user_data.pop("pending_order", None)
    return 1


async def helper_back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Back to helper category menu."""
    query = update.callback_query
    await query.answer()
    async with get_session() as session:
        cats = await get_categories(session)
    categories = [(c.id, c.title) for c in cats]
    await query.edit_message_text("همیار ریشه\n\nیک دسته‌بندی را انتخاب کنید.", reply_markup=helper_menu_kb(categories), parse_mode=ParseMode.HTML)
    return 1


async def helper_back_to_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Back to options of the current category."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    category_id = int(parts[-1])
    async with get_session() as session:
        items = await get_items_by_category(session, category_id)
    opts = [it.title for it in items]
    options_text = "\n".join([f"{i+1}- {title}" for i, title in enumerate(opts)])
    desc = "گزینه‌های مرتبط:"
    text = f"{desc}\n\n{options_text}\n\nلطفاً یکی از گزینه‌های عددی را انتخاب کنید."
    await query.edit_message_text(text, reply_markup=helper_options_kb(category_id, len(opts)), parse_mode=ParseMode.HTML)
    return 1

