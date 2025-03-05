from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from eth_utils import is_address

from constants.bot import urls
from constants.protocol import chains, tokens
from services import get_coingecko, get_defined, get_dextools, get_etherscan

cg = get_coingecko()
defined = get_defined()
dextools = get_dextools()
etherscan = get_etherscan()


async def command(
    update: Update, context: ContextTypes.DEFAULT_TYPE, search, chain=None
):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    search = await resolve_search(search, chain)
    if not search:
        await update.message.reply_text("No result found.")
        return

    token_data, found_chain = await fetch_token_data(search, chain)

    if not token_data:
        await update.message.reply_text("No result found.")
        return

    if token_data and "price" in token_data:
        await send_coingecko_response(update, search, token_data)
        return

    message, buttons = await send_dextools_response(
        search, found_chain, token_data
    )
    await update.message.reply_text(
        message,
        disable_web_page_preview=True,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def resolve_search(search, chain):
    if not is_address(search):
        if search.lower() in tokens.BLUE_CHIPS:
            token = await cg.search(search)

            if token and "coins" in token and token["coins"]:
                for coin in token["coins"]:
                    if coin["symbol"].upper() == search.upper():
                        return coin["id"]

                return token["coins"][0]["id"]

        token = await defined.search(search, chain)

        if is_address(token):
            return token

    return search if is_address(search) else None


async def fetch_token_data(search, chain):
    if not is_address(search):
        return await cg.get_price(search), None
    if chain:
        token_data = await dextools.get_audit(search, chain)
        if token_data and token_data.get("data"):
            return token_data, chain

    for alt_chain, chain_info in chains.MAINNETS.items():
        if chain_info.live:
            token_data = await dextools.get_audit(search, alt_chain)
            if token_data and token_data.get("data"):
                return token_data, alt_chain

    return None, None


async def send_coingecko_response(update: Update, search, token_info):
    price = token_info["price"]
    price_change = token_info["change"]
    market_cap = token_info["mcap"]
    volume = token_info["volume"]

    price_change_str = (
        f"📈 24H Change: {round(price_change, 2)}%" if price_change else "N/A"
    )

    message = (
        f"*{search.capitalize()} Price*\n\n"
        f"💰 Price: ${price}\n"
        f"💎 Market Cap: {market_cap}\n"
        f"📊 24 Hour Volume: {volume}\n"
        f"{price_change_str}"
    )

    buttons = [
        [
            InlineKeyboardButton(
                text="Chart",
                url=f"https://www.coingecko.com/en/coins/{search}",
            )
        ]
    ]

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def send_dextools_response(search, chain, token_data):
    if not token_data or "data" not in token_data:
        return "No result found.", []

    data = token_data.get("data", {})

    chain_info, _ = await chains.get_info(chain)
    if not chain_info:
        chain_name, chain_dext, chain_id = "Unknown", "", ""
    else:
        chain_name = chain_info.name
        chain_dext = chain_info.dext
        chain_id = chain_info.id

    buy_tax_data = data.get("buyTax", {})
    sell_tax_data = data.get("sellTax", {})

    buy_tax = (buy_tax_data.get("max") or 0) * 100
    sell_tax = (sell_tax_data.get("max") or 0) * 100

    is_open_source = data.get("isOpenSource", "no")
    is_honeypot = data.get("isHoneypot", "no")
    is_mintable = data.get("isMintable", "no")
    is_blacklisted = data.get("isBlacklisted", "no")
    is_renounced = data.get("isContractRenounced", "no")
    is_scam = data.get("isPotentiallyScam", "no")

    open_source = (
        "✅ Contract Verified"
        if is_open_source == "yes"
        else "⚠️ Contract Not Verified"
    )
    honey_pot = (
        "❌ Honey Pot" if is_honeypot == "yes" else "✅ Not a Honey Pot"
    )
    mint = "⚠️ Mintable" if is_mintable == "yes" else "✅ Not Mintable"
    blacklist = (
        "⚠️ Has Blacklist Functions"
        if is_blacklisted == "yes"
        else "✅ No Blacklist Functions"
    )
    renounced = (
        "✅ Contract Renounced"
        if is_renounced == "yes"
        else "⚠️ Contract Not Renounced"
    )
    scam = "⚠️ Potential Scam" if is_scam == "yes" else "✅ Not a Scam"

    tax = f"{'⚠️' if buy_tax > 5 or sell_tax > 5 else '✅'} Tax: {int(buy_tax)}/{int(sell_tax)}"

    status = f"{open_source}\n{renounced}\n{tax}\n{mint}\n{honey_pot}\n{blacklist}\n{scam}"

    name_info = await dextools.get_token_name(search, chain)
    token_name = name_info.get("name", "Unknown")
    token_symbol = name_info.get("symbol", "N/A")

    info = await dextools.get_token_info(search, chain)
    holders = info.get("holders", "N/A")
    mcap = info.get("mcap", "N/A")

    pair = await defined.get_pair(search, chain)
    dex = await dextools.get_dex(pair, chain)

    price, price_change = await dextools.get_price(search, chain)
    price = f"${price}" if price else "N/A"

    volume = await defined.get_volume(pair, chain) or "N/A"
    liquidity = await dextools.get_liquidity(pair, chain).get("total", "N/A")

    message = (
        f"*{token_name} ({token_symbol})* - {chain_name}\n"
        f"`{search}`\n\n"
        f"💰 Price: {price}\n"
        f"💎 Market Cap: {mcap}\n"
        f"📊 24 Hour Volume: {volume}\n"
        f"💦 Liquidity: {liquidity} {dex}\n"
        f"👪 Holders: {holders}\n\n"
        f"{price_change}\n\n"
        f"{status}"
    )

    buttons = [
        [
            InlineKeyboardButton(
                text="Chart",
                url=urls.dex_tools_link(chain_dext, pair)
                if chain_dext
                else "#",
            ),
            InlineKeyboardButton(
                text="Buy",
                url=urls.xchange_buy_link(chain_id, search)
                if chain_id
                else "#",
            ),
        ]
    ]

    return message, buttons
