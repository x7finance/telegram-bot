from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

import asyncio
import io
import json
import os
import random
import requests
import sentry_sdk
import websockets
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from constants.bot import urls
from constants.protocol import addresses, abis, chains, tokens
from media import fonts, blackhole
from utils import tools
from services import get_defined, get_dextools

defined = get_defined()
dextools = get_dextools()

sentry_sdk.init(dsn=os.getenv("SENTRY_SCANNER_DSN"), traces_sample_rate=1.0)

TITLE_FONT = fonts.BARTOMES
FONT = fonts.FREE_MONO_BOLD
LIVE_LOAN = "005"


async def error(context):
    print(context)
    sentry_sdk.capture_exception(Exception(context))


async def create_image(token_image, title, message, chain_info):
    im1 = Image.open(random.choice(blackhole.RANDOM)).convert("RGBA")

    try:
        im2 = Image.open(requests.get(token_image, stream=True).raw).convert(
            "RGBA"
        )
    except Exception:
        im2 = Image.open(chain_info.logo).convert("RGBA")

    im1.paste(im2, (700, 20), im2)
    i1 = ImageDraw.Draw(im1)

    i1.text(
        xy=(26, 30),
        text=f"{title} ({chain_info.name.upper()})\n\n\n",
        font=ImageFont.truetype(TITLE_FONT, 30),
        fill=(255, 255, 255),
    )

    i1.text(
        xy=(26, 80),
        text=message,
        font=ImageFont.truetype(FONT, 26),
        fill=(255, 255, 255),
    )

    image_buffer = io.BytesIO()
    im1.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    return image_buffer


async def handle_log(log_data, chain, contracts):
    try:
        factory, ill_term, time_lock, xchange_create = contracts
        chain_info, _ = chains.get_info(chain)

        topics = log_data.get("topics", [])
        if not topics:
            return

        event_signature = topics[0]
        token_deployed = False

        if event_signature == xchange_create.events.TokenDeployed().topic:
            log = xchange_create.events.TokenDeployed().process_log(log_data)
            await format_token_alert(log, chain)
            token_deployed = True

        elif event_signature == ill_term.events.LoanOriginated().topic:
            log = ill_term.events.LoanOriginated().process_log(log_data)
            await format_loan_alert(log, chain, is_completed=False)

        elif event_signature == ill_term.events.LoanComplete().topic:
            tx = await chain_info.w3.eth.get_transaction(
                log_data["transactionHash"]
            )
            input_sig = tx["input"][:10]
            was_liquidated = input_sig == "0x415f1240"

            log = ill_term.events.LoanComplete().process_log(log_data)
            await format_loan_alert(
                log,
                chain,
                is_completed=True,
                was_liquidated=was_liquidated,
            )

        elif event_signature == factory.events.PairCreated().topic:
            if not token_deployed:
                log = factory.events.PairCreated().process_log(log_data)
                await format_pair_alert(log, chain)

        elif (
            event_signature
            == time_lock.events.GlobalUnlockTimestampSet().topic
        ):
            log = time_lock.events.GlobalUnlockTimestampSet().process_log(
                log_data
            )
            await format_time_lock_alert(log, chain, is_global=True)

        elif (
            event_signature == time_lock.events.TokenUnlockTimestampSet().topic
        ):
            log = time_lock.events.TokenUnlockTimestampSet().process_log(
                log_data
            )
            await format_time_lock_alert(log, chain)

    except Exception as e:
        await error(f"Error processing log: {e}")


