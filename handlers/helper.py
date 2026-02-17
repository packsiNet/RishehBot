"""
Helper (همیار ریشه) section handlers.
"""

from __future__ import annotations

import random
from typing import Dict, List
import os
from datetime import datetime

from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from db.database import get_session
from db.crud import create_order
from keyboards import (
    helper_menu_kb,
    helper_options_kb,
    helper_confirm_kb,
    after_confirm_kb,
    helper2_main_kb,
    helper2_category_kb,
    helper2_item_actions_kb,
    helper2_health_assess_kb,
)
from db.database import get_session
from db.crud import get_categories, get_items_by_category, get_category_by_id, get_or_create_user_by_telegram, update_user_phone, get_admin_telegram_ids


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
    """Show new helper v2 menu with predefined categories and intro."""
    query = update.callback_query
    await query.answer()
    text = (
        "🌿 همراهی از اینجا شروع میشه!\n"
        "همراهی می‌تونه از توجه به سلامتی 🩺، رسیدگی به امور روزمره 🛍️\n"
        "یا حتی یک سوپرایز که حال دل رو بهتر می‌کنه 🎁 شروع بشه.\n"
        "بهمون بگو ریشه چیکار می‌تونه برات انجام بده؟ 🤍\n"
        "برای اطلاعات بیشتر از هر سرویس، می‌تونی روی هرکدوم کلیک کنی تا توضیحات کامل برات ارسال بشه ✨"
    )
    await query.edit_message_text(text, reply_markup=helper2_main_kb(), parse_mode=ParseMode.HTML)
    return 1


def _helper2_titles():
    cat_titles = {
        "PREVENTIVE": "⚜️ سلامت پیشگیرانه⚜️",
        "MEMORIES": "⚜️ تجربه لحظه‌های به‌یاد ماندنی از راه‌دور⚜️",
        "DAILY": "⚜️ انجام نیازهای روزمره⚜️",
        "WANT": "⚜️ میخوام .....⚜️",
    }
    item_titles = {
        "HEALTH_ASSESS": "سنجش سلامت 📋",
        "ALZHEIMER_SCREEN": "🧠 غربالگری آلزایمر",
        "SPECIAL_CHECKUPS": "چکاپ‌های تخصصی 🏥",
        "HOME_REDESIGN": "🏠 بازطراحی محیط زندگی سالمندان",
        "HOSTING_EXPERIENCE": "سور (مهمان‌کردن و ساخت تجربه) 🍽️",
        "SURPRISE": "🎶 سورپرایز (اجرای غافلگیرکننده)",
        "GIFT_FLOWERS_SWEETS": "خرید هدیه، گل و شیرینی 🌸",
        "DAILY_SHOPPING": "خرید روزمره 🧺",
        "DIGITAL_HELP": "💻 حل مشکلات دیجیتالی",
        "WANT_HEALTH_TRACK": "می‌خوام پیگیر وضعیت سلامت خانواده و عزیزان باشم!",
        "WANT_SURPRISE": "می‌خوام خانواده یا یکی از عزیزانم رو سوپرایز یا خوشحال کنم!",
        "WANT_SEND_GIFT": "میخوام برای خانوده یا یکی از عزیزانم هدیه، گل یا شیرینی ارسال کنم!",
        "WANT_REMOTE_HELP": "نیاز به همیاری دارن و من از راه دور نمی‌تونم انجامش بدم!",
        "WANT_NOT_FOUND": "اونی که می‌خوام اینحا نیست!",
    }
    return cat_titles, item_titles


async def helper2_open_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, cat_key = query.data.split(":", 2)
    cat_titles, _ = _helper2_titles()
    header = cat_titles.get(cat_key, "—")
    await query.edit_message_text(header, reply_markup=helper2_category_kb(cat_key), parse_mode=ParseMode.HTML)
    return 1


