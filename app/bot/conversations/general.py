from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes

from constants.protocol import addresses, chains
from media import stickers
from utils import onchain
from services import get_dbmanager, get_etherscan

db = get_dbmanager()
etherscan = get_etherscan()


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data.split(":")
    operation = callback_data[0]

    if operation in ["mint", "redeem"]:
        chain = callback_data[1]
        token = "X7D"
        amount = callback_data[2]
    elif operation == "withdraw":
        chain = callback_data[1]
        token = callback_data[2]
        amount = callback_data[3]
        address = context.user_data["withdraw_address"]

    chain_info, _ = await chains.get_info(chain)

    if token == "native":
        token_str = chain_info.native.upper()
    else:
        token_str = token.upper()

    message = await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"{operation.capitalize()}ing {amount} {token_str} ({chain_info.name}), Please wait...",
    )

    try:
        if operation == "mint":
            result = await onchain.x7d_mint(amount, chain, user_id)
        elif operation == "redeem":
            result = await onchain.x7d_redeem(amount, chain, user_id)
        elif operation == "withdraw":
            if token == "native":
                result = await onchain.withdraw_native(
                    amount, chain, user_id, address
                )
            else:
                result = await onchain.withdraw_tokens(
                    user_id, amount, addresses.x7d(chain), 18, address, chain
                )
        await message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=result,
            message_effect_id=stickers.CONFETTI,
        )
    except Exception as e:
        await message.delete()
        await query.edit_message_text(text=f"An error occurred: {str(e)}")

    context.user_data.clear()

    return ConversationHandler.END
