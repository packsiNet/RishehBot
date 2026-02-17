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
    helper2_alzheimer_screen_kb,
    helper2_hosting_experience_kb,
    helper2_surprise_kb,
    helper2_gift_flowers_sweets_kb,
    helper2_home_redesign_kb,
    helper2_special_checkups_kb,
    helper2_daily_shopping_kb,
    helper2_digital_help_kb,
    helper2_want_request_kb,
)
from db.database import get_session
from db.crud import get_categories, get_items_by_category, get_category_by_id, get_or_create_user_by_telegram, update_user_phone, get_admin_telegram_ids, create_custom_request


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
    if cat_key == "WANT" and item_key == "WANT_NOT_FOUND":
        text = (
            "❓ اونی که می‌خوام اینجا نیست!\n\n"
            "اگه چیزی که مدنظرته داخل گزینه‌ها پیدا نکردی، اینجا بهمون بگو دقیقاً چی نیاز داری ✍️\n"
            "درخواستت ثبت می‌شه و تیم ریشه بررسیش می‌کنه 🔎 تا ببینیم امکان انجامش وجود داره یا نه.\n"
            "اگه قابل اجرا باشه، کارشناسانمون باهات تماس می‌گیرن 📞، جزئیات رو هماهنگ می‌کنن و مسیر انجامش رو برات شفاف توضیح می‌دن.\n"
            "هدف ما اینه که همراهی محدود به چند خدمت ثابت نباشه 🤍\n"
            "هر جا نیاز واقعی وجود داشته باشه، بررسیش می‌کنیم.\n\n"
            "درخواستت رو برامون بنویس 📝\n"
            "کافیه دکمه زیر رو بزنی و بعدش متن، ویس 🎙️ یا ویدیوی مدنظرت رو برامون ارسال کنی 🎥"
        )
        await query.edit_message_text(text, reply_markup=helper2_want_request_kb("WANT"), parse_mode=ParseMode.HTML)
        return 1
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
    elif cat_key == "PREVENTIVE" and item_key == "ALZHEIMER_SCREEN":
        text = (
            "🧠 غربالگری آلزایمر\n\n"
            "این خدمت برای بررسی اولیه حافظه و عملکرد شناختی طراحی شده.\n"
            "ریشه هماهنگ می‌کنه تا ارزیابی‌های استاندارد توسط متخصص انجام بشه 👩🏻‍⚕️ و نتیجه به‌صورت گزارش شفاف ارائه بشه.\n"
            "اگه نیاز به بررسی تخصصی‌تر باشه، مسیر ارجاع هم مشخص می‌شه 📋\n"
            "این کار کمک می‌کنه آلزایمر زودتر دیده بشه و مدیریت‌ش راحت‌تر باشه.\n"
            "برای اطلاع از نحوه سفارش و اینکه سنجش سلامت چطور انجام میشه، حتما ویدیو/ فایل بالا رو نگاه کن 🎥📎"
        )
        await query.edit_message_text(text, reply_markup=helper2_alzheimer_screen_kb(cat_key), parse_mode=ParseMode.HTML)
    elif cat_key == "MEMORIES" and item_key == "HOSTING_EXPERIENCE":
        text = (
            "🍽️ سور (مهمان‌کردن و ساخت تجربه)\n\n"
            "اگه می‌خوای عزیزت رو مهمون کنی و یه تجربه خوب براش بسازی، این گزینه برای توئه 🎉\n"
            "ریشه هماهنگی رزرو، طراحی تجربه مناسبتی، اجرای برنامه و گزارش نهایی رو مدیریت می‌کنه.\n"
            "تو جزئیات رو می‌گی ✍️، ما پیگیری می‌کنیم تا اتفاق درست و دقیق اجرا بشه ✨\n"
            "برای اطلاع از نحوه سفارش و اینکه سنجش سلامت چطور انجام میشه، حتما ویدیو/ فایل بالا رو نگاه کن 🎥📎"
        )
        await query.edit_message_text(text, reply_markup=helper2_hosting_experience_kb(cat_key), parse_mode=ParseMode.HTML)
    elif cat_key == "MEMORIES" and item_key == "SURPRISE":
        text = (
            "🎉 سورپرایز (اجرای غافلگیرکننده)\n\n"
            "برای وقتی که می‌خوای یه لحظه غافلگیرکننده بسازی؛ مثل نوازنده 🎶، برنامه کوتاه هنری، تولد 🎂 یا یه اجرای ویژه در خانه یا لوکیشن مشخص.\n"
            "ریشه هماهنگی‌ها رو انجام می‌ده، اجرای برنامه رو مدیریت می‌کنه و مستندات/گزارش انجام رو برات می‌فرسته 📸📄\n"
            "برای اطلاع از نحوه سفارش و اینکه سنجش سلامت چطور انجام میشه، حتما ویدیو/ فایل بالا رو نگاه کن 🎥📎"
        )
        await query.edit_message_text(text, reply_markup=helper2_surprise_kb(cat_key), parse_mode=ParseMode.HTML)
    elif cat_key == "MEMORIES" and item_key == "GIFT_FLOWERS_SWEETS":
        text = (
            "🎁 خرید هدیه، گل و شیرینی\n\n"
            "اگه می‌خوای هدیه، گل 🌸 یا شیرینی 🍰 برای عزیزت در ایران ارسال کنی، اینجا ثبت کن.\n"
            "ریشه از تأمین‌کننده‌های معتبر در شهر مقصد خرید رو هماهنگ می‌کنه و روند انتخاب، پرداخت، تحویل و تأیید انجام رو مدیریت می‌کنه.\n"
            "تمرکز این خدمته: کیفیت قابل اتکا ✔️، قیمت شفاف 💳، و اطمینان از تحویل 📦\n"
            "برای اطلاع از نحوه سفارش و اینکه سنجش سلامت چطور انجام میشه، حتما ویدیو/ فایل بالا رو نگاه کن 🎥📎"
        )
        await query.edit_message_text(text, reply_markup=helper2_gift_flowers_sweets_kb(cat_key), parse_mode=ParseMode.HTML)
    elif cat_key == "PREVENTIVE" and item_key == "HOME_REDESIGN":
        text = (
            "🏠 بازطراحی محیط زندگی سالمند\n\n"
            "این خدمت برای کم کردن ریسک حادثه در خانه ⚠️ و راحت‌تر شدن زندگی سالمند طراحی شده.\n"
            "ریشه ارزیابی محیط رو هماهنگ می‌کنه، نقاط پرخطر مشخص می‌شه 🔎 و پیشنهادهای اصلاحی داده می‌شه.\n"
            "اگه تأیید کنی، اجرای اصلاحات هم هماهنگ می‌شه؛ مثل اصلاح سرویس بهداشتی 🚿، نصب تجهیزات کمکی، بهتر کردن نور 💡 یا اصلاح چیدمان.\n"
            "در پایان هم گزارش ارزیابی و نتیجه اقدامات برای تو ارسال می‌شه 📄\n"
            "برای اطلاع از نحوه سفارش و اینکه سنجش سلامت چطور انجام میشه، حتما ویدیو/ فایل بالا رو نگاه کن 🎥📎"
        )
        await query.edit_message_text(text, reply_markup=helper2_home_redesign_kb(cat_key), parse_mode=ParseMode.HTML)
    elif cat_key == "PREVENTIVE" and item_key == "SPECIAL_CHECKUPS":
        text = (
            "🩺 چکاپ‌های تخصصی\n\n"
            "آگاهی قبل از بحران. ⚠️\n"
            "این خدمت برای انجام چکاپ‌های تخصصی دوره‌ای طراحی شده؛\n"
            "همون بررسی‌هایی که هر فرد در طول زندگی باید انجام بده تا از وضعیت دقیق سلامت خودش باخبر باشه.\n"
            "از چکاپ‌های مرتبط با سن سالمندی 👵👴 گرفته تا بررسی‌هایی که بهتره در سنین پایین‌تر انجام بشه تا ریسک‌ها زودتر شناسایی بشن.\n"
            "تو درخواست رو ثبت می‌کنی ✍️، ریشه هماهنگی با مراکز معتبر رو انجام می‌ده\n"
            "و بعد از انجام چکاپ، گزارش شفاف برای خود فرد و در صورت درخواست برای تو ارسال می‌شه 📄\n"
            "برای اطلاع از نحوه سفارش و اینکه سنجش سلامت چطور انجام میشه، حتما ویدیو/ فایل بالا رو نگاه کن 🎥📎"
        )
        await query.edit_message_text(text, reply_markup=helper2_special_checkups_kb(cat_key), parse_mode=ParseMode.HTML)
    elif cat_key == "DAILY" and item_key == "DAILY_SHOPPING":
        text = (
            "🛒 خریدهای روزمره (انجام امور روزانه)\n\n"
            "اگه والدین یا عزیزت برای انجام خریدهای روزمره به کمک نیاز دارن،\n"
            "اینجا می‌تونی درخواست ثبت کنی.\n"
            "ریشه هماهنگ می‌کنه تا فرد معتمد خریدهای موردنیاز رو انجام بده؛\n"
            "از خریدهای سوپرمارکتی 🏪 و دارویی 💊 گرفته\n"
            "تا اقلام ضروری روزمره‌ای که انجامش برای سالمند سخت شده.\n"
            "فرآیند خرید، تحویل 📦 و تأیید انجام مدیریت می‌شه و گزارش برات ارسال می‌شه 📄\n"
            "این خدمت برای وقت‌هایی طراحی شده که حضور تو لازمه، اما امکانش رو نداری 🤍\n"
            "برای اطلاع از نحوه سفارش و اینکه سنجش سلامت چطور انجام میشه، حتما ویدیو/ فایل بالا رو نگاه کن 🎥📎"
        )
        await query.edit_message_text(text, reply_markup=helper2_daily_shopping_kb(cat_key), parse_mode=ParseMode.HTML)
    elif cat_key == "DAILY" and item_key == "DIGITAL_HELP":
        text = (
            "💻 همراهی در خدمات دیجیتال\n\n"
            "برای خیلی از سالمندان، انجام کارهای دیجیتال ساده نیست.\n"
            "از خرید اشتراک پلتفرم‌های نمایش خانگی 🎬\n"
            "گرفته تا خرید اینترنت 🌐، نصب و راه‌اندازی تجهیزات، تنظیم تلویزیون 📺 یا حتی نصب نرم‌افزارهای موردنیاز.\n"
            "اگه عزیزت در انجام این کارها نیاز به همراهی داره،\n"
            "ریشه هماهنگ می‌کنه تا فردی متخصص کمکش کنه 👨🏻‍🔧\n"
            "تو درخواست رو ثبت می‌کنی ✍️،\n"
            "ما هماهنگی و اجرا رو مدیریت می‌کنیم\n"
            "و نتیجه انجام کار رو برات گزارش می‌دیم 📄\n"
            "هدف؛ کم‌کردن وابستگی و ساده‌تر کردن زندگی روزمره 🤍\n"
            "برای اطلاع از نحوه سفارش و اینکه سنجش سلامت چطور انجام میشه، حتما ویدیو/ فایل بالا رو نگاه کن 🎥📎"
        )
        await query.edit_message_text(text, reply_markup=helper2_digital_help_kb(cat_key), parse_mode=ParseMode.HTML)
    else:
        text = (
            f"{cat_title}\n\n"
            f"خدمت انتخابی: {item_title}\n\n"
            "برای ثبت سفارش و پیگیری توسط تیم ریشه، دکمه زیر را بزن."
        )
        await query.edit_message_text(text, reply_markup=helper2_item_actions_kb(cat_key, item_key), parse_mode=ParseMode.HTML)
    return 1