async def helper2_item_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, cat_key, item_key = query.data.split(":", 3)
    cat_titles, item_titles = _helper2_titles()
    cat_title = cat_titles.get(cat_key, "—")
    item_title = item_titles.get(item_key, "—")
    if cat_key == "PREVENTIVE" and item_key == "HEALTH_ASSESS":
        text = (
            "🩺 سنجش سلامت\n\n"
            "یه ارزیابی جامع و پیشگیرانه برای اینکه تصویر دقیقی از وضعیت سلامت پدر یا مادرت داشته باشی — بدون مراجعه حضوری.\n"
            "فقط با یک گفتگوی ۲۰ تا ۳۰ دقیقه‌ای با پزشک متخصص 👨🏻‍⚕️، شش حوزه کلیدی سلامت بررسی می‌شه و در پایان، "
            "یک نقشه روشن از وضعیت سلامت در سه سطح (مطلوب، قابل اصلاح، پرریسک) دریافت می‌کنی.\n"
            "اقدامی ساده برای آگاهی قبل از بحران ⚠️\n"
            "برای اطلاع از نحوه سفارش و اینکه سنجش سلامت چطور انجام میشه، حتما ویدیو/ فایل بالا رو نگاه کن 🎥📎"
        )
        await query.edit_message_text(text, reply_markup=helper2_health_assess_kb(cat_key), parse_mode=ParseMode.HTML)
    else:
        text = (
            f"{cat_title}\n\n"
            f"خدمت انتخابی: {item_title}\n\n"
            "برای ثبت سفارش و پیگیری توسط تیم ریشه، دکمه زیر را بزن."
        )
        await query.edit_message_text(text, reply_markup=helper2_item_actions_kb(cat_key, item_key), parse_mode=ParseMode.HTML)
    return 1


async def helper2_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, _, cat_key, item_key = query.data.split(":", 3)
    _, item_titles = _helper2_titles()
    cat_title = cat_key
    item_title = item_titles.get(item_key, item_key)
    user = update.effective_user
    full_name = user.full_name if hasattr(user, "full_name") else (f"{user.first_name} {getattr(user, 'last_name', '')}".strip() if user else None)
    async with get_session() as session:
        user_row = await get_or_create_user_by_telegram(
            session,
            int(user.id),
            username=user.username if user else None,
            full_name=full_name,
            update_if_exists=False,
        )
        tracking_code = _generate_tracking_code()
        await create_order(
            session,
            int(user_row.id),
            tracking_code,
            "درحال انجام",
            category_key=cat_title,
            option_title=item_title,
        )
    text = (
        "سفارش شما ثبت شد ✅\n\n"
        f"کد پیگیری: {tracking_code}\n"
        "پشتیبانی ریشه تا یکساعت آینده با شما تماس خواهد گرفت."
    )
    await query.edit_message_text(text, reply_markup=after_confirm_kb(), parse_mode=ParseMode.HTML)
    display_name = (user_row.full_name.strip() if user_row.full_name and user_row.full_name.strip() else (f"@{user_row.username.strip()}" if user_row.username and str(user_row.username).strip() else "کاربر ناشناس"))
    await _notify_admins_new_order(context, user_row.telegram_id, display_name, tracking_code, cat_title, item_title, user_row.username)
    return 1


async def helper2_back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "🌿 همراهی از اینجا شروع میشه!\n"
        "همراهی می‌تونه از توجه به سلامتی 🩺، رسیدگی به امور روزمره 🛍️\n"
        "یا حتی یک سوپرایز که حال دل رو بهتر می‌کنه 🎁 شروع بشه.\n"
        "بهمون بگو ریشه چیکار می‌تونه برات انجام بده؟ 🤍\n"
        "برای اطلاعات بیشتر از هر سرویس، می‌تونی روی هرکدوم کلیک کنی تا توضیحات کامل برات ارسال بشه ✨"
    )
    await query.edit_message_text(text, reply_markup=helper2_main_kb(), parse_mode=ParseMode.HTML)
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


def _now_jalali_str() -> str:
    try:
        from jdatetime import datetime as jdt
        return jdt.now().strftime("%Y/%m/%d %H:%M")
    except Exception:
        return datetime.now().strftime("%Y/%m/%d %H:%M")


