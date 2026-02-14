"""
Root application entrypoint for the Telegram bot.

Uses python-telegram-bot async API to provide a clean, modular flow.
"""

from __future__ import annotations

import logging
import os

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from handlers.start import start, back_to_main
from handlers.about import open_about_menu, about_cred, about_iran, about_channel, about_website
from handlers.helper import (
    open_helper_menu,
    helper_category_selected,
    helper_option_selected,
    helper_confirm,
    helper_back_to_menu,
    helper_back_to_options,
    handle_contact,
)
from handlers.orders import open_orders_menu, orders_filter_selected, order_code_selected
from handlers.admin import (
    open_admin_orders_menu,
    admin_orders_filter_selected,
    admin_order_code_selected,
    admin_orders_change_page,
    open_status_menu,
    set_status,
    open_admin_users_menu,
    admin_users_open,
    admin_users_change_page,
    admin_user_selected,
    admin_make_user_admin,
)


import asyncio
from db.database import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Single conversation state to keep navigation in one flow
MENU = 1


async def invalid_callback(update, context):
    """Handle unknown/invalid callback data gracefully."""
    query = update.callback_query
    await query.answer()
    # Reuse start handler to show main menu
    await back_to_main(update, context)
    return MENU


async def unexpected_text(update, context):
    """Handle unexpected user messages by nudging to use buttons."""
    await update.message.reply_text("لطفاً از دکمه‌های موجود استفاده کنید.")
    return MENU


def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                # Main / Back
                CallbackQueryHandler(back_to_main, pattern=r"^BACK:MAIN$"),
                # About section
                CallbackQueryHandler(open_about_menu, pattern=r"^NAV:ABOUT$"),
                CallbackQueryHandler(about_cred, pattern=r"^ABOUT:CRED$"),
                CallbackQueryHandler(about_iran, pattern=r"^ABOUT:IRAN$"),
                CallbackQueryHandler(about_channel, pattern=r"^ABOUT:CHANNEL$"),
                CallbackQueryHandler(about_website, pattern=r"^ABOUT:WEBSITE$"),
                # Helper section
                CallbackQueryHandler(open_helper_menu, pattern=r"^NAV:HELPER$"),
                CallbackQueryHandler(helper_category_selected, pattern=r"^(HELPER:CATEGORY|HELPER:CATEGORY_ID):.*"),
                CallbackQueryHandler(helper_option_selected, pattern=r"^HELPER:OPTION:.*"),
                CallbackQueryHandler(helper_confirm, pattern=r"^HELPER:CONFIRM:.*"),
                CallbackQueryHandler(helper_back_to_menu, pattern=r"^HELPER:BACK:MENU$"),
                CallbackQueryHandler(helper_back_to_options, pattern=r"^HELPER:BACK:OPTIONS:.*"),
                # Contact share for phone number
                MessageHandler(filters.CONTACT, handle_contact),
                # Orders section
                CallbackQueryHandler(open_orders_menu, pattern=r"^NAV:ORDERS$"),
                CallbackQueryHandler(orders_filter_selected, pattern=r"^ORDERS:FILTER:.*"),
                CallbackQueryHandler(order_code_selected, pattern=r"^ORDERS:CODE:\d{6}$"),
                # Admin orders section
                CallbackQueryHandler(open_admin_orders_menu, pattern=r"^NAV:ADMIN_ORDERS$"),
                CallbackQueryHandler(admin_orders_filter_selected, pattern=r"^ORDERS_ADMIN:FILTER:.*"),
                CallbackQueryHandler(admin_orders_change_page, pattern=r"^ORDERS_ADMIN:PAGE:[A-Z_]+:\d+$"),
                CallbackQueryHandler(admin_order_code_selected, pattern=r"^ORDERS_ADMIN:CODE:\d{6}$"),
                CallbackQueryHandler(open_status_menu, pattern=r"^ORDERS_ADMIN:STATUSMENU:\d{6}$"),
                CallbackQueryHandler(set_status, pattern=r"^ORDERS_ADMIN:SETSTATUS:\d{6}:[A-Z_]+$"),
                CallbackQueryHandler(admin_order_code_selected, pattern=r"^ORDERS_ADMIN:CODE:\d{6}:\d+$"),
                # Admin users section
                CallbackQueryHandler(open_admin_users_menu, pattern=r"^NAV:ADMIN_USERS$"),
                CallbackQueryHandler(admin_users_open, pattern=r"^ADMIN_USERS:OPEN$"),
                CallbackQueryHandler(admin_users_change_page, pattern=r"^ADMIN_USERS:PAGE:\d+$"),
                CallbackQueryHandler(admin_user_selected, pattern=r"^ADMIN_USERS:USER:\d+:\d+$"),
                CallbackQueryHandler(admin_make_user_admin, pattern=r"^ADMIN_USERS:MAKE_ADMIN:\d+:\d+$"),
                # Fallback last
                CallbackQueryHandler(invalid_callback),
            ]
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, unexpected_text)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    return app


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN env variable is required")
    db_url = os.getenv("DB_URL", "sqlite+aiosqlite:///./data/app.db")
    asyncio.run(init_db(db_url))
    app = build_app(token)
    logger.info("Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()

