from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from eth_utils import is_address

from constants.protocol import addresses, chains
from services import get_dbmanager, get_etherscan

db = get_dbmanager()
etherscan = get_etherscan()

TOKEN, AMOUNT, ADDRESS, CONFIRM = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, chain = query.data.split(":")

    chain_info, _ = await chains.get_info(chain)

    await query.message.reply_text(
        text="Which token do you want to withdraw?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"{chain_info.native.upper()}",
                        callback_data=f"withdraw:native:{chain}",
                    ),
                    InlineKeyboardButton(
                        "X7D", callback_data=f"withdraw:x7d:{chain}"
                    ),
                ]
            ]
        ),
    )

    return TOKEN


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    (
        _,
        token,
        chain,
    ) = query.data.split(":")
    context.user_data["withdraw_chain"] = chain
    context.user_data["withdraw_token"] = token

    chain_info, _ = await chains.get_info(chain)

    if token == "native":
        token_str = chain_info.native.upper()
    else:
        token_str = token.upper()

    await query.message.reply_text(
        text=f"How much do {token_str} want to withdraw? Please reply with the amount (e.g., `0.5`).",
    )

    return AMOUNT


async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chain = context.user_data["withdraw_chain"]
    token = context.user_data["withdraw_token"]

    try:
        amount = float(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "Invalid amount. Please enter a valid number."
        )

        return AMOUNT

    chain_info, _ = await chains.get_info(chain)
    wallet = await db.wallet.get(user_id)

    if token == "native":
        balance = await etherscan.get_native_balance(wallet["wallet"], chain)
        token_str = chain_info.native.upper()
    else:
        balance = await etherscan.get_token_balance(
            wallet["wallet"], addresses.x7d(chain), 18, chain
        )
        token_str = token.upper()

    if amount <= 0 or amount > balance:
        await update.message.reply_text(
            f"Invalid amount. You have {balance} {token_str} available to withdraw."
        )

        return AMOUNT

    context.user_data["withdraw_amount"] = amount

    await update.message.reply_text(
        text=f"Please send the {chain.upper()} address you want to withdraw to",
    )

    return ADDRESS


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = context.user_data["withdraw_chain"]
    token = context.user_data["withdraw_token"]
    amount = context.user_data["withdraw_amount"]
    address = update.message.text

    chain_info, _ = await chains.get_info(chain)

    if not is_address(address):
        await update.message.reply_text(
            "Invalid address. Please provide a valid EVM address."
        )

        return AMOUNT

    context.user_data["withdraw_address"] = address

    if token == "native":
        token_str = chain_info.native.upper()
    else:
        token_str = token.upper()

    await update.message.reply_text(
        f"Are you sure you want to withdraw {amount} {token_str} ({chain_info.name}) to the following address?\n\n"
        f"`{address}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Yes",
                        callback_data=f"withdraw:{chain}:{token}:{amount}",
                    ),
                    InlineKeyboardButton("No", callback_data="cancel"),
                ]
            ]
        ),
    )

    return CONFIRM
