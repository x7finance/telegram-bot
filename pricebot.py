from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from hooks import api, tools
from constants import ca, chains, tokens, urls

coingecko = api.CoinGecko()
defined = api.Defined()
dextools = api.Dextools()
etherscan = api.Etherscan()


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE, search, chain):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    if not tools.is_eth(search):
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
            
    if tools.is_eth(search):
        if chain is None:
            for chain, chain_info in chains.MAINNETS.items():
                if chain_info.live:
                    token_data = dextools.get_audit(search, chain)
                    if token_data:
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
        
        if "data" in token_data:
            buy_tax_data = token_data.get("buyTax", {})
            sell_tax_data = token_data.get("sellTax", {})
            buy_tax = buy_tax_data.get("max", 0) * 100
            sell_tax = sell_tax_data.get("max", 0) * 100
            if buy_tax > 5 or sell_tax > 5:
                tax = f"⚠️ Tax: {int(buy_tax)}/{int(sell_tax)}"
            else:
                tax = f"✅️ Tax: {int(buy_tax)}/{int(sell_tax)}"

            is_open_source = token_data.get("isOpenSource", "no")
            open_source = "✅ Contract Verified" if is_open_source == "yes" else "⚠️ Contract Not Verified"

            is_renounced = token_data.get("isContractRenounced", "no")
            renounced = "✅ Contract Renounced" if is_renounced == "yes" else "⚠️ Contract Not Renounced"

            is_mintable = token_data.get("isMintable", "no")
            mint = "⚠️ Mintable" if is_mintable == "yes" else "✅️ Not Mintable"

            is_honeypot = token_data.get("isHoneypot", "no")
            honey_pot = "❌ Honey Pot" if is_honeypot == "yes" else "✅️ Not Honey Pot"


            is_blacklisted = token_data.get("isBlacklisted", "no")
            blacklist = "⚠️ Has Blacklist Functions" if is_blacklisted == "yes" else "✅️ No Blacklist Functions"

            slippage_modifiable = token_data.get("slippageModifiable", "no")
            sellable = "❌ Not Sellable" if slippage_modifiable == "yes" else "✅️ Sellable"


        else:
            renounced = "❓ Renounced - Unknown"
            tax = "❓ Tax - Unknown"
            mint = "❓ Mintable - Unknown"
            honey_pot = "❓ Honey Pot - Unknown"
            blacklist = "❓ Blacklist Functions - Unknown"
            sellable = "❓ Sellable - Unknown"
            open_source = "❓ Contract Verification - Unknown"

        status = f"{open_source}\n{renounced}\n{tax}\n{sellable}\n{mint}\n{honey_pot}\n{blacklist}\n"

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