async def initialize_alerts(chain):
    print(f"🔄 Initializing {chain.upper()} alerts...")
    retry_delay = 10
    first_connect = True
    retry_count = 0
    MAX_RETRIES = 6

    while True:
        ws = None
        try:
            w3 = chains.MAINNETS[chain].w3_ws
            (
                factory,
                ill_term,
                time_lock,
                xchange_create,
            ) = await initialize_contracts(w3, chain)

            ws_url = chains.MAINNETS[chain].ws_rpc_url
            async with websockets.connect(ws_url) as ws:
                sub_payload = {
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": [
                        "logs",
                        {
                            "address": [
                                factory.address,
                                ill_term.address,
                                time_lock.address,
                                xchange_create.address,
                            ]
                        },
                    ],
                }

                await ws.send(json.dumps(sub_payload))
                response = await ws.recv()
                sub_id = json.loads(response)["result"]

                if first_connect:
                    print(f"✅ {chain.upper()} alerts initialized")
                    first_connect = False

                retry_count = 0

                while True:
                    try:
                        message = await ws.recv()
                        data = json.loads(message)

                        if (
                            "method" in data
                            and data["method"] == "eth_subscription"
                        ):
                            if data["params"]["subscription"] == sub_id:
                                await handle_log(
                                    data["params"]["result"],
                                    chain,
                                    (
                                        factory,
                                        ill_term,
                                        time_lock,
                                        xchange_create,
                                    ),
                                )

                    except websockets.ConnectionClosed:
                        break

        except asyncio.CancelledError:
            if ws and not ws.closed:
                if sub_id:
                    unsub_payload = {
                        "id": 1,
                        "method": "eth_unsubscribe",
                        "params": [sub_id],
                    }
                    await ws.send(json.dumps(unsub_payload))
                    await ws.recv()
                await ws.close()
            raise

        except Exception as e:
            retry_count += 1
            if retry_count >= MAX_RETRIES:
                await error(
                    f"{chain.upper()} max retries ({MAX_RETRIES}) reached, stopping alerts"
                )
                break

            await error(
                f"{chain.upper()} connection error: {e} (attempt {retry_count}/{MAX_RETRIES})"
            )
            if ws and not ws.closed:
                if sub_id:
                    try:
                        unsub_payload = {
                            "id": 1,
                            "method": "eth_unsubscribe",
                            "params": [sub_id],
                        }
                        await ws.send(json.dumps(unsub_payload))
                        await ws.recv()
                    except Exception:
                        pass
                await ws.close()

            await asyncio.sleep(retry_delay)


async def initialize_contracts(w3, chain):
    factory = w3.eth.contract(
        address=addresses.factory(chain),
        abi=abis.read("factory"),
    )

    ill_term = w3.eth.contract(
        address=addresses.ill_addresses(chain)[LIVE_LOAN],
        abi=abis.read(f"ill{LIVE_LOAN}"),
    )

    xchange_create = w3.eth.contract(
        address=addresses.xchange_create(chain), abi=abis.read("xchangecreate")
    )

    time_lock = w3.eth.contract(
        address=addresses.token_time_lock(chain), abi=abis.read("timelock")
    )

    return factory, ill_term, time_lock, xchange_create


async def format_loan_alert(
    log, chain, is_completed=False, was_liquidated=False
):
    chain_info, _ = chains.get_info(chain)

    loan_id = log["args"]["loanID"]
    ill_address = addresses.ill_addresses(chain)[LIVE_LOAN]

    ill_contract = chain_info.w3.eth.contract(
        address=ill_address, abi=abis.read(f"ill{LIVE_LOAN}")
    )

    loan_amount = (
        await ill_contract.functions.loanAmount(int(loan_id)).call() / 10**18
    )

    pool_contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(
            addresses.lending_pool(chain)
        ),
        abi=abis.read("lendingpool"),
    )

    token_address = await pool_contract.functions.loanToken(
        int(loan_id)
    ).call()
    pair_address = await pool_contract.functions.loanPair(int(loan_id)).call()

    token_info = dextools.get_token_name(token_address, chain)

    if is_completed:
        title = "Loan Liquidated" if was_liquidated else "Loan Completed"
    else:
        title = "Loan Originated"

    schedule1 = await ill_contract.functions.getPremiumPaymentSchedule(
        int(loan_id)
    ).call()
    schedule2 = await ill_contract.functions.getPrincipalPaymentSchedule(
        int(loan_id)
    ).call()
    schedule = tools.format_schedule(
        schedule1,
        schedule2,
        chain_info.native.upper(),
        isComplete=is_completed,
    )

    message = (
        f"{token_info['name']} ({token_info['symbol']})\n\n{loan_amount} {chain_info.native.upper()}\n\nLoan ID: {loan_id}\n\n"
        f"Payment Schedule (UTC):\n{schedule}"
    )

    image_buffer = await create_image(
        defined.get_token_image(token_address, chain),
        title,
        message,
        chain_info,
    )

    caption = f"*{title} ({chain_info.name.upper()})*\n\n{message}\n\n"

    token_by_id = await tools.get_loan_token_id(loan_id, chain)
    ill_number = tools.get_ill_number(ill_address, chain)

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
                    text="Buy",
                    url=urls.xchange_buy_link(chain_info.id, token_address),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Chart",
                    url=urls.dex_tools_link(chain_info.dext, pair_address),
                )
            ],
        ]
    )

    await send_alert(image_buffer, caption, buttons, application)


