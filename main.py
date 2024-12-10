from telegram import *
from telegram.ext import *

import os, sys, sentry_sdk,subprocess

from bot import admin, auto, callbacks, commands
from constants import settings, urls
from hooks import db, tools

application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
job_queue = application.job_queue


sentry_sdk.init(
    dsn = os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0
)


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
        return


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


def scanners():
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), "scanner.py")
    if os.path.exists(script_path):
        command = [python_executable, script_path]
        process = subprocess.Popen(command)
        return process


if __name__ == "__main__":
    application.add_error_handler(error)

    application.add_handler(CommandHandler("about", commands.about))
    application.add_handler(CommandHandler("admins", commands.admins))
    application.add_handler(CommandHandler("alerts", commands.alerts))
    application.add_handler(CommandHandler("announcements", commands.announcements))
    application.add_handler(CommandHandler(["arb", "arbitrage"], commands.arb))
    application.add_handler(CommandHandler("blocks", commands.blocks))
    application.add_handler(CommandHandler("blog", commands.blog))
    application.add_handler(CommandHandler("borrow", commands.borrow))
    application.add_handler(CommandHandler("burn", commands.burn))
    application.add_handler(CommandHandler("buy", commands.buy))
    application.add_handler(CommandHandler("channels", commands.channels))
    application.add_handler(CommandHandler(["chart", "charts"], commands.chart))
    application.add_handler(CommandHandler("check", commands.check))
    application.add_handler(CommandHandler("compare", commands.compare))
    application.add_handler(CommandHandler(["constellations", "constellation", "quints"], commands.constellations))
    application.add_handler(CommandHandler(["ca", "contract", "contracts"], commands.contracts))
    application.add_handler(CommandHandler("contribute", commands.contribute))
    application.add_handler(CommandHandler("convert", commands.convert))
    application.add_handler(CommandHandler(["dao", "vote", "snapshot", "propose"], commands.dao_command))
    application.add_handler(CommandHandler(["docs", "documents"], commands.docs,))
    application.add_handler(CommandHandler(["ecosystem", "tokens"], commands.ecosystem))
    application.add_handler(CommandHandler("factory", commands.factory))
    application.add_handler(CommandHandler("faq", commands.faq))
    application.add_handler(CommandHandler("feeto", commands.feeto))
    application.add_handler(CommandHandler(["fg", "feargreed"], commands.fg))
    application.add_handler(CommandHandler(["fee", "fees", "costs", "gas"], commands.gas))
    application.add_handler(CommandHandler("github", commands.github_command))
    application.add_handler(CommandHandler("holders", commands.holders))
    application.add_handler(CommandHandler(["hub", "hubs", "buybacks"], commands.hub))
    application.add_handler(CommandHandler("leaderboard", commands.leaderboard))
    application.add_handler(CommandHandler(["links", "socials", "dune", "reddit"], commands.links))
    application.add_handler(CommandHandler("liquidate", commands.liquidate))
    application.add_handler(CommandHandler(["liquidity", "liq", "supply"], commands.liquidity))
    application.add_handler(CommandHandler(["loan", "loans"], commands.loan))
    application.add_handler(CommandHandler("locks", commands.locks))
    application.add_handler(CommandHandler("me", commands.me))
    application.add_handler(CommandHandler(["mcap", "marketcap", "cap"], commands.mcap))
    application.add_handler(CommandHandler("media", commands.media_command))
    application.add_handler(CommandHandler(["nft", "nfts"], commands.nft))
    application.add_handler(CommandHandler(["on_chain", "onchain", "deployer"], commands.onchains))
    application.add_handler(CommandHandler(["pair", "pairs"], commands.pair))
    application.add_handler(CommandHandler("pfp", commands.pfp))
    application.add_handler(CommandHandler("pioneer", commands.pioneer))
    application.add_handler(CommandHandler(["pool", "lpool", "lendingpool"], commands.pool))
    application.add_handler(CommandHandler(["price", "prices"], commands.price))
    application.add_handler(CommandHandler("router", commands.router))
    application.add_handler(CommandHandler("smart", commands.smart))
    application.add_handler(CommandHandler(["split", "splitters", "splitter"], commands.splitters_command))
    application.add_handler(CommandHandler(["tax", "slippage"], commands.tax_command))
    application.add_handler(CommandHandler("timestamp", commands.timestamp_command))
    application.add_handler(CommandHandler(["time", "clock"], commands.time_command))
    application.add_handler(CommandHandler("treasury", commands.treasury))
    application.add_handler(CommandHandler(["trending", "trend"], commands.trending))
    application.add_handler(CommandHandler(["twitter", "xtrader", "0xtrader"], commands.twitter_command))
    application.add_handler(CommandHandler(["website", "site", "swap", "dex", "xchange"], commands.website))
    application.add_handler(CommandHandler(["volume"], commands.volume))
    application.add_handler(CommandHandler("wei", commands.wei))
    application.add_handler(CommandHandler("warpcast", commands.warpcast_command))
    application.add_handler(CommandHandler("wallet", commands.wallet))
    application.add_handler(CommandHandler(["website", "site"], commands.website))
    application.add_handler(CommandHandler(["whitepaper", "wp", "wpquote"], commands.wp))
    application.add_handler(CommandHandler("x7r", commands.x7r))
    application.add_handler(CommandHandler("x7d", commands.x7d))
    application.add_handler(CommandHandler("x7dao", commands.x7dao))
    application.add_handler(CommandHandler(["x7101", "101"], commands.x7101))
    application.add_handler(CommandHandler(["x7102", "102"], commands.x7102))
    application.add_handler(CommandHandler(["x7103", "103"], commands.x7103))
    application.add_handler(CommandHandler(["x7104", "104"], commands.x7104))
    application.add_handler(CommandHandler(["x7105", "105"], commands.x7105))
    application.add_handler(CommandHandler("x", commands.x))

    application.add_handler(CommandHandler("admin", admin.command))
    application.add_handler(CommandHandler("clickme", admin.click_me))
    application.add_handler(CommandHandler("ping", admin.ping))
    application.add_handler(CommandHandler("wen", admin.wen))

    application.add_handler(CallbackQueryHandler(callbacks.click_me, pattern=r"^click_button:\d+$"))
    application.add_handler(CallbackQueryHandler(callbacks.admin_toggle, pattern="^admin_toggle_"))
    application.add_handler(CallbackQueryHandler(callbacks.clicks_reset, pattern="^clicks_reset_start$"))
    application.add_handler(CallbackQueryHandler(callbacks.clicks_reset_yes, pattern="^clicks_reset_yes$"))
    application.add_handler(CallbackQueryHandler(callbacks.clicks_reset_no, pattern="^clicks_reset_no$"))
    application.add_handler(CallbackQueryHandler(callbacks.pushall, pattern="^push_(eco|treasury|x7r|x7dao|x7100):"))
    application.add_handler(CallbackQueryHandler(callbacks.liquidate, pattern=r"^liquidate:[a-zA-Z0-9-]+:\d+$"))
    application.add_handler(CallbackQueryHandler(callbacks.welcome_button, pattern=r"unmute:.+"))
    
    application.add_handler(ChatMemberHandler(auto.welcome_message, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.StatusUpdate._NewChatMembers(Update) | filters.StatusUpdate._LeftChatMember(Update), auto.welcome_delete))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), auto.replies))

    if not tools.is_local():
        print("Running on server")
        if db.settings_get("click_me"):
            job_queue.run_once(
                auto.button_send,
                settings.FIRST_BUTTON_TIME,
                chat_id=urls.TG_MAIN_CHANNEL_ID,
                name="Click Me",
            )

        scanners()
    else:
        application.add_handler(CommandHandler("test", test_command))
        print("Running Bot locally for testing")

    application.run_polling(allowed_updates=Update.ALL_TYPES)
