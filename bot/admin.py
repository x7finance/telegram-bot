from telegram import *
from telegram.ext import *

import os, requests
from datetime import datetime, timedelta

from bot import auto
from constants import ca, settings
from hooks import  db, api

defined = api.Defined()

async def command(update, context):
    user_id = update.effective_user.id
    if user_id != int(os.getenv("TELEGRAM_ADMIN_ID")):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    valid_settings = ['click_me', 'welcome_restrictions', 'burn']

    if len(context.args) == 0:
        click_me_status = "ON" if db.settings_get('click_me') else "OFF"
        restrictions_status = "ON" if db.settings_get('welcome_restrictions') else "OFF"
        burn_status = "ON" if db.settings_get('burn') else "OFF"

        await update.message.reply_text(
            f"Click Me: {click_me_status}\n"
            f"Burn: {burn_status}\n"
            f"Welcome Restrictions: {restrictions_status}"
            
        )
        return

    setting = context.args[0].lower()

    if setting == 'reset':
        reset_text = db.clicks_reset()
        await update.message.reply_text(f"{reset_text}")
        return

    if len(context.args) == 2:
        value = context.args[1].lower()

        if setting not in valid_settings:
            formatted_settings = "\n".join([setting for setting in valid_settings])
            
            await update.message.reply_text(
                f"Error: '{setting}' is not a valid setting. Please use one of the following:\n\n{formatted_settings}"
            )
            return

        if value not in ['on', 'off']:
            await update.message.reply_text("Error: Value must be 'on' or 'off'.")
            return

        value_bool = value == 'on'
        
        db.settings_set(setting, value_bool)
        await update.message.reply_text(f"Setting '{setting}' updated to {value.upper()}.")
    else:
        await update.message.reply_text("Invalid usage. Use '/admin <setting> <on/off>' or '/admin reset'.")


async def click_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
        if db.settings_get("click_me"):
            await auto.button_send(context)
        else:
            await update.message.reply_text(f"Next Click Me:\n\nDisabled\n\n"
                )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
        status = []

        bitquery_url = "https://streaming.bitquery.io/graphql"
        bitquery_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("BITQUERY_API_KEY")}'
        }
        bitquery_response = requests.post(bitquery_url, headers=bitquery_headers)
        if bitquery_response.status_code == 200:
            status.append("🟢 BitQuery: Connected Successfully")
        else:
            status.append(f"🔴 BitQuery: Connection failed with status {bitquery_response.status_code}")

        blockspan_url = f"https://api.blockspan.com/v1/collections/contract/{ca.PIONEER}?chain=eth-main"
        blockspan_headers={
                "accept": "application/json",
                "X-API-KEY": os.getenv("BLOCKSPAN_API_KEY"),
            }
        blockspan_response = requests.get(blockspan_url, headers=blockspan_headers)
        if blockspan_response.status_code == 200:
            status.append("🟢 Blockspan: Connected Successfully")
        else:
            status.append(f"🔴 Blockspan: Connection failed with status {blockspan_response.status_code}")

        dextools_url = "http://public-api.dextools.io/trial/v2/token/ethereum/TOKEN_ADDRESS/price"
        dextools_headers = {
            'accept': 'application/json',
            'x-api-key': os.getenv("DEXTOOLS_API_KEY")
        }
        dextools_response = requests.get(dextools_url, headers=dextools_headers)
        if dextools_response.status_code == 200:
            status.append("🟢 Dextools: Connected Successfully")
        else:
            status.append(f"🔴 Dextools: Connection failed with status {dextools_response.status_code}")

        cg_url = "https://api.coingecko.com/api/v3/ping"
        cg_response = requests.get(cg_url)
        if cg_response.status_code == 200:
            status.append("🟢 CoinGecko: Connected Successfully")
        else:
            status.append(f"🔴 CoinGecko: Connection failed with status {cg_response.status_code}")

        defined_headers = {
            "Content-Type": "application/json",
            "Authorization": os.getenv("DEFINED_API_KEY")
        }
        pair_query = f"""query {{
            listPairsWithMetadataForToken (tokenAddress: "{ca.X7R("eth")}" networkId: 1) {{
                results {{
                    pair {{
                        address
                    }}
                }}
            }}
            }}"""
        defined_response = requests.post("https://graph.defined.fi/graphql", headers=defined_headers, json={"query": pair_query})
        if defined_response.status_code == 200:
            status.append("🟢 Defined: Connected Successfully")
        else:
            status.append(f"🔴 Defined: Connection failed with status {defined_response.status_code}")

        opensea_url = f"https://api.opensea.io/v2/chain/ethereum/contract/{ca.PIONEER}/nfts/2"
        opensea_headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("OPENSEA_API_KEY")
        }
        opensea_response = requests.get(opensea_url, headers=opensea_headers)
        if opensea_response.status_code == 200:
            status.append("🟢 Opensea: Connected Successfully")
        else:
            status.append(f"🔴 Opensea: Connection failed with status {opensea_response.status_code}")

        etherscan_url = "https://api.etherscan.io/v2/api"
        etherscan_key = os.getenv('ETHERSCAN_API_KEY')
        etherscan_url = f"{etherscan_url}?module=stats&action=ethprice&apikey={etherscan_key}"
        response = requests.get(etherscan_url)
        if response.status_code == 200:
            status.append(f"🟢 Etherscan: Connected Successfully")
        else:
            status.append(f"🔴 Etherscan: Connection failed with status {response.status_code}")

        rpc_url = f"https://lb.drpc.org/ogrpc?network=ethereum&dkey={os.getenv('DRPC_API_KEY')}"
        rpc_payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        rpc_response = requests.post(rpc_url, json=rpc_payload)
        if rpc_response.status_code == 200:
            status.append(f"🟢 DRPC: Connected Successfully")
        else:
            status.append(f"🔴 DRPC: Connection failed with status {rpc_response.status_code}")

        await update.message.reply_text(
            "*X7 Finance Telegram Bot API Status*\n\n" + "\n".join(status),
            parse_mode="Markdown")


async def wen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
        if update.effective_chat.type == "private":
            if db.settings_get("click_me"):
                if settings.BUTTON_TIME is not None:
                    time = settings.BUTTON_TIME
                else:    
                    time = settings.FIRST_BUTTON_TIME
                target_timestamp = settings.RESTART_TIME + time
                time_difference_seconds = target_timestamp - datetime.now().timestamp()
                time_difference = timedelta(seconds=time_difference_seconds)
                hours, remainder = divmod(time_difference.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                await update.message.reply_text(f"Next Click Me:\n\n{hours} hours, {minutes} minutes, {seconds} seconds\n\n"
                )
            else:
                await update.message.reply_text(f"Next Click Me:\n\nDisabled\n\n"
                )