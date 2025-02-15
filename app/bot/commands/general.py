from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

import math
import os
import pytz
import random
import re
import requests
import time
from datetime import datetime
from eth_account import Account
from eth_utils import is_address

from bot.commands import pricebot
from utils import onchain, tools
from constants.bot import settings, text, urls
from constants.protocol import (
    abis,
    addresses,
    chains,
    dao,
    nfts,
    splitters,
    tax,
    tokens,
)
from media import x7_images
from services import (
    get_coingecko,
    get_dbmanager,
    get_defined,
    get_dextools,
    get_dune,
    get_etherscan,
    get_github,
    get_opensea,
    get_snapshot,
    get_twitter,
)

coingecko = get_coingecko()
db = get_dbmanager()
defined = get_defined()
dextools = get_dextools()
dune = get_dune()
etherscan = get_etherscan()
github = get_github()
opensea = get_opensea()
snapshot = get_snapshot()
twitter = get_twitter()


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text.about(),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="X7Finance.org", url=urls.XCHANGE)]]
        ),
    )


async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    administrators = await context.bot.get_chat_administrators(
        urls.TG_MAIN_CHANNEL_ID
    )
    team = [
        f"@{admin.user.username}"
        for admin in administrators
        if admin.custom_title
        and "x7" in admin.custom_title.lower()
        and admin.user.username
    ]
    team.sort(key=lambda username: username.lower())

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption="*X7 Finance Telegram Admins*\n\n" + "\n".join(team),
        parse_mode="Markdown",
    )


async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="XChange Alerts", url=urls.TG_ALERTS)]]
        ),
    )


async def announcements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7 Announcement Channel",
                        url=urls.TG_ANNOUNCEMENTS,
                    )
                ]
            ]
        ),
    )


async def arbitrage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text(
            "Please follow the command with an X7 token name"
        )
        return

    token = context.args[0].lower()
    chain = (
        context.args[1].lower()
        if len(context.args) == 2
        else chains.get_chain(update.effective_message.message_thread_id)
    )

    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    if token.lower() in tokens.get_tokens():
        pairs = tokens.get_tokens()[token.lower()][chain].pairs

        message = await update.message.reply_text(
            f"Getting {token.upper()} ({chain_info.name}) arbitrage opportunities, Please wait..."
        )
        await context.bot.send_chat_action(update.effective_chat.id, "typing")

        if token in ["x7dao", "x7r"]:
            pair_x, pair_y = pairs[0], pairs[1]
            price_x = dextools.get_pool_price(pair_x, chain)
            price_y = dextools.get_pool_price(pair_y, chain)

            if price_x and price_y:
                price_diff = abs(price_x - price_y)
                percentage_diff = (
                    (price_diff / price_x) * 100 if price_x != 0 else 0
                )

                comparison_text = (
                    f"*{token.upper()} ({chain_info.name}) Arbitrage Opportunities*\n\n"
                    f"Xchange: ${price_x:.6f}\n"
                    f"Uniswap: ${price_y:.6f}\n"
                    f"Difference: {percentage_diff:.2f}%\n"
                )

                await update.message.reply_photo(
                    photo=tools.get_random_pioneer(),
                    caption=comparison_text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Xchange Chart",
                                    url=urls.dex_tools_link(
                                        chain_info.dext, pair_x
                                    ),
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    text="Uniswap Chart",
                                    url=urls.dex_tools_link(
                                        chain_info.dext, pair_y
                                    ),
                                )
                            ],
                        ]
                    ),
                )

            else:
                await update.message.reply_text(
                    "Unable to retrieve prices for Xchange or Uniswap. Please try again later."
                )

        elif token in addresses.X7100:
            price_x = dextools.get_pool_price(pairs, chain)

            all_tokens = tokens.get_tokens()

            prices = {
                t: dextools.get_pool_price(
                    all_tokens[t.lower()][chain].pairs, chain
                )
                for t in addresses.X7100
                if t in all_tokens and chain in all_tokens[t.lower()]
            }

            if price_x is not None:
                comparison_text = (
                    f"*{token.upper()} Arbitrage Opportunities*\n\n"
                )
                comparison_text += (
                    f"{token.upper()}:\nPrice: ${price_x:.6f}\n\n"
                )

                for t, price in prices.items():
                    if t == token:
                        continue
                    price_diff = abs(price_x - price)
                    percentage_diff = (
                        (price_diff / price_x) * 100 if price_x != 0 else 0
                    )
                    comparison_text += (
                        f"{t.upper()}:\n"
                        f"Price: ${price:.6f}\n"
                        f"Difference: {percentage_diff:.2f}%\n\n"
                    )

                await update.message.reply_photo(
                    photo=tools.get_random_pioneer(),
                    caption=comparison_text,
                    parse_mode="Markdown",
                )
            else:
                await update.message.reply_text(
                    "Unable to retrieve price for the requested token. Please try again later."
                )

        await message.delete()
    else:
        await update.message.reply_text(
            "Invalid token name. Please provide a valid X7 token."
        )


async def blocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    when = round(time.time())
    try:
        blocks = {
            chain: etherscan.get_block(chain, when)
            for chain in chains.get_active_chains()
        }
    except Exception:
        blocks = 0
    blocks_text = "\n".join(
        [
            f"{block_type.upper()}: `{block}`"
            for block_type, block in blocks.items()
        ]
    )

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*Latest Blocks*\n\n{blocks_text}",
        parse_mode="Markdown",
    )


async def blog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7 Finance Blog", url=f"{urls.XCHANGE}blog"
                    )
                ]
            ]
        ),
    )


async def borrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) >= 1:
        amount = context.args[0]
        if amount.replace(".", "", 1).isdigit():
            amount_in_wei = int(float(amount) * 10**18)
            chain = (
                chains.get_chain(update.effective_message.message_thread_id)
                if len(context.args) < 2
                else context.args[1]
            )
        else:
            await update.message.reply_text(
                "The amount must be a number. Please try again with a valid numeric value."
            )
            return
    else:
        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption="*X7 Finance Loan Rates*\n\n"
            "Follow the /borrow command with an amount to borrow",
            parse_mode="Markdown",
        )
        return

    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text(
        f"Getting {chain_info.name} loan rate info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    loan_info = ""
    native_price = etherscan.get_native_price(chain)
    borrow_usd = native_price * float(amount)

    lending_pool = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(
            addresses.lending_pool(chain)
        ),
        abi=abis.read("lendingpool"),
    )

    loan_contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(
            addresses.ill_addresses(chain)["005"]
        ),
        abi=abis.read("ill005"),
    )

    liquidation_fee = (
        lending_pool.functions.liquidationReward().call() / 10**18
    )
    liquidation_dollar = liquidation_fee * native_price

    loan_name = loan_contract.functions.name().call()
    loan_data = loan_contract.functions.getQuote(int(amount_in_wei)).call()

    min_loan = loan_contract.functions.minimumLoanAmount().call()
    max_loan = loan_contract.functions.maximumLoanAmount().call()
    min_loan_duration = (
        loan_contract.functions.minimumLoanLengthSeconds().call()
    )
    max_loan_duration = (
        loan_contract.functions.maximumLoanLengthSeconds().call()
    )

    x7100_share = (
        lending_pool.functions.X7100PremiumShare().call()
        + lending_pool.functions.X7100OriginationShare().call()
    )
    x7dao_share = (
        lending_pool.functions.X7DAOPremiumShare().call()
        + lending_pool.functions.X7DAOOriginationShare().call()
    )
    ecosystem_share = (
        lending_pool.functions.ecosystemSplitterPremiumShare().call()
        + lending_pool.functions.ecosystemSplitterOriginationShare().call()
    )
    lpool_share = (
        lending_pool.functions.lendingPoolPremiumShare().call()
        + lending_pool.functions.lendingPoolOriginationShare().call()
    )

    total_share = x7100_share + x7dao_share + ecosystem_share + lpool_share

    origination_fee, premium_fee = [value / 10**18 for value in loan_data[1:]]
    origination_dollar, premium_fee_dollar = [
        value * native_price for value in [origination_fee, premium_fee]
    ]

    total_fees_eth = origination_fee + premium_fee
    total_fees_dollars = origination_dollar + premium_fee_dollar

    x7100_share_eth = (x7100_share / total_share) * total_fees_eth
    x7dao_share_eth = (x7dao_share / total_share) * total_fees_eth
    ecosystem_share_eth = (ecosystem_share / total_share) * total_fees_eth
    lpool_share_eth = (lpool_share / total_share) * total_fees_eth

    x7100_share_dollars = (x7100_share / total_share) * total_fees_dollars
    x7dao_share_dollars = (x7dao_share / total_share) * total_fees_dollars
    ecosystem_share_dollars = (
        ecosystem_share / total_share
    ) * total_fees_dollars
    lpool_share_dollars = (lpool_share / total_share) * total_fees_dollars

    distribution = (
        f"Fee Distribution:\n"
        f"X7100: {x7100_share_eth:.4f} {chain_info.native.upper()} (${x7100_share_dollars:,.2f})\n"
        f"X7DAO: {x7dao_share_eth:.4f} {chain_info.native.upper()} (${x7dao_share_dollars:,.2f})\n"
        f"Ecosystem Splitter: {ecosystem_share_eth:.4f} {chain_info.native.upper()} (${ecosystem_share_dollars:,.2f})\n"
        f"Lending Pool: {lpool_share_eth:.4f} {chain_info.native.upper()} (${lpool_share_dollars:,.2f})\n\n"
    )

    loan_info += (
        f"*{loan_name}*\n"
        f"Origination Fee: {origination_fee} {chain_info.native.upper()} (${origination_dollar:,.2f})\n"
    )

    premium_periods = loan_contract.functions.numberOfPremiumPeriods().call()
    if premium_periods > 0:
        per_period_premium = premium_fee / premium_periods
        per_period_premium_dollar = premium_fee_dollar / premium_periods

        loan_info += f"Premium Fees: {premium_fee} {chain_info.native.upper()} (${premium_fee:,.0f}) over {premium_periods} payments:\n"
        for period in range(1, premium_periods + 1):
            loan_info += f"  - Payment {period}: {per_period_premium:.4f} {chain_info.native.upper()} (${per_period_premium_dollar:,.2f})\n"
    else:
        loan_info += f"Premium Fees: {premium_fee} {chain_info.native.upper()} (${premium_fee:,.0f})\n"

    loan_info += (
        f"Total Loan Cost: {total_fees_eth} {chain_info.native.upper()} (${total_fees_dollars:,.2f})\n"
        f"Min Loan: {min_loan / 10**18} {chain_info.native.upper()}\n"
        f"Max Loan: {max_loan / 10**18} {chain_info.native.upper()}\n"
        f"Min Loan Duration: {math.floor(min_loan_duration / 84600)} days\n"
        f"Max Loan Duration: {math.floor(max_loan_duration / 84600)} days\n\n"
    )

    loan_info += distribution

    await message.delete()
    await update.message.reply_text(
        f"*X7 Finance Loan Rates ({chain_info.name})*\n\n"
        f"Borrowing {amount} {chain_info.native.upper()} (${borrow_usd:,.0f}) will cost:\n\n"
        f"{loan_info}"
        f"Liquidation Deposit: {liquidation_fee} {chain_info.native.upper()} (${liquidation_dollar:,.0f})\n\n",
        parse_mode="Markdown",
    )


