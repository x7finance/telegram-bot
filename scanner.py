from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

import asyncio, os, requests, random, sentry_sdk, traceback
from PIL import Image, ImageDraw, ImageFont

from constants import abis, ca, urls, chains
from hooks import api, tools
import media

defined = api.Defined()
dextools = api.Dextools()
etherscan = api.Etherscan()

channels = [
    (urls.TG_MAIN_CHANNEL_ID, None, urls.TG_ALERTS),
    (urls.TG_MAIN_CHANNEL_ID, 892, urls.TG_ALERTS),
    (urls.TG_ALERTS_CHANNEL_ID, None, urls.TG_PORTAL)
]

nft_names = {
    "ECO": "Ecosystem Maxi",
    "LIQ": "Liquidity Maxi",
    "DEX": "DEX Maxi",
    "BORROW": "Borrowing Maxi",
    "MAGISTER": "Magister",
}


async def error(context):
    sentry_sdk.capture_exception(
        Exception(
            f"Scanner Error: {context} | Traceback: {traceback.format_exc()}"
        )
    )


async def log_loop(chain, poll_interval):
    try:
        w3 = chains.active_chains()[chain].w3
        factory = w3.eth.contract(address=ca.FACTORY(chain), abi=abis.read("factory"))
        pair_filter = factory.events.PairCreated.create_filter(fromBlock="latest")

        loan_filters = {}
        chain_addresses = ca.ILL_ADDRESSES.get(chain, {})

        for ill_key, ill_address in chain_addresses.items():
            contract = w3.eth.contract(address=ill_address, abi=etherscan.get_abi(ill_address, chain))
            loan_filters[ill_key] = contract.events.LoanOriginated.create_filter(fromBlock="latest")

        nft_contracts = ca.NFTS(chain)
        nft_filters = {}
        for contract_type, nft_address in nft_contracts.items():
            contract = w3.eth.contract(address=w3.to_checksum_address(nft_address), abi=etherscan.get_abi(nft_address, chain))
            nft_filters[contract_type] = contract.events.Transfer.create_filter(fromBlock="latest")

        
        while True:
            try:
                for PairCreated in pair_filter.get_new_entries():
                    await pair_alert(PairCreated, chain)

                for ill_key, loan_filter in loan_filters.items():
                    for LoanOriginated in loan_filter.get_new_entries():
                        await loan_alert(LoanOriginated, chain)

                for contract_type, nft_filter in nft_filters.items():
                    for event in nft_filter.get_new_entries():
                        if event["args"]["from"] == "0x0000000000000000000000000000000000000000":
                            await nft_mint_alert(event, contract_type, chain)

                await asyncio.sleep(poll_interval)

            except Exception as inner_e:
                await error(f"Error while processing events for chain {chain}: {inner_e}")
                await asyncio.sleep(10)

    except Exception as outer_e:
        await error(f"Error initializing log loop for chain {chain}: {outer_e}")


