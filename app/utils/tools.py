import os
import random
import requests
import socket
from datetime import datetime

from constants.bot import urls
from constants.protocol import abis, addresses, chains, splitters, tokens
from bot.commands import admin, general
from services import get_etherscan

etherscan = get_etherscan()


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


def format_seconds(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return (
        f"{minutes} minutes and {remaining_seconds:.0f} seconds"
        if minutes > 0
        else f"{remaining_seconds:.3f} seconds"
    )


def get_event_topic(contract, event_name, chain):
    chain_info, _ = chains.get_info(chain)
    abi = abis.read(contract)
    for item in abi:
        if item.get("type") == "event" and item["name"] == event_name:
            event_inputs = ",".join([inp["type"] for inp in item["inputs"]])
            event_signature = f"{event_name}({event_inputs})"
            return "0x" + chain_info.w3.keccak(text=event_signature).hex()
    return None


def get_ill_number(term: str) -> str | None:
    for chain in chains.get_active_chains():
        for ill_number, contract_address in addresses.ill_addresses(
            chain
        ).items():
            if term.lower() == contract_address.lower():
                return ill_number

    return None


async def get_last_action(address, chain):
    chain_info, _ = chains.get_info(chain)
    chain_native = chain_info.native
    tx = etherscan.get_internal_tx(address, chain)

    word = "txn"
    filter = []
    tokens_data = tokens.get_tokens()

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
    dollar = float(value) * float(etherscan.get_native_price(chain_native))
    timestamp = get_time_difference(int(last_txn["timeStamp"]))

    return f"Last {word}:\n{value:.3f} {chain_native.upper()} (${dollar:,.0f})\n{timestamp}"


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


def update_bot_commands():
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/setMyCommands"

    general_commands = [
        {
            "command": cmd[0] if isinstance(cmd, list) else cmd,
            "description": desc,
        }
        for cmd, _, desc in general.HANDLERS
    ]

    admin_commands = [
        {"command": cmd, "description": desc}
        for cmd, _, desc in admin.HANDLERS
    ]

    all_commands = general_commands + admin_commands

    results = []

    response = requests.post(
        url, json={"commands": general_commands, "scope": {"type": "default"}}
    )

    results.append(
        "✅ General commands updated"
        if response.status_code == 200
        else f"⚠️ Failed to update commands: {response.text}"
    )

    response = requests.post(
        url,
        json={
            "commands": all_commands,
            "scope": {
                "type": "chat",
                "chat_id": int(os.getenv("TELEGRAM_ADMIN_ID")),
            },
        },
    )

    results.append(
        "✅ Admin commands updated"
        if response.status_code == 200
        else f"⚠️ Failed to update Admin commands: {response.text}"
    )

    return "\n".join(results)
