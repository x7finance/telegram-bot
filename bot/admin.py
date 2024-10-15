from telegram import *
from telegram.ext import *

import os, requests
from datetime import datetime, timedelta

from constants import ca, chains, settings
from hooks import  db, api

defined = api.Defined()


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(os.getenv("OWNER_TELEGRAM_CHANNEL_ID")):
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

        for chain_name, chain_info in chains.CHAINS.items():
            scan_url = f"{chain_info.api}?module=stats&action=ethprice&apikey={chain_info.key}"
            response = requests.get(scan_url)
            if response.status_code == 200:
                status.append(f"🟢 {chain_info.scan_name}: Connected Successfully")
            else:
                status.append(f"🔴 {chain_info.scan_name}: Connection failed with status {response.status_code}")

        for chain_name, chain_info in chains.CHAINS.items():
            rpc_url = chain_info.w3
            rpc_payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
            rpc_response = requests.post(rpc_url, json=rpc_payload)
            if rpc_response.status_code == 200:
                status.append(f"🟢 {chain_info.name} RPC: Connected Successfully")
            else:
                status.append(f"🔴 {chain_info.name} RPC: Connection failed with status {rpc_response.status_code}")

        await update.message.reply_text(
            "*X7 Finance Telegram Bot API Status*\n\n" + "\n".join(status),
            parse_mode="Markdown")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(os.getenv("OWNER_TELEGRAM_CHANNEL_ID")):
        reset_text = db.clicks_reset()
        await update.message.reply_text(f"{reset_text}")


async def wen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(os.getenv("OWNER_TELEGRAM_CHANNEL_ID")):
        if update.effective_chat.type == "private":
            if settings.CLICK_ME_ENABLED:
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