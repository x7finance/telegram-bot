from eth_utils import is_checksum_address, to_checksum_address
import random, re, socket
from datetime import datetime

from constants import ca, chains, urls
from hooks import api

etherscan = api.Etherscan()


def convert_datetime(input_value):
    try:
        if isinstance(input_value, str):
            datetime_obj = datetime.strptime(input_value, '%Y-%m-%d %H:%M')
            return datetime_obj.timestamp()
        elif isinstance(input_value, (int, float)):
            datetime_obj = datetime.fromtimestamp(input_value)
            return datetime_obj.strftime('%Y-%m-%d %H:%M')
        else:
            return "Invalid input type. Provide a datetime string or a timestamp."
    except ValueError:
        return "Invalid input format. Ensure datetime strings use 'YYYY-MM-DD HH:MM'."


def escape_markdown(text):
    characters_to_escape = ['*', '_', '`']
    for char in characters_to_escape:
        text = text.replace(char, '\\' + char)
    return text


def format_schedule(schedule1, schedule2, native_token, isComplete):
    current_datetime = datetime.now()
    next_payment_datetime = None
    next_payment_value = None

    all_dates = sorted(set(schedule1[0] + schedule2[0]))
    schedule = []

    for date in all_dates:
        value1 = next((v for d, v in zip(schedule1[0], schedule1[1]) if d == date), 0)
        value2 = next((v for d, v in zip(schedule2[0], schedule2[1]) if d == date), 0)

        total_value = value1 + value2

        formatted_date = datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")
        formatted_value = total_value / 10**18
        sch = f"{formatted_date} - {formatted_value:.3f} {native_token}"
        schedule.append(sch)

        if datetime.fromtimestamp(date) > current_datetime:
            if next_payment_datetime is None or datetime.fromtimestamp(date) < next_payment_datetime:
                next_payment_datetime = datetime.fromtimestamp(date)
                next_payment_value = formatted_value

    if isComplete:
        schedule.append("\nLoan Complete")
    elif next_payment_datetime:
        time_until_next_payment_timestamp = next_payment_datetime.timestamp()
        time_remaining_str = get_time_difference(time_until_next_payment_timestamp)

        schedule.append(f"\nNext Payment Due:\n{next_payment_value} {native_token}\n{time_remaining_str}")

    return "\n".join(schedule)


def get_ill_number(term):
    for chain, addresses in ca.ILL_ADDRESSES.items():
        for ill_number, contract_address in addresses.items():
            if term.lower() == contract_address.lower():
                return ill_number


def get_last_buyback(hub_address, chain):
    chain_native = chains.active_chains()[chain].native
    hub = etherscan.get_internal_tx(hub_address, chain)
    hub_filter = [d for d in hub["result"] if d["to"].lower() == ca.ROUTER(chain).lower()]
    last_txn = hub_filter[0]
    value = int(last_txn["value"]) / 10**18
    dollar = float(value) * float(etherscan.get_native_price(chain_native))
    timestamp = int(last_txn["timeStamp"])
    
    return value, dollar, timestamp


def get_random_pioneer():
    number = f"{random.randint(1, 12)}".zfill(4)
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
        month_part = f"{months} month{'s' if months > 1 else ''}"
        day_part = f"{remaining_days} day{'s' if remaining_days > 1 else ''}" if remaining_days > 0 else ""
        return f"{month_part}{' and ' if months > 0 and remaining_days > 0 else ''}{day_part} {suffix}"
    elif weeks > 0:
        week_part = f"{weeks} week{'s' if weeks > 1 else ''}"
        day_part = f"{days} day{'s' if days > 1 else ''}" if days > 0 else ""
        return f"{week_part}{' and ' if weeks > 0 and days > 0 else ''}{day_part} {suffix}"
    elif days > 0 or hours > 0:
        day_part = f"{days} day{'s' if days > 1 else ''}" if days > 0 else ""
        hour_part = f"{hours} hour{'s' if hours > 1 else ''}" if hours > 0 else ""
        return f"{day_part}{' and ' if days > 0 and hours > 0 else ''}{hour_part} {suffix}"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} {suffix}"
    else:
        return "just now" if not is_future else "in a moment"


def is_eth(address):
    if not address.startswith("0x") or len(address) != 42:
        return False

    return bool(re.match(r"^0x[a-f0-9]{40}$", address))


def is_local():
    ip = socket.gethostbyname(socket.gethostname())
    return ip.startswith("127.") or ip.startswith("192.168.") or ip == "localhost"