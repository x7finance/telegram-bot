from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

import asyncio, os, requests, random, sentry_sdk, traceback
from PIL import Image, ImageDraw, ImageFont

from constants import abis, ca, urls, chains
from hooks import api
import media

defined = api.Defined()
dextools = api.Dextools()
etherscan = api.Etherscan()


async def error(context):
    sentry_sdk.capture_exception(
        Exception(
            f"Scanner Error: {context} | Traceback: {traceback.format_exc()}"
        )
    )


async def log_loop(chain, poll_interval):
    w3 = chains.CHAINS[chain].w3
    factory = w3.eth.contract(address=ca.FACTORY(chain), abi=abis.read("factory"))
    pair_filter = factory.events.PairCreated.create_filter(fromBlock="latest")

    loan_filters = {}
    chain_addresses = ca.ILL_ADDRESSES.get(chain, {})

    for ill_key, ill_address in chain_addresses.items():
        contract = w3.eth.contract(address=ill_address, abi=etherscan.get_abi(ill_address, chain))
        loan_filters[ill_key] = contract.events.LoanOriginated.create_filter(fromBlock="latest")
    
    while True:
        try:
        
            for PairCreated in pair_filter.get_new_entries():
                await pair_alert(PairCreated, chain)

            for ill_key, loan_filter in loan_filters.items():
                for LoanOriginated in loan_filter.get_new_entries():
                    await loan_alert(LoanOriginated, chain)

            await asyncio.sleep(poll_interval)

        except Exception as e:
            await error(Exception(f"Error in log loop for chain {chain}: {e}"))
            await asyncio.sleep(10)


async def loan_alert(event, chain):
    try:
        chain_info, error_message = chains.get_info(chain)
        loan_id = event["args"]["loanID"]
        contract_address = event["address"]
        contract = chain_info.w3.eth.contract(address=chain_info.w3.to_checksum_address(contract_address), abi=etherscan.get_abi(contract_address, chain))

        liability = contract.functions.getRemainingLiability(int(loan_id)).call() / 10**18
        schedule1 = contract.functions.getPremiumPaymentSchedule(int(loan_id)).call()
        schedule2 = contract.functions.getPrincipalPaymentSchedule(int(loan_id)).call()
        schedule_str = api.format_schedule(schedule1, schedule2, chain_info.native.upper())

        index = 0
        token_by_id = None
        while True:
            try:
                token_id = contract.functions.tokenByIndex(index).call()
                if token_id == int(loan_id):
                    token_by_id = index
                    break
                index += 1
            except Exception:
                break
    
        ill_number = api.get_ill_number(contract_address)

        im1 = Image.open((random.choice(media.BLACKHOLE))).convert("RGBA")
        im2 = Image.open(chain_info.logo).convert("RGBA")
        im1.paste(im2, (700, 20), im2)

        message = (
            f"{liability} {chain_info.native.upper()}\n\n"
            f"Payment Schedule UTC:\n{schedule_str}"
        )

        i1 = ImageDraw.Draw(im1)
        i1.text(
            (26, 30),
            f"New Loan Originated ({chain_info.name.upper()})\n\n"
            f"{message}",
            font = ImageFont.truetype(media.FONT, 26),
            fill = (255, 255, 255),
        )
        im1.save(r"media/blackhole.png")

        channels = [
            urls.TG_MAIN_CHANNEL_ID, 
            urls.TG_ALERTS_CHANNEL_ID
        ]

        for channel in channels:
            if channel:  

                await application.bot.send_photo(
                    channel,
                    photo=open(r"media/blackhole.png", "rb"),
                    caption=
                        f"*New Loan Originated ({chain_info.name.upper()})*\n\n"
                        f"{message}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text=f"View Loan",
                                    url=f"{urls.XCHANGE}lending/{chain_info.name.lower()}/{ill_number}/{token_by_id}",
                                )
                            ]
                        ]
                    ),
                )  
    except Exception as e:
        await error(Exception(f"Error in loan alert for chain {chain}: {e}"))


async def pair_alert(event, chain):
    try:
        chain_info, error_message = chains.get_info(chain)
        paired_token = ca.WETH(chain)

        token_0_info = dextools.get_token_name(event["args"]["token0"], chain)
        token_0_name = token_0_info["name"]
        token_0_symbol = token_0_info["symbol"]

        token_1_info = dextools.get_token_name(event["args"]["token1"], chain)
        token_1_name = token_1_info["name"]
        token_1_symbol = token_1_info["symbol"]

        if event["args"]["token0"] == paired_token:
            token_address = event["args"]["token1"]
            token_name = token_1_name
        else:
            token_address = event["args"]["token0"]
            token_name = token_0_name
        try:
            if etherscan.get_verified(token_address, chain):
                verified = "Contract Verified"
            else:
                verified = "Contract Unverified"
        except Exception:
            verified = "Contract Verification Unknown"

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
                    buy_tax = (
                        float(scan[token_address_str]["buy_tax"]) * 100
                    )
                    sell_tax = (
                        float(scan[token_address_str]["sell_tax"]) * 100
                    )
                    tax = f"Tax: {int(buy_tax)}/{int(sell_tax)}"
                except Exception:
                    tax = f"Tax: Unavailable"
            else:
                tax = f"Tax: Unavailable"
            status = f"{verified}\n{tax}\n{renounced}"
        except Exception:
            status = "Scan Unavailable"
        
        liq_data = dextools.get_liquidity(event['args']['pair'], chain)
        liq = liq_data["total"]
        if liq == "$0":
            liq = "Unknown"

        im1 = Image.open((random.choice(media.BLACKHOLE))).convert("RGBA")
        try:
            image_url = defined.get_token_image(token_address, chain)
            im2 = Image.open(requests.get(image_url, stream=True).raw).convert("RGBA")
        except:
            im2 = Image.open(chain_info.logo).convert("RGBA")
        
        im1.paste(im2, (700, 20), im2)

        message = (
            f"{token_name} ({token_0_symbol}/{token_1_symbol})\n\n"
            f"Liquidity: {liq}\n"
            f"{status}"
        )

        i1 = ImageDraw.Draw(im1)
        i1.text(
            (26, 30),
            f"New Pair Created ({chain_info.name.upper()})\n\n"
            f"{message}",
            font = ImageFont.truetype(media.FONT, 26),
            fill = (255, 255, 255),
        )
        im1.save(r"media/blackhole.png")

        channels = [
            urls.TG_MAIN_CHANNEL_ID, 
            urls.TG_ALERTS_CHANNEL_ID
        ]

        for channel in channels:
            if channel:  
                await application.bot.send_photo(
                    channel,
                    photo=open(r"media/blackhole.png", "rb"),
                    caption=
                        f"*New Pair Created ({chain_info.name.upper()})*\n\n"
                        f"{message}\n\n"
                        f"Token Address:\n`{token_address}`",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Buy On Xchange",
                                    url=f"{urls.XCHANGE_BUY(chain_info.id, token_address)}",
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    text="Chart",
                                    url=f"{urls.DEX_TOOLS(chain_info.dext)}{event['args']['pair']}",
                                )
                            ],
                        ]
                    ),
                )
    except Exception as e:
        await error(Exception(f"Error in pair alert for chain {chain}: {e}"))
        

async def main():
    while True:
    
        tasks = []
        for chain, chain_info in chains.CHAINS.items():
            if chain_info.live:
                task = log_loop(chain, 20)
                tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    application = (
        ApplicationBuilder()
        .token(os.getenv("TELEGRAM_SCANNER_BOT_TOKEN"))
        .build()
    )
    asyncio.run(main())
