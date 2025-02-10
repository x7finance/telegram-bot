from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import os
import requests
import tweepy
from datetime import datetime, timedelta

from bot import auto
from constants.bot import settings
from constants.protocol import addresses
from utils import tools
from services import get_mysql

mysql = get_mysql()


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        settings = mysql.settings_get_all()
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
        count = mysql.wallet_count()
        await update.message.reply_text(
            f"Wallet users: {count}", reply_markup=reply_markup
        )


async def click_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        if mysql.settings_get("click_me"):
            await auto.button_send(context)
        else:
            await update.message.reply_text("Click Me is disabled")


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        user_to_remove = " ".join(context.args)
        result = mysql.wallet_remove(user_to_remove)
        await update.message.reply_text(result)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        status = []

        blockspan_url = f"https://api.blockspan.com/v1/collections/contract/{addresses.PIONEER}?chain=eth-main"
        blockspan_headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("BLOCKSPAN_API_KEY"),
        }
        blockspan_response = requests.get(
            blockspan_url, headers=blockspan_headers
        )
        if blockspan_response.status_code == 200:
            status.append("🟢 Blockspan: Connected Successfully")
        else:
            status.append(
                f"🔴 Blockspan: Connection failed with status {blockspan_response.status_code}"
            )

        cg_url = "https://api.coingecko.com/api/v3/ping"
        cg_response = requests.get(cg_url)
        if cg_response.status_code == 200:
            status.append("🟢 CoinGecko: Connected Successfully")
        else:
            status.append(
                f"🔴 CoinGecko: Connection failed with status {cg_response.status_code}"
            )

        defined_headers = {
            "Content-Type": "application/json",
            "Authorization": os.getenv("DEFINED_API_KEY"),
        }
        defined_query = f"""query {{
            listPairsWithMetadataForToken (tokenAddress: "{addresses.x7r("eth")}" networkId: 1) {{
                results {{
                    pair {{
                        address
                    }}
                }}
            }}
            }}"""
        defined_response = requests.post(
            "https://graph.defined.fi/graphql",
            headers=defined_headers,
            json={"query": defined_query},
        )
        if defined_response.status_code == 200:
            status.append("🟢 Defined: Connected Successfully")
        else:
            status.append(
                f"🔴 Defined: Connection failed with status {defined_response.status_code}"
            )

        dextools_url = "http://public-api.dextools.io/trial/v2/token/ethereum/TOKEN_ADDRESS/price"
        dextools_headers = {
            "accept": "application/json",
            "x-api-key": os.getenv("DEXTOOLS_API_KEY"),
        }
        dextools_response = requests.get(
            dextools_url, headers=dextools_headers
        )
        if dextools_response.status_code == 200:
            status.append("🟢 Dextools: Connected Successfully")
        else:
            status.append(
                f"🔴 Dextools: Connection failed with status {dextools_response.status_code}"
            )

        drpc_url = f"https://lb.drpc.org/ogrpc?network=ethereum&dkey={os.getenv('DRPC_API_KEY')}"
        drpc_payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1,
        }
        drpc_response = requests.post(drpc_url, json=drpc_payload)
        if drpc_response.status_code == 200:
            status.append("🟢 DRPC: Connected Successfully")
        else:
            status.append(
                f"🔴 DRPC: Connection failed with status {drpc_response.status_code}"
            )

        etherscan_url = "https://api.etherscan.io/v2/api"
        etherscan_key = os.getenv("ETHERSCAN_API_KEY")
        etherscan_url = f"{etherscan_url}?module=stats&action=ethprice&apikey={etherscan_key}"
        etherscan_response = requests.get(etherscan_url)
        if etherscan_response.status_code == 200:
            status.append("🟢 Etherscan: Connected Successfully")
        else:
            status.append(
                f"🔴 Etherscan: Connection failed with status {etherscan_response.status_code}"
            )

        github_url = "https://api.github.com/repos/x7finance/monorepo/issues"
        github_headers = {"Authorization": f"token {os.getenv('GITHUB_PAT')}"}
        response = requests.get(github_url, headers=github_headers)
        if response.status_code == 200:
            status.append("🟢 GitHub: Connected Successfully")
        else:
            status.append(
                f"🔴 GitHub: Connection failed with status {response.status_code}"
            )

        opensea_url = f"https://api.opensea.io/v2/chain/ethereum/contract/{addresses.PIONEER}/nfts/2"
        opensea_headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("OPENSEA_API_KEY"),
        }
        opensea_response = requests.get(opensea_url, headers=opensea_headers)
        if opensea_response.status_code == 200:
            status.append("🟢 Opensea: Connected Successfully")
        else:
            status.append(
                f"🔴 Opensea: Connection failed with status {opensea_response.status_code}"
            )

        snapshot_url = "https://hub.snapshot.org/graphql"
        snapshot_query = {
            "query": 'query { proposals ( first: 1, skip: 0, where: { space_in: ["x7finance.eth"]}, '
            'orderBy: "created", orderDirection: desc ) { id title start end snapshot state choices '
            "scores scores_total author }}"
        }
        snapshot_response = requests.get(snapshot_url, snapshot_query)

        if snapshot_response.status_code == 200:
            status.append("🟢 Snapshot: Connected Successfully")
        else:
            status.append(
                f"🔴 Snashot: Connection failed with status {response.status_code}"
            )

        try:
            twitter_client = tweepy.Client(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN")
            )
            response = twitter_client.get_user(username="x7_finance")
            if response.data:
                status.append("🟢 Twitter: Connected Successfully")
            else:
                status.append(
                    "🔴 Twitter: Connection failed (No data returned)"
                )
        except tweepy.TweepyException as e:
            if hasattr(e, "response") and e.response is not None:
                status_code = e.response.status_code
                status.append(
                    f"🔴 Twitter: Connection failed with status {status_code}"
                )
            else:
                status.append("🔴 Twitter: Connection failed (Unknown Error)")

        await update.message.reply_text(
            "*X7 Finance Telegram Bot API Status*\n\n" + "\n".join(status),
            parse_mode="Markdown",
        )


async def wen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if tools.is_admin(update.effective_user.id):
        if update.effective_chat.type == "private":
            if mysql.settings_get("click_me"):
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
