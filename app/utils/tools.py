from telegram import Update

import aiohttp
import math
import os
import random
import sentry_sdk
import socket
from datetime import datetime

from bot import commands
from constants.bot import urls
from constants.protocol import abis, addresses, chains, splitters, tokens
from services import get_etherscan

etherscan = get_etherscan()

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=1.0)


def adjust_loan_count(amount, chain):
    latest_loan = amount
    adjusted_amount = max(0, amount - 20) if chain != "eth" else amount
    return adjusted_amount, latest_loan


async def error_handler(
    update_or_msg: Update | str, context=None, alerts=False
):
    if isinstance(update_or_msg, str) and "httpx.ReadError" in update_or_msg:
        return

    if update_or_msg is None:
        return

    if isinstance(update_or_msg, Update):
        if update_or_msg.edited_message is not None:
            return

    if alerts:
        error_text = f"Alerts Error: {update_or_msg}"
    else:
        error = context.error if hasattr(context, "error") else str(context)
        if isinstance(update_or_msg, Update):
            message = update_or_msg.message
            if message is not None and message.text is not None:
                error_text = f"{message.text} caused error: {error}"
                await message.reply_text(
                    "Uh oh! You trusted code and it failed you! The error has been logged."
                )
            else:
                error_text = f"Error: {error}"
        else:
            error_text = f"Error: {error}"

    if not is_local():
        sentry_sdk.capture_exception(Exception(error_text))
    else:
        print(error_text)


def escape_markdown(text):
    characters_to_escape = ["*", "_", "`"]
    for char in characters_to_escape:
        text = text.replace(char, "\\" + char)
    return text


def format_millions(value):
    if value is None or value == 0:
        return None
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.0f}"


def format_schedule(schedule1, schedule2, native_token, isComplete):
    current_datetime = datetime.now()
    next_payment_datetime = None
    next_payment_value = None

    all_dates = sorted(set(schedule1[0] + schedule2[0]))
    schedule = []

    for date in all_dates:
        value1 = next(
            (v for d, v in zip(schedule1[0], schedule1[1]) if d == date), 0
        )
        value2 = next(
            (v for d, v in zip(schedule2[0], schedule2[1]) if d == date), 0
        )

        total_value = value1 + value2

        formatted_date = datetime.fromtimestamp(date).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        formatted_value = total_value / 10**18
        sch = f"{formatted_date} - {formatted_value:.3f} {native_token}"
        schedule.append(sch)

        if datetime.fromtimestamp(date) > current_datetime:
            if (
                next_payment_datetime is None
                or datetime.fromtimestamp(date) < next_payment_datetime
            ):
                next_payment_datetime = datetime.fromtimestamp(date)
                next_payment_value = formatted_value

    if isComplete:
        schedule.append("\nLoan Complete")
    elif next_payment_datetime:
        time_until_next_payment_timestamp = next_payment_datetime.timestamp()
        time_remaining_str = get_time_difference(
            time_until_next_payment_timestamp
        )

        schedule.append(
            f"\nNext Payment Due:\n{next_payment_value} {native_token}\n{time_remaining_str}"
        )

    return "\n".join(schedule)


def format_seconds(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return (
        f"{minutes} minutes and {remaining_seconds:.0f} seconds"
        if minutes > 0
        else f"{remaining_seconds:.3f} seconds"
    )


async def generate_loan_terms(chain, loan_amount):
    chain_info, _ = await chains.get_info(chain)

    loan_in_wei = chain_info.w3.to_wei(loan_amount, "ether")

    loan_contract_address = addresses.ill_addresses(chain).get(
        addresses.LIVE_LOAN
    )

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(loan_contract_address),
        abi=abis.read(f"ill{addresses.LIVE_LOAN}"),
    )

    quote = await contract.functions.getQuote(loan_in_wei).call()
    origination_fee = quote[1]

    lending_pool = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(
            addresses.lending_pool(chain)
        ),
        abi=abis.read("lendingpool"),
    )

    liquidation_fee = (
        await lending_pool.functions.liquidationReward().call() / 10**18
    )

    min_loan = await contract.functions.minimumLoanAmount().call() / 10**18
    max_loan = await contract.functions.maximumLoanAmount().call() / 10**18
    min_loan_duration = math.floor(
        await contract.functions.minimumLoanLengthSeconds().call() / 84600
    )
    max_loan_duration = math.floor(
        await contract.functions.maximumLoanLengthSeconds().call() / 84600
    )

    liquidation_deposit = (
        await lending_pool.functions.liquidationReward().call() / 10**18
    )

    total_fee = origination_fee + liquidation_deposit

    text = (
        f"Borrow between {min_loan} and {max_loan} {chain_info.native.upper()} between {min_loan_duration} and {max_loan_duration} days"
        f" at a cost of {chain_info.w3.from_wei(origination_fee, 'ether')} {chain_info.native.upper()} + {liquidation_fee} {chain_info.native.upper()} deposit"
    )
    return total_fee, text