async def loan_alert(event, chain):
    try:
        chain_info, error_message = chains.get_info(chain)
        loan_id = event["args"]["loanID"]
        contract_address = event["address"]
        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(contract_address),
            abi=etherscan.get_abi(contract_address, chain)
        )

        liability = contract.functions.getRemainingLiability(int(loan_id)).call() / 10**18
        schedule1 = contract.functions.getPremiumPaymentSchedule(int(loan_id)).call()
        schedule2 = contract.functions.getPrincipalPaymentSchedule(int(loan_id)).call()
        schedule_str = tools.format_schedule(schedule1, schedule2, chain_info.native.upper())

        index, token_by_id = 0, None
        while True:
            try:
                token_id = contract.functions.tokenByIndex(index).call()
                if token_id == int(loan_id):
                    token_by_id = index
                    break
                index += 1
            except Exception:
                break

        ill_number = tools.get_ill_number(contract_address)

        im1 = Image.open(random.choice(media.BLACKHOLE)).convert("RGBA")
        im2 = Image.open(chain_info.logo).convert("RGBA")
        im1.paste(im2, (700, 20), im2)

        message = (
            f"{liability} {chain_info.native.upper()}\n\n"
            f"Payment Schedule UTC:\n{schedule_str}"
        )

        i1 = ImageDraw.Draw(im1)
        i1.text(
            (26, 30),
            f"New Loan Originated ({chain_info.name.upper()})\n\n{message}",
            font=ImageFont.truetype(media.FONT, 26),
            fill=(255, 255, 255)
        )
        image_path = r"media/blackhole.png"
        im1.save(image_path)

        caption = (
            f"*New Loan Originated ({chain_info.name.upper()})*\n\n"
            f"{message}\n\n"
        )

        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="View Loan",
                        url=f"{urls.XCHANGE}lending/{chain_info.name.lower()}/{ill_number}/{token_by_id}"
                    )
                ]
            ]
        )

        for channel, thread_id, link in channels:
            with open(image_path, "rb") as photo:
                send_params = {
                    "chat_id": channel,
                    "photo": photo,
                    "caption": f"{caption}{tools.escape_markdown(link)}",
                    "parse_mode": "Markdown",
                    "reply_markup": button
                }

                if thread_id is not None:
                    send_params["message_thread_id"] = thread_id

                await application.bot.send_photo(**send_params)

    except Exception as e:
        await error(f"Error in loan alert for chain {chain}: {e}")


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
            scan = tools.get_scan(token_address, chain)
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
        if liq_data["total"] == "N/A":
            liq = "Unknown"

        im1 = Image.open(random.choice(media.BLACKHOLE)).convert("RGBA")
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
            f"New Pair Created ({chain_info.name.upper()})\n\n{message}",
            font=ImageFont.truetype(media.FONT, 26),
            fill=(255, 255, 255)
        )
        image_path = r"media/blackhole.png"
        im1.save(image_path)

        caption = (
            f"*New Pair Created ({chain_info.name.upper()})*\n\n"
            f"{message}\n\n"
            f"Token Address:\n`{token_address}`\n\n"
        )

        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Buy On Xchange", url=f"{urls.XCHANGE_BUY(chain_info.id, token_address)}")],
                [InlineKeyboardButton("Chart", url=f"{urls.DEX_TOOLS(chain_info.dext)}{event['args']['pair']}")]
            ]
        )

        for channel, thread_id, link in channels:
            with open(image_path, "rb") as photo:
                send_params = {
                    "chat_id": channel,
                    "photo": photo,
                    "caption": f"{caption}{tools.escape_markdown(link)}",
                    "parse_mode": "Markdown",
                    "reply_markup": buttons
                }

                if thread_id is not None:
                    send_params["message_thread_id"] = thread_id

                await application.bot.send_photo(**send_params)
    except Exception as e:
        await error(f"Error in pair alert for chain {chain}: {e}")


async def nft_mint_alert(event, contract_type, chain):
    try:
        chain_info, error_message = chains.get_info(chain)
        to_address = event["args"]["to"]
        token_id = event["args"]["tokenId"]
        transaction_hash = event["transactionHash"].hex()
        transaction = chain_info.w3.eth.get_transaction(transaction_hash)
        value_wei = transaction["value"]
        value = chain_info.w3.from_wei(value_wei, 'ether')

        contract_name = nft_names.get(contract_type, contract_type)

        message = (
            f"{contract_name} ({token_id})\n"
            f"Mint Price: {value} {chain_info.native.upper()}\n"
        )

        im1 = Image.open(random.choice(media.BLACKHOLE)).convert("RGBA")
        im2 = Image.open(chain_info.logo).convert("RGBA")
        im1.paste(im2, (700, 20), im2)

        i1 = ImageDraw.Draw(im1)
        i1.text(
            (26, 30),
            f"New NFT Mint ({chain_info.name.upper()})\n\n{message}",
            font=ImageFont.truetype(media.FONT, 26),
            fill=(255, 255, 255),
        )
        image_path = r"media/blackhole.png"
        im1.save(image_path)

        caption = (
            f"*New NFT Mint ({chain_info.name.upper()})*\n\n"
            f"{contract_name} ({token_id})\n"
            f"Minter: `{to_address}`\n"
            f"Mint Price: {value} {chain_info.native.upper()}\n"
        )

        for channel, thread_id, link in channels:
            with open(image_path, "rb") as photo:
                send_params = {
                    "chat_id": channel,
                    "photo": photo,
                    "caption": f"{caption}\n{tools.escape_markdown(link)}",
                    "parse_mode": "Markdown"
                }

                if thread_id:
                    send_params["message_thread_id"] = thread_id

                await application.bot.send_photo(**send_params)

    except Exception as e:
        await error(f"Error in NFT mint alert for chain {chain}: {e}")


async def main():
    while True:
    
        tasks = []
        for chain, chain_info in chains.active_chains().items():
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