async def burn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text(
        f"Getting X7R ({chain_info.name}) burn info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    burn = etherscan.get_token_balance(
        addresses.DEAD, addresses.x7r(chain), 18, chain
    )
    percent = round(burn / addresses.SUPPLY * 100, 2)
    x7r_price = dextools.get_price(addresses.x7r(chain), chain)[0] or 0
    burn_dollar = float(x7r_price) * float(burn)

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7R Tokens Burned ({chain_info.name})*\n\n"
        f"{burn:,.0f} X7R (${burn_dollar:,.0f})\n"
        f"{percent}% of Supply",
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Burn Wallet",
                        url=f"{chain_info.scan_token}{addresses.x7r(chain)}?a={addresses.DEAD}",
                    )
                ]
            ]
        ),
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Buy Links ({chain_info.name})*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7R - Rewards Token",
                        url=urls.xchange_buy_link(
                            chain_info.id, addresses.x7r(chain)
                        ),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="X7DAO - Governance Token",
                        url=urls.xchange_buy_link(
                            chain_info.id, addresses.x7dao(chain)
                        ),
                    )
                ],
            ]
        ),
    )


async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Contract Addresses ({chain_info.name})*\n\n"
        f"*X7R - Rewards Token *\n`{addresses.x7r(chain)}`\n\n"
        f"*X7DAO - Governance Token*\n`{addresses.x7dao(chain)}`\n\n"
        f"For advanced trading and arbitrage opportunities see `/constellations`",
        parse_mode="Markdown",
    )


async def channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(text="X7 Portal", url=urls.TG_PORTAL)],
        [InlineKeyboardButton(text="Xchange Alerts", url=urls.TG_ALERTS)],
        [InlineKeyboardButton(text="DAO Chat", url=urls.TG_DAO)],
        [
            InlineKeyboardButton(
                text="Xchange Create Bot", url=urls.TG_XCHANGE_CREATE
            )
        ],
    ]

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Chart Links ({chain_info.name})*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7R - Rewards Token",
                        url=urls.dex_tools_link(
                            chain_info.dext, addresses.x7r(chain)
                        ),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="X7DAO - Governance Token",
                        url=urls.dex_tools_link(
                            chain_info.dext, addresses.x7dao(chain)
                        ),
                    )
                ],
            ]
        ),
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide an address to check.")
        return

    address = context.args[0]
    result = is_address(address)

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=(
            f"*X7 Finance Address Checker*\n\n"
            f"`{address}`\n\n"
            f"{'✅ Is a valid address' if result else '❌ Is not a valid address'}"
        ),
        parse_mode="Markdown",
    )


async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = (
        context.args[2].lower()
        if len(context.args) > 2
        else chains.get_chain(update.effective_message.message_thread_id)
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    if len(context.args) < 1:
        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance Market Cap Comparison ({chain_info.name})*\n\n"
            f"Please enter X7 token first followed by token to compare\n\n"
            f"ie. `/compare x7r uni`",
            parse_mode="Markdown",
        )
        return

    x7token = context.args[0].lower()
    if x7token.lower() not in tokens.get_tokens():
        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance Market Cap Comparison* ({chain_info.name})\n\n"
            f"Please enter X7 token first followed by token to compare\n\n"
            f"ie. `/compare x7r uni`",
            parse_mode="Markdown",
        )
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Please provide a token to compare, e.g., `/compare x7r uni`."
        )
        return

    token2 = context.args[1].lower()
    search = coingecko.search(token2)
    if "coins" not in search or not search["coins"]:
        await update.message.reply_text(
            f"Comparison with `{token2}` is not available."
        )
        return

    message = await update.message.reply_text(
        f"Getting {x7token.upper()} ({chain_info.name}) comparison info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    token_id = search["coins"][0]["api_symbol"]

    token_market_cap = coingecko.get_mcap(token_id)
    if x7token == "x7r":
        x7_supply = etherscan.get_x7r_supply(chain)
    else:
        x7_supply = addresses.SUPPLY

    token_ca = tokens.get_tokens()[x7token.lower()][chain].ca
    x7_price, _ = dextools.get_price(token_ca, chain)
    x7_market_cap = float(x7_price) * float(x7_supply)

    percent = ((token_market_cap - x7_market_cap) / x7_market_cap) * 100
    x = (token_market_cap - x7_market_cap) / x7_market_cap
    token_value = token_market_cap / x7_supply

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Market Cap Comparison* ({chain_info.name})\n\n"
        f"{token2.upper()} Market Cap:\n"
        f"${token_market_cap:,.0f}\n\n"
        f"Token value of {x7token.upper()} at {token2.upper()} Market Cap:\n"
        f"${token_value:,.3f}\n"
        f"{percent:,.0f}%\n"
        f"{x:,.3f}x",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{token2.upper()} Chart",
                        url=f"https://www.coingecko.com/en/coins/{token_id}",
                    )
                ]
            ]
        ),
    )


async def constellations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Constellation Addresses ({chain_info.name})*\n\n"
        f"X7101\n"
        f"`{addresses.x7101(chain)}`\n\n"
        f"X7102:\n"
        f"`{addresses.x7102(chain)}`\n\n"
        f"X7103\n"
        f"`{addresses.x7103(chain)}`\n\n"
        f"X7104\n"
        f"`{addresses.x7104(chain)}`\n\n"
        f"X7105\n"
        f"`{addresses.x7105(chain)}`",
        parse_mode="Markdown",
    )


async def contribute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=text.CONTRIBUTE,
        parse_mode="Markdown",
    )


async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) >= 2:
        amount_raw = context.args[0]
        amount = amount_raw.replace(",", "")
        token = context.args[1]
        chain = (
            chains.get_chain(update.effective_message.message_thread_id)
            if len(context.args) < 3
            else context.args[2]
        )

        if not amount.isdigit():
            await context.bot.send_message(
                update.effective_chat.id, "Please provide a valid amount"
            )
            return
    else:
        await context.bot.send_message(
            update.effective_chat.id,
            "Please provide the amount and X7 token name",
        )
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    if token.lower() in tokens.get_tokens():
        ca = tokens.get_tokens()[token.lower()][chain].ca
        price, _ = dextools.get_price(ca, chain)

    elif token.lowe() == "x7d":
        price = etherscan.get_native_price(chain)
    else:
        await update.message.reply_text(
            "Token not found. Please use X7 tokens only"
        )
        return

    value = float(price) * float(amount)

    caption = (
        f"*X7 Finance Price Conversion - {token.upper()} ({chain_info.name})*\n\n"
        f"{amount} {token.upper()} is currently worth:\n\n${value:,.0f}\n\n"
    )

    if amount == "500000" and token.upper() == "X7DAO":
        caption += "Holding 500,000 X7DAO tokens earns you the right to make X7DAO proposals\n\n"

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=caption,
        parse_mode="Markdown",
    )


async def dao_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = "eth"
    buttons = []
    input_contract = " ".join(context.args).lower()
    contract_names = list(dao.map(chain))
    formatted_contract_names = "\n".join(contract_names)
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="Vote Here", url=urls.SNAPSHOT)],
            [InlineKeyboardButton(text="DAO Chat", url=urls.TG_DAO)],
        ]
    )
    if not input_contract:
        latest = snapshot.get_latest()
        proposal = latest["data"]["proposals"][0]
        end = datetime.fromtimestamp(proposal["end"])
        when = tools.get_time_difference(int(end.timestamp()))
        if proposal["state"] == "active":
            end_status = f"Vote Closing: {end.strftime('%Y-%m-%d %H:%M:%S')} UTC\n{when}\n\n"
            header = "Current Open Proposal"
            buttons.extend(
                [
                    [
                        InlineKeyboardButton(
                            text="Vote Here",
                            url=f"{urls.SNAPSHOT}/proposal/{proposal['id']}",
                        )
                    ]
                ]
            )
        else:
            end_status = (
                f"Vote Closed: {end.strftime('%Y-%m-%d %H:%M:%S')}\n{when}"
            )
            header = "No Current Open Proposal\n\nLast Proposal:"
            buttons.extend(
                [
                    [
                        InlineKeyboardButton(
                            text="X7DAO Snapshot", url=urls.SNAPSHOT
                        )
                    ],
                ]
            )

        choices_text = "\n".join(
            f"{choice} - {score:,.0f} Votes"
            for choice, score in zip(proposal["choices"], proposal["scores"])
        )

        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance DAO*\n"
            f"use `/dao functions` for a list of call callable contracts\n\n"
            f"*{header}*\n\n"
            f"{proposal['title']} by - "
            f"{proposal['author'][-5:]}\n\n"
            f"{choices_text}\n\n"
            f"{proposal['scores_total']:,.0f} Total Votes\n\n"
            f"{end_status}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return
    else:
        if input_contract == "functions":
            await update.message.reply_photo(
                photo=tools.get_random_pioneer(),
                caption=f"*X7 Finance DAO*\n\nUse `/dao [contract-name]` for a list of DAO callable functions\n\n"
                f"*Contract Names:*\n\n{formatted_contract_names}\n\n",
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
        else:
            matching_contract = None
            for contract in dao.map(chain).keys():
                if contract.lower() == input_contract:
                    matching_contract = contract
                    break
            if matching_contract:
                contract_text, contract_ca = dao.map(chain)[matching_contract]

                await update.message.reply_photo(
                    photo=tools.get_random_pioneer(),
                    caption=f"*X7 Finance DAO Functions* - {matching_contract}\n\n"
                    f"The following functions can be called on the {matching_contract} contract:\n\n"
                    f"{contract_text}",
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                )
            else:
                await update.message.reply_photo(
                    photo=tools.get_random_pioneer(),
                    caption=f"*X7 Finance DAO Functions*\n\n"
                    f"'{input_contract}' not found - Use `/dao` followed by one of the contract names below:\n\n"
                    f"{formatted_contract_names}",
                    parse_mode="Markdown",
                )


async def onchains(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption="*X7 Finance Onchain Messages*\n\n"
        "The stealth launch story of X7 Finance was heralded as an "
        '"incredible way to launch a project in this day and age."\n\n'
        "The on-chain, decentralized communications from X7's global collective "
        "of developers to the community provide chronological evidence on how the "
        "X7 community and ecosystem was born - and how the foundation was built.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="View all on chain messages",
                        url=f"{urls.XCHANGE}docs/onchains",
                    )
                ]
            ]
        ),
    )


async def docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [
            InlineKeyboardButton(
                text="Get Started", url=f"{urls.XCHANGE}getstarted"
            )
        ],
        [
            InlineKeyboardButton(
                text="How to - Create Pair",
                url=f"{urls.XCHANGE}docs/guides/liquidity-provider",
            ),
            InlineKeyboardButton(
                text="How to - Initiate Loan",
                url=f"{urls.XCHANGE}docs/guides/initiate-loan",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Trader", url=f"{urls.XCHANGE}docs/guides/trade"
            ),
            InlineKeyboardButton(
                text="Capital Allocator",
                url=f"{urls.XCHANGE}docs/guides/lending",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Project Engineer",
                url=f"{urls.XCHANGE}docs/guides/integrate",
            ),
            InlineKeyboardButton(
                text="Project Launcher",
                url=f"{urls.XCHANGE}docs/guides/launch",
            ),
        ],
    ]

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def ecosystem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text.ECOSYSTEM,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="X7Finance.org", url=urls.XCHANGE)]]
        ),
    )


