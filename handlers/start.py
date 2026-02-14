"""
Start and main menu handlers.
"""

from __future__ import annotations

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from keyboards import main_menu


WELCOME_TEXT = (
    "سلام! به ریشه خوش آمدید.\n\n"
    "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start and show the main menu."""
    if update.message:
        await update.message.reply_text(WELCOME_TEXT, reply_markup=main_menu(), parse_mode=ParseMode.HTML)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(WELCOME_TEXT, reply_markup=main_menu(), parse_mode=ParseMode.HTML)
    return 1


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle back to main from anywhere."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(WELCOME_TEXT, reply_markup=main_menu(), parse_mode=ParseMode.HTML)
    return 1

