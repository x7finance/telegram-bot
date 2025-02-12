from telegram import Message, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
)

import os
import requests
import sys
import sentry_sdk
import subprocess
from pathlib import Path
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings

from constants.bot import settings
from bot.commands import admin, general
from bot import auto, callbacks
from constants.bot import urls
from utils import tools
from services import get_dbmanager

db = get_dbmanager()

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

application = (
    ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
)

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=1.0)


async def error(update: Update, context: CallbackContext):
    if update is None:
        return
    if update.edited_message is not None:
        return
    else:
        message: Message = update.message
        if message is not None and message.text is not None:
            await update.message.reply_text(
                "Uh oh! You trusted code and it failed you! Please try again"
            )
            print(f"{message.text} caused error: {context.error}")
            sentry_sdk.capture_exception(
                Exception(f"{message.text} caused error: {context.error}")
            )
        else:
            print(f"Error occurred without a valid message: {context.error}")
            sentry_sdk.capture_exception(
                Exception(
                    f"Error occurred without a valid message: {context.error}"
                )
            )


def init_alerts_bot():
    print("🔄 Initializing alerts bot...")
    python_executable = sys.executable
    script_path = Path(__file__).parent / "alerts.py"

    command = [python_executable, str(script_path)]
    process = subprocess.Popen(command)
    return process


def init_main_bot():
    print("🔄 Initializing main bot...")
    application.add_error_handler(error)

    for cmd, handler, _ in general.LIST:
        application.add_handler(CommandHandler(cmd, handler))

    for cmd, handler, _ in admin.LIST:
        application.add_handler(CommandHandler(cmd, handler))

    callback_query_handlers = [
        (callbacks.cancel, r"^cancel$"),
        (callbacks.click_me, r"^click_button:\d+$"),
        (callbacks.clicks_reset, r"^clicks_reset$"),
        (callbacks.confirm_simple, r"^question:.*"),
        (callbacks.liquidate, r"^liquidate:\d+:[a-z]+$"),
        (
            callbacks.pushall,
            r"^push:(eco|treasury|x7r|x7dao|x710[1-5]):[a-z]+$",
        ),
        (callbacks.settings_toggle, r"^settings_toggle_"),
        (callbacks.stuck, r"^stuck:.*$"),
        (callbacks.wallet_remove, r"^wallet_remove$"),
        (callbacks.welcome_button, r"unmute:.+"),
    ]

    for handler, pattern in callback_query_handlers:
        application.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    x7d_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                callbacks.x7d_start, pattern="^(mint|redeem):.*$"
            )
        ],
        states={
            callbacks.X7D_AMOUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, callbacks.x7d_amount
                )
            ],
            callbacks.X7D_CONFIRM: [
                CallbackQueryHandler(
                    callbacks.confirm_conv, pattern="^(mint|redeem):.*$"
                ),
                CallbackQueryHandler(callbacks.cancel, pattern="^cancel$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", callbacks.cancel)],
    )
    application.add_handler(x7d_conv_handler)

    withdraw_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                callbacks.withdraw_start, pattern="^withdraw:.*$"
            )
        ],
        states={
            callbacks.WITHDRAW_TOKEN: [
                CallbackQueryHandler(
                    callbacks.withdraw_token, pattern="^withdraw:.*$"
                )
            ],
            callbacks.WITHDRAW_AMOUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, callbacks.withdraw_amount
                )
            ],
            callbacks.WITHDRAW_ADDRESS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, callbacks.withdraw_address
                )
            ],
            callbacks.WITHDRAW_CONFIRM: [
                CallbackQueryHandler(
                    callbacks.confirm_conv, pattern="^withdraw:.*$"
                ),
                CallbackQueryHandler(callbacks.cancel, pattern="^cancel$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", callbacks.cancel)],
    )
    application.add_handler(withdraw_conv_handler)

    auto_handlers = [
        (
            ChatMemberHandler(
                auto.welcome_message, ChatMemberHandler.CHAT_MEMBER
            )
        ),
        (
            MessageHandler(
                filters.StatusUpdate._NewChatMembers(Update)
                | filters.StatusUpdate._LeftChatMember(Update),
                auto.welcome_delete,
            )
        ),
        (MessageHandler(filters.TEXT & (~filters.COMMAND), auto.replies)),
    ]

    for handler in auto_handlers:
        application.add_handler(handler)
    print("✅ Main bot initialized")


def update_bot_commands():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/setMyCommands"

    general_commands = []
    for cmd, _, desc in general.LIST:
        general_commands.append({"command": cmd, "description": desc})

    user_response = requests.post(
        url, json={"commands": general_commands, "scope": {"type": "default"}}
    )

    if user_response.status_code == 200:
        print("✅ General commands updated")
    else:
        print(f"⚠️ Failed to update general commands: {user_response.text}")

    admin_commands = []
    for cmd, _, desc in admin.LIST:
        admin_commands.append({"command": cmd, "description": desc})

    admin_response = requests.post(
        url,
        json={
            "commands": admin_commands,
            "scope": {"type": "all_chat_administrators"},
        },
    )

    if admin_response.status_code == 200:
        print("✅ Admin commands updated")
    else:
        print(f"⚠️ Failed to update admin commands: {admin_response.text}")


if __name__ == "__main__":
    if not tools.is_local():
        print("✅ Bot Running on server")

        if db.settings_get("click_me"):
            application.job_queue.run_once(
                auto.button_send,
                settings.FIRST_BUTTON_TIME,
                chat_id=urls.TG_MAIN_CHANNEL_ID,
                name="Click Me",
            )

        update_bot_commands()
        init_alerts_bot()

    else:
        print("✅ Bot Running locally")

    init_main_bot()
    application.run_polling(allowed_updates=Update.ALL_TYPES)