async def factory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    for chain in chains.get_active_chains():
        name = chains.get_active_chains()[chain].name
        address = chains.get_active_chains()[chain].scan_address
        buttons.append(
            [
                InlineKeyboardButton(
                    text=name,
                    url=address + addresses.factory(chain),
                )
            ]
        )

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [
            InlineKeyboardButton(
                text="Airdrop Questions", url=f"{urls.XCHANGE}docs/faq/airdrop"
            ),
            InlineKeyboardButton(
                text="Constellation Tokens",
                url=f"{urls.XCHANGE}docs/faq/constellations",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Developer Questions", url=f"{urls.XCHANGE}docs/faq/devs"
            ),
            InlineKeyboardButton(
                text="General Questions", url=f"{urls.XCHANGE}docs/faq/general"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Governance Questions",
                url=f"{urls.XCHANGE}docs/faq/governance",
            ),
            InlineKeyboardButton(
                text="Investor Questions", url=f"{urls.XCHANGE}faq/investors"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Liquidity Lending Questions",
                url=f"{urls.XCHANGE}docs/faq/liquiditylending",
            ),
            InlineKeyboardButton(
                text="NFT Questions", url=f"{urls.XCHANGE}faq/nfts"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Snapshot.org Questions",
                url=f"{urls.XCHANGE}docs/faq/daosnapshot",
            ),
            InlineKeyboardButton(
                text="Xchange Questions", url=f"{urls.XCHANGE}faq/xchange"
            ),
        ],
    ]

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def gas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text(
        f"Getting {chain_info.name} gas data, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    try:
        gas_data = etherscan.get_gas(chain)
        gas_text = (
            f"Gas:\n"
            f"Low: {float(gas_data['result']['SafeGasPrice']):.0f} Gwei\n"
            f"Average: {float(gas_data['result']['ProposeGasPrice']):.0f} Gwei\n"
            f"High: {float(gas_data['result']['FastGasPrice']):.0f} Gwei\n\n"
        )
    except Exception:
        gas_text = ""

    pair_gas = onchain.estimate_gas(chain, "pair")
    mint_gas = onchain.estimate_gas(chain, "mint")
    process_fees_gas = onchain.estimate_gas(chain, "processfees")
    push_gas = onchain.estimate_gas(chain, "push")
    swap_gas = onchain.estimate_gas(chain, "swap")

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*Live Xchange Gas Fees ({chain_info.name})*\n\n"
        f"Create Pair: {pair_gas}\n"
        f"Mint X7D: {mint_gas}\n"
        f"Process Fees: {process_fees_gas}\n"
        f"Push Splitter: {push_gas}\n"
        f"Swap Cost: {swap_gas}\n\n"
        f"{gas_text}",
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{chain_info.name} Gas Tracker",
                        url=chain_info.gas,
                    )
                ]
            ]
        ),
    )


async def feeto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text(
        f"Getting {chain_info.name} fee to data, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    native_price = etherscan.get_native_price(chain)
    eth = etherscan.get_native_balance(
        addresses.liquidity_treasury(chain), chain
    )
    eth_dollar = float(eth) * float(native_price)

    tx = etherscan.get_tx(addresses.liquidity_treasury(chain), chain)
    tx_filter = [
        d
        for d in tx["result"]
        if addresses.liquidity_treasury(chain).lower() in d["to"].lower()
        and any(
            fn in d.get("functionName", "").lower()
            for fn in ["breaklp", "breaklpandsendeth", "withdraweth"]
        )
    ]
    recent_tx = max(
        tx_filter, key=lambda tx: int(tx["timeStamp"]), default=None
    )

    if recent_tx:
        time = datetime.fromtimestamp(int(recent_tx["timeStamp"]))
        when = tools.get_time_difference(int(recent_tx["timeStamp"]))
        recent_tx_text = f"Last Liquidation: {time} UTC\n{when}\n\n"
    else:
        recent_tx_text = "Last Liquidation: Not Found"

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*Xchange Liquidity Treasury ({chain_info.name})*\n\n"
        f"{eth} (${eth_dollar})\n\n"
        f"{recent_tx_text}",
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{chain_info.scan_name} Contract",
                        url=chain_info.scan_address
                        + addresses.liquidity_treasury(chain),
                    )
                ]
            ]
        ),
    )


async def fg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fear_response = requests.get("https://api.alternative.me/fng/?limit=0")
    fear_data = fear_response.json()
    fear_values = []
    for i in range(7):
        timestamp = float(fear_data["data"][i]["timestamp"])
        localtime = datetime.fromtimestamp(timestamp)
        fear_values.append(
            (
                fear_data["data"][i]["value"],
                fear_data["data"][i]["value_classification"],
                localtime,
            )
        )

    duration_in_s = float(fear_data["data"][0]["time_until_update"])
    next_update = tools.get_time_difference(time.time() + duration_in_s)

    caption = "*Market Fear and Greed Index*\n\n"
    caption += f"{fear_values[0][0]} - {fear_values[0][1]} - {fear_values[0][2].strftime('%B %d')}\n\n"
    caption += "Change:\n"

    for i in range(1, 7):
        caption += f"{fear_values[i][0]} - {fear_values[i][1]} - {fear_values[i][2].strftime('%B %d')}\n"

    caption += f"\nNext Update:\n{next_update}"

    await update.message.reply_photo(
        photo=f"https://alternative.me/crypto/fear-and-greed-index.png?timestamp={int(time.time())}",
        caption=caption,
        parse_mode="Markdown",
    )


async def holders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    x7dao_info = dextools.get_token_info(addresses.x7dao(chain), chain)
    x7dao_holders = x7dao_info["holders"] or "N/A"
    x7r_info = dextools.get_token_info(addresses.x7r(chain), chain)
    x7r_holders = x7r_info["holders"] or "N/A"
    x7d_info = dextools.get_token_info(addresses.x7d(chain), chain)
    x7d_holders = x7d_info["holders"] or "N/A"

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Token Holders ({chain_info.name})*\n\n"
        f"X7R:        {x7r_holders}\n"
        f"X7DAO:  {x7dao_holders}\n"
        f"X7D:        {x7d_holders}",
        parse_mode="Markdown",
    )


async def github_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    arg = " ".join(context.args).lower()
    if arg == "issues":
        issues = github.get_issues()
        issue_chunks = []
        current_chunk = ""

        for issue in issues.split("\n\n"):
            if len(current_chunk) + len(issue) + 2 > 900:
                issue_chunks.append(current_chunk.strip())
                current_chunk = issue
            else:
                current_chunk += f"\n\n{issue}"
        if current_chunk:
            issue_chunks.append(current_chunk.strip())

        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance GitHub Monorepo Issues*\n\n{issue_chunks[0]}",
            parse_mode="Markdown",
        )

        for chunk in issue_chunks[1:]:
            await update.message.reply_text(chunk, parse_mode="Markdown")
            return

    elif arg == "pr":
        pr = github.get_pull_requests()

        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance GitHub Monorepo Pull Requests*\n\n{pr}",
            parse_mode="Markdown",
        )
        return
    else:
        latest = github.get_latest_commit()

        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance GitHub*\n"
            f"use `/github issues` or `pr` for more details \n\n{latest}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="X7 Finance GitHub", url=urls.GITHUB
                        )
                    ]
                ]
            ),
        )


async def hub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not (1 <= len(context.args) <= 2):
        await update.message.reply_text(
            "Please follow the command with token liquidity hub name"
        )
        return

    token = context.args[0].lower()
    chain = (
        context.args[1].lower()
        if len(context.args) == 2
        else chains.get_chain(update.effective_message.message_thread_id)
    )

    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    if token.lower() in tokens.get_tokens():
        message = await update.message.reply_text(
            f"Getting {token.upper()} ({chain_info.name}) liquidity hub data, Please wait..."
        )
        await context.bot.send_chat_action(update.effective_chat.id, "typing")

        address = tokens.get_tokens()[token.lower()][chain].hub

        split_text = splitters.get_hub_split(chain, address, token)
    else:
        await update.message.reply_text(
            "Please follow the command with an X7 token name"
        )
        return

    buy_back_text = tools.get_last_action(address, chain)
    eth_price = etherscan.get_native_price(chain)
    eth_balance = etherscan.get_native_balance(address, chain)
    eth_dollar = eth_balance * eth_price

    config = splitters.get_push_settings(chain)[token]
    threshold = config["threshold"]
    abi = config["abi"]

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(address), abi=abi
    )

    available_tokens = config["calculate_tokens"](contract)

    buttons = []
    cost_str = ""

    if float(available_tokens) > float(threshold):
        cost = onchain.estimate_gas(chain, "processfees")
        cost_str = f"Estimated process fees gas cost: {cost}"

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Process {token.upper()} Fees",
                    callback_data=f"push:{token}:{chain}",
                )
            ]
        )

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*{token.upper()} Liquidity Hub ({chain_info.name})*\n\n"
        f"{eth_balance:,.4f} {chain_info.native.upper()} (${eth_dollar:,.0f})\n"
        f"{split_text}\n\n"
        f"{buy_back_text}\n\n{cost_str}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = db.clicks_get_leaderboard()
    click_counts_total = db.clicks_get_total()
    fastest_user, fastest_time = db.clicks_fastest_time()
    streak_user, streak_value = db.clicks_check_highest_streak()
    formatted_fastest_time = tools.format_seconds(fastest_time)

    year = datetime.now().year

    burn_active = db.settings_get("burn")
    clicks_needed = (
        settings.CLICK_ME_BURN - (click_counts_total % settings.CLICK_ME_BURN)
        if burn_active
        else None
    )

    message = (
        f"*X7 Finance Fastest Pioneer {year} Leaderboard*\n\n"
        f"{tools.escape_markdown(board)}\n"
        f"Total clicks: *{click_counts_total}*\n"
        + (
            f"Clicks till next X7R Burn: *{clicks_needed}*\n"
            if burn_active
            else ""
        )
        + f"\nFastest click:\n"
        f"{formatted_fastest_time}\n"
        f"by @{tools.escape_markdown(fastest_user)}\n\n"
        f"@{tools.escape_markdown(streak_user)} clicked the button last and is on a *{streak_value}* click streak!"
    )

    await update.message.reply_text(message, parse_mode="Markdown")


