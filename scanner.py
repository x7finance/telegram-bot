from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

import asyncio, os, requests, random, sentry_sdk, traceback
from PIL import Image, ImageDraw, ImageFont
import textwrap

from constants import abis, ca, urls, chains
from hooks import api, tools
import media

sentry_sdk.init(
    dsn = os.getenv("SCANNER_SENTRY_DSN"),
    traces_sample_rate=1.0
)

defined = api.Defined()
dextools = api.Dextools()
etherscan = api.Etherscan()

channels = [
    (urls.TG_MAIN_CHANNEL_ID, None, urls.TG_ALERTS),
    (urls.TG_MAIN_CHANNEL_ID, 892, urls.TG_ALERTS),
    (urls.TG_ALERTS_CHANNEL_ID, None, urls.TG_PORTAL)
]

font = ImageFont.truetype(media.FONT, 26)

async def error(context):
    sentry_sdk.capture_exception(
        Exception(
            f"Scanner Error: {context} | Traceback: {traceback.format_exc()}"
        )
    )


async def log_loop(chain, poll_interval):
    while True:
        try:
            w3 = chains.MAINNETS[chain].w3
            factory = w3.eth.contract(address=ca.FACTORY(chain), abi=abis.read("factory"))
            xchange_create = w3.eth.contract(address=ca.XCHANGE_CREATE(chain), abi=etherscan.get_abi(ca.XCHANGE_CREATE(chain), chain))
            
            pair_filter = factory.events.PairCreated.create_filter(fromBlock="latest")
            token_filter = xchange_create.events.TokenDeployed.create_filter(fromBlock="latest")
            
            loan_filters = {}
            ill_addresses = ca.ILL_ADDRESSES.get(chain, {})

            for ill_key, ill_address in ill_addresses.items():
                contract = w3.eth.contract(address=ill_address, abi=etherscan.get_abi(ill_address, chain))
                loan_filters[ill_key] = contract.events.LoanOriginated.create_filter(fromBlock="latest")

            while True:
                try:
                    for PairCreated in pair_filter.get_new_entries():
                        await pair_alert(PairCreated, chain)

                    for TokenDeployed in token_filter.get_new_entries():
                        await token_alert(TokenDeployed, chain)

                    for ill_key, loan_filter in loan_filters.items():
                        for LoanOriginated in loan_filter.get_new_entries():
                            await loan_alert(LoanOriginated, chain)

                    await asyncio.sleep(poll_interval)

                except Exception as e:
                    await error(f"Error in inner loop for chain '{chain}': {str(e)}. Restarting loop.")
                    await asyncio.sleep(5)
                    break

        except Exception as e:
            await error(f"Error in log loop for chain '{chain}': {str(e)}. Retrying after 10 seconds.")
            await asyncio.sleep(10)


