"""
About section handlers.
"""

from __future__ import annotations

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from keyboards import about_menu_kb, channel_kb, website_kb


ABOUT_INTRO = (
    "درباره ریشه\n\n"
    "برای مشاهده اطلاعات، یکی از گزینه‌ها را انتخاب کنید."
)


async def open_about_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show about menu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(ABOUT_INTRO, reply_markup=about_menu_kb(), parse_mode=ParseMode.HTML)
    return 1


async def about_cred(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "اعتبار ریشه\n\n"
        "ریشه با تکیه بر تیم متخصص و شبکه همیارانِ مورداعتماد فعالیت می‌کند."
    )
    await query.edit_message_text(text, reply_markup=about_menu_kb(), parse_mode=ParseMode.HTML)
    return 1


async def about_iran(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "ریشه در ایران\n\n"
        "ما در سراسر ایران همراه خانواده‌ها هستیم و خدمات همیاری را پوشش می‌دهیم."
    )
    await query.edit_message_text(text, reply_markup=about_menu_kb(), parse_mode=ParseMode.HTML)
    return 1


async def about_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "کانال تلگرام\n\n"
        "آخرین اخبار و اطلاع‌رسانی‌ها را در کانال ما دنبال کنید."
    )
    await query.edit_message_text(text, reply_markup=channel_kb("https://t.me/risheh"), parse_mode=ParseMode.HTML)
    return 1


async def about_website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "وبسایت ریشه\n\n"
        "برای اطلاعات بیشتر و خدمات آنلاین، به وبسایت مراجعه کنید."
    )
    await query.edit_message_text(text, reply_markup=website_kb("https://risheh.app"), parse_mode=ParseMode.HTML)
    return 1

