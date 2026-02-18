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
    "🌿 ریشه؛ جایی برای اینکه حتی از دور هم کنار خانواده‌ت باشی\n\n"
    "ریشه برای وقت‌هایی شکل گرفت که از خونه دوری، 🏠\n\n"
    "اما نمی‌خوای فاصله باعث بشه از مراقبت و پیگیری جا بمونی. 🤍\n\n"
    "برای اینکه از وضعیت سلامت عزیزت باخبر باشی، 🩺\n\n"
    "نیازهاشون رو مدیریت کنی و با خیال راحت‌تری زندگی کنی. 🕊️\n\n"
    "اینجا خدمات سلامت، همراهی و کارهای روزمره خانواده تو یک ساختار یکپارچه کنار هم قرار گرفته 🔗\n\n"
    "تا بتونی با آگاهی بیشتر و دغدغه کمتر کنارشون بمونی. 🌱\n\n"
    "اگه آماده‌ای این همراهی رو شروع کنی، قدم اول رو تو بردار. 👣\n\n"
    "✨ از منو یکی از مسیرها رو انتخاب کن تا با هم جلو بریم."
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
    is_admin = False
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
                is_admin = True
    display_name = (f"@{user.username}" if getattr(user, "username", None) else (user.full_name if hasattr(user, "full_name") and user.full_name else "ادمین"))
    admin_text = (
        f"{display_name} عزیز خوش آمدید.\n\n"
        "از اینجا می‌توانید مدیریت سفارشات ثبت‌شده و مدیریت کاربران را انجام دهید."
    )
    if update.message:
        if not is_admin:
            video_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "files", "RishehVideo.mp4")
            if os.path.exists(video_path):
                try:
                    with open(video_path, "rb") as vf:
                        await update.message.reply_video(video=vf)
                except Exception:
                    pass
        await update.message.reply_text(admin_text if is_admin else WELCOME_TEXT, reply_markup=kb, parse_mode=ParseMode.HTML)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(admin_text if is_admin else WELCOME_TEXT, reply_markup=kb, parse_mode=ParseMode.HTML)
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
    # Build admin-specific welcome if needed
    is_admin = False
    if user:
        async with get_session() as session:
            db_user = await get_or_create_user_by_telegram(session, user.id, update_if_exists=False)
            if db_user and db_user.role_id == 1:
                is_admin = True
    display_name = (f"@{user.username}" if getattr(user, "username", None) else (user.full_name if hasattr(user, "full_name") and user.full_name else "ادمین"))
    admin_text = (
        f"{display_name} عزیز خوش آمدید.\n\n"
        "از اینجا می‌توانید مدیریت سفارشات ثبت‌شده و مدیریت کاربران را انجام دهید."
    )
    await query.edit_message_text(admin_text if is_admin else WELCOME_TEXT, reply_markup=kb, parse_mode=ParseMode.HTML)
    return 1