def get_ill_number(term, chain):
    for ill_number, contract_address in addresses.ill_addresses(chain).items():
        if term.lower() == contract_address.lower():
            return ill_number
    return None


async def get_last_action(address, chain):
    chain_info, _ = await chains.get_info(chain)
    chain_native = chain_info.native
    tx = await etherscan.get_internal_tx(address, chain)

    word = "txn"
    filter = []
    tokens_data = await tokens.get_tokens()

    if any(
        address == token_info.hub
        for token_dict in tokens_data.values()
        for token_info in token_dict.values()
        if token_info.hub
    ):
        word = "buy back"
        filter = [
            d
            for d in tx["result"]
            if d["to"].lower() == addresses.router(chain).lower()
        ]

    elif address in addresses.splitters(chain).values():
        word = "push"
        splitter = next(
            key
            for key, value in addresses.splitters(chain).items()
            if value == address
        )
        settings = await splitters.get_push_settings(chain, splitter)
        recipient = settings["recipient"]
        filter = [
            d for d in tx["result"] if d["to"].lower() == recipient.lower()
        ]
    if not filter:
        return f"Last {word}: None found"

    last_txn = filter[0]
    value = int(last_txn["value"]) / 10**18
    native_price = await etherscan.get_native_price(chain_native)
    dollar = float(value) * float(native_price)
    timestamp = get_time_difference(int(last_txn["timeStamp"]))

    return f"Last {word}:\n{value:.3f} {chain_native.upper()} (${dollar:,.0f})\n{timestamp}"


async def get_loan_token_id(loan_id, chain):
    chain_info, _ = await chains.get_info(chain)

    pool_contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(
            addresses.lending_pool(chain)
        ),
        abi=abis.read("lendingpool"),
    )

    term = await pool_contract.functions.loanTermLookup(int(loan_id)).call()
    term_contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(term),
        abi=abis.read(f"ill{addresses.LIVE_LOAN}"),
    )

    index = 0
    while True:
        try:
            token_id = await term_contract.functions.tokenByIndex(index).call()
            if token_id == int(loan_id):
                return index
            index += 1
        except Exception:
            return 0


def get_random_pioneer():
    number = f"{random.randint(1, 4473)}".zfill(4)
    return f"{urls.PIONEERS}{number}.png"


def get_time_difference(timestamp):
    current_time = datetime.now()
    timestamp_time = datetime.fromtimestamp(int(timestamp))

    time_difference = current_time - timestamp_time
    is_future = time_difference.total_seconds() < 0
    time_difference = abs(time_difference)

    days = time_difference.days
    seconds = time_difference.seconds

    months = days // 30
    remaining_days = days % 30
    weeks = remaining_days // 7
    days = remaining_days % 7
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60

    suffix = "ago" if not is_future else "from now"

    if months > 0:
        return f"{months} month{'s' if months > 1 else ''} and {remaining_days} day{'s' if remaining_days > 1 else ''} {suffix}"
    elif weeks > 0:
        return f"{weeks} week{'s' if weeks > 1 else ''} and {days} day{'s' if days > 1 else ''} {suffix}"
    elif days > 0 or hours > 0:
        return f"{days} day{'s' if days > 1 else ''} and {hours} hour{'s' if hours > 1 else ''} {suffix}"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} {suffix}"
    else:
        return "Just now" if not is_future else "In a moment"


def is_admin(user_id):
    if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
        return True


def is_local():
    ip = socket.gethostbyname(socket.gethostname())
    return (
        ip.startswith("127.") or ip.startswith("192.168.") or ip == "localhost"
    )


async def update_bot_commands():
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/setMyCommands"

    general_commands = [
        {
            "command": cmd[0] if isinstance(cmd, list) else cmd,
            "description": desc,
        }
        for cmd, _, desc in commands.GENERAL_HANDLERS
    ]

    admin_commands = [
        {"command": cmd, "description": desc}
        for cmd, _, desc in commands.ADMIN_HANDLERS
    ]

    all_commands = general_commands + admin_commands

    results = []

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={"commands": general_commands, "scope": {"type": "default"}},
        ) as response:
            results.append(
                "✅ General commands updated"
                if response.status == 200
                else f"⚠️ Failed to update commands: {await response.text()}"
            )

        async with session.post(
            url,
            json={
                "commands": all_commands,
                "scope": {
                    "type": "chat",
                    "chat_id": int(os.getenv("TELEGRAM_ADMIN_ID")),
                },
            },
        ) as response:
            results.append(
                "✅ Admin commands updated"
                if response.status == 200
                else f"⚠️ Failed to update Admin commands: {await response.text()}"
            )

    return "\n".join(results)
