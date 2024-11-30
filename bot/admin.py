from telegram import *
from telegram.ext import *

import os, requests
from datetime import datetime, timedelta

from bot import auto
from constants import ca, chains, settings
from hooks import  db, api, functions

defined = api.Defined()
etherscan = api.Etherscan()


async def command(update, context):
    user_id = update.effective_user.id
    if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
        settings = db.settings_get_all()
        if not settings:
            await update.message.reply_text("Error fetching settings.")
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    f"{setting.replace("_", " ").title()}: {'ON' if status else 'OFF'}",
                    callback_data=f"toggle_{setting}"
                )
            ]
            for setting, status in settings.items()
        ]

        keyboard.append(
            [
                InlineKeyboardButton("Reset Clicks", callback_data="reset_clicks_prompt")
            ]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Current Bot Settings:", reply_markup=reply_markup)


async def command_toggle(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != int(os.getenv("TELEGRAM_ADMIN_ID")):
        await query.answer(
            text="Admin only.",
            show_alert=True
        )
        return

    callback_data = query.data
    if not callback_data.startswith("toggle_"):
        return

    setting = callback_data.replace("toggle_", "")

    try:
        current_status = db.settings_get(setting)
        new_status = not current_status

        db.settings_set(setting, new_status)

        formatted_setting = setting.replace("_", " ").title()
        await query.edit_message_text(
            text=f"{formatted_setting} updated to {'ON' if new_status else 'OFF'}."
        )


        settings = db.settings_get_all()
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{s.replace("_", " ").title()}: {'ON' if v else 'OFF'}",
                    callback_data=f"toggle_{s}"
                )
            ]
            for s, v in settings.items()
        ]
        keyboard.append(
            [
                InlineKeyboardButton("Reset Clicks", callback_data="reset_start")
            ]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Current Bot Settings:", reply_markup=reply_markup)

    except Exception as e:
        await query.answer(
            text=f"An error occurred: {str(e)}",
            show_alert=True
        )


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


async def pushall_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = update.callback_query
    
    is_admin = user_id == int(os.getenv("TELEGRAM_ADMIN_ID"))
    if not is_admin:
        await query.answer("Admin only.", show_alert=True)
        return

    action, chain = query.data.split(":")
    chain_info, error_message = chains.get_info(chain)

    if action == "push_eco":
        splitter_address = ca.ECO_SPLITTER(chain)
        splitter_name = "Ecosystem Splitter"
    elif action == "push_treasury":
        splitter_address = ca.TREASURY_SPLITTER(chain)
        splitter_name = "Treasury Splitter"
    else:
        await query.answer("Invalid action.", show_alert=True)
        return

    splitter_balance = float(etherscan.get_native_balance(splitter_address, chain))
    if splitter_balance <= 0:
        await query.answer(f"{chain_info.name} {splitter_name} has no balance to push.", show_alert=True)
        return

    try:
        result = functions.splitter_push(splitter_address, chain)
        await query.answer(result, show_alert=True)
    except Exception as e:
        await query.answer(f"Error during {splitter_name} push: {str(e)}", show_alert=True)


async def reset_no(update, context):
    query = update.callback_query

    await query.edit_message_text(
        text="Action canceled. No changes were made."
    )


async def reset_yes(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != int(os.getenv("TELEGRAM_ADMIN_ID")):
        await query.answer(
            text="Admin only.",
            show_alert=True
        )
        return

    try:
        result_text = db.clicks_reset()
        await query.edit_message_text(
            text=f"Clicks have been reset. {result_text}"
        )
    except Exception as e:
        await query.answer(
            text=f"An error occurred: {str(e)}",
            show_alert=True
        )


async def reset_start(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != int(os.getenv("TELEGRAM_ADMIN_ID")):
        await query.answer(
            text="Admin only.",
            show_alert=True
        )
        return

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="reset_yes"),
            InlineKeyboardButton("No", callback_data="reset_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Are you sure you want to reset clicks?",
        reply_markup=reply_markup
    )


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