from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from eth_utils import is_address

from hooks import api, tools
from constants import ca, chains, tokens, urls

coingecko = api.CoinGecko()
defined = api.Defined()
dextools = api.Dextools()
etherscan = api.Etherscan()


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE, search, chain):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    if not is_address(search):
        if search.lower() in tokens.BLUE_CHIPS:
            token = coingecko.search(search)
            if token['coins']:
                search = token["coins"][0]["id"]
        else:
            token = defined.search(search, chain)
            if token:
                search = token
            else:
                await update.message.reply_text(
                    f"No result found",
                )
                return
            
    if is_address(search):
        if chain is None:
            for chain, chain_info in chains.MAINNETS.items():
                if chain_info.live:
                    token_data = dextools.get_audit(search, chain)
                    if token_data and token_data.get("data"):
                        break
            else:
                await update.message.reply_text(
                    f"No result found",
                )
                return
        else:
            token_data = dextools.get_audit(search, chain)
            if not token_data:
                await update.message.reply_text(
                    f"No result found",
                )
                return

        if token_data.get("statusCode") == 200 and token_data.get("data"):
            data = token_data["data"]

            buy_tax_data = data.get("buyTax", {})
            sell_tax_data = data.get("sellTax", {})
            buy_tax = (buy_tax_data.get("max") or 0) * 100
            sell_tax = (sell_tax_data.get("max") or 0) * 100

            is_open_source = data.get("isOpenSource", "no")
            open_source = "✅ Contract Verified" if is_open_source == "yes" else "⚠️ Contract Not Verified"

            is_honeypot = data.get("isHoneypot", "no")
            honey_pot = "❌ Honey Pot" if is_honeypot == "yes" else "✅️ Not Honey Pot"

            is_mintable = data.get("isMintable", "no")
            mint = "⚠️ Mintable" if is_mintable == "yes" else "✅️ Not Mintable"

            is_blacklisted = data.get("isBlacklisted", "no")
            blacklist = "⚠️ Has Blacklist Functions" if is_blacklisted == "yes" else "✅️ No Blacklist Functions"

            if buy_tax > 5 or sell_tax > 5:
                tax = f"⚠️ Tax: {int(buy_tax)}/{int(sell_tax)}"
            else:
                tax = f"✅️ Tax: {int(buy_tax)}/{int(sell_tax)}"

            is_renounced = data.get("isContractRenounced", "no")
            renounced = "✅ Contract Renounced" if is_renounced == "yes" else "⚠️ Contract Not Renounced"

            is_scam = data.get("isPotentiallyScam", "no")
            scam = "⚠️ Is Potentially a Scam" if is_scam == "yes" else "✅️ Not a Scam"

        else:
            open_source = "❓ Contract Verification - Unknown"
            honey_pot = "❓ Honey Pot - Unknown"
            mint = "❓ Mintable - Unknown"
            blacklist = "❓ Blacklist Functions - Unknown"
            tax = "❓ Tax - Unknown"
            renounced = "❓ Renounced - Unknown"
            scam = "❓ Scam - Unknown"
            
        status = f"{open_source}\n{renounced}\n{tax}\n{mint}\n{honey_pot}\n{blacklist}\n{scam}"

        chain_info = chains.active_chains()[chain]
        chain_name = chain_info.name
        chain_dext = chain_info.dext
        chain_id = chain_info.id

        name_info = dextools.get_token_name(search, chain)
        token_name = name_info["name"]
        token_symbol = name_info["symbol"]
        
        info = dextools.get_token_info(search, chain)
        holders = info["holders"] or "N/A"
        mcap = info["mcap"] or "N/A"

        pair = defined.get_pair(search, chain)
        dex = dextools.get_dex(pair, chain)

        price, price_change = dextools.get_price(search, chain)
        if price:
            price = f"${price}"
        else:
            price = "N/A"

        volume = defined.get_volume(pair, chain) or "N/A"

        liquidity = dextools.get_liquidity(pair, chain)['total'] or "N/A"

        await update.message.reply_text(
            f"*{token_name} ({token_symbol})* - {chain_name}\n"
            f"`{search}`\n\n"
            f'💰 Price: {price}\n'
            f"💎 Market Cap: {mcap}\n"
            f"📊 24 Hour Volume: {volume}\n"
            f"💦 Liquidity: {liquidity} {dex}\n"
            f"👪 Holders: {holders}\n\n"
            f"{price_change}\n\n"
            f"{status}",
        disable_web_page_preview=True,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Chart", url=urls.DEX_TOOLS(chain_dext, pair)
                    ),
                    InlineKeyboardButton(
                        text="Buy",
                        url=f"{urls.XCHANGE_BUY(chain_id, search)}",
                    )
                ]
            ]
            )
        )
        return
    
    else:
        try:
            token_info = coingecko.get_price(search)
        except Exception:
            return

        price = token_info["price"]
        price_change = token_info["change"]
        if price_change is None:
            price_change_str = 0
        else:
            emoji_up = "📈"
            emoji_down = "📉"
            price_change_str = f"{emoji_up if price_change > 0 else emoji_down} 24H Change: {round(price_change, 2)}"

        market_cap = token_info["mcap"]
        volume = token_info["volume"]   

        await update.message.reply_text(
            f"*{search.capitalize()} price*\n\n"
            f'💰 Price: ${price}\n'
            f'💎 Market Cap: {market_cap}\n'
            f'📊 24 Hour Volume: {volume}\n'
            f'{price_change_str}%',
        parse_mode="Markdown",
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="Chart",
                    url=f"https://www.coingecko.com/en/coins/{search}"
                )
            ]
        ])
    )

