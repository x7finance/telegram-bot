from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes

import asyncio
import io

import os
import random
import requests
import sentry_sdk
import textwrap
import traceback
from PIL import Image, ImageDraw, ImageFont

from constants.bot import urls
from constants.protocol import addresses, abis, chains
from media import fonts, blackhole
from utils import tools
from services import get_defined, get_dextools, get_etherscan

defined = get_defined()
dextools = get_dextools()
etherscan = get_etherscan()

sentry_sdk.init(dsn=os.getenv("SCANNER_SENTRY_DSN"), traces_sample_rate=1.0)

FONT = fonts.BARTOMES
POLL_INTERVAL = 60


async def error(context):
    sentry_sdk.capture_exception(
        Exception(
            f"Scanner Error: {context} | Traceback: {traceback.format_exc()}"
        )
    )


async def log_loop(
    chain, context: ContextTypes.DEFAULT_TYPE, poll_interval=POLL_INTERVAL
):
    while True:
        try:
            w3 = chains.MAINNETS[chain].w3

            factory = w3.eth.contract(
                address=addresses.factory(chain), abi=abis.read("factory")
            )

            xchange_create = w3.eth.contract(
                address=addresses.xchange_create(chain),
                abi=abis.read("xchangecreate"),
            )

            ill_contracts = {
                ill_key: w3.eth.contract(
                    address=ill_address, abi=abis.read("ill005")
                )
                for ill_key, ill_address in addresses.ill_addresses(
                    chain
                ).items()
            }

            latest_block = context.bot_data.get(
                f"last_block_{chain}", w3.eth.block_number
            )

            pair_created_topic = tools.get_event_topic(
                "factory", "PairCreated", chain
            )
            token_deployed_topic = tools.get_event_topic(
                "xchangecreate", "TokenDeployed", chain
            )
            loan_originated_topic = tools.get_event_topic(
                "ill005", "LoanOriginated", chain
            )

            while True:
                try:
                    current_block = w3.eth.block_number
                    from_block = latest_block + 1

                    pair_logs = w3.eth.get_logs(
                        {
                            "fromBlock": from_block,
                            "toBlock": current_block,
                            "address": factory.address,
                            "topics": [pair_created_topic],
                        }
                    )

                    token_logs = w3.eth.get_logs(
                        {
                            "fromBlock": from_block,
                            "toBlock": current_block,
                            "address": xchange_create.address,
                            "topics": [token_deployed_topic],
                        }
                    )

                    loan_logs = []
                    for ill_contract in ill_contracts.values():
                        logs = w3.eth.get_logs(
                            {
                                "fromBlock": from_block,
                                "toBlock": current_block,
                                "address": ill_contract.address,
                                "topics": [loan_originated_topic],
                            }
                        )
                        loan_logs.extend(logs)

                    for log in pair_logs:
                        try:
                            decoded_event = (
                                factory.events.PairCreated().process_log(log)
                            )
                            await pair_alert(decoded_event, chain)
                        except Exception as e:
                            await error(
                                f"Error decoding PairCreated: {str(e)}"
                            )

                    for log in token_logs:
                        try:
                            decoded_event = xchange_create.events.TokenDeployed().process_log(
                                log
                            )
                            await token_alert(decoded_event, chain)
                        except Exception as e:
                            await error(
                                f"Error decoding TokenDeployed: {str(e)}"
                            )

                    for log in loan_logs:
                        try:
                            contract_address = log["address"]
                            ill_contract = ill_contracts.get(contract_address)
                            if ill_contract:
                                decoded_event = ill_contract.events.LoanOriginated().process_log(
                                    log
                                )
                                await loan_alert(decoded_event, chain)
                        except Exception as e:
                            await error(
                                f"Error decoding LoanOriginated: {str(e)}"
                            )

                    context.bot_data[f"last_block_{chain}"] = current_block
                    await asyncio.sleep(poll_interval)

                except Exception as e:
                    await error(
                        f"Polling error on {chain}: {str(e)}. Retrying in {poll_interval} seconds..."
                    )
                    await asyncio.sleep(poll_interval)

        except Exception as e:
            await error(
                f"Web3 connection error on {chain}: {str(e)}. Retrying in {poll_interval} seconds..."
            )
            await asyncio.sleep(poll_interval)