async def helper2_request_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["await_custom_request"] = True
    context.user_data.pop("await_phone", None)
    text = (
        "❓ اونی که می‌خوای اینجا نیست!\n\n"
        "لطفاً درخواستت رو برامون بفرست؛ می‌تونی متن، ویس یا ویدیو ارسال کنی.\n"
        "بعد از دریافت، تیم ریشه بررسی می‌کنه و در صورت امکان اجرا باهات تماس می‌گیره."
    )
    await query.edit_message_text(text, parse_mode=ParseMode.HTML)
    return 1


async def handle_custom_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message:
        return 1
    if not context.user_data.get("await_custom_request"):
        return 1
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
            category_key="WANT",
            option_title="درخواست سفارشی",
        )
        content_text = None
        try:
            if update.message.text:
                content_text = update.message.text
            elif getattr(update.message, "caption", None):
                content_text = update.message.caption
        except Exception:
            content_text = None
        await create_custom_request(session, int(user_row.id), content_text, tracking_code)
    confirm_text = (
        "✅ درخواستت ثبت شد.\n"
        "تیم ریشه بررسیش می‌کنه 🔎 تا امکان انجامش رو بسنجه.\n"
        "به‌محض اینکه نتیجه بررسی مشخص بشه،\n"
        "باهات ارتباط می‌گیریم 📞 و جزئیات رو برات توضیح می‌دیم.\n"
        "🤍 ممنون که برای همراهی، ریشه رو انتخاب کردی."
    )
    await update.message.reply_text(confirm_text, reply_markup=after_confirm_kb(), parse_mode=ParseMode.HTML)
    display_name = (user_row.full_name.strip() if user_row.full_name and user_row.full_name.strip() else (f"@{user_row.username.strip()}" if user_row.username and str(user_row.username).strip() else "کاربر ناشناس"))
    await _notify_admins_new_order(context, user_row.telegram_id, display_name, tracking_code, "WANT", "درخواست سفارشی", user_row.username)
    try:
        async with get_session() as session:
            admin_ids = await get_admin_telegram_ids(session)
    except Exception:
        admin_ids = []
    for aid in admin_ids:
        try:
            await context.bot.copy_message(chat_id=aid, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
        except Exception:
            try:
                text = update.message.text if update.message.text else "محتوای غیرمتنی دریافت شد."
                await context.bot.send_message(chat_id=aid, text=f"جزئیات درخواست ({tracking_code}):\n{text}")
            except Exception:
                pass
    context.user_data.pop("await_custom_request", None)
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