async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(text="X7Finance.org", url=urls.XCHANGE)],
        [
            InlineKeyboardButton(text="Snapshot", url=urls.SNAPSHOT),
            InlineKeyboardButton(text="Twitter", url=urls.TWITTER),
        ],
        [
            InlineKeyboardButton(text="Reddit", url=urls.REDDIT),
            InlineKeyboardButton(text="Warpcast", url=urls.WARPCAST),
        ],
        [
            InlineKeyboardButton(text="GitHub", url=urls.GITHUB),
            InlineKeyboardButton(text="Dune", url=urls.DUNE),
        ],
    ]

    await update.message.reply_photo(
        photo=x7_images.WEBSITE_LOGO,
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def liquidity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text(
        f"Getting {chain_info.name} liquidity data, Please wait..."
    )

    x7r_pair = tokens.get_tokens()["Xx7r"].get(chain).pairs[0]
    x7dao_pair = tokens.get_tokens()["x7dao"].get(chain).pairs[0]

    total_x7r_liquidity = 0
    total_x7dao_liquidity = 0
    total_x7r_eth = 0
    total_x7dao_eth = 0

    x7r_liquidity_data = dextools.get_liquidity(x7r_pair, chain)

    x7r_text = "*X7R*\n"
    x7r_token_liquidity = x7r_liquidity_data.get("token")
    x7r_eth_liquidity = x7r_liquidity_data.get("eth")
    x7r_total_liquidity = x7r_liquidity_data.get("total")

    x7r_percentage = (
        (float(x7r_token_liquidity.replace(",", "")) / addresses.SUPPLY) * 100
        if x7r_token_liquidity and addresses.SUPPLY
        else 0
    )

    if x7r_eth_liquidity:
        total_x7r_eth += float(x7r_eth_liquidity.replace(",", ""))

    x7r_text += (
        f"{x7r_token_liquidity} X7R ({x7r_percentage:.2f}%)\n"
        f"{x7r_eth_liquidity} {chain_info.native.upper()}\n{x7r_total_liquidity}"
    )

    if x7r_total_liquidity:
        total_x7r_liquidity += float(
            x7r_total_liquidity.replace("$", "").replace(",", "")
        )

    x7dao_liquidity_data = dextools.get_liquidity(x7dao_pair, chain)
    x7dao_text = "*X7DAO*\n"
    x7dao_token_liquidity = x7dao_liquidity_data.get("token")
    x7dao_eth_liquidity = x7dao_liquidity_data.get(
        "eth",
    )
    x7dao_total_liquidity = x7dao_liquidity_data.get("total")

    x7dao_percentage = (
        (float(x7dao_token_liquidity.replace(",", "")) / addresses.SUPPLY)
        * 100
        if x7dao_token_liquidity and addresses.SUPPLY
        else 0
    )

    if x7dao_eth_liquidity:
        total_x7dao_eth += float(x7dao_eth_liquidity.replace(",", ""))

    x7dao_text += (
        f"{x7dao_token_liquidity} X7DAO ({x7dao_percentage:.2f}%)\n"
        f"{x7dao_eth_liquidity} {chain_info.native.upper()}\n{x7dao_total_liquidity}"
    )

    if x7dao_total_liquidity:
        total_x7dao_liquidity += float(
            x7dao_total_liquidity.replace("$", "").replace(",", "")
        )

    final_text = f"{x7r_text}\n\n{x7dao_text}"

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Liquidity ({chain_info.name})*\n\n{final_text}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7R Liquidty Pair",
                        url=chain_info.scan_address + x7r_pair,
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="X7DAO Liquidty Pair",
                        url=chain_info.scan_address + x7dao_pair,
                    )
                ],
            ]
        ),
    )


async def liquidate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    loan_id = None
    chain = None

    if len(context.args) == 1:
        try:
            loan_id = int(context.args[0])
            chain = chains.get_chain(
                update.effective_message.message_thread_id
            )
        except ValueError:
            chain = context.args[0].lower()
    elif len(context.args) == 2:
        try:
            loan_id = int(context.args[0])
            chain = context.args[1].lower()
        except ValueError:
            await update.message.reply_text(
                "Invalid Loan ID. Please provide a valid number."
            )
            return
    else:
        chain = chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(
            addresses.lending_pool(chain)
        ),
        abi=abis.read("lendingpool"),
    )

    reward = contract.functions.liquidationReward().call() / 10**18
    escrow = contract.functions.liquidationEscrow().call() / 10**18

    if escrow > 0:
        live_loans = escrow / reward
    else:
        live_loans = 0

    if loan_id is None:
        message = await update.message.reply_text(
            f"Getting {chain_info.name} liquidation info, Please wait..."
        )
        await context.bot.send_chat_action(update.effective_chat.id, "typing")

        num_loans = contract.functions.nextLoanID().call()
        liquidatable_loans = 0
        results = []
        ignored_loans = range(21, 25)

        for loan in range(num_loans):
            if chain == "eth-sepolia" and loan in ignored_loans:
                continue
            try:
                result = contract.functions.canLiquidate(int(loan)).call()
                if result > 0:
                    if liquidatable_loans == 0:
                        first_loan_id = loan
                    liquidatable_loans += 1
                    results.append(f"Loan ID {loan}")
            except Exception:
                continue

        liquidatable_loans_text = (
            f"Liquidation reward: {reward} {chain_info.native.upper()}\n"
            f"Live loans: {live_loans:.0f}\n"
            f"Liquidatable loans: {liquidatable_loans}"
        )

        if liquidatable_loans > 0:
            liquidation_instructions = f"Use `/liquidate loanID {chain}`"
            cost = onchain.estimate_gas(chain, "liquidate", first_loan_id)
            results_text = "\n".join(results)
            output = (
                f"{liquidatable_loans_text}\n\n"
                f"{results_text}\n\n"
                f"{liquidation_instructions}\n"
                f"Estimated gas cost: {cost}"
            )
        else:
            output = liquidatable_loans_text

        await message.delete()
        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance Loan Liquidations ({chain_info.name})*\n\n{output}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Lending Dashboard",
                            url=f"{urls.XCHANGE}lending",
                        )
                    ]
                ]
            ),
        )
    else:
        try:
            try:
                can = contract.functions.canLiquidate(int(loan_id)).call()
                if not can or can == 0:
                    await update.message.reply_text(
                        f"Loan {loan_id} is not eligible for liquidation"
                    )
                    return
            except Exception:
                await update.message.reply_text(
                    f"Loan {loan_id} is not eligible for liquidation"
                )
                return

            await update.message.reply_text(
                f"Liquidating Loan {loan_id} ({chain_info.name})..."
            )
            result = onchain.liquidate_loan(loan_id, chain, user_id)
            await update.message.reply_text(result)

        except Exception as e:
            await update.message.reply_text(
                f"Error liquidating Loan ID {loan_id}: {e}"
            )


async def loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 1 and not context.args[0].isdigit():
        chain = context.args[0].lower()

        chain_info, error_message = chains.get_info(chain)
        if error_message:
            await update.message.reply_text(error_message)
            return

        message = await update.message.reply_text(
            f"Getting Loan Info for {chain_info.name}, Please wait..."
        )
        await context.bot.send_chat_action(update.effective_chat.id, "typing")

        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(
                addresses.lending_pool(chain)
            ),
            abi=abis.read("lendingpool"),
        )

        amount = contract.functions.nextLoanID().call() - 1
        live_loans = (
            contract.functions.liquidationEscrow().call()
            / contract.functions.liquidationReward().call()
        )

        latest_loan_text = ""
        ill_number = None
        token_by_id = None

        if chain != "eth":
            adjusted_amount = max(0, amount - 20)
            latest_loan = amount
            amount = adjusted_amount
        else:
            latest_loan = amount

        if amount > 0:
            latest_loan_text = f"Latest ID: {latest_loan}"

            term = contract.functions.loanTermLookup(int(latest_loan)).call()
            term_contract = chain_info.w3.eth.contract(
                address=chain_info.w3.to_checksum_address(term),
                abi=abis.read("ill005"),
            )
            index = 0
            while True:
                try:
                    token_id = term_contract.functions.tokenByIndex(
                        index
                    ).call()
                    if token_id == int(latest_loan):
                        token_by_id = index
                        break
                    index += 1
                except Exception:
                    break

            ill_number = tools.get_ill_number(term)

        loan_text = (
            f"Total: {amount}\nLive: {live_loans:.0f}\n{latest_loan_text}\n"
        )

        buttons = [
            [
                InlineKeyboardButton(
                    text="Loans Dashboard", url=f"{urls.XCHANGE}lending"
                )
            ]
        ]

        if ill_number is not None and token_by_id is not None:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"Latest Loan - ID: {latest_loan}",
                        url=f"{urls.XCHANGE}lending/{chain_info.name.lower()}/{ill_number}/{token_by_id}",
                    )
                ]
            )

        await message.delete()
        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=(
                f"*X7 Finance Loan Count ({chain_info.name})*\n\n{loan_text}\n"
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return

    if len(context.args) < 1:
        message = await update.message.reply_text(
            "Getting Loan Info, Please wait..."
        )
        await context.bot.send_chat_action(update.effective_chat.id, "typing")

        loan_text = ""
        total = 0
        total_live = 0

        for chain in chains.get_active_chains():
            chain_info, error_message = chains.get_info(chain)

            contract = chain_info.w3.eth.contract(
                address=chain_info.w3.to_checksum_address(
                    addresses.lending_pool(chain)
                ),
                abi=abis.read("lendingpool"),
            )

            amount = contract.functions.nextLoanID().call() - 1
            live_loans = (
                contract.functions.liquidationEscrow().call()
                / contract.functions.liquidationReward().call()
            )

            latest_loan_text = ""

            if chain != "eth":
                adjusted_amount = max(0, amount - 20)
                latest_loan = amount
                amount = adjusted_amount
            else:
                latest_loan = amount

            if amount != 0:
                latest_loan_text = f"- Latest ID: {latest_loan}"

            loan_text += f"{chain_info.name}: {live_loans:.0f}/{amount} {latest_loan_text}\n"

            total_live += live_loans
            total += amount

        await message.delete()
        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance Loan Count*\n\n"
            f"{loan_text}\n"
            f"Total: {total}\n"
            f"Total Live: {total_live:.0f}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Loans Dashboard",
                            url=f"{urls.XCHANGE}lending",
                        )
                    ]
                ]
            ),
        )
        return

    loan_id = None
    chain = None

    if len(context.args) == 1 and context.args[0].isdigit():
        loan_id = int(context.args[0])
        chain = chains.get_chain(update.effective_message.message_thread_id)
    elif len(context.args) > 1:
        if context.args[0].isdigit():
            loan_id = int(context.args[0])
            chain = context.args[1].lower()
        else:
            await update.message.reply_text("Loan ID should be a number")
            return
    else:
        chain = chains.get_chain(update.effective_message.message_thread_id)

    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    if loan_id is None:
        await update.message.reply_text(
            "Loan ID is required and should be a number"
        )
        return

    message = await update.message.reply_text(
        f"Getting loan {loan_id} ({chain_info.name}) info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    chain_lpool = addresses.lending_pool(chain, int(loan_id))
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(chain_lpool),
        abi=abis.read("lendingpool"),
    )

    try:
        term = contract.functions.loanTermLookup(int(loan_id)).call()
        term_contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(term),
            abi=abis.read("ill005"),
        )

        schedule1 = contract.functions.getPremiumPaymentSchedule(
            int(loan_id)
        ).call()
        schedule2 = contract.functions.getPrincipalPaymentSchedule(
            int(loan_id)
        ).call()
        isComplete = term_contract.functions.isComplete(loan_id).call()

        schedule = tools.format_schedule(
            schedule1, schedule2, chain_info.native.upper(), isComplete
        )

        if not isComplete:
            liability = (
                contract.functions.getRemainingLiability(int(loan_id)).call()
                / 10**18
            )
            remaining = f"Total Remaining Liability:\n{liability} {chain_info.native.upper()}"
        else:
            remaining = ""

        token = contract.functions.loanToken(int(loan_id)).call()
        name = dextools.get_token_name(token, chain)["name"]
        pair = contract.functions.loanPair(int(loan_id)).call()

        term = contract.functions.loanTermLookup(int(loan_id)).call()
        term_contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(term),
            abi=abis.read("ill005"),
        )

        index = 0
        token_by_id = None
        while True:
            try:
                token_id = term_contract.functions.tokenByIndex(index).call()
                if token_id == int(loan_id):
                    token_by_id = index
                    break
                index += 1
            except Exception:
                break

        ill_number = tools.get_ill_number(term)

        liquidation_status = ""
        liquidation_button = []

        try:
            liquidation = contract.functions.canLiquidate(int(loan_id)).call()
            if liquidation != 0:
                reward = contract.functions.liquidationReward().call() / 10**18
                cost = onchain.estimate_gas(chain, "liquidate", loan_id)
                liquidation_status = (
                    f"\n\n*Eligible For Liquidation*\n"
                    f"Reward: {reward} {chain_info.native.upper()}\n"
                    f"Estimated gas cost: {cost}"
                )
                liquidation_button = [
                    InlineKeyboardButton(
                        text="Liquidate Loan",
                        callback_data=f"liquidate:{loan_id}:{chain}",
                    )
                ]
        except Exception:
            pass

        keyboard = [
            [
                InlineKeyboardButton(
                    text="Chart",
                    url=urls.dex_tools_link(chain_info.dext, pair),
                )
            ],
            [
                InlineKeyboardButton(
                    text="View Loan",
                    url=f"{urls.XCHANGE}lending/{chain_info.name.lower()}/{ill_number}/{token_by_id}",
                )
            ],
        ]

        if liquidation_button:
            keyboard.append(liquidation_button)

        await message.delete()
        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance Initial Liquidity Loan - {loan_id} ({chain_info.name})*\n\n"
            f"{name}\n\n"
            f"Payment Schedule UTC:\n{schedule}\n\n"
            f"{remaining}"
            f"{liquidation_status}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception:
        await message.delete()
        await update.message.reply_text(
            f"Loan ID {loan_id} on {chain_info.name} not found"
        )


