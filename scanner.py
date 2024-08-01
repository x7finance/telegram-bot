from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

import asyncio, os
from web3 import Web3
from PIL import Image, ImageDraw, ImageFont
import requests, random

from constants import ca, urls, chains
from hooks import api
import media

defined = api.Defined()
dextools = api.Dextools()
chainscan = api.ChainScan()


async def log_loop(chain, poll_interval):
    web3 = Web3(Web3.HTTPProvider(chains.CHAINS[chain].w3))
    factory = web3.eth.contract(address=ca.FACTORY(chain), abi=chainscan.get_abi(ca.FACTORY(chain), chain))
    pair_filter = factory.events.PairCreated.create_filter(fromBlock="latest")

    while True:
        try:

            for PairCreated in pair_filter.get_new_entries():
                await alert(PairCreated, chain)
            await asyncio.sleep(poll_interval)

        except Exception as e:
            print(f"Error occurred on chain {chain}: {e}. Restarting")
            break

    await log_loop(chain, poll_interval)


async def alert(event, chain):
    chain_info = chains.CHAINS.get(chain)
    if chain_info:
        logo = chain_info.logo
        paired_token = ca.WETH(chain)
        dext = chain_info.dext
        chain_name = chain_info.name
        chain_id = chain_info.id

    token_0_info = dextools.get_token_name(event["args"]["token0"], chain)
    token_0_name = token_0_info["name"]
    token_0_symbol = token_0_info["symbol"]

    token_1_info = dextools.get_token_name(event["args"]["token1"], chain)
    token_1_name = token_1_info["name"]
    token_1_symbol = token_1_info["symbol"]

    if event["args"]["token0"] == paired_token:
        token_address = event["args"]["token1"]
        token_name = token_1_name
        token_symbol = token_1_symbol
    else:
        token_address = event["args"]["token0"]
        token_name = token_0_name
        token_symbol = token_0_symbol
    
    if chainscan.get_verified(token_address, chain):
        verified = "Contract Verified"
    else:
        verified = "Contract Unverified"
    status = ""
    renounced = ""
    tax = ""
    try:
        scan = api.get_scan(token_address, chain)
        token_address_str  = str(token_address).lower()
        if "owner_address" in scan[token_address_str]:
            if scan[token_address_str]["owner_address"] == "0x0000000000000000000000000000000000000000":
                renounced = "Contract Renounced"
            else:
                renounced = "Contract Not Renounced"
        if scan[token_address_str]["is_in_dex"] == "1":
            try:
                if (
                    scan[token_address_str]["sell_tax"] == "1"
                    or scan[token_address_str]["buy_tax"] == "1"
                ):
                    return
                buy_tax_raw = (
                    float(scan[token_address_str]["buy_tax"]) * 100
                )
                sell_tax_raw = (
                    float(scan[token_address_str]["sell_tax"]) * 100
                )
                buy_tax = int(buy_tax_raw)
                sell_tax = int(sell_tax_raw)
                if sell_tax > 10 or buy_tax > 10:
                    tax = f"Tax: {buy_tax}/{sell_tax}"
                else:
                    tax = f"Tax: {buy_tax}/{sell_tax}"
            except Exception:
                tax = f"Tax: Unavailable"
        else:
            tax = f"Tax: Unavailable"
        status = f"{verified}\n{tax}\n{renounced}"
    except Exception:
        status = "Scan Unavailable"
    
    liq_data = dextools.get_liquidity(event['args']['pair'], chain)
    liq = liq_data["total"]
    if liq == "0":
        liq = "Unavailable"

    im1 = Image.open((random.choice(media.BLACKHOLE))).convert("RGBA")
    try:
        image_url = defined.get_token_image(token_address, chain)
        im2 = Image.open(requests.get(image_url, stream=True).raw).convert("RGBA")
    except:
        im2 = Image.open(logo).convert("RGBA")
    
    im1.paste(im2, (700, 20), im2)
    i1 = ImageDraw.Draw(im1)
    i1.text(
        (26, 30),
            f"New Pair Created ({chain_name.upper()})\n\n"
            f"{token_name} ({token_0_symbol}/{token_1_symbol})\n\n"
            f"Liquidity: {liq}\n\n"
            f"{status}\n",
        font = ImageFont.truetype(media.FONT, 26),
        fill = (255, 255, 255),
    )
    im1.save(r"media/blackhole.png")
    
    channels = [os.getenv("ALERTS_TELEGRAM_CHANNEL_ID"), 
                os.getenv(f"MAIN_TELEGRAM_CHANNEL_ID"), 
                os.getenv(f"{chain.upper()}_TELEGRAM_CHANNEL_ID")]
    
    for channel in channels:
        if channel:  
            await application.bot.send_photo(
                channel,
                photo=open(r"media/blackhole.png", "rb"),
                caption=
                    f"*New Pair Created ({chain_name.upper()})*\n\n"
                    f"{token_name} ({token_0_symbol}/{token_1_symbol})\n\n"
                    f"Token Address:\n`{token_address}`\n\n"
                    f"Liquidity: {liq}\n\n"
                    f"{status}\n",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"Buy On Xchange",
                                url=f"{urls.XCHANGE_BUY(chain_id, token_address)}",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="Chart",
                                url=f"{urls.dex_tools(dext)}{event['args']['pair']}",
                            )
                        ],
                    ]
                ),
            )
        

async def main():
    while True:
    
        tasks = []
        for chain, chain_info in chains.CHAINS.items():
            if chain_info.live:
                task = log_loop(chain, 5)
                tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    application = (
        ApplicationBuilder()
        .token(os.getenv("TELEGRAM_SCANNER_BOT_TOKEN"))
        .connection_pool_size(512)
        .build()
    )
    asyncio.run(main())