async def loan_alert(event, chain):
    chain_info, error_message = chains.get_info(chain)
    loan_id = event["args"]["loanID"]
    term_contract_address = event["address"]
    term_contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(term_contract_address),
        abi=etherscan.get_abi(term_contract_address, chain)
    )

    liability = term_contract.functions.getRemainingLiability(int(loan_id)).call() / 10**18
    schedule1 = term_contract.functions.getPremiumPaymentSchedule(int(loan_id)).call()
    schedule2 = term_contract.functions.getPrincipalPaymentSchedule(int(loan_id)).call()
    schedule = tools.format_schedule(schedule1, schedule2, chain_info.native.upper(), isComplete=False)

    index, token_by_id = 0, None
    while True:
        try:
            token_id = term_contract.functions.tokenByIndex(index).call()
            if token_id == int(loan_id):
                token_by_id = index
                break
            index += 1
        except Exception:
            break

    pool_contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(ca.LPOOL(chain)),
        abi=etherscan.get_abi(ca.LPOOL(chain), chain)
    )

    token = pool_contract.functions.loanToken(int(loan_id)).call()
    pair = pool_contract.functions.loanPair(int(loan_id)).call()
    token_info = dextools.get_token_name(token, chain)
    token_name = token_info["name"]
    token_symbol = token_info["symbol"]

    ill_number = tools.get_ill_number(term_contract_address)

    im1 = Image.open(random.choice(media.BLACKHOLE)).convert("RGBA")
    try:
        image_url = defined.get_token_image(token, chain)
        im2 = Image.open(requests.get(image_url, stream=True).raw).convert("RGBA")
    except Exception:
        im2 = Image.open(chain_info.logo).convert("RGBA")
        
    im1.paste(im2, (700, 20), im2)

    message = (
        f"{token_name} ({token_symbol})\n\n"
        f"{liability} {chain_info.native.upper()}\n\n"
        f"Loan ID: {loan_id}\n\n"
        f"Payment Schedule UTC:\n{schedule}"
    )

    i1 = ImageDraw.Draw(im1)
    i1.text(
        (26, 30),
        f"New Loan Originated ({chain_info.name.upper()})\n\n{message}",
        font=font,
        fill=(255, 255, 255)
    )
    image_path = r"media/blackhole.png"
    im1.save(image_path)

    caption = (
        f"*New Loan Originated ({chain_info.name.upper()})*\n\n"
        f"{message}\n\n"
    )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="View Loan",
                    url=f"{urls.XCHANGE}lending/{chain_info.name.lower()}/{ill_number}/{token_by_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Buy",
                    url=urls.XCHANGE_BUY(chain_info.id, token)
                )
            ],
            [
                InlineKeyboardButton(
                    text="Chart",
                    url=urls.DEX_TOOLS(chain_info.dext, pair)
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
                "reply_markup": buttons
            }

            if thread_id is not None:
                send_params["message_thread_id"] = thread_id

            await application.bot.send_photo(**send_params)


async def pair_alert(event, chain):
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


    token_data = dextools.get_audit(token_address, chain)
    if token_data.get("statusCode") == 200 and token_data.get("data"):
        data = token_data["data"]
        
        buy_tax_data = data.get("buyTax", {})
        sell_tax_data = data.get("sellTax", {})
        buy_tax = buy_tax_data.get("max", 0) * 100
        sell_tax = sell_tax_data.get("max", 0) * 100
        if buy_tax > 5 or sell_tax > 5:
            tax = f"⚠️ Tax: {int(buy_tax)}/{int(sell_tax)}"
        else:
            tax = f"✅️ Tax: {int(buy_tax)}/{int(sell_tax)}"

        is_open_source = data.get("isOpenSource", "no")
        open_source = "✅ Contract Verified" if is_open_source == "yes" else "⚠️ Contract Not Verified"

        is_renounced = data.get("isContractRenounced", "no")
        renounced = "✅ Contract Renounced" if is_renounced == "yes" else "⚠️ Contract Not Renounced"

    else:
        open_source = "❓ Contract Verification - Unknown"
        tax = "❓ Tax - Unknown"
        renounced = "❓ Renounced - Unknown"

    status = f"{open_source}\n{tax}\n{renounced}"

    im1 = Image.open(random.choice(media.BLACKHOLE)).convert("RGBA")
    try:
        image_url = defined.get_token_image(token_address, chain)
        im2 = Image.open(requests.get(image_url, stream=True).raw).convert("RGBA")
    except Exception:
        im2 = Image.open(chain_info.logo).convert("RGBA")
    
    im1.paste(im2, (700, 20), im2)

    message = (
        f"{token_name} ({token_0_symbol}/{token_1_symbol})\n\n"
        f"{status}"
    )

    i1 = ImageDraw.Draw(im1)
    i1.text(
        (26, 30),
        f"New Pair Created ({chain_info.name.upper()})\n\n{message}",
        font=font,
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
            [InlineKeyboardButton("Buy", url=urls.XCHANGE_BUY(chain_info.id, token_address))],
            [InlineKeyboardButton("Chart", url=urls.DEX_TOOLS(chain_info.dext, event['args']['pair']))]
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


async def token_alert(event, chain):
    chain_info, error_message = chains.get_info(chain)

    args = event["args"]
    token_address = args["tokenAddress"]
    token_name = args["name"]
    token_symbol = args["symbol"]
    supply = args["supply"] / 10 ** 18
    description = args["description"]
    token_uri = args["tokenURI"]
    twitter_link = args.get("twitterLink", None)
    telegram_link = args.get("telegramLink", None)
    website_link = args.get("websiteLink", None)
    buy_tax = args.get("buyTax", 0)
    sell_tax = args.get("sellTax", 0)

    im1 = Image.open(random.choice(media.BLACKHOLE)).convert("RGBA")
    try:
        im2 = Image.open(requests.get(token_uri, stream=True).raw).convert("RGBA")
    except Exception:
        im2 = Image.open(chain_info.logo).convert("RGBA")

    im1.paste(im2, (700, 20), im2)

    message = f"{token_name} ({token_symbol})\n\nSupply: {supply:,.0f}\nTax: {buy_tax}/{sell_tax}"

    i1 = ImageDraw.Draw(im1)
    i1.text(
        (26, 30),
        f"New Token Deployed ({chain_info.name.upper()})\n\n{message}",
        font=font,
        fill=(255, 255, 255)
    )

    wrapped_text = textwrap.fill(description, width=50)
    y_offset = 300
    for line in wrapped_text.split("\n"):
        line_bbox = i1.textbbox((0, 0), line, font=font)
        line_height = line_bbox[3] - line_bbox[1]
        i1.text((26, y_offset), line, font=font, fill=(255, 255, 255))
        y_offset += line_height + 5
    
    image_path = r"media/blackhole.png"
    im1.save(image_path)

    caption = (
        f"*New Token Deployed ({chain_info.name.upper()})*\n\n"
        f"{message}\n\n{description}\n\n"
        f"Token Address:\n`{token_address}`\n\n"
    )

    button_list = [
        [InlineKeyboardButton(text="Buy", url=urls.XCHANGE_BUY(chain_info.id, token_address))],
        [InlineKeyboardButton(text="Chart", url=urls.DEX_TOOLS(chain_info.dext, token_address))]
    ]

    if twitter_link:
        button_list.append([InlineKeyboardButton(text=f"{token_name} Twitter", url=twitter_link)])
    if telegram_link:
        button_list.append([InlineKeyboardButton(text=f"{token_name} Telegram", url=telegram_link)])
    if website_link:
        button_list.append([InlineKeyboardButton(text=f"{token_name} Website", url=website_link)])

    buttons = InlineKeyboardMarkup(button_list)
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


async def main():
    tasks = [
        log_loop(chain, 20) 
        for chain, chain_info in chains.MAINNETS.items() 
        if chain_info.live
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    application = (
        ApplicationBuilder()
        .token(os.getenv("TELEGRAM_SCANNER_BOT_TOKEN"))
        .build()
    )
    application.add_error_handler(lambda update, context: error(context.error))
    asyncio.run(main())