async def locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(
            addresses.token_time_lock(chain)
        ),
        abi=abis.read("timelock"),
    )

    def get_lock_info(pair):
        effective_timestamp = contract.functions.getTokenUnlockTimestamp(
            chain_info.w3.to_checksum_address(pair)
        ).call()

        when = tools.get_time_difference(effective_timestamp)
        date = datetime.fromtimestamp(effective_timestamp)
        return date.strftime("%Y-%m-%d %H:%M"), when

    x7r_date, x7r_remaining_time = get_lock_info(addresses.x7r_pair(chain)[0])
    x7dao_date, x7dao_remaining_time = get_lock_info(
        addresses.x7dao_pair(chain)[0]
    )
    x7100_date, x7100_remaining_time = get_lock_info(
        addresses.x7101_pair(chain)
    )
    x7d_date, x7d_remaining_time = get_lock_info(addresses.x7d(chain))

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Liquidity Locks ({chain_info.name})*\n\n"
        f"*X7R*\n"
        f"{x7r_date}\n{x7r_remaining_time}\n\n"
        f"*X7DAO*\n"
        f"{x7dao_date}\n{x7dao_remaining_time}\n\n"
        f"*X7100*\n"
        f"{x7100_date}\n{x7100_remaining_time}\n\n"
        f"*X7D*\n"
        f"{x7d_date}\n{x7d_remaining_time}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{chain_info.scan_name} Contract",
                        url=chain_info.scan_address
                        + addresses.token_time_lock(chain),
                    )
                ]
            ]
        ),
    )


async def mcap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    caps_info = {}
    caps = {}

    for token, chains_info in tokens.get_tokens().items():
        token_info = chains_info.get(chain)
        if token_info:
            address = token_info.ca
            caps_info[address] = dextools.get_token_info(address, chain)
            caps[address] = caps_info[address]["mcap"]

    total_mcap = 0
    for token, mcap in caps.items():
        if not mcap:
            continue
        mcap_value = float("".join(filter(str.isdigit, mcap)))
        total_mcap += mcap_value

    total_cons = 0
    for token, mcap in caps.items():
        if token in (addresses.x7dao(chain), addresses.x7r(chain)):
            continue
        if not mcap:
            continue
        cons_mcap_value = float("".join(filter(str.isdigit, mcap)))
        total_cons += cons_mcap_value

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Market Cap Info ({chain_info.name})*\n\n"
        f"X7R: {caps[addresses.x7r(chain)]}\n"
        f"X7DAO: {caps[addresses.x7dao(chain)]}\n"
        f"X7100: ${total_cons:,.0f}\n\n"
        f"Total Market Cap: ${total_mcap:,.0f}",
        parse_mode="Markdown",
    )


async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    buttons = []
    message = f"*X7 Finance Member Details*\n\nTelegram User ID:\n`{user.id}`"

    wallet = db.wallet_get(user.id)

    if not wallet:
        message += "\n\nUse /register to register an EVM wallet"
    else:
        chain = " ".join(context.args).lower() or chains.get_chain(
            update.effective_message.message_thread_id
        )
        chain_info, error_message = chains.get_info(chain)
        if error_message:
            await update.message.reply_text(error_message)
            return

        native_balance = etherscan.get_native_balance(wallet["wallet"], chain)
        x7d_balance = etherscan.get_token_balance(
            wallet["wallet"], addresses.x7d(chain), 18, chain
        )
        if native_balance > 0:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "Withdraw", callback_data=f"withdraw:{chain}"
                    )
                ]
            )
            buttons.append(
                [
                    InlineKeyboardButton(
                        "Mint X7D", callback_data=f"mint:{chain}"
                    )
                ]
            )
        if x7d_balance > 0:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "Redeem X7D", callback_data=f"redeem:{chain}"
                    )
                ]
            )

        message += (
            f"\n\nWallet Address:\n`{wallet['wallet']}`\n\n"
            f"*{chain_info.name} Chain*\n"
            f"{chain_info.native.upper()} Balance: {native_balance:.4f}\n"
            f"X7D Balance: {x7d_balance}\n\n"
            f"To view balances on other chains, use `/me chain-name`\n\n"
            f"If your TXs are failing, you likely have a stuck nonce, use to the button to attempt to clear it."
        )

        buttons.append(
            [
                InlineKeyboardButton(
                    "View Onchain",
                    url=chain_info.scan_address + wallet["wallet"],
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    "Clear Stuck TX", callback_data=f"question:stuck:{chain}"
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    "Remove Wallet", callback_data="question:wallet_remove"
                )
            ]
        )

    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
        )
        if update.effective_chat.type != "private":
            await update.message.reply_text("Check DMs!")
    except Exception:
        await update.message.reply_text("Use this command in private!")


async def media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token_names = [token.lower() for token in tokens.get_tokens().keys()]
    token_dirs = [urls.token_img_link(token) for token in token_names]
    token_dirs_str = "\n".join(token_dirs)
    caption = f"*X7 Finance Media*\n\n{token_dirs_str}"
    buttons = [
        [
            InlineKeyboardButton(
                text="X7 Official Images", url="https://imgur.com/a/WEszZTa"
            ),
            InlineKeyboardButton(
                text="X7 TG Sticker Pack 1",
                url="https://t.me/addstickers/x7financestickers",
            ),
        ],
        [
            InlineKeyboardButton(
                text="X7 TG Sticker Pack 2",
                url="https://t.me/addstickers/X7finance",
            ),
            InlineKeyboardButton(
                text="X7 TG Sticker Pack 3",
                url="https://t.me/addstickers/x7financ",
            ),
        ],
        [
            InlineKeyboardButton(
                text="X7 TG Sticker Pack 4",
                url="https://t.me/addstickers/GavalarsX7",
            ),
            InlineKeyboardButton(
                text="X7 Emojis Pack",
                url="https://t.me/addemoji/x7FinanceEmojis",
            ),
        ],
    ]

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def nft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain)

    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text(
        f"Getting {chain_info.name} NFT info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    nft_data = nfts.get_info(chain)

    buttons = [
        [
            InlineKeyboardButton(
                text="Mint Here", url=f"{urls.XCHANGE}dashboard/marketplace"
            ),
            InlineKeyboardButton(
                text="OS - Ecosystem Maxi",
                url=urls.opensea_link("eco") + chain_info.opensea,
            ),
        ],
        [
            InlineKeyboardButton(
                text="OS - Liquidity Maxi",
                url=urls.opensea_link("liq") + chain_info.opensea,
            ),
            InlineKeyboardButton(
                text="OS - DEX Maxi",
                url=urls.opensea_link("dex") + chain_info.opensea,
            ),
        ],
        [
            InlineKeyboardButton(
                text="OS - Borrowing Maxi",
                url=urls.opensea_link("borrow") + chain_info.opensea,
            ),
            InlineKeyboardButton(
                text="OS - Magister",
                url=urls.opensea_link("magister") + chain_info.opensea,
            ),
        ],
    ]

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*NFT Info ({chain_info.name})*\n\n{nft_data}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    if len(context.args) == 1:
        chain = context.args[0].lower()

        chain_info, error_message = chains.get_info(chain)
        if error_message:
            await update.message.reply_text(error_message)
            return

        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(
                addresses.factory(chain)
            ),
            abi=abis.read("factory"),
        )

        amount = contract.functions.allPairsLength().call()

        if chain == "eth":
            amount += 141

        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=(
                f"*X7 Finance Pair Count*\n\n{chain_info.name} Pairs: {amount:,.0f}\n"
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Xchange Pairs Dashboard",
                            url=f"{urls.XCHANGE}liquidity?=all-pools",
                        )
                    ]
                ]
            ),
        )
        return

    pair_text = ""
    total = 0

    for chain in chains.get_active_chains():
        chain_info, error_message = chains.get_info(chain)

        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(
                addresses.factory(chain)
            ),
            abi=abis.read("factory"),
        )

        amount = contract.functions.allPairsLength().call()

        if chain == "eth":
            amount += 141

        pair_text += f"{chain_info.name}: {amount:,.0f}\n"
        total += amount

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Pair Count*\n\n{pair_text}\nTotal: {total:,.0f}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Xchange Pairs Dashboard",
                        url=f"{urls.XCHANGE}liquidity?=all-pools",
                    )
                ]
            ]
        ),
    )


async def pioneer(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    message = await update.message.reply_text(
        "Getting Pioneer Info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    pioneer_id = " ".join(context.args)
    chain = "eth"
    chain_info, error_message = chains.get_info(chain)

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(addresses.PIONEER),
        abi=abis.read("pioneer"),
    )

    native_price = etherscan.get_native_price(chain)
    if pioneer_id == "":
        data = opensea.get_nft_by_slug("x7-pioneer")
        floor_price = data["total"]["floor_price"]
        floor_dollar = floor_price * float(native_price)
        pioneer_pool = etherscan.get_native_balance(addresses.PIONEER, "eth")
        total_dollar = float(pioneer_pool) * float(native_price)
        tx = etherscan.get_tx(addresses.PIONEER, "eth")
        tx_filter = [
            d
            for d in tx["result"]
            if addresses.PIONEER.lower() in d["to"].lower()
            and d.get("functionName", "") == "claimRewards(uint256[] _pids)"
        ]
        recent_tx = max(
            tx_filter, key=lambda tx: int(tx["timeStamp"]), default=None
        )
        unlock_fee = contract.functions.transferUnlockFee().call() / 10**18
        unlock_fee_dollar = float(unlock_fee) * float(native_price)

        total_claimed = (
            contract.functions.totalRewards().call()
            - contract.functions.lastETHBalance().call()
        ) / 10**18
        total_claimed_dollar = float(total_claimed) * float(native_price)

        if recent_tx:
            by = recent_tx["from"][-5:]
            time = datetime.fromtimestamp(int(recent_tx["timeStamp"]))
            timestamp = recent_tx["timeStamp"]
            when = tools.get_time_difference(timestamp)
            recent_tx_text = f"Last Claim: {time} UTC (by {by})\n{when}\n\n"
        else:
            recent_tx_text = "Last Claim: Not Found\n\n"

        await message.delete()
        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Pioneer NFT Info*\n\n"
            f"Floor Price: {floor_price:,.3f} ETH (${floor_dollar:,.0f})\n"
            f"Total Unclaimed Rewards: {pioneer_pool:.3f} ETH (${total_dollar:,.0f})\n"
            f"Total Claimed Rewards: {total_claimed:.3f} ETH (${total_claimed_dollar:,.0f})\n"
            f"Unlock Fee: {unlock_fee:.2f} ETH (${unlock_fee_dollar:,.0f})\n\n"
            f"{recent_tx_text}",
            parse_mode="markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="X7 Pioneer Dashboard",
                            url=f"{urls.XCHANGE}dashboard/pioneer",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Opensea", url=urls.opensea_link("pioneer")
                        )
                    ],
                ]
            ),
        )
    else:
        data = opensea.get_nft_by_id(addresses.PIONEER, pioneer_id)
        if "nft" in data and data["nft"]:
            status = data["nft"]["traits"][0]["value"]
            image_url = data["nft"]["image_url"]
            unclaimed = (
                contract.functions.unclaimedRewards(int(pioneer_id)).call()
                / 10**18
            )
            unclaimed_dollar = float(unclaimed) * float(native_price)
            claimed = (
                contract.functions.rewardsClaimed(int(pioneer_id)).call()
                / 10**18
            )
            claimed_dollar = float(claimed) * float(native_price)
        else:
            await update.message.reply_text(f"Pioneer {pioneer_id} not found")
            return

        await message.delete()
        await update.message.reply_photo(
            photo=image_url,
            caption=f"*X7 Pioneer {pioneer_id} NFT Info*\n\n"
            f"Transfer Lock Status: {status}\n"
            f"Unclaimed Rewards: {unclaimed:.3f} ETH (${unclaimed_dollar:,.0f})\n"
            f"Claimed Rewards: {claimed:.3f} ETH (${claimed_dollar:,.0f})\n\n"
            f"https://pro.opensea.io/nft/ethereum/{addresses.PIONEER}/{pioneer_id}",
            parse_mode="markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="X7 Pioneer Dashboard",
                            url=f"{urls.XCHANGE}dashboard/pioneer",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Opensea",
                            url=f"https://pro.opensea.io/nft/ethereum/{addresses.PIONEER}/{pioneer_id}",
                        )
                    ],
                ]
            ),
        )


