from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import aiohttp
import os

from datetime import datetime, timedelta

from bot.callbacks import clickme
from constants.general import settings
from utils import tools
from services import (
    get_codex,
    get_coingecko,
    get_dbmanager,
    get_dextools,
    get_dune,
    get_etherscan,
    get_github,
    get_simplehash,
    get_snapshot,
    get_twitter,
)

codex = get_codex()
cg = get_coingecko()
db = get_dbmanager()
dextools = get_dextools()
dune = get_dune()
etherscan = get_etherscan()
github = get_github()
simplehash = get_simplehash()
snapshot = get_snapshot()
twitter = get_twitter()


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        return


async def clickme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        if await db.settings.get("click_me"):
            await clickme.send(context)
        else:
            await update.message.reply_text("Click Me is disabled")


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        user_to_remove = " ".join(context.args)
        result = await db.wallet.remove(user_to_remove)
        await update.message.reply_text(result)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        settings = await db.settings.get_all()
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
        await update.message.reply_text(
            "Bot Settings", reply_markup=reply_markup
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        message = await update.message.reply_text(
            "Pinging services, Please wait..."
        )
        await context.bot.send_chat_action(update.effective_chat.id, "typing")

        status = []

        codex_result = await codex.ping()
        if codex_result is True:
            status.append("🟢 Codex: Connected Successfully")
        else:
            status.append(codex_result)

        cg_result = await cg.ping()
        if cg_result is True:
            status.append("🟢 CoinGecko: Connected Successfully")
        else:
            status.append(cg_result)

        db_result = await db.ping()
        if db_result is True:
            status.append("🟢 MySql: Connected Successfully")
        else:
            status.append(db_result)

        dextools_result = await dextools.ping()
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
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    drpc_url, json=drpc_payload
                ) as drpc_response:
                    if drpc_response.status == 200:
                        status.append("🟢 DRPC: Connected Successfully")
                    else:
                        status.append(
                            f"🔴 DRPC: Connection failed: {drpc_response.status}"
                        )
        except Exception as e:
            status.append(f"🔴 DRPC: Connection failed: {str(e)}")

        dune_result = await dune.ping()
        if dune_result is True:
            status.append("🟢 Dune: Connected Successfully")
        else:
            status.append(dune_result)

        etherscan_result = await etherscan.ping()
        if etherscan_result is True:
            status.append("🟢 Etherscan: Connected Successfully")
        else:
            status.append(etherscan_result)

        github_result = await github.ping()
        if github_result is True:
            status.append("🟢 GitHub: Connected Successfully")
        else:
            status.append(github_result)

        simplehash_result = await simplehash.ping()
        if simplehash_result is True:
            status.append("🟢 SimpleHash: Connected Successfully")
        else:
            status.append(simplehash_result)

        snapshot_result = await snapshot.ping()
        if snapshot_result is True:
            status.append("🟢 Snapshot: Connected Successfully")
        elif isinstance(snapshot_result, str):
            status.append(snapshot_result)

        twitter_result = await twitter.ping()
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
            if await db.settings.get("click_me"):
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
