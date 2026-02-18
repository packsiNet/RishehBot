"""
Root application entrypoint for the Telegram bot.

Uses python-telegram-bot async API to provide a clean, modular flow.
"""

from __future__ import annotations

import logging
import os
import os as _os

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from handlers.start import start, back_to_main
from handlers.about import open_trust, open_ask, open_contact_menu, open_contact_socials, open_contact_website, open_contact_support
from handlers.helper import (
    open_helper_menu,
    helper2_open_category,
    helper2_item_selected,
    helper2_confirm,
    helper2_back_to_menu,
    helper2_check_channel_and_confirm,
    helper2_request_start,
    handle_custom_request,
    helper_category_selected,
    helper_option_selected,
    helper_confirm,
    helper_check_join,
    helper_back_to_menu,
    helper_back_to_options,
    handle_phone_text,
)
from handlers.orders import open_orders_menu, orders_filter_selected, order_code_selected, orders_reorder
from handlers.admin import (
    open_admin_orders_menu,
    admin_orders_filter_selected,
    admin_order_code_selected,
    admin_orders_change_page,
    admin_orders_group_selected,
    admin_orders_group_item_page,
    open_status_menu,
    set_status,
    open_admin_users_menu,
    admin_users_open,
    admin_users_change_page,
    admin_user_selected,
    admin_set_user_role,
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
                # Info section
                CallbackQueryHandler(open_trust, pattern=r"^NAV:TRUST$"),
                CallbackQueryHandler(open_contact_menu, pattern=r"^NAV:CONTACT$"),
                CallbackQueryHandler(open_contact_socials, pattern=r"^CONTACT:SOCIALS$"),
                CallbackQueryHandler(open_contact_website, pattern=r"^CONTACT:WEBSITE$"),
                CallbackQueryHandler(open_contact_support, pattern=r"^CONTACT:SUPPORT$"),
                CallbackQueryHandler(open_ask, pattern=r"^NAV:ASK$"),
                # Helper section (v2)
                CallbackQueryHandler(open_helper_menu, pattern=r"^NAV:HELPER$"),
                CallbackQueryHandler(helper2_open_category, pattern=r"^HELP2:CAT:[A-Z_]+$"),
                CallbackQueryHandler(helper2_item_selected, pattern=r"^HELP2:ITEM:[A-Z_]+:[A-Z_]+$"),
                CallbackQueryHandler(helper2_confirm, pattern=r"^HELP2:CONFIRM:[A-Z_]+:[A-Z_]+$"),
                CallbackQueryHandler(helper2_check_channel_and_confirm, pattern=r"^HELP2:CHECK_CHANNEL:[A-Z_]+:[A-Z_]+$"),
                CallbackQueryHandler(helper2_back_to_menu, pattern=r"^HELP2:BACK:MENU$"),
                CallbackQueryHandler(helper2_request_start, pattern=r"^HELP2:REQUEST:START:WANT$"),
                CallbackQueryHandler(helper_category_selected, pattern=r"^(HELPER:CATEGORY|HELPER:CATEGORY_ID):.*"),
                CallbackQueryHandler(helper_option_selected, pattern=r"^HELPER:OPTION:.*"),
                CallbackQueryHandler(helper_check_join, pattern=r"^HELPER:CHECK_JOIN:\d+:\d+$"),
                CallbackQueryHandler(helper_confirm, pattern=r"^HELPER:CONFIRM:.*"),
                CallbackQueryHandler(helper_back_to_menu, pattern=r"^HELPER:BACK:MENU$"),
                CallbackQueryHandler(helper_back_to_options, pattern=r"^HELPER:BACK:OPTIONS:.*"),
                # Capture custom free-form requests first (text/voice/video)
                MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.VOICE | filters.VIDEO, handle_custom_request),
                # Optional phone capture by text when requested
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone_text),
                # Orders section
                CallbackQueryHandler(open_orders_menu, pattern=r"^NAV:ORDERS$"),
                CallbackQueryHandler(orders_filter_selected, pattern=r"^ORDERS:FILTER:.*"),
                CallbackQueryHandler(order_code_selected, pattern=r"^ORDERS:CODE:\d{6}$"),
                CallbackQueryHandler(orders_reorder, pattern=r"^ORDERS:REORDER:\d{6}$"),
                # Admin orders section
                CallbackQueryHandler(open_admin_orders_menu, pattern=r"^NAV:ADMIN_ORDERS$"),
                CallbackQueryHandler(admin_orders_filter_selected, pattern=r"^ORDERS_ADMIN:FILTER:.*"),
                # New grouped admin flows
                CallbackQueryHandler(admin_orders_group_selected, pattern=r"^ORDERS_ADMIN:GROUP:[A-Z_]+$"),
                CallbackQueryHandler(admin_orders_group_item_page, pattern=r"^ORDERS_ADMIN:GROUP_ITEM:[A-Z_]+:\d+:\d+$"),
                CallbackQueryHandler(admin_orders_change_page, pattern=r"^ORDERS_ADMIN:GROUP_ITEM_PAGE:[A-Z_]+:\d+:\d+$"),
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
                CallbackQueryHandler(admin_set_user_role, pattern=r"^ADMIN_USERS:SET_ROLE:\d+:(1|2):\d+$"),
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
    def _load_env_file():
        p = _os.path.join(_os.getcwd(), ".env")
        if _os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        s = line.strip()
                        if not s or s.startswith("#") or "=" not in s:
                            continue
                        k, v = s.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k:
                            _os.environ[k] = v
            except Exception:
                pass

    _load_env_file()
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

