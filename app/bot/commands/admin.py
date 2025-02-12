from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import os
import requests
from datetime import datetime, timedelta

from bot import auto
from constants.bot import settings
from utils import tools
from services import (
    get_blockspan,
    get_coingecko,
    get_dbmanager,
    get_dextools,
    get_dune,
    get_etherscan,
    get_github,
    get_opensea,
    get_snapshot,
    get_twitter,
)

blockspan = get_blockspan()
cg = get_coingecko()
db = get_dbmanager()
dextools = get_dextools()
dune = get_dune()
etherscan = get_etherscan()
github = get_github()
opensea = get_opensea()
snapshot = get_snapshot()
twitter = get_twitter()


async def clickme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        if db.settings_get("click_me"):
            await auto.button_send(context)
        else:
            await update.message.reply_text("Click Me is disabled")


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        user_to_remove = " ".join(context.args)
        result = db.wallet_remove(user_to_remove)
        await update.message.reply_text(result)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        settings = db.settings_get_all()
        if not settings:
            await update.message.reply_text("Error fetching settings.")
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    f"{setting.replace('_', ' ').title()}: {'ON' if status else 'OFF'}",
                    callback_data=f"settings_toggle_{setting}",
                )
            ]
            for setting, status in settings.items()
        ]

        keyboard.append(
            [
                InlineKeyboardButton(
                    "Reset Clicks", callback_data="question:clicks_reset"
                )
            ]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)
        count = db.wallet_count()
        await update.message.reply_text(
            f"Wallet users: {count}", reply_markup=reply_markup
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        message = await update.message.reply_text(
            "Pinging services, Please wait..."
        )
        await context.bot.send_chat_action(update.effective_chat.id, "typing")

        status = []

        blockspan_result = blockspan.ping()
        if blockspan_result is True:
            status.append("🟢 Blockspan: Connected Successfully")
        else:
            status.append(blockspan_result)

        cg_result = cg.ping()
        if cg_result is True:
            status.append("🟢 CoinGecko: Connected Successfully")
        else:
            status.append(cg_result)

        db_result = db.ping()
        if db_result is True:
            status.append("🟢 MySql: Connected Successfully")
        else:
            status.append(db_result)

        defined_result = dextools.ping()
        if defined_result is True:
            status.append("🟢 Defined: Connected Successfully")
        else:
            status.append(defined_result)

        dextools_result = dextools.ping()
        if dextools_result is True:
            status.append("🟢 Dextools: Connected Successfully")
        else:
            status.append(dextools_result)

        drpc_url = f"https://lb.drpc.org/ogrpc?network=ethereum&dkey={os.getenv('DRPC_API_KEY')}"
        drpc_payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1,
        }
        try:
            drpc_response = requests.post(drpc_url, json=drpc_payload)
            if drpc_response.status_code == 200:
                status.append("🟢 DRPC: Connected Successfully")
            else:
                status.append(
                    f"🔴 DRPC: Connection failed: {drpc_response.status_code}"
                )
        except Exception as e:
            status.append(f"🔴 DRPC: Connection failed: {str(e)}")

        dune_result = dune.ping()
        if dune_result is True:
            status.append("🟢 Dune: Connected Successfully")
        else:
            status.append(dune_result)

        etherscan_result = etherscan.ping()
        if etherscan_result is True:
            status.append("🟢 Etherscan: Connected Successfully")
        else:
            status.append(etherscan_result)

        github_result = github.ping()
        if github_result is True:
            status.append("🟢 GitHub: Connected Successfully")
        else:
            status.append(github_result)

        opensea_result = opensea.ping()
        if opensea_result is True:
            status.append("🟢 Opensea: Connected Successfully")
        else:
            status.append(opensea_result)

        snapshot_result = snapshot.ping()
        if snapshot_result is True:
            status.append("🟢 Snapshot: Connected Successfully")
        elif isinstance(snapshot_result, str):
            status.append(snapshot_result)

        twitter_result = twitter.ping()
        if twitter_result is True:
            status.append("🟢 Twitter: Connected Successfully")
        else:
            status.append(twitter_result)

        await message.delete()
        await update.message.reply_text(
            "X7 Finance Telegram Bot Services Status\n\n" + "\n".join(status),
            parse_mode="Markdown",
        )


async def wen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        if update.effective_chat.type == "private":
            if db.settings_get("click_me"):
                if settings.BUTTON_TIME is not None:
                    time = settings.BUTTON_TIME
                else:
                    time = settings.FIRST_BUTTON_TIME
                target_timestamp = settings.RESTART_TIME + time
                time_difference_seconds = (
                    target_timestamp - datetime.now().timestamp()
                )
                time_difference = timedelta(seconds=time_difference_seconds)
                hours, remainder = divmod(time_difference.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                await update.message.reply_text(
                    f"Next Click Me:\n\n{hours} hours, {minutes} minutes, {seconds} seconds\n\n"
                )
            else:
                await update.message.reply_text(
                    "Next Click Me:\n\nDisabled\n\n"
                )


LIST = [
    (func.__name__.split("_")[0], func, description)
    for func, description in [
        (settings_command, "Bot settings"),
        (clickme, "Send Click Me!"),
        (remove, "Remove an wallet"),
        (status, "View bot status"),
        (wen, "Next Click Me!"),
    ]
]
