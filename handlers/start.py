"""
Start and main menu handlers.
"""

from __future__ import annotations

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import os
from db.database import get_session
from db.crud import get_or_create_user_by_telegram, set_user_role

from keyboards import main_menu, admin_main_menu


WELCOME_TEXT = (
    "سلام! به ریشه خوش آمدید.\n\n"
    "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start and show the main menu."""
    # Upsert user on first interaction
    user = update.effective_user
    if user:
        full_name = user.full_name if hasattr(user, "full_name") else (f"{user.first_name} {getattr(user, 'last_name', '')}".strip() if user.first_name else None)
        admins = {int(x) for x in os.getenv("ADMIN_TELEGRAM_IDS", "").split(",") if x.strip().isdigit()}
        default_role = 1 if user.id in admins else 2
        async with get_session() as session:
            await get_or_create_user_by_telegram(
                session,
                user.id,
                username=user.username,
                full_name=full_name,
                default_role_id=default_role,
                update_if_exists=False,
            )
    # Choose menu based on role
    kb = main_menu()
    if user:
        async with get_session() as session:
            db_user = await get_or_create_user_by_telegram(session, user.id, update_if_exists=False)
            try:
                admins_env = {int(x) for x in os.getenv("ADMIN_TELEGRAM_IDS", "").split(",") if x.strip().isdigit()}
            except Exception:
                admins_env = set()
            if db_user and db_user.role_id != 1 and user.id in admins_env:
                await set_user_role(session, db_user.id, 1)
                db_user.role_id = 1
            if db_user and db_user.role_id == 1:
                kb = admin_main_menu()
    if update.message:
        await update.message.reply_text(WELCOME_TEXT, reply_markup=kb, parse_mode=ParseMode.HTML)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(WELCOME_TEXT, reply_markup=kb, parse_mode=ParseMode.HTML)
    return 1


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle back to main from anywhere."""
    query = update.callback_query
    await query.answer()
    # Choose menu based on role
    user = update.effective_user
    kb = main_menu()
    if user:
        async with get_session() as session:
            db_user = await get_or_create_user_by_telegram(session, user.id, update_if_exists=False)
            try:
                admins_env = {int(x) for x in os.getenv("ADMIN_TELEGRAM_IDS", "").split(",") if x.strip().isdigit()}
            except Exception:
                admins_env = set()
            if db_user and db_user.role_id != 1 and user.id in admins_env:
                await set_user_role(session, db_user.id, 1)
                db_user.role_id = 1
            if db_user and db_user.role_id == 1:
                kb = admin_main_menu()
    await query.edit_message_text(WELCOME_TEXT, reply_markup=kb, parse_mode=ParseMode.HTML)
    return 1