async def _notify_admins_new_order(context: ContextTypes.DEFAULT_TYPE, user_tel_id: int, user_display: str, tracking_code: str, category_title: str | None, item_title: str | None, username: str | None) -> None:
    # Fetch admins (role_id=1) from DB dynamically
    try:
        async with get_session() as session:
            admin_ids = await get_admin_telegram_ids(session)
    except Exception:
        admin_ids = []
    if not admin_ids:
        return
    when_str = _now_jalali_str()
    item_text = item_title or "—"
    cat_text = category_title or "—"
    text = (
        f"درخواست جدید ثبت شد ✅\n\n"
        f"کاربر: {user_display}\n"
        f"زمان: {when_str}\n"
        f"دسته: {cat_text}\n"
        f"آیتم: {item_text}\n"
        f"کد پیگیری: {tracking_code}"
    )
    contact_url = f"https://t.me/{username}" if username else f"tg://user?id={user_tel_id}"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("تغییر وضعیت", callback_data=f"ORDERS_ADMIN:STATUSMENU:{tracking_code}")],
        [InlineKeyboardButton("ارتباط با کاربر", url=contact_url)],
    ])
    for aid in admin_ids:
        try:
            await context.bot.send_message(chat_id=aid, text=text, reply_markup=kb)
        except Exception:
            continue


async def helper_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Create order immediately and optionally ask for typed phone if missing."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    category_id = int(parts[2]) if len(parts) > 2 else context.user_data.get("helper_category_id")
    idx = int(parts[3]) if len(parts) > 3 else context.user_data.get("helper_option_idx")
    async with get_session() as session:
        items = await get_items_by_category(session, int(category_id)) if category_id else []
        chosen = items[idx - 1].title if isinstance(idx, int) and 0 < idx <= len(items) else None
        cat = await get_category_by_id(session, int(category_id)) if category_id else None
        cat_title = cat.title if cat else None

    user = update.effective_user
    full_name = user.full_name if hasattr(user, "full_name") else (f"{user.first_name} {getattr(user, 'last_name', '')}".strip() if user else None)
    async with get_session() as session:
        user_row = await get_or_create_user_by_telegram(
            session,
            int(user.id),
            username=user.username if user else None,
            full_name=full_name,
            update_if_exists=False,
        )
        tracking_code = _generate_tracking_code()
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
    await query.edit_message_text(text, reply_markup=after_confirm_kb(), parse_mode=ParseMode.HTML)
    display_name = (user_row.full_name.strip() if user_row.full_name and user_row.full_name.strip() else (f"@{user_row.username.strip()}" if user_row.username and str(user_row.username).strip() else "کاربر ناشناس"))
    await _notify_admins_new_order(context, user_row.telegram_id, display_name, tracking_code, cat_title, chosen, user_row.username)
    if not user_row.phone_number:
        context.user_data["await_phone"] = True
        opt_text = (
            "در صورت تمایل به دریافت تماس از پشتیبانی ریشه، شماره تماس خود را تایپ کنید\n"
        )
        await query.message.reply_text(opt_text)
    return 1


def _fa_to_en_digits(s: str) -> str:
    fa = "۰۱۲۳۴۵۶۷۸۹"
    ar = "٠١٢٣٤٥٦٧٨٩"
    trans = {}
    for i, d in enumerate(fa):
        trans[ord(d)] = ord(str(i))
    for i, d in enumerate(ar):
        trans[ord(d)] = ord(str(i))
    return s.translate(trans)


def _is_valid_phone(text: str) -> bool:
    import re
    t = _fa_to_en_digits(text).strip().replace(" ", "")
    return bool(re.fullmatch(r"\+?\d{8,15}", t))


async def handle_phone_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.message.text:
        return 1
    if not context.user_data.get("await_phone"):
        return 1
    raw = update.message.text
    phone = _fa_to_en_digits(raw).strip().replace(" ", "")
    if not _is_valid_phone(phone):
        await update.message.reply_text("شماره واردشده معتبر نیست. لطفاً با قالب 0912… یا +98912… وارد کنید.")
        return 1
    user = update.effective_user
    async with get_session() as session:
        user_row = await get_or_create_user_by_telegram(session, int(user.id), username=user.username if user else None, full_name=(user.full_name if hasattr(user, "full_name") else None), update_if_exists=False)
        await update_user_phone(session, user_row, phone)
    context.user_data.pop("await_phone", None)
    await update.message.reply_text("شماره تماس شما با موفقیت ثبت شد.", reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text("می‌توانید از گزینه‌های زیر استفاده کنید.", reply_markup=after_confirm_kb())
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
