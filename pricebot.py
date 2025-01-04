from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from hooks import api, tools
from constants import ca, chains, tokens, urls

coingecko = api.CoinGecko()
defined = api.Defined()
dextools = api.Dextools()
etherscan = api.Etherscan()
goplus = api.GoPlus()


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE, search, chain):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    if not tools.is_eth(search):
        if search.lower() in tokens.BLUE_CHIPS:
            token = coingecko.search(search)
            if token['coins'] != []:
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
        if chain == None:
            for chain in chains.active_chains():
                scan = goplus.get_security_scan(search, chain)
                if scan:
                    break
            else:
                await update.message.reply_text(
                    f"No result found",
                )
                return
        else:
            scan = goplus.get_security_scan(search, chain)
            if not scan:
                await update.message.reply_text(
                    f"No result found",
                )
                return
        chain_id = chains.active_chains()[chain].id
        token_address = str(search.lower())
        if token_address in scan:
            if "token_name" in scan[token_address]:
                token_name = f"{scan[token_address]['token_name']}"
            else:
                token_name = ""
            if "token_symbol" in scan[token_address]:
                token_symbol = f"({scan[token_address]['token_symbol']})"
            else:
                token_symbol = ""

            if scan[token_address]["is_in_dex"] == "1" and scan[token_address]["buy_tax"] and scan[token_address]["buy_tax"]:
                buy_tax = float(scan[token_address]["buy_tax"]) * 100
                sell_tax = float(scan[token_address]["sell_tax"]) * 100
                if sell_tax > 5 or buy_tax > 5:
                    tax = f"⚠️ Tax: {int(buy_tax)}/{int(sell_tax)}"
                else:
                    tax = f"✅️ Tax: {int(buy_tax)}/{int(sell_tax)}"
            else:
                tax = f"❓ Tax - Unknown"

            if "holders" in scan[token_address]:
                top_holders = scan[token_address].get("holders", [])
                for holder in top_holders:
                    if holder.get("is_contract", 0) == 0 and holder.get("address").lower() != "0x000000000000000000000000000000000000dead":
                        top_holder = holder.get("percent")
                        break
                    else:
                        top_percent = "❓ Top Holder Unknown"

                top_holder_str = float(top_holder)
                formatted_top_percent = "{:.1f}".format(float(top_holder_str) * 100)
                if top_holder_str >= 0.05:
                    top_percent = f'⚠️ Top Holder Holds {formatted_top_percent}% of Supply'
                else:
                    top_percent = f'✅️ Top Holder Holds {formatted_top_percent}% of Supply'
            else:
                top_percent = "❓ Top Holder - Unknown"

            if "owner_address" in scan[token_address]:
                if scan[token_address]["owner_address"] == "0x0000000000000000000000000000000000000000":
                    renounced = "✅ Contract Renounced"
                else:
                    renounced = "⚠️ Contract Not Renounced"

            if "is_mintable" in scan[token_address]:
                if scan[token_address]["is_mintable"] == "1":
                    mint = "⚠️ Mintable"
                else:
                    mint = "✅️ Not Mintable"
            else:
                mint = "❓ Mintable - Unknown"

            if "is_honeypot" in scan[token_address]:
                if scan[token_address]["is_honeypot"] == "1":
                    honey_pot = "❌ Honey Pot"
                else:
                    honey_pot = "✅️ Not Honey Pot"
            else:
                honey_pot = "❓ Honey Pot - Unknown"

            if "is_blacklisted" in scan[token_address]:
                if scan[token_address]["is_blacklisted"] == "1":
                    blacklist = "⚠️ Has Blacklist Functions"
                else:
                    blacklist = "✅️ No Blacklist Functions"
            else:
                blacklist = "❓ Blacklist Functions - Unknown"

            if "cannot_sell_all" in scan[token_address]:
                if scan[token_address]["cannot_sell_all"] == "1":
                    sellable = "❌ Not Sellable"
                else:
                    sellable = "✅️ Sellable"
            else:
                sellable = "❓ Sellable - Unknown"

            if "owner_percent" in scan[token_address]:
                if renounced == "✅ Contract Renounced":
                    owner_percent = f'✅️ Owner Holds 0.0% of Supply'
                else:
                    owner_percent_str = float(scan[token_address]["owner_percent"])
                    formatted_owner_percent = "{:.1f}".format(owner_percent_str * 100)
                    if owner_percent_str >= 0.05:
                        owner_percent = f'⚠️ Owner Holds {formatted_owner_percent}% of Supply'
                    else:
                        owner_percent = f'✅️ Owner Holds {formatted_owner_percent}% of Supply'
            else:
                owner_percent = "❓ Tokens Held By Owner - Unknown"

            try:
                pair = defined.get_pair(token_address, chain)
                if not pair and "dex" in scan[token_address] and scan[token_address]["dex"]:
                    pair = scan[token_address]["dex"][0]["pair"]
            except Exception:
                pair = ca.DEAD
        else:
            renounced = "❓ Renounced - Unknown"
            tax = "❓ Tax - Unknown"
            mint = "❓ Mintable - Unknown"
            honey_pot = "❓ Honey Pot - Unknown"
            blacklist = "❓ Blacklist Functions - Unknown"
            sellable = "❓ Sellable - Unknown"
            owner_percent = "❓ Tokens Held By Owner - Unknown"
            top_percent = "❓ Top Holder - Unknown"
            

        chain_name = chains.active_chains()[chain].name
        chain_dext = chains.active_chains()[chain].dext
        try:
            if etherscan.get_verified(token_address, chain):
                verified = "✅️ Contract Verified"
            else:
                verified = "❌ Contract Unverified"
        except Exception:
            verified = "❓ Contract Verification - Unknown"
        status = f"{verified}\n{renounced}\n{tax}\n{sellable}\n{mint}\n{honey_pot}\n{blacklist}\n{owner_percent}\n{top_percent}"
        info = dextools.get_token_info(search, chain)
        holders = info["holders"] or "N/A"
        mcap = info["mcap"] or "N/A"
        dex = dextools.get_dex(pair, chain)
        price, price_change = dextools.get_price(search, chain)
        if price:
            price = f"${price}"
        else:
            price = "N/A"
        volume = defined.get_volume(pair, chain) or "N/A"
        liquidity = dextools.get_liquidity(pair, chain)['total'] or "N/A"
        await update.message.reply_text(
            f"*{token_name} {token_symbol}* - {chain_name}\n"
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