async def pool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or None

    if not chain:
        message = await update.message.reply_text(
            "Getting lending pool info, Please wait..."
        )
        await context.bot.send_chat_action(update.effective_chat.id, "typing")

        pool_text = ""
        total_lpool_reserve_dollar = 0
        total_lpool_dollar = 0
        total_dollar = 0
        eth_price = None

        for chain in chains.get_active_chains():
            native = chains.get_active_chains()[chain].native.lower()
            chain_name = chains.get_active_chains()[chain].name
            try:
                if chain in chains.ETH_CHAINS and eth_price is None:
                    eth_price = etherscan.get_native_price(chain)
                native_price = (
                    eth_price
                    if chain in chains.ETH_CHAINS
                    else etherscan.get_native_price(chain)
                )

                lpool_reserve = etherscan.get_native_balance(
                    addresses.lending_pool_reserve(chain), chain
                )
                lpool = etherscan.get_native_balance(
                    addresses.lending_pool(chain), chain
                )
            except Exception:
                native_price = 0
                lpool_reserve = 0
                lpool = 0

            lpool_reserve_dollar = lpool_reserve * native_price
            lpool_dollar = lpool * native_price
            pool = lpool_reserve + lpool
            dollar = lpool_reserve_dollar + lpool_dollar
            pool_text += f"{chain_name}:   {pool:,.3f} {native.upper()} (${dollar:,.0f})\n"
            total_lpool_reserve_dollar += lpool_reserve_dollar
            total_lpool_dollar += lpool_dollar
            total_dollar += dollar

        await message.delete()

        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance Lending Pool Info*\n\n"
            f"{pool_text}\n"
            f"Lending Pool: ${total_lpool_dollar:,.0f}\n"
            f"Lending Pool Reserve: ${total_lpool_reserve_dollar:,.0f}\n"
            f"Total: ${total_dollar:,.0f}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Lending Pool Dashboard",
                            url=f"{urls.XCHANGE}lending",
                        )
                    ]
                ]
            ),
        )
    else:
        chain_info, error_message = chains.get_info(chain)
        if error_message:
            await update.message.reply_text(error_message)
            return

        message = await update.message.reply_text(
            f"Getting {chain_info.name} lending pool info, Please wait..."
        )
        await context.bot.send_chat_action(update.effective_chat.id, "typing")

        native_price = etherscan.get_native_price(chain)
        lpool_reserve = etherscan.get_native_balance(
            addresses.lending_pool_reserve(chain), chain
        )
        lpool_reserve_dollar = lpool_reserve * native_price
        lpool = etherscan.get_native_balance(
            addresses.lending_pool(chain), chain
        )
        lpool_dollar = lpool * native_price
        pool = lpool_reserve + lpool
        dollar = lpool_reserve_dollar + lpool_dollar

        try:
            contract = chain_info.w3.eth.contract(
                address=chain_info.w3.to_checksum_address(
                    addresses.lending_pool(chain)
                ),
                abi=abis.read("lendingpool"),
            )

            count = contract.functions.nextLoanID().call()
            total_borrowed = 0

            ignored_loans = range(21, 25)

            for loan_id in range(21, count):
                if chain == "eth-sepolia" and loan_id in ignored_loans:
                    continue

                borrowed = (
                    contract.functions.getRemainingLiability(loan_id).call()
                    / 10**18
                )
                total_borrowed += borrowed

            total_borrowed_dollar = float(total_borrowed) * float(native_price)

        except Exception:
            total_borrowed = 0
            total_borrowed_dollar = 0

        if total_borrowed != 0:
            borrowed_percentage = (total_borrowed / pool) * 100
        else:
            borrowed_percentage = 0

        await message.delete()
        await update.message.reply_photo(
            photo=tools.get_random_pioneer(),
            caption=f"*X7 Finance Lending Pool Info ({chain_info.name})*\n\n"
            f"Lending Pool:\n"
            f"{lpool:,.3f} {chain_info.native.upper()} (${lpool_dollar:,.0f})\n\n"
            f"Lending Pool Reserve:\n"
            f"{lpool_reserve:,.3f} {chain_info.native.upper()} (${lpool_reserve_dollar:,.0f})\n\n"
            f"Total\n"
            f"{pool:,.3f} {chain_info.native.upper()} (${dollar:,.0f})\n\n"
            f"Total Currently Borrowed\n"
            f"{total_borrowed:,.3f} {chain_info.native.upper()} (${total_borrowed_dollar:,.0f}) - {borrowed_percentage:.0f}%",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Lending Pool Dashboard",
                            url=f"{urls.XCHANGE}lending",
                        )
                    ]
                ]
            ),
        )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    x7r_price, x7r_change = dextools.get_price(addresses.x7r(chain), chain)
    x7dao_price, x7dao_change = dextools.get_price(
        addresses.x7dao(chain), chain
    )

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Token Price Info ({chain_info.name})*\n\n"
        f"X7R\n"
        f"💰 Price: {x7r_price}\n"
        f"{x7r_change}\n\n"
        f"X7DAO\n"
        f"💰 Price: {x7dao_price}\n"
        f"{x7dao_change}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7R Chart - Rewards Token",
                        url=urls.dex_tools_link(
                            chain_info.dext, addresses.x7r(chain)
                        ),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="X7DAO Chart - Governance Token",
                        url=urls.dex_tools_link(
                            chain_info.dext, addresses.x7dao(chain)
                        ),
                    )
                ],
            ]
        ),
    )


async def pushall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    existing_wallet = db.wallet_get(user_id)

    if not existing_wallet:
        await update.message.reply_text(
            "You have not registered a wallet. Please use /register in private."
        )
        return

    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text(
        f"Pushing {chain_info.name} splitters, Please wait..."
    )

    eco_config = splitters.get_push_settings(chain)["eco"]
    address = eco_config["address"]
    abi = eco_config["abi"]
    name = eco_config["name"]
    threshold = eco_config["threshold"]

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(address), abi=abi
    )

    available_tokens = eco_config["calculate_tokens"](contract)

    if float(available_tokens) < float(threshold):
        await message.delete()
        await update.message.reply_text(
            f"{chain_info.name} {name} balance too low to push."
        )
    else:
        result = onchain.splitter_push(
            "splitter", address, abi, chain, user_id
        )
        await message.delete()
        await update.message.reply_text(result)

    if chain.lower() == "eth":
        treasury_config = splitters.get_push_settings(chain)["treasury"]
        address = treasury_config["address"]
        abi = treasury_config["abi"]
        name = treasury_config["name"]
        threshold = treasury_config["threshold"]

        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(address), abi=abi
        )

        available_tokens = treasury_config["calculate_tokens"](contract)

        if float(available_tokens) < float(threshold):
            await update.message.reply_text(
                f"{chain_info.name} {name} balance too low to push."
            )
        else:
            result = onchain.splitter_push(
                "splitter", address, abi, chain, user_id
            )
            await update.message.reply_text(result)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    existing_wallet = db.wallet_get(user_id)
    if existing_wallet:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="Youve already registed, your details are as follows...",
                parse_mode="Markdown",
            )
            await me(update, context)
        except Exception:
            await update.message.reply_text("Use this command in private!")
        return

    account = Account.create()
    db.wallet_add(user_id, account.address, account.key.hex())

    message = (
        "*New EVM wallet created*\n\n"
        "You can now deposit to this address to initiate loan liquidations and splitter pushes\n\n"
        f"Address:\n`{account.address}`\n\n"
        "To withdraw use /me in private."
    )

    try:
        await context.bot.send_message(
            chat_id=user_id, text=message, parse_mode="Markdown"
        )
        if update.effective_chat.type != "private":
            await update.message.reply_text("Check DMs!")
    except Exception:
        await update.message.reply_text("Use this command in private!")


