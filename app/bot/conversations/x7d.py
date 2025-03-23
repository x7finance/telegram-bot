from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants.protocol import addresses, chains
from services import get_dbmanager, get_etherscan

db = get_dbmanager()
etherscan = get_etherscan()

AMOUNT, CONFIRM = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action, chain = query.data.split(":")
    context.user_data["x7d_action"] = action
    context.user_data["x7d_chain"] = chain

    await query.message.reply_text(
        text=f"How much do you want to {action}? Please reply with the amount (e.g., `0.5`).",
    )

    return AMOUNT


async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    action = context.user_data["x7d_action"]
    chain = context.user_data["x7d_chain"]

    try:
        amount = float(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "Invalid amount. Please enter a valid number."
        )

        return AMOUNT

    chain_info, _ = await chains.get_info(chain)

    wallet = await db.wallet.get(user_id)

    if action == "mint":
        balance = await etherscan.get_native_balance(wallet["wallet"], chain)
    elif action == "redeem":
        balance = await etherscan.get_token_balance(
            wallet["wallet"], addresses.x7d(chain), 18, chain
        )

    if amount <= 0 or amount > balance:
        await update.message.reply_text(
            f"Invalid amount. You have {balance} {chain_info.native.upper()} available to {action}"
        )

        return AMOUNT

    context.user_data["x7d_amount"] = amount

    await update.message.reply_text(
        text=f"Are you sure you want to {action} {amount} X7D ({chain_info.name})?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Yes", callback_data=f"{action}:{chain}:{amount}"
                    ),
                    InlineKeyboardButton("No", callback_data="cancel"),
                ]
            ]
        ),
    )

    return CONFIRM
