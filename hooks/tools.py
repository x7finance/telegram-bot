import random, requests, socket
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


def format_schedule(schedule1, schedule2, native_token):
    current_datetime = datetime.now()
    next_payment_datetime = None
    next_payment_value = None

    def format_date(date):
        return datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")

    def calculate_time_remaining_str(time_remaining):
        days, seconds = divmod(time_remaining.total_seconds(), 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes"

    all_dates = sorted(set(schedule1[0] + schedule2[0]))

    schedule_list = []

    for date in all_dates:
        value1 = next((v for d, v in zip(schedule1[0], schedule1[1]) if d == date), 0)
        value2 = next((v for d, v in zip(schedule2[0], schedule2[1]) if d == date), 0)

        total_value = value1 + value2

        formatted_date = format_date(date)
        formatted_value = total_value / 10**18
        sch = f"{formatted_date} - {formatted_value:.3f} {native_token}"
        schedule_list.append(sch)

        if datetime.fromtimestamp(date) > current_datetime:
            if next_payment_datetime is None or datetime.fromtimestamp(date) < next_payment_datetime:
                next_payment_datetime = datetime.fromtimestamp(date)
                next_payment_value = formatted_value

    if next_payment_datetime:
        time_until_next_payment = next_payment_datetime - current_datetime
        time_remaining_str = calculate_time_remaining_str(time_until_next_payment)

        schedule_list.append(f"\nNext Payment Due:\n{next_payment_value} {native_token}\n{time_remaining_str}")

    return "\n".join(schedule_list)


def get_ill_number(term):
    for chain, addresses in ca.ILL_ADDRESSES.items():
        for ill_number, contract_address in addresses.items():
            if term.lower() == contract_address.lower():
                return ill_number


def get_last_buyback(hub_address, chain):
    chain_native = chains.active_chains()[chain].native
    hub = etherscan.get_internal_tx(hub_address, chain)
    hub_filter = [d for d in hub["result"] if d["from"] in f"{hub_address}".lower()]
    value = round(int(hub_filter[0]["value"]) / 10**18, 3)
    dollar = float(value) * float(etherscan.get_native_price(chain_native))
    time = datetime.fromtimestamp(int(hub_filter[0]["timeStamp"]))
    timestamp =int(hub_filter[0]["timeStamp"])
    return value, dollar, time, timestamp


def get_random_pioneer():
    number = f"{random.randint(1, 12)}".zfill(4)
    return f"{urls.PIONEERS}{number}.png"


def get_scan(token: str, chain: str) -> dict:
    chain_info = chains.active_chains()[chain]
    url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_info.id}?contract_addresses={token}"
    response = requests.get(url)
    return response.json()["result"]


def get_time_difference(timestamp):
    timestamp_int = int(timestamp)
    current_time = datetime.now()
    timestamp_time = datetime.fromtimestamp(timestamp_int)

    time_difference = current_time - timestamp_time
    is_future = time_difference.total_seconds() < 0
    time_difference = abs(time_difference)

    days = time_difference.days
    seconds = time_difference.seconds

    months = days // 30
    weeks = (days % 30) // 7
    days = days % 7
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60

    suffix = "ago" if not is_future else "from now"

    if months > 0:
        return f"{months} month{'s' if months > 1 else ''} {suffix}"
    elif weeks > 0:
        return f"{weeks} week{'s' if weeks > 1 else ''} {suffix}"
    elif days > 0:
        return f"{days} day{'s' if days > 1 else ''} {suffix}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} {suffix}"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} {suffix}"
    else:
        return "just now" if not is_future else "in a moment"


def is_eth(address):
    if address.startswith("0x") and len(address) == 42:
        return True
    else:
        return False
    

def is_local():
    ip = socket.gethostbyname(socket.gethostname())
    return ip.startswith("127.") or ip.startswith("192.168.") or ip == "localhost"