async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    for chain in chains.get_active_chains():
        name = chains.get_active_chains()[chain].name
        address = chains.get_active_chains()[chain].scan_address
        buttons.append(
            [
                InlineKeyboardButton(
                    text=name,
                    url=address + addresses.router(chain),
                )
            ]
        )

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def spaces(update: Update, context: ContextTypes.DEFAULT_TYPE):
    space = twitter.get_next_space("x7_finance")
    caption = "*X7 Finance Twitter Spaces*\n\n"

    if space is None:
        button_text = "Twitter"
        caption += "No live or upcoming Spaces found."
        url = urls.TWITTER
    elif space.get("state") == "Live Now":
        button_text = "Join Now"
        caption += f"{space['title']} - {space['state']}"
        url = f"https://twitter.com/i/spaces/{space['space_id']}"
    elif space.get("state") == "Scheduled":
        button_text = "Set Reminder"
        when = tools.get_time_difference(space["scheduled_start"].timestamp())
        caption += f"{space['title']}\n\n{space['state']} UTC - {space['scheduled_start']}\n{when}"
        url = f"https://twitter.com/i/spaces/{space['space_id']}"

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=button_text, url=url)]]
    )

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=caption,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def smart(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )

    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    buttons = [
        [
            InlineKeyboardButton(
                text="Contracts Dashboard", url=f"{urls.XCHANGE}dashboard"
            )
        ],
        [
            InlineKeyboardButton(
                text="X7100 Liquidity Hub",
                url=chain_info.scan_address
                + addresses.x7100_liquidity_hub(chain),
            ),
            InlineKeyboardButton(
                text="X7R Liquidity Hub",
                url=chain_info.scan_address
                + addresses.x7r_liquidity_hub(chain),
            ),
        ],
        [
            InlineKeyboardButton(
                text="X7DAO Liquidity Hub",
                url=chain_info.scan_address
                + addresses.x7dao_liquidity_hub(chain),
            ),
            InlineKeyboardButton(
                text="X7100 Discount Authority",
                url=chain_info.scan_address + addresses.x7100_discount(chain),
            ),
        ],
        [
            InlineKeyboardButton(
                text="X7R Discount Authority",
                url=chain_info.scan_address + addresses.x7r_discount(chain),
            ),
            InlineKeyboardButton(
                text="X7DAO Discount Authority",
                url=chain_info.scan_address + addresses.x7dao_discount(chain),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Xchange Discount Authority",
                url=chain_info.scan_address
                + addresses.xchange_discount(chain),
            ),
            InlineKeyboardButton(
                text="Lending Discount Authority",
                url=chain_info.scan_address
                + addresses.lending_discount(chain),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Token Burner",
                url=chain_info.scan_address + addresses.token_burner(chain),
            ),
            InlineKeyboardButton(
                text="Token Time Lock",
                url=chain_info.scan_address + addresses.token_time_lock(chain),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Ecosystem Splitter",
                url=chain_info.scan_address + addresses.eco_splitter(chain),
            ),
            InlineKeyboardButton(
                text="Treasury Splitter",
                url=chain_info.scan_address
                + addresses.treasury_splitter(chain),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Liquidity Treasury",
                url=chain_info.scan_address
                + addresses.liquidity_treasury(chain),
            ),
            InlineKeyboardButton(
                text="Default Token List",
                url=chain_info.scan_address
                + addresses.default_token_list(chain),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Lending Pool",
                url=chain_info.scan_address + addresses.lending_pool(chain),
            ),
            InlineKeyboardButton(
                text="Lending Pool Reserve",
                url=chain_info.scan_address
                + addresses.lending_pool_reserve(chain),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Xchange Factory",
                url=chain_info.scan_address + addresses.factory(chain),
            ),
            InlineKeyboardButton(
                text="Xchange Router",
                url=chain_info.scan_address + addresses.router(chain),
            ),
        ],
    ]

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Smart Contracts ({chain_info.name})*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def splitters_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text(
        f"Getting {chain_info.name} splitter info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    native_price = etherscan.get_native_price(chain)

    eco_address = addresses.eco_splitter(chain)
    eco_eth = etherscan.get_native_balance(eco_address, chain)
    eco_dollar = eco_eth * native_price

    eco_splitter_text = "Distribution:\n"
    eco_distribution = splitters.get_eco_split(chain)
    for location, (share, percentage) in eco_distribution.items():
        eco_splitter_text += f"{location}: {share:.4f} {chain_info.native.upper()} ({percentage:.0f}%)\n"

    config = splitters.get_push_settings(chain)["eco"]
    threshold = config["threshold"]
    abi = config["abi"]

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(eco_address), abi=abi
    )

    available_tokens = config["calculate_tokens"](contract)

    push_text = tools.get_last_action(eco_address, chain)

    caption = (
        f"*X7 Finance Splitters ({chain_info.name})*\n\n"
        f"*Ecosystem Splitter*\n{eco_eth:.4f} {chain_info.native.upper()} (${eco_dollar:,.0f})\n"
        f"{eco_splitter_text}\n{push_text}\n"
    )

    buttons = []
    cost_str = ""
    cost = None

    if float(available_tokens) > float(threshold):
        cost = onchain.estimate_gas(chain, "push")
        cost_str = f"\nEstimated push gas cost: {cost}"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Push {chain_info.name} Ecosystem Splitter",
                    callback_data=f"push:eco:{chain}",
                )
            ]
        )

    treasury_splitter_text = ""
    if chain == "eth":
        treasury_address = addresses.treasury_splitter(chain)
        treasury_eth = etherscan.get_native_balance(treasury_address, chain)
        treasury_dollar = treasury_eth * native_price

        treasury_splitter_text = "Distribution:\n"
        treasury_distribution = splitters.get_treasury_split(chain)
        for location, (share, percentage) in treasury_distribution.items():
            treasury_splitter_text += f"{location}: {share:.4f} {chain_info.native.upper()} ({percentage:.0f}%)\n"

        config = splitters.get_push_settings(chain)["treasury"]
        threshold = config["threshold"]
        abi = config["abi"]

        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(treasury_address),
            abi=abi,
        )

        available_tokens = config["calculate_tokens"](contract)

        push_text = tools.get_last_action(treasury_address, chain)

        caption += (
            f"\n*Treasury Splitter*\n{treasury_eth:.4f} {chain_info.native.upper()} (${treasury_dollar:,.0f})\n"
            f"{treasury_splitter_text}\n{push_text}"
        )

        if float(available_tokens) > float(threshold):
            if cost is None:
                cost = onchain.estimate_gas(chain, "push")
                cost_str = f"\nEstimated push gas cost: {cost}"

            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"Push {chain_info.name} Treasury Splitter",
                        callback_data=f"push:treasury:{chain}",
                    )
                ]
            )
    else:
        treasury_dollar = 0

    caption += cost_str

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def tax_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    tax_info = tax.get_info(chain)

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Tax Info ({chain_info.name})*\n\n{tax_info}\n",
        parse_mode="Markdown",
    )


async def timestamp_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        text = " ".join(context.args)
        if text == "":
            await update.message.reply_text(
                "Please follow the command with the timestamp you wish to convert"
            )
        else:
            stamp = int(" ".join(context.args).lower())
            time = datetime.fromtimestamp(stamp)
            when = tools.get_time_difference(stamp)

            await update.message.reply_photo(
                photo=tools.get_random_pioneer(),
                caption=f"*X7 Finance Timestamp Conversion*\n\n"
                f"{stamp}\n{time} UTC\n\n"
                f"{when}",
                parse_mode="Markdown",
            )
    except Exception:
        await update.message.reply_text("Timestamp not recognised")


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.split(" ")
    timezones = [
        ("America/Los_Angeles", "PST"),
        ("America/New_York", "EST"),
        ("UTC", "UTC"),
        ("Europe/London", "GMT"),
        ("Europe/Berlin", "CET"),
        ("Asia/Dubai", "GST"),
        ("Asia/Kolkata", "IST"),
        ("Asia/Tokyo", "JST"),
        ("Australia/Queensland", "AEST"),
    ]

    now_time = datetime.now(pytz.UTC)

    try:
        if len(message) > 1:
            time_variable = message[1].strip().upper()

            pattern_12h = r"^\d{1,2}(:\d{2})?(AM|PM)$"
            pattern_24h = r"^([01]?\d|2[0-3]):[0-5]\d$"

            input_time = None
            if re.match(pattern_12h, time_variable, re.IGNORECASE):
                time_format = "%I:%M%p" if ":" in time_variable else "%I%p"
                input_time = datetime.strptime(time_variable, time_format)
            elif re.match(pattern_24h, time_variable):
                time_format = "%H:%M"
                input_time = datetime.strptime(time_variable, time_format)

            input_time = input_time.replace(
                year=now_time.year, month=now_time.month, day=now_time.day
            )

            if len(message) > 2:
                time_zone = message[2].upper()
                for tz, tz_name in timezones:
                    if time_zone == tz_name:
                        tz_time = pytz.timezone(tz).localize(input_time)
                        time_info = f"{time_variable} {time_zone}:\n\n"
                        for tz_inner, tz_name_inner in timezones:
                            converted_time = tz_time.astimezone(
                                pytz.timezone(tz_inner)
                            )
                            time_info += f"{converted_time.strftime('%I:%M %p')} - {tz_name_inner}\n"

                        await update.message.reply_text(
                            time_info, parse_mode="Markdown"
                        )
                        return

            time_info = f"{time_variable} UTC:\n\n"
            for tz, tz_name in timezones:
                tz_time = input_time.astimezone(pytz.timezone(tz))
                time_info += f"{tz_time.strftime('%I:%M %p')} - {tz_name}\n"

            await update.message.reply_text(time_info, parse_mode="Markdown")
            return

        time_info = "Current time:\n\n"
        for tz, tz_name in timezones:
            tz_time = now_time.astimezone(pytz.timezone(tz))
            time_info += f"{tz_time.strftime('%I:%M %p')} - {tz_name}\n"

        await update.message.reply_text(time_info, parse_mode="Markdown")

    except Exception:
        await update.message.reply_text(
            "Invalid format. Use `/time 2AM` or `/time 02:00` with or without a timezone.\n\n",
            parse_mode="Markdown",
        )


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower()

    message = await update.message.reply_text(
        "Getting Xchange Top Pairs Info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    top_text = await dune.get_top_tokens(chain)

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=top_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="X7 Dune Dashboard", url=urls.DUNE)]]
        ),
    )


async def treasury(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text(
        f"Getting {chain_info.name} treasury info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    native_price = etherscan.get_native_price(chain)
    eth_balance = etherscan.get_native_balance(chain_info.dao_multi, chain)
    eth_dollar = eth_balance * native_price
    x7r_balance = etherscan.get_token_balance(
        chain_info.dao_multi, addresses.x7r(chain), 18, chain
    )
    x7r_price = dextools.get_price(addresses.x7r(chain), chain)[0] or 0
    x7r_dollar = float(x7r_balance) * float(x7r_price)
    x7dao_balance = etherscan.get_token_balance(
        chain_info.dao_multi, addresses.x7dao(chain), 18, chain
    )
    x7dao_price = dextools.get_price(addresses.x7dao(chain), chain)[0] or 0
    x7dao_dollar = float(x7dao_balance) * float(x7dao_price)
    x7d_balance = etherscan.get_token_balance(
        chain_info.dao_multi, addresses.x7d(chain), 18, chain
    )
    x7d_dollar = x7d_balance * native_price
    total = x7r_dollar + eth_dollar + x7d_dollar + x7dao_dollar
    x7r_percent = round(x7r_balance / addresses.SUPPLY * 100, 2)
    x7dao_percent = round(x7dao_balance / addresses.SUPPLY * 100, 2)

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7 Finance Treasury ({chain_info.name})*\n\n"
        f"{eth_balance:,.3f} {chain_info.native.upper()} (${eth_dollar:,.0f})\n\n"
        f"{x7r_balance:,.0f} X7R (${x7r_dollar:,.0f}) - {x7r_percent}% \n"
        f"{x7dao_balance:,.0f} X7DAO (${x7dao_dollar:,.0f}) - {x7dao_percent}%\n"
        f"{x7d_balance} X7D (${x7d_dollar:,.0f})\n\n"
        f"Total: ${total:,.0f}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="DAO Multi-Sig Wallet",
                        url=chain_info.scan_address + chain_info.dao_multi,
                    )
                ]
            ]
        ),
    )


async def twitter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.lower()

    if any(
        keyword in command for keyword in ["xtrader", "0xtrader", "0xtraderai"]
    ):
        username = "0xtraderai"
        display_name = "0xTraderAi Twitter/X"
        image = x7_images.XTRADER_LOGO
    elif tools.is_admin(update.effective_user.id) and context.args:
        username = " ".join(context.args).lower()
        display_name = f"{username.capitalize()} Twitter/X"
        image = (
            twitter.get_user_data(username)["profile_image"]
            or tools.get_random_pioneer()
        )
    else:
        username = "x7_finance"
        display_name = "X7 Finance Twitter/X"
        image = tools.get_random_pioneer()

    tweet_data = twitter.get_latest_tweet(username)
    followers = twitter.get_user_data(username)["followers"]

    created_at = tweet_data.get("created_at", "")
    when = (
        tools.get_time_difference(created_at.timestamp()) if created_at else ""
    )

    tweet = (
        f"Latest {tweet_data['type']} - {when}\n\n"
        f"{tools.escape_markdown(tweet_data['text'])}\n\n"
        f"Likes: {tweet_data['likes']}\n"
        f"Retweets: {tweet_data['retweets']}\n"
        f"Replies: {tweet_data['replies']}\n\n"
        f"{random.choice(text.X_REPLIES)}"
    )

    await update.message.reply_photo(
        photo=image,
        caption=f"*{display_name}*\n\nFollowers: {followers}\n\n{tweet}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Tweet", url=tweet_data["url"])]]
        ),
    )