async def loan_alert(event, chain):
    chain_info, _ = chains.get_info(chain)
    loan_id = event["args"]["loanID"]
    ill_address = event["address"]
    ill_contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(ill_address),
        abi=abis.read("ill005"),
    )

    liability = (
        ill_contract.functions.getRemainingLiability(int(loan_id)).call()
        / 10**18
    )
    schedule1 = ill_contract.functions.getPremiumPaymentSchedule(
        int(loan_id)
    ).call()
    schedule2 = ill_contract.functions.getPrincipalPaymentSchedule(
        int(loan_id)
    ).call()
    schedule = tools.format_schedule(
        schedule1, schedule2, chain_info.native.upper(), isComplete=False
    )

    index, token_by_id = 0, None
    while True:
        try:
            token_id = ill_contract.functions.tokenByIndex(index).call()
            if token_id == int(loan_id):
                token_by_id = index
                break
            index += 1
        except Exception:
            break

    pool_contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(
            addresses.lending_pool(chain)
        ),
        abi=abis.read("lendingpool"),
    )

    token = pool_contract.functions.loanToken(int(loan_id)).call()
    pair = pool_contract.functions.loanPair(int(loan_id)).call()
    token_info = dextools.get_token_name(token, chain)
    token_name = token_info["name"]
    token_symbol = token_info["symbol"]

    ill_number = tools.get_ill_number(ill_address)

    im1 = Image.open(random.choice(blackhole.RANDOM)).convert("RGBA")
    try:
        image_url = defined.get_token_image(token, chain)
        im2 = Image.open(requests.get(image_url, stream=True).raw).convert(
            "RGBA"
        )
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
        font=ImageFont.truetype(FONT, 26),
        fill=(255, 255, 255),
    )
    image_buffer = io.BytesIO()
    im1.save(image_buffer, format="JPEG")
    image_buffer.seek(0)

    caption = (
        f"*New Loan Originated ({chain_info.name.upper()})*\n\n{message}\n\n"
    )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="View Loan",
                    url=f"{urls.XCHANGE}lending/{chain_info.name.lower()}/{ill_number}/{token_by_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Buy", url=urls.xchange_buy_link(chain_info.id, token)
                )
            ],
            [
                InlineKeyboardButton(
                    text="Chart",
                    url=urls.dex_tools_link(chain_info.dext, pair),
                )
            ],
        ]
    )

    for channel, thread_id, link in urls.TG_ALERTS_CHANNELS:
        send_params = {
            "chat_id": channel,
            "photo": image_buffer,
            "caption": f"{caption}{tools.escape_markdown(link)}",
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }

        if thread_id is not None:
            send_params["message_thread_id"] = thread_id

        await application.bot.send_photo(**send_params)

    image_buffer.close()


async def pair_alert(event, chain):
    chain_info, _ = chains.get_info(chain)
    paired_token = addresses.weth(chain)

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

        buy_tax_data = data.get("buyTax") or {}
        sell_tax_data = data.get("sellTax") or {}
        buy_tax = (buy_tax_data.get("max") or 0) * 100
        sell_tax = (sell_tax_data.get("max") or 0) * 100
        if buy_tax > 5 or sell_tax > 5:
            tax = f"⚠️ Tax: {int(buy_tax)}/{int(sell_tax)}"
        else:
            tax = f"✅️ Tax: {int(buy_tax)}/{int(sell_tax)}"

        is_open_source = data.get("isOpenSource", "no")
        open_source = (
            "✅ Contract Verified"
            if is_open_source == "yes"
            else "⚠️ Contract Not Verified"
        )

        is_renounced = data.get("isContractRenounced", "no")
        renounced = (
            "✅ Contract Renounced"
            if is_renounced == "yes"
            else "⚠️ Contract Not Renounced"
        )

    else:
        open_source = "❓ Contract Verification - Unknown"
        tax = "❓ Tax - Unknown"
        renounced = "❓ Renounced - Unknown"

    status = f"{open_source}\n{tax}\n{renounced}"

    im1 = Image.open(random.choice(blackhole.RANDOM)).convert("RGBA")
    try:
        image_url = defined.get_token_image(token_address, chain)
        im2 = Image.open(requests.get(image_url, stream=True).raw).convert(
            "RGBA"
        )
    except Exception:
        im2 = Image.open(chain_info.logo).convert("RGBA")

    im1.paste(im2, (700, 20), im2)

    message = f"{token_name} ({token_0_symbol}/{token_1_symbol})\n\n{status}"

    i1 = ImageDraw.Draw(im1)
    i1.text(
        (26, 30),
        f"New Pair Created ({chain_info.name.upper()})\n\n{message}",
        font=ImageFont.truetype(FONT, 26),
        fill=(255, 255, 255),
    )
    image_buffer = io.BytesIO()
    im1.save(image_buffer, format="JPEG")
    image_buffer.seek(0)

    caption = (
        f"*New Pair Created ({chain_info.name.upper()})*\n\n"
        f"{message}\n\n"
        f"Token Address:\n`{token_address}`\n\n"
    )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Buy",
                    url=urls.xchange_buy_link(chain_info.id, token_address),
                )
            ],
            [
                InlineKeyboardButton(
                    "Chart",
                    url=urls.dex_tools_link(
                        chain_info.dext, event["args"]["pair"]
                    ),
                )
            ],
        ]
    )

    for channel, thread_id, link in urls.TG_ALERTS_CHANNELS:
        send_params = {
            "chat_id": channel,
            "photo": image_buffer,
            "caption": f"{caption}{tools.escape_markdown(link)}",
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }

        if thread_id is not None:
            send_params["message_thread_id"] = thread_id

        await application.bot.send_photo(**send_params)

    image_buffer.close()


