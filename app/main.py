from telegram import Message, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    filters,
    MessageHandler,
)

import os
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
from utils.tools import is_local
from media import videos
from services import get_dbmanager

db = get_dbmanager()

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

application = (
    ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
)

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=1.0)


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_video(
        video=open(videos.WELCOMEVIDEO, "rb"),
        caption="hello",
        parse_mode="Markdown",
    )


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
            print({context.error})
            sentry_sdk.capture_exception(
                Exception(f"{message.text} caused error: {context.error}")
            )
        else:
            sentry_sdk.capture_exception(
                Exception(
                    f"Error occurred without a valid message: {context.error}"
                )
            )


def run_alerts():
    python_executable = sys.executable
    script_path = Path(__file__).parent / "alerts.py"

    if script_path.exists():
        command = [python_executable, str(script_path)]
        process = subprocess.Popen(command)
        return process
    else:
        print(f"Error: {script_path} not found")


if __name__ == "__main__":
    application.add_error_handler(error)

    application.add_handler(CommandHandler("about", general.about))
    application.add_handler(CommandHandler("admins", general.admins))
    application.add_handler(CommandHandler("alerts", general.alerts))
    application.add_handler(
        CommandHandler("announcements", general.announcements)
    )
    application.add_handler(CommandHandler(["arb", "arbitrage"], general.arb))
    application.add_handler(CommandHandler("blocks", general.blocks))
    application.add_handler(CommandHandler("blog", general.blog))
    application.add_handler(CommandHandler("borrow", general.borrow))
    application.add_handler(CommandHandler("burn", general.burn))
    application.add_handler(CommandHandler("buy", general.buy))
    application.add_handler(CommandHandler("channels", general.channels))
    application.add_handler(CommandHandler(["chart", "charts"], general.chart))
    application.add_handler(CommandHandler("check", general.check))
    application.add_handler(CommandHandler("compare", general.compare))
    application.add_handler(
        CommandHandler(
            ["constellations", "constellation", "quints", "x7100"],
            general.constellations,
        )
    )
    application.add_handler(
        CommandHandler(["ca", "contract", "contracts"], general.contracts)
    )
    application.add_handler(CommandHandler("contribute", general.contribute))
    application.add_handler(CommandHandler("convert", general.convert))
    application.add_handler(
        CommandHandler(
            ["dao", "vote", "snapshot", "propose"], general.dao_command
        )
    )
    application.add_handler(
        CommandHandler(
            ["docs", "documents"],
            general.docs,
        )
    )
    application.add_handler(
        CommandHandler(["ecosystem", "tokens"], general.ecosystem)
    )
    application.add_handler(CommandHandler("factory", general.factory))
    application.add_handler(CommandHandler("faq", general.faq))
    application.add_handler(CommandHandler("feeto", general.feeto))
    application.add_handler(CommandHandler(["fg", "feargreed"], general.fg))
    application.add_handler(
        CommandHandler(["fee", "fees", "costs", "gas"], general.gas)
    )
    application.add_handler(CommandHandler("github", general.github_command))
    application.add_handler(CommandHandler("holders", general.holders))
    application.add_handler(
        CommandHandler(["hub", "hubs", "buybacks"], general.hub)
    )
    application.add_handler(CommandHandler("leaderboard", general.leaderboard))
    application.add_handler(
        CommandHandler(["links", "socials", "dune", "reddit"], general.links)
    )
    application.add_handler(CommandHandler("liquidate", general.liquidate))
    application.add_handler(
        CommandHandler(["liquidity", "liq", "supply"], general.liquidity)
    )
    application.add_handler(CommandHandler(["loan", "loans"], general.loan))
    application.add_handler(CommandHandler("locks", general.locks))
    application.add_handler(CommandHandler(["me", "balance"], general.me))
    application.add_handler(
        CommandHandler(["mcap", "marketcap", "cap"], general.mcap)
    )
    application.add_handler(CommandHandler("media", general.media_command))
    application.add_handler(CommandHandler(["nft", "nfts"], general.nft))
    application.add_handler(
        CommandHandler(["on_chain", "onchain", "deployer"], general.onchains)
    )
    application.add_handler(CommandHandler(["pair", "pairs"], general.pair))
    application.add_handler(CommandHandler("pioneer", general.pioneer))
    application.add_handler(
        CommandHandler(["pool", "lpool", "lendingpool"], general.pool)
    )
    application.add_handler(CommandHandler(["price", "prices"], general.price))
    application.add_handler(
        CommandHandler(["push_all", "pushall"], general.pushall)
    )
    application.add_handler(CommandHandler("register", general.register))
    application.add_handler(CommandHandler("router", general.router))
    application.add_handler(
        CommandHandler(["space", "spaces"], general.spaces)
    )
    application.add_handler(CommandHandler("smart", general.smart))
    application.add_handler(
        CommandHandler(
            ["split", "splitters", "splitter"], general.splitters_command
        )
    )
    application.add_handler(
        CommandHandler(["tax", "slippage"], general.tax_command)
    )
    application.add_handler(
        CommandHandler("timestamp", general.timestamp_command)
    )
    application.add_handler(
        CommandHandler(["time", "clock"], general.time_command)
    )
    application.add_handler(CommandHandler("treasury", general.treasury))
    application.add_handler(
        CommandHandler(["trending", "trend", "top"], general.top)
    )
    application.add_handler(
        CommandHandler(
            ["twitter", "xtrader", "0xtrader"], general.twitter_command
        )
    )
    application.add_handler(
        CommandHandler(
            ["website", "site", "swap", "dex", "xchange"], general.website
        )
    )
    application.add_handler(CommandHandler(["volume"], general.volume))
    application.add_handler(CommandHandler("wei", general.wei))
    application.add_handler(CommandHandler("wallet", general.wallet))
    application.add_handler(
        CommandHandler(["website", "site"], general.website)
    )
    application.add_handler(
        CommandHandler(["whitepaper", "wp", "wpquote"], general.wp)
    )
    application.add_handler(CommandHandler("x7r", general.x7r))
    application.add_handler(CommandHandler("x7d", general.x7d))
    application.add_handler(CommandHandler("x7dao", general.x7dao))
    application.add_handler(CommandHandler(["x7101", "101"], general.x7101))
    application.add_handler(CommandHandler(["x7102", "102"], general.x7102))
    application.add_handler(CommandHandler(["x7103", "103"], general.x7103))
    application.add_handler(CommandHandler(["x7104", "104"], general.x7104))
    application.add_handler(CommandHandler(["x7105", "105"], general.x7105))
    application.add_handler(CommandHandler("x", general.x))

    application.add_handler(CommandHandler("settings", admin.command))
    application.add_handler(CommandHandler("clickme", admin.click_me))
    application.add_handler(CommandHandler("remove", admin.remove))
    application.add_handler(CommandHandler("status", admin.status))
    application.add_handler(CommandHandler("wen", admin.wen))

    application.add_handler(
        CallbackQueryHandler(callbacks.cancel, pattern="^cancel$")
    )
    application.add_handler(
        CallbackQueryHandler(callbacks.click_me, pattern=r"^click_button:\d+$")
    )
    application.add_handler(
        CallbackQueryHandler(callbacks.clicks_reset, pattern="^clicks_reset$")
    )
    application.add_handler(
        CallbackQueryHandler(callbacks.confirm_simple, pattern="^question:.*")
    )
    application.add_handler(
        CallbackQueryHandler(
            callbacks.liquidate, pattern=r"^liquidate:\d+:[a-z]+$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callbacks.pushall,
            pattern=r"^push:(eco|treasury|x7r|x7dao|x710[1-5]):[a-z]+$",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callbacks.settings_toggle, pattern="^settings_toggle_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(callbacks.stuck, pattern="^stuck:.*$")
    )
    application.add_handler(
        CallbackQueryHandler(
            callbacks.wallet_remove, pattern="^wallet_remove$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(callbacks.welcome_button, pattern=r"unmute:.+")
    )

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

    application.add_handler(
        ChatMemberHandler(auto.welcome_message, ChatMemberHandler.CHAT_MEMBER)
    )
    application.add_handler(
        MessageHandler(
            filters.StatusUpdate._NewChatMembers(Update)
            | filters.StatusUpdate._LeftChatMember(Update),
            auto.welcome_delete,
        )
    )
    application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), auto.replies)
    )

    if not is_local():
        print("Running on server")
        if db.settings_get("click_me"):
            application.job_queue.run_once(
                auto.button_send,
                settings.FIRST_BUTTON_TIME,
                chat_id=urls.TG_MAIN_CHANNEL_ID,
                name="Click Me",
            )
        run_alerts()
    else:
        application.add_handler(CommandHandler("test", test_command))
        print("Running locally")

    application.run_polling(allowed_updates=Update.ALL_TYPES)