async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    volume_text = await dune.get_volume()

    message = await update.message.reply_text(
        "Getting Volume Info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=volume_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="X7 Dune Dashboard", url=urls.DUNE)]]
        ),
    )


async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if len(args) < 1:
        await update.message.reply_text(
            "Please follow the command with a valid wallet address.",
            parse_mode="Markdown",
        )
        return

    wallet = args[0].lower()

    if not re.match(r"^0x[a-fA-F0-9]{40}$", wallet):
        await update.message.reply_text(
            "Please provide a valid wallet address.", parse_mode="Markdown"
        )
        return

    chain = (
        args[1].lower()
        if len(args) == 2
        else chains.get_chain(update.effective_message.message_thread_id)
    )
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text(
        f"Getting {chain_info.name} Wallet Info, Please wait..."
    )
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    native_price = etherscan.get_native_price(chain)
    eth_balance = float(etherscan.get_native_balance(wallet, chain)) / 10**18
    dollar = eth_balance * native_price

    x7r_price = dextools.get_price(addresses.x7r(chain), chain)[0] or 0
    x7dao_price = dextools.get_price(addresses.x7dao(chain), chain)[0] or 0

    x7r_balance = etherscan.get_token_balance(
        wallet, addresses.x7r(chain), 18, chain
    )
    x7r_dollar = float(x7r_balance) * float(x7r_price)

    x7dao_balance = etherscan.get_token_balance(
        wallet, addresses.x7dao(chain), 18, chain
    )
    x7dao_dollar = float(x7dao_balance) * float(x7dao_price)

    x7d_balance = etherscan.get_token_balance(
        wallet, addresses.x7d(chain), 18, chain
    )
    x7d_dollar = x7d_balance * native_price

    total = x7d_dollar + x7r_dollar + x7dao_dollar

    if x7dao_balance == 0:
        x7dao_percentage = 0
    else:
        x7dao_percentage = round(x7dao_balance / addresses.SUPPLY * 100, 2)
    if x7r_balance == 0:
        x7r_percent = 0
    else:
        x7r_percent = round(
            x7r_balance / etherscan.get_x7r_supply(chain) * 100, 2
        )
    txs = etherscan.get_daily_tx_count(wallet, chain)

    if wallet == os.getenv("BURN_WALLET"):
        header = f"*X7 Finance Bot Wallet Info ({chain_info.name})*"
    else:
        header = f"*X7 Finance Wallet Tracker Info ({chain_info.name})*"

    await message.delete()
    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"{header}\n\n"
        f"`{wallet}`\n\n"
        f"{eth_balance:.3f} {chain_info.native.upper()} (${dollar:,.0f})\n\n"
        f"{x7r_balance:,.0f} X7R (${x7r_dollar:,.0f}) -  {x7r_percent}%\n"
        f"{x7dao_balance:,.0f} X7DAO (${x7dao_dollar:,.0f}) - {x7dao_percentage}%\n"
        f"{x7d_balance:.3f} X7D (${x7d_dollar:,.0f})\n\n"
        f"{txs} tx's in the last 24 hours\n\n"
        f"Total X7 Finance token value ${total:,.0f}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Wallet Link",
                        url=chain_info.scan_address + wallet,
                    )
                ]
            ]
        ),
    )


async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=x7_images.WEBSITE_LOGO,
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="X7Finance.org", url=urls.XCHANGE)]]
        ),
    )


async def wei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eth = " ".join(context.args)
    if eth == "":
        await update.message.reply_text(
            "Please follow the command with the amount of eth you wish to convert"
        )
    else:
        wei = int(float(eth) * 10**18)

        await update.message.reply_text(
            f"{eth} ETH is equal to \n`{wei}` wei", parse_mode="Markdown"
        )


async def wp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"*X7 Finance Whitepaper Quote*\n\n{random.choice(text.QUOTES)}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="Website", url=urls.XCHANGE)],
                [InlineKeyboardButton(text="Full WP", url=urls.WP_LINK)],
            ]
        ),
    )


async def x7d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    native_price = etherscan.get_native_price(chain)
    lpool_reserve = etherscan.get_native_balance(
        addresses.lending_pool_reserve(chain), chain
    )
    lpool_reserve_dollar = lpool_reserve * native_price
    lpool = etherscan.get_native_balance(addresses.lending_pool(chain), chain)
    lpool_dollar = lpool * native_price
    dollar = lpool_reserve_dollar + lpool_dollar
    supply = lpool_reserve + lpool
    info = dextools.get_token_info(addresses.x7d(chain), chain)
    holders = info["holders"] or "N/A"

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*X7D ({chain_info.name}) Info*\n\n"
        f"Holders: {holders}\n\n"
        f"Lending Pool:\n{lpool:,.3f} X7D (${lpool_dollar:,.0f})\n\n"
        f"Lending Pool Reserve:\n{lpool_reserve:,.3f} X7D (${lpool_reserve_dollar:,.0f})\n\n"
        f"Total Supply:\n{supply:,.3f} X7D (${dollar:,.0f})",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7D Funding Dashboard", url=f"{urls.XCHANGE}fund"
                    )
                ]
            ]
        ),
    )


async def x7_token(
    update: Update, context: ContextTypes.DEFAULT_TYPE, token_name, token_ca
):
    chain = " ".join(context.args).lower() or chains.get_chain(
        update.effective_message.message_thread_id
    )
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    pairs = tokens.get_tokens()[token_name.lower()][chain].pairs
    if isinstance(pairs, str):
        pair = pairs
    elif isinstance(pairs, list) and pairs:
        pair = pairs[0]

    info = dextools.get_token_info(token_ca(chain), chain)
    holders = info.get("holders", "N/A")
    market_cap = info.get("mcap", "N/A")
    price, price_change = dextools.get_price(token_ca(chain), chain)
    price = f"${price}" if price else "N/A"
    volume = defined.get_volume(pair, chain) or "N/A"
    liquidity_data = dextools.get_liquidity(pair, chain)
    liquidity = liquidity_data.get("total", "N/A")

    if chain == "eth":
        ath_data = coingecko.get_ath(token_name)
        if ath_data:
            ath_change = f"{ath_data[1]}"
            ath_value = ath_data[0]
            ath = f"${ath_value} (${ath_value * addresses.SUPPLY:,.0f}) {ath_change[:3]}%"
        else:
            ath = "Unavailable"
    else:
        ath = "Unavailable"

    await update.message.reply_photo(
        photo=tools.get_random_pioneer(),
        caption=f"*{token_name} Info ({chain_info.name})*\n\n"
        f"💰 Price: {price}\n"
        f"💎 Market Cap:  {market_cap}\n"
        f"📊 24 Hour Volume: {volume}\n"
        f"💦 Liquidity: {liquidity}\n"
        f"👪 Holders: {holders}\n"
        f"🔝 ATH: {ath}\n\n"
        f"{price_change}\n\n"
        f"Contract Address:\n`{token_ca(chain)}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Chart",
                        url=urls.dex_tools_link(chain_info.dext, pair),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Buy",
                        url=urls.xchange_buy_link(
                            chain_info.id, token_ca(chain)
                        ),
                    )
                ],
            ]
        ),
    )


async def x7dao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await x7_token(update, context, "X7DAO", addresses.x7dao)


async def x7r(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await x7_token(update, context, "X7R", addresses.x7r)


async def x7101(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await x7_token(update, context, "X7101", addresses.x7101)


async def x7102(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await x7_token(update, context, "X7102", addresses.x7102)


async def x7103(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await x7_token(update, context, "X7103", addresses.x7103)


async def x7104(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await x7_token(update, context, "X7104", addresses.x7104)


async def x7105(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await x7_token(update, context, "X7105", addresses.x7105)


async def x(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        if len(context.args) > 1:
            search = " ".join(context.args[:-1])
            chain_name = context.args[-1].lower()

            if chain_name in chains.get_active_chains():
                chain = chains.get_active_chains()[chain_name].name.lower()
            else:
                search = " ".join(context.args)
                chain = None
        else:
            search = " ".join(context.args)
            chain = None
    else:
        await update.message.reply_text(
            "Please provide Contract Address/Project Name and optional chain name",
        )
        return
    await pricebot.command(update, context, search, chain)


HANDLERS = [
    (func.__name__.split("_")[0], func, description)
    for func, description in [
        (about, "About X7 Finance"),
        (admins, "List of admins"),
        (alerts, "Xchange Alerts Channel"),
        (announcements, "Latest announcements"),
        (arbitrage, "Arbitrage opportunities"),
        (blocks, "Block info"),
        (blog, "Read the latest blog posts"),
        (borrow, "Loan rates"),
        (burn, "Burn info"),
        (buy, "Buy links"),
        (ca, "Contract addresses"),
        (channels, "X7 channels"),
        (chart, "Charts links"),
        (check, "Check valid input"),
        (compare, "Compare token metrics"),
        (constellations, "Constellations"),
        (contribute, "Contribute to X7"),
        (convert, "Convert token values"),
        (dao_command, "DAO info"),
        (docs, "View documentation"),
        (ecosystem, "View ecosystem tokens"),
        (factory, "Factory contracts"),
        (fg, "Market fear greed data"),
        (faq, "Frequently Asked Questions"),
        (feeto, "X7 FeeTo info"),
        (gas, "Check gas fees"),
        (github_command, "View GitHub repository"),
        (holders, "Check token holders"),
        (hub, "View hubs and buybacks"),
        (leaderboard, "View leaderboard"),
        (links, "View important links"),
        (liquidate, "Liquidate loans"),
        (liquidity, "View liquidity details"),
        (loan, "Check active loans"),
        (locks, "View token locks"),
        (me, "Check your balance"),
        (mcap, "Check market cap"),
        (media_command, "View media links"),
        (nft, "View NFTs"),
        (onchains, "View onchain messages"),
        (pair, "Check trading pairs"),
        (pioneer, "Pioneer information"),
        (pool, "View lending pool"),
        (price, "Check token prices"),
        (pushall, "Push X7 splitters"),
        (register, "Register a wallet"),
        (router, "View router contracts"),
        (smart, "X7 smart contracts"),
        (spaces, "Check available spaces"),
        (splitters_command, "View splitters"),
        (tax_command, "Check tax"),
        (timestamp_command, "Convert timestamps"),
        (time_command, "View system time"),
        (treasury, "View treasury details"),
        (top, "View trending tokens"),
        (twitter_command, "Twitter link"),
        (volume, "Check trading volume"),
        (wallet, "View wallet information"),
        (website, "Website link"),
        (wei, "Convert values to Wei"),
        (wp, "Read the whitepaper"),
        (x7r, "View X7R details"),
        (x7d, "View X7D details"),
        (x7dao, "View X7DAO details"),
        (x7101, "View X7101 details"),
        (x7102, "View X7102 details"),
        (x7103, "View X7103 details"),
        (x7104, "View X7104 details"),
        (x7105, "View X7105 details"),
        (x, "X7 Price Bot"),
    ]
]
HANDLERS.extend(
    [
        (["0xtrader"], twitter_command, "0xTrader Twitter link"),
    ]
)
