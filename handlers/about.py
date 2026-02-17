"""Info section handlers simplified."""

from __future__ import annotations

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from keyboards import back_to_main_button


async def open_trust(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "چطور به ریشه اعتماد کنم؟\n\n"
        "ریشه با اتکا به همیاران احرازشده، سازوکار پیگیری شفاف و ثبت سفارش با کد رهگیری کار می‌کند. "
        "ارزیابی کیفی خدمات و ارتباط مستقیم با تیم پشتیبانی برای هر سفارش فراهم است."
    )
    await query.edit_message_text(text, reply_markup=back_to_main_button(), parse_mode=ParseMode.HTML)
    return 1


async def open_whatis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "ریشه چیه؟\n\n"
        "ریشه یک سرویس همراهی و مراقبت خانوادگیه که خدمات سلامت، همراهی و کارهای روزمره را "
        "به‌صورت یکپارچه برای عزیزانت فراهم می‌کند تا حتی از دور کنارشان بمانی."
    )
    await query.edit_message_text(text, reply_markup=back_to_main_button(), parse_mode=ParseMode.HTML)
    return 1


async def open_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "سوالت رو بپرس!\n\n"
        "هر سوالی داری همینجا تایپ کن تا راهنمایی‌ت کنیم. "
        "اگر موضوعت فوریه، از طریق ثبت سفارش در «شروع همراهی» اقدام کن."
    )
    await query.edit_message_text(text, reply_markup=back_to_main_button(), parse_mode=ParseMode.HTML)
    return 1

