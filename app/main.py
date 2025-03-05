from telegram import Message, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)

import os
import sys
import sentry_sdk
import subprocess
from pathlib import Path
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings

from bot import auto, callbacks, commands, conversations
from constants.bot import settings, urls
from utils import tools
from services import get_dbmanager

db = get_dbmanager()

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

application = (
    Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
)

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=1.0)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    for handler in conversations.HANDLERS:
        application.add_handler(
            ConversationHandler(
                entry_points=handler["entry_points"],
                states=handler["states"],
                fallbacks=handler.get(
                    "fallbacks", [CommandHandler("cancel", callbacks.cancel)]
                ),
            )
        )

    for cmd, handler, _ in commands.GENERAL_HANDLERS:
        if isinstance(cmd, list):
            for alias in cmd:
                application.add_handler(CommandHandler(alias, handler))
        else:
            application.add_handler(CommandHandler(cmd, handler))

    for cmd, handler, _ in commands.ADMIN_HANDLERS:
        application.add_handler(CommandHandler(cmd, handler))

    for handler, pattern in callbacks.HANDLERS:
        application.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    for handler in auto.HANDLERS:
        application.add_handler(handler)

    print("✅ Main bot initialized")


async def post_init(application: Application):
    if not tools.is_local():
        print("✅ Bot Running on server")

        if await db.settings_get("click_me"):
            application.job_queue.run_once(
                auto.button_send,
                settings.FIRST_BUTTON_TIME,
                chat_id=urls.TG_MAIN_CHANNEL_ID,
                name="Click Me",
            )

        print(await tools.update_bot_commands())

        init_alerts_bot()

    else:
        print("✅ Bot Running locally")


if __name__ == "__main__":
    init_main_bot()
    application.post_init = post_init
    application.run_polling(allowed_updates=Update.ALL_TYPES)
