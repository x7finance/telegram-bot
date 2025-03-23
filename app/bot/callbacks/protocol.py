from telegram import Update
from telegram.ext import ContextTypes

from constants.protocol import chains, splitters
from media import stickers
from utils import onchain
from services import get_dbmanager

db = get_dbmanager()


async def liquidate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    existing_wallet = await db.wallet.get(user_id)

    if not existing_wallet:
        await query.answer(
            "You have not registered a wallet. Please use /register in private.",
            show_alert=True,
        )
        return

    try:
        _, loan_id, chain = query.data.split(":")
        chain_info, _ = await chains.get_info(chain)

        message = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"Liquidating loan {loan_id} ({chain_info.name}), Please wait...",
        )

        result = await onchain.liquidate_loan(int(loan_id), chain, user_id)

        if result.startswith("Error"):
            await query.answer(result, show_alert=True)
            return

        await message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=result,
            message_effect_id=stickers.CONFETTI
            if query.message.chat.type == "private"
            else None,
        )
        await query.answer()

    except Exception as e:
        await message.delete()
        await query.answer(
            f"Error during liquidation: {str(e)}", show_alert=True
        )


async def pushall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    existing_wallet = await db.wallet.get(user_id)

    if not existing_wallet:
        await query.answer(
            "You have not registered a wallet. Please use /register in private.",
            show_alert=True,
        )
        return

    _, token, chain = query.data.split(":")
    chain_info, _ = await chains.get_info(chain)

    config = await splitters.get_push_settings(chain, token)
    address = config["address"]
    abi = config["abi"]
    name = config["name"]
    threshold = config["threshold"]
    contract_type = config["contract_type"]

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(address), abi=abi
    )

    available_tokens = await config["calculate_tokens"](contract)

    if float(available_tokens) < float(threshold):
        await query.answer(
            f"{chain_info.name} {name} balance to low to push.",
            show_alert=True,
        )
        return

    try:
        message = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"Pushing {contract_type} ({chain_info.name}), Please wait...",
        )

        if contract_type == "hub":
            token_address = config["token_address"]
            result = await onchain.splitter_push(
                contract_type, address, abi, chain, user_id, token_address
            )
        else:
            result = await onchain.splitter_push(
                contract_type, address, abi, chain, user_id
            )

        if result.startswith("Error"):
            await query.answer(result, show_alert=True)
            return

        await message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=result,
            message_effect_id=stickers.CONFETTI
            if query.message.chat.type == "private"
            else None,
        )
        await query.answer()

    except Exception as e:
        await message.delete()
        await query.answer(
            f"Error during {name} push: {str(e)}", show_alert=True
        )


async def stuck_tx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, chain = query.data.split(":")
    user_id = query.from_user.id

    try:
        result_text = await onchain.stuck_tx(chain, user_id)

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=result_text,
            message_effect_id=stickers.CONFETTI
            if query.message.chat.type == "private"
            else None,
        )
        await query.answer()
    except Exception as e:
        await query.answer(
            text=f"An error occurred: {str(e)}", show_alert=True
        )
