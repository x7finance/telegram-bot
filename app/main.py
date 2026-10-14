import os
import subprocess
import sys
from pathlib import Path
from warnings import filterwarnings

from bot import callbacks, commands, conversations
from constants.general import settings, urls
from services import get_dbmanager
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)
from telegram.warnings import PTBUserWarning
from utils import tools

db = get_dbmanager()

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()


def init_alerts_bot():
    print("🔄 Initializing alerts bot...")
    python_executable = sys.executable
    script_path = Path(__file__).parent / "alertsbot.py"

    command = [python_executable, str(script_path)]
    process = subprocess.Popen(command)
    return process


def init_main_bot():
    print("🔄 Initializing main bot...")
    application.add_error_handler(tools.error_handler)

    for handler in conversations.HANDLERS:
        application.add_handler(
            ConversationHandler(
                entry_points=handler["entry_points"],
                states=handler["states"],
                fallbacks=handler.get(
                    "fallbacks",
                    [CommandHandler("cancel", callbacks.general.cancel)],
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

    for handler in callbacks.AUTO_HANDLERS:
        application.add_handler(handler)

    print("✅ Main bot initialized")


def init_price_bot():
    print("🔄 Initializing price bot...")
    python_executable = sys.executable
    script_path = Path(__file__).parent / "pricebot.py"

    command = [python_executable, str(script_path)]
    process = subprocess.Popen(command)
    return process


async def post_init(application: Application):
    if not tools.is_local():
        print("✅ Bot Running on server")

        if await db.settings.get("click_me"):
            application.job_queue.run_once(
                callbacks.clickme.send,
                settings.FIRST_BUTTON_TIME,
                chat_id=urls.TG_MAIN_CHANNEL_ID,
                name="Click Me",
            )

        print(await tools.update_bot_commands())
        print(await tools.set_reminders(application))

        init_alerts_bot()
        # init_price_bot()

    else:
        print("✅ Main bot Running locally")


if __name__ == "__main__":
    init_main_bot()
    application.post_init = post_init
    application.run_polling(allowed_updates=Update.ALL_TYPES)