async def token_alert(event, chain):
    chain_info, _ = chains.get_info(chain)

    args = event["args"]
    token_address = args["tokenAddress"]
    token_name = args["name"]
    token_symbol = args["symbol"]
    supply = args["supply"] / 10**18
    description = args["description"]
    token_uri = args["tokenURI"]
    twitter_link = args.get("twitterLink", None)
    telegram_link = args.get("telegramLink", None)
    website_link = args.get("websiteLink", None)
    buy_tax = args.get("buyTax", 0)
    sell_tax = args.get("sellTax", 0)

    im1 = Image.open(random.choice(blackhole.RANDOME)).convert("RGBA")
    try:
        im2 = Image.open(requests.get(token_uri, stream=True).raw).convert(
            "RGBA"
        )
    except Exception:
        im2 = Image.open(chain_info.logo).convert("RGBA")

    im1.paste(im2, (700, 20), im2)

    message = f"{token_name} ({token_symbol})\n\nSupply: {supply:,.0f}\nTax: {buy_tax}/{sell_tax}"

    i1 = ImageDraw.Draw(im1)
    i1.text(
        (26, 30),
        f"New Token Deployed ({chain_info.name.upper()})\n\n{message}",
        font=ImageFont.truetype(FONT, 26),
        fill=(255, 255, 255),
    )

    wrapped_text = textwrap.fill(description, width=50)
    y_offset = 300
    for line in wrapped_text.split("\n"):
        line_bbox = i1.textbbox(
            (0, 0), line, font=ImageFont.truetype(FONT, 26)
        )
        line_height = line_bbox[3] - line_bbox[1]
        i1.text(
            (26, y_offset),
            line,
            font=ImageFont.truetype(FONT, 26),
            fill=(255, 255, 255),
        )
        y_offset += line_height + 5

    image_buffer = io.BytesIO()
    im1.save(image_buffer, format="JPEG")
    image_buffer.seek(0)

    caption = (
        f"*New Token Deployed ({chain_info.name.upper()})*\n\n"
        f"{message}\n\n{description}\n\n"
        f"Token Address:\n`{token_address}`\n\n"
    )

    button_list = [
        [
            InlineKeyboardButton(
                text="Buy",
                url=urls.xchange_buy_link(chain_info.id, token_address),
            )
        ],
        [
            InlineKeyboardButton(
                text="Chart",
                url=urls.dex_tools_link(chain_info.dext, token_address),
            )
        ],
    ]

    if twitter_link:
        button_list.append(
            [
                InlineKeyboardButton(
                    text=f"{token_name} Twitter", url=twitter_link
                )
            ]
        )
    if telegram_link:
        button_list.append(
            [
                InlineKeyboardButton(
                    text=f"{token_name} Telegram", url=telegram_link
                )
            ]
        )
    if website_link:
        button_list.append(
            [
                InlineKeyboardButton(
                    text=f"{token_name} Website", url=website_link
                )
            ]
        )

    buttons = InlineKeyboardMarkup(button_list)
    for channel, thread_id, link in urls.TG_ALERTS_CHANNELS:
        send_params = {
            "chat_id": channel,
            "photo": image_buffer,
            "caption": f"{caption}{tools.escape_markdown(link)}",
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }

        if thread_id is not None:
            send_params["message_thread_id"] = thread_id

        await application.bot.send_photo(**send_params)

    image_buffer.close()


async def main():
    tasks = [
        asyncio.create_task(log_loop(chain, application))
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