async def format_pair_alert(log, chain):
    chain_info, _ = chains.get_info(chain)
    paired_token = addresses.weth(chain)

    title = "New Pair Created"

    token_0_info = dextools.get_token_name(log["args"]["token0"], chain)
    token_0_name = token_0_info["name"]
    token_0_symbol = token_0_info["symbol"]

    token_1_info = dextools.get_token_name(log["args"]["token1"], chain)
    token_1_name = token_1_info["name"]
    token_1_symbol = token_1_info["symbol"]

    if log["args"]["token0"] == paired_token:
        token_address = log["args"]["token1"]
        token_name = token_1_name
    else:
        token_address = log["args"]["token0"]
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

    message = f"{token_name} ({token_0_symbol}/{token_1_symbol})\n\n{status}"

    image_buffer = await create_image(
        defined.get_token_image(token_address, chain),
        title,
        message,
        chain_info,
    )

    caption = (
        f"*{title} ({chain_info.name.upper()})*\n\n"
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
                        chain_info.dext, log["args"]["pair"]
                    ),
                )
            ],
        ]
    )

    await send_alert(image_buffer, caption, buttons, application)


async def format_token_alert(log, chain):
    chain_info, _ = chains.get_info(chain)
    title = "New Token Deployed"

    args = log["args"]
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

    message = f"{token_name} ({token_symbol})\n\nSupply: {supply:,.0f}\nTax: {buy_tax}/{sell_tax}"

    image_buffer = await create_image(
        token_uri,
        title,
        message,
        chain_info,
    )

    caption = (
        f"*{title} ({chain_info.name.upper()})*\n\n"
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

    await send_alert(image_buffer, caption, buttons, application)


async def format_time_lock_alert(log, chain, is_global=False):
    chain_info, _ = chains.get_info(chain)

    if is_global:
        title = "Global Unlock Time Set"
        unlock_timestamp = log["args"]["unlockTimestamp"]
        unlock_date = datetime.fromtimestamp(unlock_timestamp).strftime(
            "%Y-%m-%d %H:%M"
        )
        when = tools.get_time_difference(unlock_timestamp)

        message = f"Global Unlock Time Set\n\n{unlock_date}\n{when}"

        image_buffer = await create_image(
            chain_info.logo,
            title,
            message,
            chain_info,
        )

        caption = f"*{title} ({chain_info.name.upper()})*\n\n{message}"

    else:
        title = "Token Unlock Time Set"
        token_address = chain_info.w3.to_checksum_address(
            log["args"]["tokenAddress"]
        )
        unlock_timestamp = log["args"]["unlockTimestamp"]
        unlock_date = datetime.fromtimestamp(unlock_timestamp).strftime(
            "%Y-%m-%d %H:%M"
        )
        when = tools.get_time_difference(unlock_timestamp)

        for token_key, token_data in tokens.get_tokens().items():
            if token_data[chain].ca.lower() == token_address.lower():
                token_name = token_data[chain].name
                token_image = token_data[chain].logo
                break

        message = f"{token_name}\n\n{unlock_date}\n{when}"

        image_buffer = await create_image(
            token_image,
            title,
            message,
            chain_info,
        )

        caption = f"*{title} ({chain_info.name.upper()})*\n\n{message}\n\n"

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Time Lock Contract",
                    url=chain_info.scan_address
                    + addresses.token_time_lock(chain),
                )
            ],
        ]
    )

    await send_alert(image_buffer, caption, buttons, application)


async def send_alert(image_buffer, caption, buttons, application):
    try:
        for channel, config in urls.TG_ALERTS_CHANNELS.items():
            for thread_id, link in config:
                image_buffer.seek(0)
                send_params = {
                    "chat_id": channel,
                    "photo": image_buffer,
                    "caption": f"{caption}{tools.escape_markdown(link)}",
                    "parse_mode": "Markdown",
                    "reply_markup": buttons,
                }

                if thread_id is not None:
                    send_params["message_thread_id"] = thread_id

                try:
                    await application.bot.send_photo(**send_params)
                except Exception as e:
                    await error(f"Error sending to channel ({channel}): {e}")

    finally:
        image_buffer.close()


async def main():
    tasks = [
        asyncio.create_task(initialize_alerts(chain))
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
    application.add_error_handler(lambda _, context: error(context))
    asyncio.run(main())
