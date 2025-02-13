from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
    MessageHandler,
)

from eth_utils import is_address

from constants.protocol import addresses, chains
from utils import onchain
from services import get_dbmanager, get_etherscan

db = get_dbmanager()
etherscan = get_etherscan()

X7D_AMOUNT, X7D_CONFIRM = range(2)
WITHDRAW_TOKEN, WITHDRAW_AMOUNT, WITHDRAW_ADDRESS, WITHDRAW_CONFIRM = range(4)


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

    chain_info, _ = chains.get_info(chain)

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
            result = onchain.x7d_mint(amount, chain, user_id)
        elif operation == "redeem":
            result = onchain.x7d_redeem(amount, chain, user_id)
        elif operation == "withdraw":
            if token == "native":
                result = onchain.withdraw_native(
                    amount, chain, user_id, address
                )
            else:
                result = onchain.withdraw_tokens(
                    user_id, amount, addresses.x7d(chain), 18, address, chain
                )

        await message.delete()
        await query.edit_message_text(text=result)
    except Exception as e:
        await message.delete()
        await query.edit_message_text(text=f"An error occurred: {str(e)}")

    context.user_data.clear()
    return ConversationHandler.END


async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, chain = query.data.split(":")

    chain_info, _ = chains.get_info(chain)

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

    return WITHDRAW_TOKEN


async def withdraw_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    (
        _,
        token,
        chain,
    ) = query.data.split(":")
    context.user_data["withdraw_chain"] = chain
    context.user_data["withdraw_token"] = token

    chain_info, _ = chains.get_info(chain)

    if token == "native":
        token_str = chain_info.native.upper()
    else:
        token_str = token.upper()

    await query.message.reply_text(
        text=f"How much do {token_str} want to withdraw? Please reply with the amount (e.g., `0.5`).",
    )

    return WITHDRAW_AMOUNT


async def withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chain = context.user_data["withdraw_chain"]
    token = context.user_data["withdraw_token"]

    try:
        amount = float(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "Invalid amount. Please enter a valid number."
        )

        return WITHDRAW_AMOUNT

    chain_info, _ = chains.get_info(chain)
    wallet = db.wallet_get(user_id)

    if token == "native":
        balance = etherscan.get_native_balance(wallet["wallet"], chain)
        token_str = chain_info.native.upper()
    else:
        balance = etherscan.get_token_balance(
            wallet["wallet"], addresses.x7d(chain), 18, chain
        )
        token_str = token.upper()

    if amount <= 0 or amount > balance:
        await update.message.reply_text(
            f"Invalid amount. You have {balance} {token_str} available to withdraw."
        )

        return WITHDRAW_AMOUNT

    context.user_data["withdraw_amount"] = amount

    await update.message.reply_text(
        text=f"Please send the {chain.upper()} address you want to withdraw to",
    )

    return WITHDRAW_ADDRESS


async def withdraw_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = context.user_data["withdraw_chain"]
    token = context.user_data["withdraw_token"]
    amount = context.user_data["withdraw_amount"]
    address = update.message.text

    chain_info, _ = chains.get_info(chain)

    if not is_address(address):
        await update.message.reply_text(
            "Invalid address. Please provide a valid EVM address."
        )

        return X7D_AMOUNT

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

    return WITHDRAW_CONFIRM


async def x7d_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action, chain = query.data.split(":")
    context.user_data["x7d_action"] = action
    context.user_data["x7d_chain"] = chain

    await query.message.reply_text(
        text=f"How much do you want to {action}? Please reply with the amount (e.g., `0.5`).",
    )

    return X7D_AMOUNT


async def x7d_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    action = context.user_data["x7d_action"]
    chain = context.user_data["x7d_chain"]

    try:
        amount = float(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "Invalid amount. Please enter a valid number."
        )

        return X7D_AMOUNT

    chain_info, _ = chains.get_info(chain)

    wallet = db.wallet_get(user_id)

    if action == "mint":
        balance = etherscan.get_native_balance(wallet["wallet"], chain)
    elif action == "redeem":
        balance = etherscan.get_token_balance(
            wallet["wallet"], addresses.x7d(chain), 18, chain
        )

    if amount <= 0 or amount > balance:
        await update.message.reply_text(
            f"Invalid amount. You have {balance} {chain_info.native.upper()} available to {action}"
        )

        return X7D_AMOUNT

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

    return X7D_CONFIRM


HANDLERS = [
    {
        "entry_points": [
            CallbackQueryHandler(withdraw_start, pattern="^withdraw:.*$")
        ],
        "states": {
            WITHDRAW_TOKEN: [
                CallbackQueryHandler(withdraw_token, pattern="^withdraw:.*$")
            ],
            WITHDRAW_AMOUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, withdraw_amount
                )
            ],
            WITHDRAW_ADDRESS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, withdraw_address
                )
            ],
            WITHDRAW_CONFIRM: [
                CallbackQueryHandler(confirm, pattern="^withdraw:.*$")
            ],
        },
    },
    {
        "entry_points": [
            CallbackQueryHandler(x7d_start, pattern="^(mint|redeem):.*$")
        ],
        "states": {
            X7D_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, x7d_amount)
            ],
            X7D_CONFIRM: [
                CallbackQueryHandler(confirm, pattern="^(mint|redeem):.*$")
            ],
        },
    },
]
